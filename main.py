"""Application entrypoint: wire up handlers and run the bot."""
from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import settings
from .database import init_db
from .handlers import admin, common, entry
from .handlers.wizard import build_wizard_handler
from .scheduler import register_jobs
from .utils.logger import get_logger, setup_logging

logger = get_logger(__name__)


async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception while processing update", exc_info=context.error)


def build_application() -> Application:
    settings.validate()
    application = ApplicationBuilder().token(settings.bot_token).build()

    # --- Conversation wizard (must be added before generic text handlers) ---
    application.add_handler(build_wizard_handler())

    # --- Commands ---
    application.add_handler(CommandHandler("start", common.start))
    application.add_handler(CommandHandler("help", common.help_command))
    application.add_handler(CommandHandler("giveaways", entry.list_giveaways_cmd))
    application.add_handler(CommandHandler("myentries", entry.my_entries_cmd))
    application.add_handler(CommandHandler("admin", admin.admin_command))
    application.add_handler(CommandHandler("addadmin", admin.add_admin_cmd))
    application.add_handler(CommandHandler("removeadmin", admin.remove_admin_cmd))
    application.add_handler(CommandHandler("blacklist", admin.blacklist_cmd))
    application.add_handler(CommandHandler("whitelist", admin.whitelist_cmd))
    application.add_handler(CommandHandler("editgiveaway", admin.edit_giveaway_cmd))
    application.add_handler(CommandHandler("addwinner", admin.add_winner_cmd))
    application.add_handler(CommandHandler("alerts", admin.alerts_cmd))

    # --- Navigation callbacks ---
    application.add_handler(CallbackQueryHandler(common.show_home, pattern=r"^nav:home$"))
    application.add_handler(CallbackQueryHandler(common.show_help_cb, pattern=r"^nav:help$"))
    application.add_handler(CallbackQueryHandler(common.show_language_menu, pattern=r"^nav:lang$"))
    application.add_handler(CallbackQueryHandler(common.set_language, pattern=r"^lang:set:"))
    application.add_handler(CallbackQueryHandler(entry.browse_cb, pattern=r"^nav:browse$"))
    application.add_handler(CallbackQueryHandler(entry.my_entries_cb, pattern=r"^nav:myentries$"))

    # --- Giveaway (user) callbacks ---
    application.add_handler(CallbackQueryHandler(entry.view_cb, pattern=r"^gw:view:"))
    application.add_handler(CallbackQueryHandler(entry.enter_cb, pattern=r"^gw:enter:"))
    application.add_handler(CallbackQueryHandler(entry.verify_cb, pattern=r"^gw:verify:"))
    application.add_handler(CallbackQueryHandler(entry.status_cb, pattern=r"^gw:status:"))
    application.add_handler(CallbackQueryHandler(entry.referral_cb, pattern=r"^gw:ref:"))

    # --- Admin callbacks ---
    application.add_handler(CallbackQueryHandler(admin.admin_panel_cb, pattern=r"^admin:panel$"))
    application.add_handler(CallbackQueryHandler(admin.manage_cb, pattern=r"^admin:manage$"))
    application.add_handler(CallbackQueryHandler(admin.stats_cb, pattern=r"^admin:stats$"))
    application.add_handler(CallbackQueryHandler(admin.export_cb, pattern=r"^admin:export$"))
    application.add_handler(CallbackQueryHandler(admin.admins_cb, pattern=r"^admin:admins$"))
    application.add_handler(CallbackQueryHandler(admin.manage_view_cb, pattern=r"^adm:view:"))
    application.add_handler(
        CallbackQueryHandler(
            admin.manage_action_cb,
            pattern=r"^adm:(start|pause|end|cancel|draw|gstats|gexport|edit):",
        )
    )

    # --- Quiz free-text answers (lowest priority text handler) ---
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, entry.quiz_answer_handler)
    )

    application.add_error_handler(_error_handler)

    register_jobs(application)
    return application


def main() -> None:
    setup_logging()
    logger.info("Starting Telegram Giveaway Bot v1.0.0")
    init_db()
    application = build_application()
    logger.info("Bot is polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
