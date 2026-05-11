"""
قاعدة البيانات - SQLite
جميع عمليات الحفظ والقراءة
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "alseif_data.db"
logger = logging.getLogger(__name__)


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """إنشاء الجداول عند أول تشغيل"""
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY,
                telegram_id     INTEGER UNIQUE NOT NULL,
                username        TEXT,
                full_name       TEXT,
                join_date       TEXT DEFAULT (datetime('now')),
                is_banned       INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS subscriptions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id     INTEGER NOT NULL,
                plan            TEXT NOT NULL,
                channels        TEXT NOT NULL,
                start_date      TEXT NOT NULL,
                end_date        TEXT NOT NULL,
                payment_method  TEXT,
                payment_ref     TEXT,
                amount_usd      REAL DEFAULT 0,
                is_active       INTEGER DEFAULT 1,
                broker_verified INTEGER DEFAULT 0,
                created_at      TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            );

            CREATE TABLE IF NOT EXISTS payments (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id     INTEGER NOT NULL,
                plan            TEXT NOT NULL,
                amount_usd      REAL NOT NULL,
                method          TEXT NOT NULL,
                stripe_id       TEXT,
                crypto_id       TEXT,
                status          TEXT DEFAULT 'pending',
                created_at      TEXT DEFAULT (datetime('now')),
                completed_at    TEXT
            );

            CREATE TABLE IF NOT EXISTS broker_requests (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id     INTEGER NOT NULL,
                broker_uid      TEXT,
                status          TEXT DEFAULT 'pending',
                submitted_at    TEXT DEFAULT (datetime('now')),
                verified_at     TEXT,
                verified_by     INTEGER
            );

            CREATE TABLE IF NOT EXISTS reminders_sent (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id     INTEGER NOT NULL,
                subscription_id INTEGER NOT NULL,
                sent_at         TEXT DEFAULT (datetime('now'))
            );
        """)
    logger.info("✅ تم تهيئة قاعدة البيانات")


# ========== Users ==========

def upsert_user(telegram_id: int, username: str, full_name: str):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO users (telegram_id, username, full_name)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
        """, (telegram_id, username, full_name))


def get_user(telegram_id: int):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ).fetchone()


def get_all_users():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM users WHERE is_banned = 0").fetchall()


def ban_user(telegram_id: int):
    with get_conn() as conn:
        conn.execute("UPDATE users SET is_banned = 1 WHERE telegram_id = ?", (telegram_id,))


# ========== Subscriptions ==========

def create_subscription(telegram_id: int, plan: str, channels: list,
                         duration_days: int, payment_method: str,
                         payment_ref: str = None, amount_usd: float = 0,
                         broker_verified: bool = False):
    start = datetime.now()
    end = start + timedelta(days=duration_days)
    channels_str = ",".join(channels)

    with get_conn() as conn:
        # إلغاء أي اشتراك قديم نشط
        conn.execute("""
            UPDATE subscriptions SET is_active = 0
            WHERE telegram_id = ? AND is_active = 1
        """, (telegram_id,))

        conn.execute("""
            INSERT INTO subscriptions
            (telegram_id, plan, channels, start_date, end_date,
             payment_method, payment_ref, amount_usd, broker_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (telegram_id, plan, channels_str,
              start.isoformat(), end.isoformat(),
              payment_method, payment_ref, amount_usd,
              1 if broker_verified else 0))

        return conn.lastrowid


