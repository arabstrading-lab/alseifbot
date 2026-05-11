"""
إعدادات البوت - تُقرأ من متغيرات البيئة
"""
import os
from dotenv import load_dotenv

load_dotenv()

# ===== إعدادات البوت =====
BOT_TOKEN = os.environ["BOT_TOKEN"]
BOT_USERNAME = "@AlseifChartBot"

# ===== معلومات المالك =====
OWNER_ID = int(os.environ["OWNER_ID"])
OWNER_USERNAME = "@alseif_chart"

# ===== أسماء القنوات =====
CHANNELS = {
    "forex": {
        "name": "ALSEIF FOREX 📈",
        "link": os.environ.get("FOREX_INVITE", ""),
        "chat_id": int(os.environ.get("FOREX_CHAT_ID", "0")),
        "description": "صفقات فوركس يومية + تحليل فني احترافي"
    },
    "crypto": {
        "name": "ALSEIF CRYPTO 🪙",
        "link": os.environ.get("CRYPTO_INVITE", ""),
        "chat_id": int(os.environ.get("CRYPTO_CHAT_ID", "0")),
        "description": "صفقات كريبتو + تحليل العملات الرقمية"
    },
    "analysis": {
        "name": "ALSEIF ANALYSIS 📊",
        "link": os.environ.get("ANALYSIS_INVITE", ""),
        "chat_id": int(os.environ.get("ANALYSIS_CHAT_ID", "0")),
        "description": "تعليم التحليل الفني من الصفر"
    },
    "free": {
        "name": "ALSEIF CHART - قناة مجانية",
        "link": "https://t.me/alseif_chart_free",
        "chat_id": 0,
        "description": "إشارات مجانية وأخبار السوق"
    }
}

# ===== الباقات والأسعار =====
PLANS = {
    "basic": {
        "name": "🥈 الباقة الأساسية",
        "price_usd": 40,
        "duration_days": 30,
        "channels": ["forex"],
        "description": "قناة فوركس VIP فقط"
    },
    "pro": {
        "name": "🥇 الباقة الاحترافية",
        "price_usd": 60,
        "duration_days": 30,
        "channels": ["forex", "crypto"],
        "description": "فوركس + كريبتو VIP"
    },
    "vip": {
        "name": "💎 باقة VIP الكاملة",
        "price_usd": 80,
        "duration_days": 30,
        "channels": ["forex", "crypto", "analysis"],
        "description": "جميع القنوات + التحليل من الصفر"
    },
    "broker_free": {
        "name": "🎁 مجاني عبر الوكالة",
        "price_usd": 0,
        "duration_days": 30,
        "channels": ["forex", "crypto", "analysis"],
        "description": "مجاني عند التسجيل عبر رابط الوكالة"
    }
}

# ===== إعدادات الدفع =====
# Stripe
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")

# NOWPayments (كريبتو)
NOWPAYMENTS_API_KEY = os.environ.get("NOWPAYMENTS_API_KEY", "")
NOWPAYMENTS_IPN_SECRET = os.environ.get("NOWPAYMENTS_IPN_SECRET", "")

# ===== رابط الوكالة =====
BROKER_REFERRAL_LINK = os.environ.get("BROKER_LINK", "")
BROKER_NAME = "XM / IC Markets"

# ===== إعدادات الموقع =====
WEBSITE_URL = os.environ.get("WEBSITE_URL", "https://your-app.up.railway.app")
PAYMENT_SUCCESS_URL = f"{WEBSITE_URL}/success"
PAYMENT_CANCEL_URL = f"{WEBSITE_URL}/cancel"
WEBHOOK_URL = f"{WEBSITE_URL}/webhook/stripe"

# ===== إعدادات التذكيرات =====
REMINDER_DAYS_BEFORE = 3
GRACE_PERIOD_HOURS = 24
