import os

# ===== البوت =====
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ===== القنوات =====
CHANNELS = {
    "forex": {
        "name": "ALSEIF FOREX 📈",
        "link": os.getenv("FOREX_INVITE", ""),
        "chat_id": int(os.getenv("FOREX_CHAT_ID", "0")),
        "description": "صفقات فوركس يومية"
    },
    "crypto": {
        "name": "ALSEIF CRYPTO 🪙",
        "link": os.getenv("CRYPTO_INVITE", ""),
        "chat_id": int(os.getenv("CRYPTO_CHAT_ID", "0")),
        "description": "صفقات كريبتو"
    },
    "analysis": {
        "name": "ALSEIF ANALYSIS 📊",
        "link": os.getenv("ANALYSIS_INVITE", ""),
        "chat_id": int(os.getenv("ANALYSIS_CHAT_ID", "0")),
        "description": "تحليل فني من الصفر"
    },
    "free": {
        "name": "ALSEIF CHART - مجاني",
        "link": os.getenv("FREE_INVITE", ""),
        "chat_id": int(os.getenv("FREE_CHAT_ID", "0")),
        "description": "قناة مجانية"
    }
}

# ===== الباقات =====
PLANS = {
    "basic": {
        "name": "🥈 الباقة الأساسية",
        "price_usd": 40,
        "duration_days": 30,
        "channels": ["forex"],
        "description"
