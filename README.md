# 🎁 Telegram Giveaway Bot

A production-ready, feature-rich Telegram giveaway bot built with
**python-telegram-bot v21**, **PostgreSQL** and **SQLAlchemy 2.0**. It supports
40+ features across giveaway mechanics, verification, anti-cheat, analytics,
notifications and multi-language UX.

---

## ✨ Features

### Core giveaway mechanics
- **6 giveaway types**: `random` draw, `task`-based, `referral`-weighted, `FCFS`
  (first-come-first-served), `instant`-win, and `quiz`.
- **Scheduled giveaways** with automatic start/end via a background scheduler.
- **Multiple winners** and **prize tiers** (🥇 1st / 🥈 2nd / 🥉 3rd …).
- **Instant-win** giveaways with configurable win probability.
- **Recurring giveaways** that auto-clone on a fixed interval.

### Verification & entry
- **Channel/group membership** verification (bot must be admin of the channel).
- **Social follow** tasks (Twitter/X, Instagram, YouTube) — API-ready with an
  honor-mode fallback.
- **Referral system** with per-giveaway tracking and weighted draws.
- **Task completion** verification with per-task mandatory flags.
- **Quiz/question-based** entry.
- **Minimum account-age** gating (heuristic estimation from Telegram user id).
- **Entry limits** per user and **max participants** caps.

### Admin
- **Multi-admin** with roles: `super_admin`, `admin`, `moderator`.
- **Creation wizard** (guided conversation) + `/newgiveaway`.
- **Edit** active giveaways (`/editgiveaway`).
- **Pause / resume / force-end / cancel** controls.
- **Manual winner override** (`/addwinner`) + automated draws.
- **Blacklist / whitelist** users (global or per-giveaway).
- **Export** participant & winner data to CSV.

### Anti-cheat & security
- **Duplicate-account** heuristics.
- **Bot-account filtering**.
- **Suspicious-activity alerts** with an audit log (`/alerts`).
- **Rate limiting** (sliding window per user).
- **Entry validation** pipeline.

### Notifications & engagement
- **Auto-announcements** for start, milestones and end.
- **Winner notifications** (DM + public post).
- **Reminder system** (~1h before end).
- **Entry confirmation** messages.
- **Milestone** celebration posts.

### Analytics & reporting
- Participation statistics & engagement metrics.
- Winner history.
- **CSV exports** (participants, winners, aggregate reports).

### User experience
- **Multi-language** (English & Spanish included; easily extensible).
- **Custom entry buttons** & rich **inline keyboards**.
- **Entry-status** checking and **giveaway listing/search**.

---

## 🏗 Project structure

```
telegram_giveaway_bot/
├── bot/
│   ├── config.py               # env-driven settings
│   ├── main.py                 # entrypoint & handler wiring
│   ├── scheduler.py            # auto start/end, reminders, recurrence
│   ├── database/
│   │   ├── models.py           # SQLAlchemy ORM models
│   │   ├── enums.py            # shared enumerations
│   │   └── session.py          # engine & session management
│   ├── services/               # business logic
│   │   ├── giveaway_service.py
│   │   ├── verification_service.py
│   │   ├── winner_service.py
│   │   ├── anticheat_service.py
│   │   ├── analytics_service.py
│   │   ├── notification_service.py
│   │   ├── admin_service.py
│   │   └── user_service.py
│   ├── handlers/               # Telegram update handlers
│   │   ├── common.py           # /start, help, menus, language
│   │   ├── entry.py            # browse / enter / verify / status
│   │   ├── wizard.py           # giveaway creation conversation
│   │   └── admin.py            # admin panel & controls
│   ├── utils/                  # logger, i18n, keyboards, decorators
│   └── locales/                # en.json, es.json
├── migrations/                 # Alembic migrations
├── requirements.txt
├── alembic.ini
├── .env.example
├── run.py
└── README.md
```

---

## 🚀 Setup

