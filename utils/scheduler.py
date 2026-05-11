"""
المهام التلقائية - تذكيرات + إلغاء الاشتراكات المنتهية
شغّل هذا الملف كـ cron job يومي أو مع APScheduler
"""

import asyncio
import logging
from telegram import Bot
from config.settings import BOT_TOKEN, REMINDER_DAYS_BEFORE
from database.db import (
    get_expiring_subscriptions, get_expired_subscriptions,
    deactivate_subscription, mark_reminder_sent
)

logger = logging.getLogger(__name__)


async def send_reminders(bot: Bot):
    """إرسال تذكيرات قبل 3 أيام من الانتهاء"""
    subs = get_expiring_subscriptions(days=REMINDER_DAYS_BEFORE)
    count = 0

    for sub in subs:
        try:
            await bot.send_message(
                chat_id=sub["telegram_id"],
                text=(
                    f"⏰ *تذكير — اشتراكك ينتهي قريباً!*\n\n"
                    f"📦 الباقة: *{sub['plan'].upper()}*\n"
                    f"📅 ينتهي: *{sub['end_date'][:10]}*\n\n"
                    f"جدد اشتراكك الآن لتبقى متصلاً بالسوق 📈\n\n"
                    f"اضغط /start للتجديد"
                ),
                parse_mode="Markdown"
            )
            mark_reminder_sent(sub["telegram_id"], sub["id"])
            count += 1
            await asyncio.sleep(0.5)  # تجنب rate limit
        except Exception as e:
            logger.error(f"Reminder failed for {sub['telegram_id']}: {e}")

    logger.info(f"✅ أُرسل {count} تذكير")


async def remove_expired(bot: Bot):
    """إزالة الاشتراكات المنتهية وإشعار المستخدمين"""
    expired = get_expired_subscriptions()
    count = 0

    for sub in expired:
        deactivate_subscription(sub["id"])
        try:
            await bot.send_message(
                chat_id=sub["telegram_id"],
                text=(
                    "⏰ *انتهى اشتراكك في ALSEIF CHART*\n\n"
                    "لتجديد اشتراكك:\n"
                    "👉 اضغط /start\n\n"
                    "نتمنى نشوفك مجدداً! 🏆"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        count += 1
        await asyncio.sleep(0.3)

    logger.info(f"✅ تم إلغاء {count} اشتراك منتهٍ")


async def run_daily_tasks():
    """شغّل كل المهام اليومية"""
    bot = Bot(token=BOT_TOKEN)
    async with bot:
        logger.info("🔄 تشغيل المهام اليومية...")
        await send_reminders(bot)
        await remove_expired(bot)
        logger.info("✅ انتهت المهام اليومية")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_daily_tasks())
