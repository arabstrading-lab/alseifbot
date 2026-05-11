"""
ALSEIF CHART - Trading Bot
بوت تيليغرام للاشتراك في قنوات التداول
"""

import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config.settings import BOT_TOKEN
from handlers.start import start_handler
from handlers.plans import plans_handler
from handlers.payment import payment_callback_handler
from handlers.broker import broker_handler
from handlers.admin import admin_handler
from handlers.status import status_handler
from database.db import init_db

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    init_db()
    logger.info("✅ قاعدة البيانات جاهزة")

    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("status", status_handler))
    app.add_handler(CommandHandler("admin", admin_handler))

    # Callback queries (inline buttons)
    app.add_handler(CallbackQueryHandler(plans_handler, pattern="^plan_"))
    app.add_handler(CallbackQueryHandler(broker_handler, pattern="^broker_"))
    app.add_handler(CallbackQueryHandler(payment_callback_handler, pattern="^pay_"))
    app.add_handler(CallbackQueryHandler(admin_handler, pattern="^admin_"))

    logger.info("🚀 البوت شغّال - ALSEIF CHART")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
