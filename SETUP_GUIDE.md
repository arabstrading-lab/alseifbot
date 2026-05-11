# 🏆 ALSEIF CHART BOT — دليل الرفع والتشغيل الكامل

---

## 📁 هيكل الملفات

```
alseif_bot/
├── main.py                    ← نقطة تشغيل البوت
├── requirements.txt           ← المكتبات المطلوبة
├── Procfile                   ← إعدادات Railway
├── .env.example               ← نموذج المتغيرات
├── config/
│   └── settings.py            ← كل الإعدادات هنا
├── database/
│   └── db.py                  ← قاعدة البيانات SQLite
├── handlers/
│   ├── start.py               ← رسالة /start
│   ├── plans.py               ← عرض الباقات
│   ├── payment.py             ← معالجة الدفع
│   ├── broker.py              ← طلبات الوكالة
│   ├── admin.py               ← لوحة المدير
│   └── status.py              ← /status
└── utils/
    ├── scheduler.py           ← مهام يومية تلقائية
    └── webhook_server.py      ← سيرفر Stripe/Crypto
```

---

## 🚀 المرحلة 1 — إنشاء البوت على تيليغرام

1. افتح تيليغرام → ابحث عن **@BotFather**
2. أرسل `/newbot`
3. اسم البوت: `ALSEIF CHART`
4. username: `AlseifChartBot` (أو أي اسم متاح)
5. **انسخ الـ Token** — ستحتاجه في الخطوة التالية

---

## 🔑 المرحلة 2 — إعداد الإعدادات

افتح `config/settings.py` وعدّل:

```python
BOT_TOKEN = "YOUR_TOKEN_HERE"          # من BotFather
OWNER_ID = 123456789                    # من @userinfobot
```

---

## 📢 المرحلة 3 — إنشاء القنوات

1. أنشئ قناتين خاصتين على تيليغرام:
   - **ALSEIF FOREX** 
   - **ALSEIF CRYPTO**
   - **ALSEIF ANALYSIS** (اختياري)

2. أضف البوت كـ **Admin** مع صلاحية "إضافة أعضاء"

3. أنشئ رابط دعوة لكل قناة (إعدادات القناة > دعوة)

4. احصل على Chat ID لكل قناة:
   - أضف **@userinfobot** للقناة
   - أو أرسل رسالة للقناة ثم افتح:
     `https://api.telegram.org/botYOUR_TOKEN/getUpdates`

5. عدّل في `settings.py`:
```python
CHANNELS = {
    "forex": {
        "link": "https://t.me/+رابط_القناة",
        "chat_id": -1001234567890,
    },
    ...
}
```

---

## 💳 المرحلة 4 — ربط Stripe

1. سجّل على [stripe.com](https://stripe.com)
2. من Dashboard > Developers > API Keys:
   - انسخ `Secret key` و `Publishable key`
3. من Webhooks > Add endpoint:
   - URL: `https://your-app.railway.app/webhook/stripe`
   - Events: `checkout.session.completed`
4. انسخ Webhook Secret
5. عدّل في `settings.py`

---

## ₿ المرحلة 5 — ربط NOWPayments (كريبتو)

1. سجّل على [nowpayments.io](https://nowpayments.io)
2. من API Keys: انسخ المفتاح
3. من IPN Settings: أضف URL الـ webhook
4. عدّل في `settings.py`

---

## ☁️ المرحلة 6 — رفع على Railway

### الطريقة السهلة:

```bash
# 1. ثبّت Railway CLI
npm install -g @railway/cli

# 2. سجّل الدخول
railway login

# 3. في مجلد المشروع
railway init
railway up
```

### أو من الموقع:
1. اذهب لـ [railway.app](https://railway.app)
2. New Project > Deploy from GitHub
3. ارفع الملفات على GitHub أولاً
4. أضف المتغيرات في Variables

### إضافة المتغيرات على Railway:
```
BOT_TOKEN = YOUR_TOKEN
OWNER_ID = YOUR_ID
STRIPE_SECRET_KEY = sk_live_...
STRIPE_WEBHOOK_SECRET = whsec_...
NOWPAYMENTS_API_KEY = ...
WEBSITE_URL = https://YOUR_APP.railway.app
```

---

## 🧪 المرحلة 7 — تجربة البوت محلياً

```bash
# 1. ثبّت Python 3.11
# 2. في مجلد المشروع:

pip install -r requirements.txt

# 3. أنشئ ملف .env من .env.example وعدّله

# 4. شغّل البوت
python main.py

# 5. شغّل السيرفر (في terminal ثاني)
python utils/webhook_server.py
```

---

## ⏰ المرحلة 8 — المهام اليومية التلقائية

### على Railway (Cron Job):
أضف في Railway > Cron Jobs:
```
Schedule: 0 8 * * *
Command: python utils/scheduler.py
```

### أو محلياً (Linux/Mac):
```bash
crontab -e
# أضف:
0 8 * * * cd /path/to/alseif_bot && python utils/scheduler.py
```

---

## ✅ اختبار البوت

1. افتح البوت على تيليغرام
2. أرسل `/start` — يجب أن تظهر القائمة
3. اختر باقة → تحقق من رابط Stripe
4. أرسل `/admin` من حساب المالك فقط
5. جرّب طلب وكالة وموافق عليه

---

## 🆘 مشاكل شائعة

| المشكلة | الحل |
|---------|------|
| البوت لا يرد | تحقق من BOT_TOKEN |
| Webhook لا يعمل | تأكد WEBSITE_URL صحيح في Stripe |
| لا يرسل الروابط | تأكد البوت admin في القناة |
| خطأ في Stripe | تأكد Secret Key في البيئة |

---

## 📞 للمساعدة

تواصل مع الدعم: @alseif_chart
