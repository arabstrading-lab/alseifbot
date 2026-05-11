"""
لوحة تحكم المدير
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config.settings import OWNER_ID, PLANS, CHANNELS
from database.db import (
    get_stats, get_all_users, get_active_subscription,
    get_pending_broker_requests, ban_user, create_subscription,
    deactivate_subscription, get_expired_subscriptions
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def is_admin(user_id: int) -> bool:
    return user_id == OWNER_ID


async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user = query.from_user
        data = query.data

        if data == "admin_mystatus":
            await show_my_status(query, user)
            return

        if not is_admin(user.id):
            await query.edit_message_text("🚫 غير مصرح لك بالوصول لهذه الصفحة")
            return

        if data == "admin_menu":
            await show_admin_menu(query)
        elif data == "admin_stats":
            await show_stats(query)
        elif data == "admin_users":
            await show_users(query)
        elif data == "admin_pending_broker":
            await show_pending_broker(query)
        elif data == "admin_expired":
            await handle_expired(query, context)

    elif update.message:
        user = update.effective_user
        if not is_admin(user.id):
            return

        await update.message.reply_text(
            "🛡️ *لوحة تحكم المدير*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
                [InlineKeyboardButton("👥 المشتركين", callback_data="admin_users")],
                [InlineKeyboardButton("🔔 طلبات الوكالة", callback_data="admin_pending_broker")],
                [InlineKeyboardButton("⏰ إدارة الاشتراكات المنتهية", callback_data="admin_expired")],
            ])
        )


async def show_admin_menu(query):
    keyboard = [
        [InlineKeyboardButton("📊 الإحصائيات", callback_data="admin_stats")],
        [InlineKeyboardButton("👥 المشتركين", callback_data="admin_users")],
        [InlineKeyboardButton("🔔 طلبات الوكالة", callback_data="admin_pending_broker")],
        [InlineKeyboardButton("⏰ الاشتراكات المنتهية", callback_data="admin_expired")],
    ]
    await query.edit_message_text(
        "🛡️ *لوحة تحكم ALSEIF CHART*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def show_stats(query):
    stats = get_stats()
    text = (
        "📊 *إحصائيات ALSEIF CHART*\n\n"
        f"👥 إجمالي المستخدمين: *{stats['total_users']}*\n"
        f"✅ مشتركون نشطون: *{stats['active_subs']}*\n"
        f"💰 إجمالي الإيرادات: *${stats['total_revenue']}*\n"
        f"📅 إيرادات هذا الشهر: *${stats['month_revenue']}*\n"
        f"⏳ طلبات وكالة معلقة: *{stats['pending_broker']}*\n\n"
        f"🕐 آخر تحديث: {datetime.now().strftime('%H:%M - %Y/%m/%d')}"
    )

    keyboard = [
        [InlineKeyboardButton("🔄 تحديث", callback_data="admin_stats")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu")],
    ]

    await query.edit_message_text(text, parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))


async def show_users(query):
    users = get_all_users()
    active_count = 0
    lines = []

    for u in users[-20:]:  # آخر 20 مستخدم
        sub = get_active_subscription(u["telegram_id"])
        status = "✅" if sub else "⭕"
        if sub:
            active_count += 1
        username = f"@{u['username']}" if u["username"] else u["full_name"] or "غير معروف"
        lines.append(f"{status} {username} — `{u['telegram_id']}`")

    text = (
        f"👥 *المستخدمون (آخر 20)*\n\n"
        + "\n".join(lines) +
        f"\n\n✅ نشط: {active_count} | إجمالي: {len(users)}"
    )

    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu")
        ]])
    )


async def show_pending_broker(query):
    requests = get_pending_broker_requests()

    if not requests:
        await query.edit_message_text(
            "✅ لا توجد طلبات وكالة معلقة",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu")
            ]])
        )
        return

    buttons = []
    text = f"🔔 *طلبات الوكالة المعلقة ({len(requests)})*\n\n"

    for r in requests:
        username = f"@{r['username']}" if r["username"] else r["full_name"] or str(r["telegram_id"])
        text += f"👤 {username} — `{r['telegram_id']}`\n📅 {r['submitted_at'][:10]}\n\n"
        buttons.append([
            InlineKeyboardButton(f"✅ قبول {username}", callback_data=f"broker_admin_approve_{r['telegram_id']}"),
            InlineKeyboardButton("❌", callback_data=f"broker_admin_reject_{r['telegram_id']}")
        ])

    buttons.append([InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu")])

    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


async def handle_expired(query, context):
    expired = get_expired_subscriptions()

    if not expired:
        await query.edit_message_text(
            "✅ لا توجد اشتراكات منتهية تحتاج معالجة",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu")
            ]])
        )
        return

    removed = 0
    for sub in expired:
        deactivate_subscription(sub["id"])
        try:
            await context.bot.send_message(
                chat_id=sub["telegram_id"],
                text=(
                    "⏰ *انتهى اشتراكك في ALSEIF CHART*\n\n"
                    "لتجديد اشتراكك:\n"
                    "👉 /start\n\n"
                    "نتمنى نشوفك معنا مجدداً! 🏆"
                ),
                parse_mode="Markdown"
            )
        except Exception:
            pass
        removed += 1

    await query.edit_message_text(
        f"✅ تم معالجة *{removed}* اشتراك منتهي",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🔙 رجوع", callback_data="admin_menu")
        ]])
    )


async def show_my_status(query, user):
    sub = get_active_subscription(user.id)

    if not sub:
        text = (
            "❌ *لا يوجد اشتراك نشط*\n\n"
            "اشترك الآن واستمتع بصفقات احترافية!"
        )
        keyboard = [[InlineKeyboardButton("🔔 اشترك الآن", callback_data="plan_menu")]]
    else:
        end_date = datetime.fromisoformat(sub["end_date"])
        days_left = max((end_date - datetime.now()).days, 0)
        channels_list = sub["channels"].replace(",", "\n   ✅ ")

        text = (
            f"✅ *اشتراكك نشط*\n\n"
            f"📦 الباقة: *{sub['plan'].upper()}*\n"
            f"📅 ينتهي بعد: *{days_left} يوم*\n"
            f"📆 تاريخ الانتهاء: {end_date.strftime('%Y/%m/%d')}\n\n"
            f"📲 *قنواتك:*\n   ✅ {channels_list}"
        )
        keyboard = [
            [InlineKeyboardButton("🔄 تجديد مبكر", callback_data="plan_menu")],
        ]

    await query.edit_message_text(
        text, parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
