import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

CHANNELS = {
    "forex": {
        "name": "ALSEIF FOREX",
        "link": os.getenv("FOREX_INVITE", ""),
        "chat_id": int(os.getenv("FOREX_CHAT_ID", "0")),
        "description": "صفقات فوركس يومية"
    },
    "crypto": {
        "name": "ALSEIF CRYPTO",
        "link": os.getenv("CRYPTO_INVITE", ""),
        "chat_id": int(os.getenv("CRYPTO_CHAT_ID", "0")),
        "description": "صفقات كريبتو"
    },
    "analysis": {
        "name": "ALSEIF ANALYSIS",
        "link": os.getenv("ANALYSIS_INVITE", ""),
        "chat_id": int(os.getenv("ANALYSIS_CHAT_ID", "0")),
        "description": "تحليل فني"
    },
    "free": {
        "name": "ALSEIF CHART",
        "link": os.getenv("FREE_INVITE", ""),
        "chat_id": int(os.getenv("FREE_CHAT_ID", "0")),
        "description": "قناة مجانية"
    }
}

PLANS = {
    "basic": {
        "name": "الباقة الاساسية",
        "price_usd": 40,
        "duration_days": 30,
        "channels": ["forex"],
        "description": "فوركس VIP"
    },
    "pro": {
        "name": "الباقة الاحترافية",
        "price_usd": 60,
        "duration_days": 30,
        "channels": ["forex", "crypto"],
        "description": "فوركس + كريبتو"
    },
    "vip": {
        "name": "باقة VIP",
        "price_usd": 80,
        "duration_days": 30,
        "channels": ["forex", "crypto", "analysis"],
        "description": "جميع القنوات"
    },
    "broker_free": {
        "name": "مجاني عبر الوكالة",
        "price_usd": 0,
        "duration_days": 30,
        "channels": ["forex", "crypto", "analysis"],
        "description": "مجاني"
    }
}

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
NOWPAYMENTS_API_KEY = os.getenv("NOWPAYMENTS_API_KEY", "")
NOWPAYMENTS_IPN_SECRET = os.getenv("NOWPAYMENTS_IPN_SECRET", "")
WEBSITE_URL = os.getenv("WEBSITE_URL", "")
PAYMENT_SUCCESS_URL = WEBSITE_URL + "/success"
PAYMENT_CANCEL_URL = WEBSITE_URL + "/cancel"
BROKER_REFERRAL_LINK = os.getenv("BROKER_LINK", "")
BROKER_NAME = os.getenv("BROKER_NAME", "XM")
REMINDER_DAYS_BEFORE = 3
GRACE_PERIOD_HOURS = 24
