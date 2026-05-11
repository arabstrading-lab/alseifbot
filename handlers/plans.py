"""
عرض الباقات وتفاصيلها
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import PLANS


PLAN_EMOJI = {
    "basic": "🥈",
    "pro": "🥇",
    "vip": "💎",
}


async def plans_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # plan_menu أو plan_basic أو plan_pro أو plan_vip

    if data == "plan_menu":
        await show_plans_menu(query)
    elif data.startswith("plan_detail_"):
        plan_key = data.replace("plan_detail_", "")
        await show_plan_detail(query, plan_key)


async def show_plans_menu(query):
    text = (
        "💼 *اختر الباقة المناسبة لك*\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "🥈 *الأساسية* — $40/شهر\n"
        "   └ ALSEIF FOREX فقط\n\n"
        "🥇 *الاحترافية* — $60/شهر\n"
        "   └ FOREX + CRYPTO\n\n"
        "💎 *VIP الكاملة* — $80/شهر\n"
        "   └ جميع القنوات + التحليل\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "🎁 أو *مجاناً* عند التسجيل عبر رابط الوكالة\n"
    )

    keyboard = [
        [InlineKeyboardButton("🥈 الأساسية — $40", callback_data="plan_detail_basic")],
        [InlineKeyboardButton("🥇 الاحترافية — $60", callback_data="plan_detail_pro")],
        [InlineKeyboardButton("💎 VIP الكاملة — $80", callback_data="plan_detail_vip")],
        [InlineKeyboardButton("🎁 مجاني عبر الوكالة", callback_data="broker_info")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="back_start")],
    ]

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_plan_detail(query, plan_key: str):
    plan = PLANS.get(plan_key)
    if not plan:
        await query.edit_message_text("❌ الباقة غير موجودة")
        return

    emoji = PLAN_EMOJI.get(plan_key, "⭐")
    channels_text = "\n".join([f"   ✅ {ch.upper()}" for ch in plan["channels"]])

    text = (
        f"{emoji} *{plan['name']}*\n\n"
        f"💰 السعر: *${plan['price_usd']} / شهر*\n"
        f"📅 المدة: *{plan['duration_days']} يوم*\n\n"
        f"📦 *يشمل:*\n{channels_text}\n\n"
        f"📝 {plan['description']}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"اختر طريقة الدفع:"
    )

    keyboard = [
        [InlineKeyboardButton("💳 بطاقة بنكية (Stripe)", callback_data=f"pay_stripe_{plan_key}")],
        [InlineKeyboardButton("₿ دفع بالكريبتو", callback_data=f"pay_crypto_{plan_key}")],
        [InlineKeyboardButton("🔙 رجوع للباقات", callback_data="plan_menu")],
    ]

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
