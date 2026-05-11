"""
/status — حالة الاشتراك
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import get_active_subscription, upsert_user
from datetime import datetime


async def status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username or "", user.full_name or "")
    sub = get_active_subscription(user.id)

    if not sub:
        await update.message.reply_text(
            "❌ *لا يوجد اشتراك نشط*\n\nاضغط /start للاشتراك",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔔 اشترك الآن", callback_data="plan_menu")
            ]])
        )
        return

    end_date = datetime.fromisoformat(sub["end_date"])
    days_left = max((end_date - datetime.now()).days, 0)
    channels_list = sub["channels"].replace(",", "\n   ✅ ")

    await update.message.reply_text(
        f"✅ *اشتراكك نشط — ALSEIF CHART*\n\n"
        f"📦 الباقة: *{sub['plan'].upper()}*\n"
        f"📅 ينتهي بعد: *{days_left} يوم*\n"
        f"📆 تاريخ الانتهاء: {end_date.strftime('%Y/%m/%d')}\n\n"
        f"📲 *قنواتك:*\n   ✅ {channels_list}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 تجديد", callback_data="plan_menu")
        ]])
    )
