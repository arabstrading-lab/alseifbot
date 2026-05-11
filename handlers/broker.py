"""
طلبات الوكالة - اشتراك مجاني عند التسجيل عبر رابط البروكر
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import BROKER_REFERRAL_LINK, BROKER_NAME, OWNER_ID
from database.db import create_broker_request, get_broker_request, upsert_user
import logging

logger = logging.getLogger(__name__)


async def broker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user

    data = query.data

    if data == "broker_info":
        await show_broker_info(query)
    elif data == "broker_apply":
        await apply_for_broker(query, user, context)
    elif data == "broker_confirm":
        await confirm_broker(query, user, context)
    elif data.startswith("broker_admin_approve_"):
        tg_id = int(data.split("_")[-1])
        await admin_approve_broker(query, user, tg_id, context)
    elif data.startswith("broker_admin_reject_"):
        tg_id = int(data.split("_")[-1])
        await admin_reject_broker(query, user, tg_id, context)


async def show_broker_info(query):
    text = (
        "🎁 *اشتراك مجاني عبر الوكالة*\n\n"
        "احصل على الباقة الكاملة مجاناً بخطوتين:\n\n"
        "1️⃣ سجّل حساباً عبر رابط الوكالة\n"
        f"   *(البروكر: {BROKER_NAME})*\n\n"
        "2️⃣ أرسل لنا تأكيد التسجيل وسيتم تفعيل اشتراكك فوراً\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "✅ *الباقة الكاملة تشمل:*\n"
        "   🔹 ALSEIF FOREX\n"
        "   🔹 ALSEIF CRYPTO\n"
        "   🔹 تحليل فني من الصفر\n"
        "   🔹 مدة 30 يوم قابلة للتجديد\n"
    )

    keyboard = [
        [InlineKeyboardButton("🔗 سجّل عبر رابط الوكالة", url=BROKER_REFERRAL_LINK)],
        [InlineKeyboardButton("✅ سجّلت — أريد تفعيل اشتراكي", callback_data="broker_apply")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="plan_menu")],
    ]

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )


async def apply_for_broker(query, user, context):
    # تحقق من طلب سابق
    existing = get_broker_request(user.id)
    if existing:
        status_map = {
            "pending": "⏳ طلبك قيد المراجعة. سيتم الرد خلال 24 ساعة.",
            "approved": "✅ تم قبول طلبك مسبقاً وتفعيل اشتراكك.",
            "rejected": "❌ تم رفض طلبك. تواصل مع الدعم."
        }
        await query.edit_message_text(
            status_map.get(existing["status"], "تحقق من حالة طلبك"),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("📞 الدعم", url="https://t.me/alseif_chart")
            ]])
        )
        return

    text = (
        "📋 *تأكيد طلب الوكالة*\n\n"
        "قبل الإرسال، تأكد من:\n\n"
        "✅ سجّلت حساباً جديداً عبر رابطنا\n"
        "✅ أكملت التحقق من الهوية (KYC)\n"
        "✅ الحساب باسمك أنت\n\n"
        "⚠️ سيتم التحقق خلال 24 ساعة\n\n"
        "هل تريد إرسال طلبك؟"
    )

    keyboard = [
        [InlineKeyboardButton("✅ نعم، أرسل الطلب", callback_data="broker_confirm")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="broker_info")],
    ]

    await query.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def confirm_broker(query, user, context):
    req_id = create_broker_request(user.id)
    upsert_user(user.id, user.username or "", user.full_name or "")

    await query.edit_message_text(
        "✅ *تم استلام طلبك!*\n\n"
        "⏳ سيتم مراجعته خلال 24 ساعة\n"
        "📲 ستصلك رسالة تأكيد بعد الموافقة\n\n"
        "شكراً لثقتك بـ ALSEIF CHART 🏆",
        parse_mode="Markdown"
    )

    # إشعار المالك
    try:
        username_display = f"@{user.username}" if user.username else user.full_name
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=(
                f"🔔 *طلب وكالة جديد*\n\n"
                f"👤 المستخدم: {username_display}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📋 طلب رقم: {req_id}"
            ),
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ قبول", callback_data=f"broker_admin_approve_{user.id}"),
                    InlineKeyboardButton("❌ رفض", callback_data=f"broker_admin_reject_{user.id}")
                ]
            ])
        )
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


async def admin_approve_broker(query, admin_user, target_id: int, context):
    from database.db import approve_broker, create_subscription
    from config.settings import PLANS, CHANNELS

    approve_broker(target_id, admin_user.id)

    plan = PLANS["broker_free"]
    create_subscription(
        telegram_id=target_id,
        plan="broker_free",
        channels=plan["channels"],
        duration_days=30,
        payment_method="broker",
        amount_usd=0,
        broker_verified=True
    )

    # أرسل الروابط للمستخدم
    links_text = ""
    for ch_key in plan["channels"]:
        ch = CHANNELS[ch_key]
        links_text += f"\n🔗 [{ch['name']}]({ch['link']})"

    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                f"🎉 *تم قبول طلبك وتفعيل اشتراكك مجاناً!*\n\n"
                f"📲 *قنواتك الخاصة:*{links_text}\n\n"
                f"━━━━━━━━━━━━━━━━\n"
                f"⚠️ الروابط خاصة بك — لا تشاركها\n"
                f"📞 الدعم: @alseif_chart"
            ),
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Failed to send approval to {target_id}: {e}")

    await query.edit_message_text(f"✅ تم قبول وتفعيل المستخدم {target_id}")


async def admin_reject_broker(query, admin_user, target_id: int, context):
    try:
        await context.bot.send_message(
            chat_id=target_id,
            text=(
                "❌ *لم يتم قبول طلبك*\n\n"
                "يبدو أن الحساب لا يستوفي الشروط.\n"
                "للمزيد: @alseif_chart"
            ),
            parse_mode="Markdown"
        )
    except Exception:
        pass

    await query.edit_message_text(f"❌ تم رفض المستخدم {target_id}")
