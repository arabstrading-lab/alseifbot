"""
Webhook Server — Flask
يستقبل إشعارات الدفع من Stripe و NOWPayments
شغّله بجانب البوت أو على سيرفر منفصل
"""

import logging
import json
import asyncio
import stripe
from flask import Flask, request, jsonify
from config.settings import (
    STRIPE_WEBHOOK_SECRET, STRIPE_SECRET_KEY,
    NOWPAYMENTS_IPN_SECRET, BOT_TOKEN, PLANS
)
from database.db import (
    get_payment_by_stripe, update_payment_status,
    create_subscription
)
from telegram import Bot

stripe.api_key = STRIPE_SECRET_KEY
app = Flask(__name__)
logger = logging.getLogger(__name__)


async def activate_user(telegram_id: int, plan_key: str, payment_ref: str):
    """فعّل الاشتراك وأرسل الروابط"""
    from handlers.payment import activate_subscription_after_payment
    bot = Bot(token=BOT_TOKEN)
    async with bot:
        await activate_subscription_after_payment(bot, telegram_id, plan_key)


@app.route("/webhook/stripe", methods=["POST"])
def stripe_webhook():
    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except stripe.SignatureVerificationError:
        logger.warning("❌ Stripe signature invalid")
        return jsonify({"error": "Invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        telegram_id = int(session["metadata"].get("telegram_id", 0))
        plan_key = session["metadata"].get("plan", "")
        session_id = session["id"]

        if telegram_id and plan_key:
            update_payment_status(session_id, "completed")
            asyncio.run(activate_user(telegram_id, plan_key, session_id))
            logger.info(f"✅ Payment completed: tg={telegram_id}, plan={plan_key}")

    return jsonify({"status": "ok"}), 200


@app.route("/webhook/crypto", methods=["POST"])
def crypto_webhook():
    """NOWPayments IPN"""
    data = request.get_json(silent=True) or {}

    order_id = data.get("order_id", "")
    payment_status = data.get("payment_status", "")

    if payment_status == "finished" and order_id.startswith("tg_"):
        parts = order_id.split("_")
        if len(parts) >= 3:
            telegram_id = int(parts[1])
            plan_key = parts[2]
            asyncio.run(activate_user(telegram_id, plan_key, order_id))
            logger.info(f"✅ Crypto payment: tg={telegram_id}, plan={plan_key}")

    return jsonify({"status": "ok"}), 200


@app.route("/success")
def success_page():
    return """
    <html>
    <head><meta charset="utf-8"><title>ALSEIF CHART</title></head>
    <body style="font-family:sans-serif;text-align:center;padding:60px;background:#0a0a0a;color:#fff">
        <h1 style="color:#FFD700">✅ تم الدفع بنجاح!</h1>
        <p style="font-size:18px">سيصلك رابط القناة خلال لحظات على تيليغرام</p>
        <p><a href="https://t.me/AlseifChartBot" style="color:#FFD700">العودة للبوت</a></p>
    </body>
    </html>
    """, 200


@app.route("/cancel")
def cancel_page():
    return """
    <html>
    <head><meta charset="utf-8"><title>ALSEIF CHART</title></head>
    <body style="font-family:sans-serif;text-align:center;padding:60px;background:#0a0a0a;color:#fff">
        <h1 style="color:#FF4444">❌ تم إلغاء الدفع</h1>
        <p>يمكنك المحاولة مجدداً في أي وقت</p>
        <p><a href="https://t.me/AlseifChartBot" style="color:#FFD700">العودة للبوت</a></p>
    </body>
    </html>
    """, 200


@app.route("/health")
def health():
    return jsonify({"status": "ok", "bot": "ALSEIF CHART"})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host="0.0.0.0", port=5000, debug=False)
