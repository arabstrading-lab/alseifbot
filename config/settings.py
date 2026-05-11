"""
إعدادات البوت - عدّل هذا الملف بمعلوماتك
"""

# ===== إعدادات البوت =====
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"          # من @BotFather
BOT_USERNAME = "@AlseifChartBot"

# ===== معلومات المالك =====
OWNER_ID = 123456789                        # ID التيليغرام الخاص فيك
OWNER_USERNAME = "@alseif_chart"

# ===== أسماء القنوات (عدّل بعد إنشائها) =====
CHANNELS = {
    "forex": {
        "name": "ALSEIF FOREX 📈",
        "link": "https://t.me/+XXXXXXXXXXXXXXXX",   # رابط الدعوة الخاص
        "chat_id": -1001234567890,                   # ID القناة
        "description": "صفقات فوركس يومية + تحليل فني احترافي"
    },
    "crypto": {
        "name": "ALSEIF CRYPTO 🪙",
        "link": "https://t.me/+YYYYYYYYYYYYYYYY",
        "chat_id": -1001234567891,
        "description": "صفقات كريبتو + تحليل العملات الرقمية"
    },
    "analysis": {
        "name": "ALSEIF ANALYSIS 📊",
        "link": "https://t.me/+ZZZZZZZZZZZZZZZZ",
        "chat_id": -1001234567892,
        "description": "تعليم التحليل الفني من الصفر حتى الاحتراف"
    },
    "free": {
        "name": "ALSEIF CHART - قناة مجانية",
        "link": "https://t.me/alseif_chart_free",
        "chat_id": -1001234567893,
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
STRIPE_SECRET_KEY = "sk_live_XXXXXXXXXXXXXXXXXXXXXXXX"
STRIPE_WEBHOOK_SECRET = "whsec_XXXXXXXXXXXXXXXXXXXXXXXX"
STRIPE_PUBLIC_KEY = "pk_live_XXXXXXXXXXXXXXXXXXXXXXXX"

# NOWPayments (كريبتو)
NOWPAYMENTS_API_KEY = "XXXXXXXXXXXXXXXXXXXXXXXX"
NOWPAYMENTS_IPN_SECRET = "XXXXXXXXXXXXXXXXXXXXXXXX"

# ===== رابط الوكالة (Broker Referral) =====
BROKER_REFERRAL_LINK = "https://your-broker-link.com/?ref=alseif"
BROKER_NAME = "XM / IC Markets"

# ===== إعدادات الموقع =====
WEBSITE_URL = "https://alseif-chart.com"
PAYMENT_SUCCESS_URL = f"{WEBSITE_URL}/success"
PAYMENT_CANCEL_URL = f"{WEBSITE_URL}/cancel"
WEBHOOK_URL = f"{WEBSITE_URL}/webhook/stripe"

# ===== إعدادات التذكيرات =====
REMINDER_DAYS_BEFORE = 3    # تذكير قبل كم يوم من الانتهاء
GRACE_PERIOD_HOURS = 24     # ساعات السماح بعد الانتهاء قبل الإزالة
