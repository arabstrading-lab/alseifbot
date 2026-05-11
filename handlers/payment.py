"""
معالجة المدفوعات - Stripe والكريبتو
"""

import logging
import stripe
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import (
    STRIPE_SECRET_KEY, PLANS, WEBSITE_URL,
    PAYMENT_SUCCESS_URL, PAYMENT_CANCEL_URL,
    NOWPAYMENTS_API_KEY
)
from database.db import create_payment
import requests

stripe.api_key = STRIPE_SECRET_KEY
logger = logging.getLogger(__name__)


async def payment_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data  # pay_stripe_basic / pay_crypto_pro

    parts = data.split("_")
    method = parts[1]       # stripe أو crypto
    plan_key = parts[2]     # basic / pro / vip

    plan = PLANS.get(plan_key)
    if not plan:
        await query.edit_message_text("❌ الباقة غير موجودة")
        return

    if method == "stripe":
        await handle_stripe_payment(query, plan_key, plan)
    elif method == "crypto":
        await handle_crypto_payment(query, plan_key, plan)


async def handle_stripe_payment(query, plan_key: str, plan: dict):
    user_id = query.from_user.id

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"ALSEIF CHART — {plan['name']}",
                        "description": plan["description"],
                    },
                    "unit_amount": int(plan["price_usd"] * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=f"{PAYMENT_SUCCESS_URL}?session_id={{CHECKOUT_SESSION_ID}}&tg={user_id}&plan={plan_key}",
            cancel_url=PAYMENT_CANCEL_URL,
            metadata={
                "telegram_id": str(user_id),
                "plan": plan_key
            }
        )

        create_payment(user_id, plan_key, plan["price_usd"], "stripe", stripe_id=session.id)

        keyboard = [[
            InlineKeyboardButton("💳 ادفع الآن", url=session.url),
            InlineKeyboardButton("✅ تأكيد الدفع", callback_data=f"pay_verify_{session.id}")
        ]]

        await query.edit_message_text(
            f"💳 *رابط الدفع جاهز!*\n\n"
            f"الباقة: *{plan['name']}*\n"
            f"المبلغ: *${plan['price_usd']}*\n\n"
            f"اضغط زر الدفع وبعد إتمامه اضغط «تأكيد الدفع»\n\n"
            f"⏳ الرابط صالح لـ 30 دقيقة",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except stripe.StripeError as e:
        logger.error(f"Stripe error: {e}")
        await query.edit_message_text(
            "❌ خطأ في إنشاء رابط الدفع. تواصل مع الدعم.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📞 الدعم", url="https://t.me/alseif_chart")
            ]])
        )


async def handle_crypto_payment(query, plan_key: str, plan: dict):
    user_id = query.from_user.id

    try:
        headers = {
            "x-api-key": NOWPAYMENTS_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "price_amount": plan["price_usd"],
            "price_currency": "usd",
            "pay_currency": "usdt",
            "order_id": f"tg_{user_id}_{plan_key}",
            "order_description": f"ALSEIF CHART - {plan['name']}",
            "ipn_callback_url": f"{WEBSITE_URL}/webhook/crypto",
            "success_url": f"{PAYMENT_SUCCESS_URL}?tg={user_id}&plan={plan_key}",
            "cancel_url": PAYMENT_CANCEL_URL,
        }

        response = requests.post(
            "https://api.nowpayments.io/v1/invoice",
            json=payload,
            headers=headers,
            timeout=10
        )
        data = response.json()

        if "invoice_url" in data:
            create_payment(user_id, plan_key, plan["price_usd"], "crypto", crypto_id=data.get("id"))

            keyboard = [[
                InlineKeyboardButton("₿ ادفع بالكريبتو", url=data["invoice_url"])
            ], [
                InlineKeyboardButton("🔙 رجوع", callback_data=f"plan_detail_{plan_key}")
            ]]

            await query.edit_message_text(
                f"₿ *دفع بالكريبتو*\n\n"
                f"الباقة: *{plan['name']}*\n"
                f"المبلغ: *${plan['price_usd']} USDT*\n\n"
                f"✅ يُقبل: USDT, BTC, ETH, BNB\n\n"
                f"اضغط الزر للدفع — سيتم تفعيل اشتراكك تلقائياً",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            raise Exception(f"NOWPayments error: {data}")

    except Exception as e:
        logger.error(f"Crypto payment error: {e}")
        await query.edit_message_text(
            "❌ خطأ في إنشاء رابط الدفع. تواصل مع الدعم.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📞 الدعم", url="https://t.me/alseif_chart")
            ]])
        )


async def activate_subscription_after_payment(bot, telegram_id: int, plan_key: str):
    """
    تفعيل الاشتراك وإرسال الروابط — يُستدعى من webhook
    """
    from database.db import create_subscription
    from config.settings import PLANS, CHANNELS

    plan = PLANS[plan_key]
    sub_id = create_subscription(
        telegram_id=telegram_id,
        plan=plan_key,
        channels=plan["channels"],
        duration_days=plan["duration_days"],
        payment_method="stripe",
        amount_usd=plan["price_usd"]
    )

    # بناء رسالة الروابط
    links_text = ""
    for ch_key in plan["channels"]:
        ch = CHANNELS[ch_key]
        links_text += f"\n🔗 [{ch['name']}]({ch['link']})"

    message = (
        f"🎉 *تم تفعيل اشتراكك!*\n\n"
        f"الباقة: *{plan['name']}*\n"
        f"المدة: *{plan['duration_days']} يوم*\n\n"
        f"📲 *روابط قنواتك الخاصة:*{links_text}\n\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⚠️ هذه الروابط خاصة فيك — لا تشاركها\n"
        f"📞 للدعم: @alseif_chart"
    )

    await bot.send_message(
        chat_id=telegram_id,
        text=message,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

    return sub_id