### 1. Prerequisites
- Python 3.10+
- PostgreSQL 12+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### 2. Clone & install
```bash
cd telegram_giveaway_bot
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Create the database
```bash
sudo -u postgres psql -c "CREATE USER giveaway WITH PASSWORD 'giveaway';"
sudo -u postgres psql -c "CREATE DATABASE giveaway_bot OWNER giveaway;"
```

### 4. Configure environment
```bash
cp .env.example .env
```
Edit `.env` and set at least:
- `BOT_TOKEN` — from @BotFather
- `SUPER_ADMIN_IDS` — your numeric Telegram id (get it from [@userinfobot](https://t.me/userinfobot))
- `BOT_USERNAME` — your bot's username (used for referral links)
- `DATABASE_URL` — e.g. `postgresql+psycopg2://giveaway:giveaway@localhost:5432/giveaway_bot`

### 5. Run migrations
```bash
alembic upgrade head
```
> The app also calls `init_db()` on startup as a convenience, but Alembic is the
> source of truth for schema changes in production.

### 6. Start the bot
```bash
python run.py
# or
python -m bot.main
```

---

## 🎮 Usage

### For participants
| Command | Description |
|---------|-------------|
| `/start` | Main menu (accepts referral deep links: `?start=ref_<code>_<giveawayId>`) |
| `/giveaways` | List active giveaways |
| `/myentries` | View your entries and their status |
| `/help` | Help text |

Everything else is driven by inline buttons: browse → view → **Enter** →
complete tasks → **Verify Tasks**.

### For admins
| Command | Description |
|---------|-------------|
| `/admin` | Open the admin panel |
| `/newgiveaway` | Launch the creation wizard (or use the panel button) |
| `/editgiveaway <id> <field> <value>` | Edit `title`/`prize`/`description`/`winners`/`end` |
| `/addwinner <giveawayId> <telegramId> [position]` | Manual winner override |
| `/addadmin <telegramId> [admin\|moderator]` | Grant a role (super-admins only) |
| `/removeadmin <telegramId>` | Revoke admin (super-admins only) |
| `/blacklist <telegramId> [giveawayId]` | Block a user |
| `/whitelist <telegramId> [giveawayId]` | Allow-list a user |
| `/alerts` | View recent suspicious-activity alerts |

From the admin panel you can **start / pause / end / cancel / draw** a giveaway,
view **stats**, and **export** CSV data.

> **Public announcements:** set a giveaway's `announce_chat_id` (add the bot to
> your channel/group as admin) to enable auto start/milestone/end/winner posts.
> You can set it via `/editgiveaway` support or directly in the DB.

---

## 🌐 Adding a language
Drop a new `bot/locales/<code>.json` file mirroring `en.json`'s keys — it is
auto-discovered and appears in the language menu. Update the flag/name map in
`bot/utils/keyboards.py::language_menu` for a nicer label.

---

## 🔒 Notes on verification & anti-cheat
- **Channel membership** is verified through the Telegram Bot API; the bot must
  be an **administrator** of the target channel/group.
- **Social follows** (Twitter/Instagram/YouTube) cannot be reliably verified
  without each platform's API. They default to **honor mode** (marked complete
  when the user taps *Verify*). Wire real API checks in
  `services/verification_service.py::verify_task` when you have credentials.
- **Account age** is *estimated* from the numeric Telegram user id (ids grow
  roughly monotonically with signup time). Treat it as a heuristic, not proof.

---

## 🧪 Development

Run a quick import/build smoke test (SQLite, no Postgres needed):
```bash
DATABASE_URL="sqlite+pysqlite:///dev.db" BOT_TOKEN="x" SUPER_ADMIN_IDS="1" \
  python -c "from bot.main import build_application; build_application(); print('ok')"
```

Generate a new migration after changing models:
```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

Logs are written to console and `logs/bot.log` (rotating). Set `LOG_LEVEL=DEBUG`
in `.env` for verbose SQL/tracing.

---

## ⚙️ Configuration reference
See [`.env.example`](.env.example) for all supported variables (rate limits,
minimum account age, duplicate detection toggles, timezone, logging, etc.).

---

## 📄 License
MIT — use freely for your community. Contributions welcome.