def get_active_subscription(telegram_id: int):
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM subscriptions
            WHERE telegram_id = ? AND is_active = 1
              AND end_date > datetime('now')
            ORDER BY created_at DESC LIMIT 1
        """, (telegram_id,)).fetchone()


def deactivate_subscription(subscription_id: int):
    with get_conn() as conn:
        conn.execute(
            "UPDATE subscriptions SET is_active = 0 WHERE id = ?",
            (subscription_id,)
        )


def get_expiring_subscriptions(days: int = 3):
    """اشتراكات ستنتهي خلال X أيام"""
    target = (datetime.now() + timedelta(days=days)).isoformat()
    now = datetime.now().isoformat()
    with get_conn() as conn:
        return conn.execute("""
            SELECT s.*, u.username, u.full_name FROM subscriptions s
            JOIN users u ON s.telegram_id = u.telegram_id
            WHERE s.is_active = 1
              AND s.end_date <= ?
              AND s.end_date > ?
              AND s.telegram_id NOT IN (
                  SELECT telegram_id FROM reminders_sent
                  WHERE subscription_id = s.id
              )
        """, (target, now)).fetchall()


def get_expired_subscriptions():
    """اشتراكات منتهية ولازال is_active = 1"""
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM subscriptions
            WHERE is_active = 1 AND end_date <= datetime('now')
        """).fetchall()


def mark_reminder_sent(telegram_id: int, subscription_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO reminders_sent (telegram_id, subscription_id) VALUES (?, ?)",
            (telegram_id, subscription_id)
        )


# ========== Payments ==========

def create_payment(telegram_id: int, plan: str, amount_usd: float,
                   method: str, stripe_id: str = None, crypto_id: str = None):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO payments (telegram_id, plan, amount_usd, method, stripe_id, crypto_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (telegram_id, plan, amount_usd, method, stripe_id, crypto_id))
        return conn.lastrowid


def update_payment_status(stripe_id: str, status: str):
    with get_conn() as conn:
        conn.execute("""
            UPDATE payments SET status = ?, completed_at = datetime('now')
            WHERE stripe_id = ?
        """, (status, stripe_id))


def get_payment_by_stripe(stripe_id: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM payments WHERE stripe_id = ?", (stripe_id,)
        ).fetchone()


# ========== Broker ==========

def create_broker_request(telegram_id: int, broker_uid: str = None):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO broker_requests (telegram_id, broker_uid) VALUES (?, ?)
        """, (telegram_id, broker_uid))
        return conn.lastrowid


def get_broker_request(telegram_id: int):
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM broker_requests
            WHERE telegram_id = ? ORDER BY submitted_at DESC LIMIT 1
        """, (telegram_id,)).fetchone()


def approve_broker(telegram_id: int, admin_id: int):
    with get_conn() as conn:
        conn.execute("""
            UPDATE broker_requests
            SET status = 'approved', verified_at = datetime('now'), verified_by = ?
            WHERE telegram_id = ? AND status = 'pending'
        """, (admin_id, telegram_id))


def get_pending_broker_requests():
    with get_conn() as conn:
        return conn.execute("""
            SELECT br.*, u.username, u.full_name
            FROM broker_requests br
            JOIN users u ON br.telegram_id = u.telegram_id
            WHERE br.status = 'pending'
            ORDER BY br.submitted_at ASC
        """).fetchall()


# ========== Stats ==========

def get_stats():
    with get_conn() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        active_subs = conn.execute(
            "SELECT COUNT(*) FROM subscriptions WHERE is_active=1 AND end_date > datetime('now')"
        ).fetchone()[0]
        total_revenue = conn.execute(
            "SELECT COALESCE(SUM(amount_usd), 0) FROM payments WHERE status='completed'"
        ).fetchone()[0]
        month_revenue = conn.execute("""
            SELECT COALESCE(SUM(amount_usd), 0) FROM payments
            WHERE status='completed' AND completed_at >= date('now', 'start of month')
        """).fetchone()[0]
        pending_broker = conn.execute(
            "SELECT COUNT(*) FROM broker_requests WHERE status='pending'"
        ).fetchone()[0]

        return {
            "total_users": total_users,
            "active_subs": active_subs,
            "total_revenue": round(total_revenue, 2),
            "month_revenue": round(month_revenue, 2),
            "pending_broker": pending_broker
        }
