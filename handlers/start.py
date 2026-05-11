"""
/start - أول رسالة يراها المستخدم
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import upsert_user, get_active_subscription
from config.settings import CHANNELS


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username or "", user.full_name or "")

    # تحقق إذا عنده اشتراك نشط
    sub = get_active_subscription(user.id)

    if sub:
        from datetime import datetime
        end_date = datetime.fromisoformat(sub["end_date"])
        days_left = (end_date - datetime.now()).days

        text = (
            f"👋 أهلاً {user.first_name}!\n\n"
            f"✅ اشتراكك نشط — *{sub['plan'].upper()}*\n"
            f"📅 ينتهي بعد: *{days_left} يوم*\n\n"
            f"اختر من القائمة أدناه:"
        )
        keyboard = [
            [InlineKeyboardButton("📊 حالة اشتراكي", callback_data="admin_mystatus")],
            [InlineKeyboardButton("🔄 تجديد الاشتراك", callback_data="plan_menu")],
            [InlineKeyboardButton("📞 تواصل مع الدعم", url="https://t.me/alseif_chart")],
        ]
    else:
        text = (
            "🏆 *أهلاً بك في ALSEIF CHART*\n\n"
            "منصتك الاحترافية للتداول في الفوركس والكريبتو\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "📈 *ALSEIF FOREX* — صفقات فوركس يومية\n"
            "🪙 *ALSEIF CRYPTO* — صفقات كريبتو\n"
            "📚 *تحليل فني* — من الصفر حتى الاحتراف\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "اختر طريقة الاشتراك:"
        )
        keyboard = [
            [InlineKeyboardButton("💳 اشتراك مدفوع", callback_data="plan_menu")],
            [InlineKeyboardButton("🎁 مجاني عبر الوكالة", callback_data="broker_info")],
            [InlineKeyboardButton("📊 حالة اشتراكي", callback_data="admin_mystatus")],
            [InlineKeyboardButton("📢 قناة مجانية", url=CHANNELS["free"]["link"])],
        ]

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
