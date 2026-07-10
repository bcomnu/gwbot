"""Central configuration loaded from environment variables.

All runtime settings are read once at import time from a `.env` file
(if present) or the process environment. Access via the ``settings`` singleton.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

from dotenv import load_dotenv

# Load .env from project root (if it exists). Real env vars always win.
load_dotenv()


def _get_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(key: str, default: int) -> int:
    val = os.getenv(key)
    if val is None or val.strip() == "":
        return default
    try:
        return int(val)
    except ValueError:
        return default


def _get_id_list(key: str) -> List[int]:
    raw = os.getenv(key, "")
    ids: List[int] = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            ids.append(int(chunk))
        except ValueError:
            continue
    return ids


@dataclass
class Settings:
    """Immutable-ish configuration container."""

    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    bot_username: str = field(default_factory=lambda: os.getenv("BOT_USERNAME", ""))
    super_admin_ids: List[int] = field(default_factory=lambda: _get_id_list("SUPER_ADMIN_IDS"))

    database_url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://giveaway:giveaway@localhost:5432/giveaway_bot",
        )
    )

    default_language: str = field(default_factory=lambda: os.getenv("DEFAULT_LANGUAGE", "en"))
    timezone: str = field(default_factory=lambda: os.getenv("TIMEZONE", "UTC"))

    default_entry_limit_per_user: int = field(
        default_factory=lambda: _get_int("DEFAULT_ENTRY_LIMIT_PER_USER", 1)
    )
    rate_limit_per_minute: int = field(
        default_factory=lambda: _get_int("RATE_LIMIT_PER_MINUTE", 20)
    )
    min_account_age_days: int = field(
        default_factory=lambda: _get_int("MIN_ACCOUNT_AGE_DAYS", 0)
    )

    enable_duplicate_detection: bool = field(
        default_factory=lambda: _get_bool("ENABLE_DUPLICATE_DETECTION", True)
    )
    enable_bot_filtering: bool = field(
        default_factory=lambda: _get_bool("ENABLE_BOT_FILTERING", True)
    )

    twitter_bearer_token: str = field(
        default_factory=lambda: os.getenv("TWITTER_BEARER_TOKEN", "")
    )

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_file: str = field(default_factory=lambda: os.getenv("LOG_FILE", "logs/bot.log"))

    def validate(self) -> None:
        """Raise a helpful error if critical settings are missing."""
        missing = []
        if not self.bot_token:
            missing.append("BOT_TOKEN")
        if not self.database_url:
            missing.append("DATABASE_URL")
        if missing:
            raise RuntimeError(
                "Missing required configuration: "
                + ", ".join(missing)
                + ". Copy .env.example to .env and fill in the values."
            )


settings = Settings()
