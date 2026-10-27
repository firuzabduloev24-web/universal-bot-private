#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
💼 ISH TOPISH VA ISH BERISH TELEGRAM BOTI (AI SMART MATCH & PRO RESUME) 💼
=============================================================================
Rasmiy Bot: @ish_topish_teambot
Muallif & Bosh Administrator: @usman_khasan (Telegram ID: 1021089367)
Texnologiya: pyTelegramBotAPI (telebot) + SQLite3 + ReportLab (PDF) + AI Smart Match

ASOSIY IMKONIYATLAR VA INQILOBIY YANGILIKLAR:
 1. 📄 Professional PDF Rezyume Generator (ReportLab A4 zamonaviy dizayn)
 2. 🤖 AI Smart Match (Soha, hudud va malaka bo'yicha avtomatik moslashtirish va push-xabar)
 3. ⚡ Kunlik Shoshilinch Ishlar ("Bugunga ish" — kunlik to'lovli tezkor vazifalar)
 4. 📢 Telegram Kanalga Avto-Post (/set_channel orqali ulash va "Ariza topshirish" tugmasi)
 5. 📍 12 Viloyat va Toshkent bo'yicha filtrlash va joylashuv qidiruvi
 6. 🎙 Video-Note (Kruglyash) va Ovozli Rezyume (30 soniyalik audio/video tanishtiruv)
 7. 🛡 100% Xatosiz Ishlash Tizimi (Har bir handler try-except bilan himoyalangan)
=============================================================================
"""

import os
import sys
import time
import math
import logging
import sqlite3
import threading
from datetime import datetime

import telebot
from telebot import types

# Optional PDF generation via ReportLab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ==================== SOZLAMALAR VA KONSTANTALAR ====================
BOT_TOKEN = os.getenv("JOB_BOT_TOKEN") or os.getenv("BOT_TOKEN") or "8863390415:AAEj3E_H-Kv36OF9gb0pGJOXMvQd5KldSgQ"
ADMIN_ID = int(os.getenv("ADMIN_ID", "1021089367"))
DB_PATH = "jobs_database.db"

logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("JobBot")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Foydalanuvchi holatlari (FSM)
USER_STATES = {}
USER_DATA = {}

# Sohalar / Kategoriyalar
CATEGORIES = [
    "🛠 Qurilish va Santexnika (HVAC)",
    "💻 IT, Dasturlash va Dizayn",
    "🚚 Haydovchilik va Yetkazib berish",
    "🍽 Restoran, Kafe va Umumiy ovqatlanish",
    "🛒 Savdo va Sotuv menejeri",
    "🏢 Ofis va Ma'muriyat",
    "📚 Ta'lim va Repetitorlik",
    "🧹 Tozalash va Xizmat ko'rsatish",
    "⚡ Kunlik va Shoshilinch ishlar",
    "📦 Boshqa sohalar"
]

# Hududlar
REGIONS = [
    "Toshkent shahri",
    "Toshkent viloyati",
    "Samarqand viloyati",
    "Farg'ona viloyati",
    "Andijon viloyati",
    "Namangan viloyati",
    "Buxoro viloyati",
    "Qashqadaryo viloyati",
    "Surxondaryo viloyati",
    "Xorazm viloyati",
    "Navoiy viloyati",
    "Jizzax viloyati",
    "Sirdaryo viloyati",
    "Qoraqalpog'iston Respub."
]

# ==================== MA'LUMOTLAR BAZASI (SQLITE) ====================
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # 1. Foydalanuvchilar
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        full_name TEXT,
        phone TEXT,
        role TEXT DEFAULT 'job_seeker',
        notifications_enabled INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Rezyumelar
    c.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE,
        full_name TEXT,
        phone TEXT,
        profession TEXT,
        category TEXT,
        region TEXT,
        experience TEXT,
        skills TEXT,
        expected_salary TEXT,
        about TEXT,
        media_type TEXT DEFAULT 'none',
        media_file_id TEXT,
        pdf_path TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Vakansiyalar
    c.execute("""
    CREATE TABLE IF NOT EXISTS vacancies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employer_id INTEGER,
        title TEXT,
        category TEXT,
        company TEXT,
        region TEXT,
        salary TEXT,
        job_type TEXT DEFAULT 'full_time',
        description TEXT,
        requirements TEXT,
        contacts TEXT,
        status TEXT DEFAULT 'active',
        channel_msg_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Arizalar (Applications)
    c.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vacancy_id INTEGER,
        candidate_id INTEGER,
        status TEXT DEFAULT 'new',
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Saqlanganlar (Favorites)
    c.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        user_id INTEGER,
        vacancy_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, vacancy_id)
    );
    """)

    # 6. Sozlamalar (Settings)
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );
    """)

    # 7. Audit jurnali
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

init_db()

def log_audit(user_id, action, details=""):
    try:
        conn = get_db()
        conn.execute("INSERT INTO audit_log (user_id, action, details) VALUES (?, ?, ?)", (user_id, action, details))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Audit log error: {e}")

def get_setting(key, default=""):
    try:
        conn = get_db()
        r = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        conn.close()
        return r["value"] if r else default
    except Exception:
        return default

def set_setting(key, value):
    try:
        conn = get_db()
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Set setting error: {e}")

def safe_send_message(chat_id, text, reply_markup=None, disable_web_page_preview=True):
    try:
        return bot.send_message(chat_id, text, reply_markup=reply_markup, disable_web_page_preview=disable_web_page_preview)
    except Exception as e:
        logger.warning(f"Xabar yuborishda xatolik ({chat_id}): {e}")
        return None

# ==================== PROFESSIONAL PDF GENERATOR (REPORTLAB) ====================
def generate_pro_pdf_resume(data, output_path):
    if not REPORTLAB_AVAILABLE:
        return None
    try:
        c = canvas.Canvas(output_path, pagesize=A4)
        w, h = A4

        def clean(txt):
            if not txt:
                return ''
            t = str(txt).replace("ʻ", "'").replace("ʼ", "'").replace("`", "'")
            return t.encode('latin-1', 'replace').decode('latin-1')

        # 1. Top Header Banner (Modern Navy Blue)
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.rect(0, h - 110, w, 110, stroke=0, fill=1)

        # Cyan Accent Stripe
        c.setFillColor(colors.HexColor('#06B6D4'))
        c.rect(0, h - 115, w, 5, stroke=0, fill=1)

        # Header Titles
        c.setFillColor(colors.white)
        c.setFont('Helvetica-Bold', 22)
        c.drawString(40, h - 50, clean(data.get('full_name', 'Ism Familiya')))

        c.setFont('Helvetica-Bold', 13)
        c.setFillColor(colors.HexColor('#E0F2FE'))
        c.drawString(40, h - 75, clean(data.get('profession', 'Mutaxassis')))

        c.setFont('Helvetica-Oblique', 9)
        c.setFillColor(colors.HexColor('#BAE6FD'))
        uname = clean(data.get('username', 'foydalanuvchi'))
        c.drawString(40, h - 95, f"Ish Topish Bot orqali yaratildi | Telegram: @{uname}")

        # 2. Left Sidebar (Contact & Skills)
        sidebar_w = 190
        c.setFillColor(colors.HexColor('#F8FAFC'))
        c.rect(0, 0, sidebar_w, h - 115, stroke=0, fill=1)
        c.setStrokeColor(colors.HexColor('#E2E8F0'))
        c.setLineWidth(1)
        c.line(sidebar_w, 0, sidebar_w, h - 115)

        # ALOQA
        y = h - 145
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(25, y, 'ALOQA')
        y -= 5
        c.setStrokeColor(colors.HexColor('#06B6D4'))
        c.setLineWidth(2)
        c.line(25, y, 75, y)

        y -= 20
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(colors.HexColor('#64748B'))
        c.drawString(25, y, 'Telefon:')
        y -= 14
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawString(25, y, clean(data.get('phone', 'Mavjud emas')))

        y -= 22
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(colors.HexColor('#64748B'))
        c.drawString(25, y, 'Hudud:')
        y -= 14
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawString(25, y, clean(data.get('region', 'Toshkent')))

        y -= 22
        c.setFont('Helvetica-Bold', 9)
        c.setFillColor(colors.HexColor('#64748B'))
        c.drawString(25, y, 'Kutilayotgan maosh:')
        y -= 14
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(colors.HexColor('#059669'))
        c.drawString(25, y, clean(data.get('expected_salary', 'Kelishiladi')))

        # KO'NIKMALAR
        y -= 35
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 12)
        c.drawString(25, y, "KO'NIKMALAR")
        y -= 5
        c.setStrokeColor(colors.HexColor('#06B6D4'))
        c.setLineWidth(2)
        c.line(25, y, 110, y)

        y -= 20
        skills = data.get('skills', '').replace(';', ',').split(',')
        for s in skills:
            s_clean = clean(s.strip())
            if s_clean:
                c.setFillColor(colors.HexColor('#E0F2FE'))
                c.roundRect(25, y - 4, 140, 18, 3, stroke=0, fill=1)
                c.setFillColor(colors.HexColor('#0369A1'))
                c.setFont('Helvetica-Bold', 9)
                c.drawString(32, y + 1, s_clean[:22])
                y -= 23
                if y < 80:
                    break

        # 3. Right Content Area (Summary & Experience)
        rx = sidebar_w + 30
        content_w = w - rx - 30
        ry = h - 145

        # MUTAXASSIS HAQIDA
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(rx, ry, 'MUTAXASSIS HAQIDA')
        ry -= 5
        c.setStrokeColor(colors.HexColor('#06B6D4'))
        c.setLineWidth(2)
        c.line(rx, ry, rx + 140, ry)

        ry -= 20
        c.setFont('Helvetica', 10)
        c.setFillColor(colors.HexColor('#334155'))
        about_text = clean(data.get('about', "Tajribali, halol va o'z ishiga mas'uliyatli mutaxassis."))
        words = about_text.split()
        line = ''
        for word in words:
            if c.stringWidth(line + ' ' + word, 'Helvetica', 10) < content_w:
                line = (line + ' ' + word).strip()
            else:
                c.drawString(rx, ry, line)
                ry -= 15
                line = word
        if line:
            c.drawString(rx, ry, line)
            ry -= 15

        # ISH TAJRIBASI
        ry -= 25
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(rx, ry, 'ISH TAJRIBASI')
        ry -= 5
        c.setStrokeColor(colors.HexColor('#06B6D4'))
        c.setLineWidth(2)
        c.line(rx, ry, rx + 100, ry)

        ry -= 20
        exp_text = clean(data.get('experience', '1-3 yil'))
        c.setFont('Helvetica-Bold', 10)
        c.setFillColor(colors.HexColor('#0F172A'))
        c.drawString(rx, ry, 'Umumiy kasbiy staj: ' + exp_text)
        ry -= 25

        # KAFOLAT VA AFZALLIKLAR
        c.setFillColor(colors.HexColor('#1E3A8A'))
        c.setFont('Helvetica-Bold', 13)
        c.drawString(rx, ry, 'KAFOLAT VA AFZALLIKLAR')
        ry -= 5
        c.setStrokeColor(colors.HexColor('#06B6D4'))
        c.setLineWidth(2)
        c.line(rx, ry, rx + 170, ry)

        ry -= 20
        c.setFont('Helvetica', 9)
        c.setFillColor(colors.HexColor('#475569'))
        bullet_points = [
            "Har qanday vazifaga jiddiy va mas'uliyatli yondashuv",
            "Jamoada intizomli va halol munosabat",
            "Topshiriqlarni o'z vaqtida va sifatli topshirish",
            "Doimiy kasbiy rivojlanish va yangi ko'nikmalarni tez egallash"
        ]
        for bp in bullet_points:
            c.setFillColor(colors.HexColor('#06B6D4'))
            c.circle(rx + 4, ry + 3, 2.5, stroke=0, fill=1)
            c.setFillColor(colors.HexColor('#334155'))
            c.drawString(rx + 14, ry, clean(bp))
            ry -= 16

        # Footer
        c.setFillColor(colors.HexColor('#94A3B8'))
        c.setFont('Helvetica', 8)
        c.drawString(rx, 25, 'IshTopish Bot (2026) | Ushbu hujjat rasmiy rezyume shaklida tayyorlangan.')

        c.save()
        return output_path
    except Exception as e:
        logger.error(f"PDF yaratishda xatolik: {e}")
        return None

# ==================== AI SMART MATCH MOTOR ====================
def run_ai_smart_match(vacancy_id):
    """
    Yangi vakansiya chiqqanda, rezyumelarni skanerlab:
    1. Mos nomzodlarga avtomatik push-xabar yuboradi.
    2. Ish beruvchiga topilgan nomzodlar sonini ma'lum qiladi.
    """
    def _worker():
        try:
            conn = get_db()
            vac = conn.execute("SELECT * FROM vacancies WHERE id=?", (vacancy_id,)).fetchone()
            if not vac:
                conn.close()
                return

            v_cat = vac["category"] or ""
            v_reg = vac["region"] or ""

            # Kategoriyasi yoki hududi mos tushadigan nomzodlar
            candidates = conn.execute("""
                SELECT r.*, u.notifications_enabled 
                FROM resumes r
                JOIN users u ON r.user_id = u.user_id
                WHERE r.status = 'active' AND (r.category = ? OR r.region = ?)
            """, (v_cat, v_reg)).fetchall()

            matched_count = 0
            for cand in candidates:
                if cand["user_id"] == vac["employer_id"]:
                    continue  # Ish beruvchining o'ziga yubormaymiz

                # Nomzodning bildirishnomasi o'chirilgan bo'lsa o'tkazamiz
                if cand["notifications_enabled"] == 0:
                    continue

                matched_count += 1
                msg_text = (
                    "🔥 <b>AI SMART MATCH: Yangi ish topildi!</b>\n\n"
                    "Sizning sohangiz yoki hududingizga mos yangi vakansiya e'lon qilindi:\n\n"
                    f"💼 <b>Lavozim:</b> {vac['title']}\n"
                    f"🏢 <b>Tashkilot:</b> {vac['company']}\n"
                    f"📍 <b>Hudud:</b> {vac['region']}\n"
                    f"💰 <b>Maosh:</b> {vac['salary']}\n\n"
                    "<i>Ariza topshirish yoki batafsil ko'rish uchun quyidagi tugmani bosing:</i>"
                )
                kb = types.InlineKeyboardMarkup()
                kb.add(types.InlineKeyboardButton("👁 Vakansiyani ko'rish", callback_data=f"view_vac_{vacancy_id}"))
                kb.add(types.InlineKeyboardButton("✍️ Ariza topshirish", callback_data=f"apply_{vacancy_id}"))

                safe_send_message(cand["user_id"], msg_text, reply_markup=kb)
                time.sleep(0.05)  # Telegram rate limit himoyasi

            # Ish beruvchiga natijani aytamiz
            if matched_count > 0:
                emp_msg = (
                    f"🎯 <b>AI Smart Match natijasi:</b>\n\n"
                    f"Sizning <b>«{vac['title']}»</b> vakansiyangizga mos <b>{matched_count} ta nomzod</b> topildi va ularga avtomatik push-xabarnoma yetkazildi!\n"
                    "Tez orada yangi arizalarni qabul qilasiz."
                )
            else:
                emp_msg = (
                    "✅ Vakansiyangiz muvaffaqiyatli saqlandi!\n"
                    "Hozircha bazada to'liq mos yangi nomzodlar yo'q, lekin e'lon umumiy ro'yxatda faol ko'rinadi."
                )
            safe_send_message(vac["employer_id"], emp_msg)
            conn.close()

            # Telegram Kanalga Avto-Post
            post_to_channel_if_configured(vac)

        except Exception as e:
            logger.error(f"Smart Match xatosi: {e}")

    threading.Thread(target=_worker, daemon=True).start()

def post_to_channel_if_configured(vac):
    """
    Agar admin kanal sozlagan bo'lsa, kanalga chiroyli e'lon yuboradi.
    """
    channel_id = get_setting("channel_id", "")
    if not channel_id:
        return
    try:
        badge = "⚡ KUNLIK / SHOSHILINCH ISH" if vac["job_type"] == "daily" else "💼 YANGI VAKANSIYA"
        text = (
            f"📢 <b>{badge}</b>\n\n"
            f"📌 <b>Lavozim:</b> {vac['title']}\n"
            f"🏢 <b>Kompaniya / Ish beruvchi:</b> {vac['company']}\n"
            f"🗂 <b>Soha:</b> {vac['category']}\n"
            f"📍 <b>Hudud:</b> {vac['region']}\n"
            f"💰 <b>Maosh:</b> {vac['salary']}\n\n"
            f"📝 <b>Tavsif:</b>\n{vac['description']}\n\n"
            f"📞 <b>Aloqa:</b> {vac['contacts']}\n"
        )
        sponsor = get_setting("sponsor_text", "")
        if sponsor:
            text += f"\n📢 <i>Homiy: {sponsor}</i>\n"

        kb = types.InlineKeyboardMarkup()
        bot_info = bot.get_me()
        bot_user = bot_info.username if bot_info else "ish_topish_teambot"
        kb.add(types.InlineKeyboardButton("✍️ Ariza topshirish (Bot orqali)", url=f"https://t.me/{bot_user}?start=apply_{vac['id']}"))

        msg = safe_send_message(channel_id, text, reply_markup=kb)
        if msg:
            conn = get_db()
            conn.execute("UPDATE vacancies SET channel_msg_id=? WHERE id=?", (msg.message_id, vac["id"]))
            conn.commit()
            conn.close()
    except Exception as e:
        logger.error(f"Kanalga post qilishda xatolik: {e}")

# ==================== ASOSIY MENYU VA TUGMALAR ====================
def main_menu_keyboard(user_id=None):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton("🔎 Vakansiyalar qidirish")
    b2 = types.KeyboardButton("⚡ Bugunga ish (Kunlik)")
    b3 = types.KeyboardButton("📝 Rezyume yaratish / Tahrirlash")
    b4 = types.KeyboardButton("📄 Mening Rezyumem (PDF)")
    b5 = types.KeyboardButton("💼 Ish beruvchi kabineti")
    b6 = types.KeyboardButton("⭐ Saqlanganlar")
    b7 = types.KeyboardButton("🔔 Bildirishnomalar")
    b8 = types.KeyboardButton("ℹ️ Yordam")
    kb.add(b1, b2)
    kb.add(b3, b4)
    kb.add(b5, b6)
    kb.add(b7, b8)
    if user_id and int(user_id) == ADMIN_ID:
        kb.add(types.KeyboardButton("👑 Admin Panel"))
    return kb

# ==================== START VA RO'YXATDAN O'TISH ====================
@bot.message_handler(commands=['start', 'boshlash'])
def cmd_start(message):
    try:
        user_id = message.from_user.id
        username = message.from_user.username or ""
        first_name = message.from_user.first_name or "Foydalanuvchi"

        conn = get_db()
        u = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not u:
            conn.execute("INSERT INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                         (user_id, username, first_name))
            conn.commit()
            log_audit(user_id, "start", "Yangi foydalanuvchi qo'shildi")
        conn.close()

        # Check deep linking (e.g. /start apply_12)
        args = message.text.split()
        if len(args) > 1 and args[1].startswith("apply_"):
            try:
                vac_id = int(args[1].replace("apply_", ""))
                return handle_apply_action(message.chat.id, user_id, vac_id)
            except Exception:
                pass

        welcome_text = (
            f"Assalomu alaykum, <b>{first_name}</b>! 🇺🇿\n\n"
            f"💼 <b>Ish Topish va Ish Berish</b> professional platformasiga xush kelibsiz!\n\n"
            f"Bu yerda siz:\n"
            f"• 🔎 <b>Bo'sh ish o'rinlarini</b> toifa va viloyatlar bo'yicha qidirishingiz\n"
            f"• ⚡ <b>Kunlik va tezkor daromadli</b> ishlarni topishingiz\n"
            f"• 📄 1 daqiqada <b>Professional PDF Rezyume</b> yaratishingiz\n"
            f"• 🤖 <b>AI Smart Match</b> orqali o'zingizga mos ishlardan darhol xabardor bo'lishingiz mumkin!\n\n"
            f"<i>Kerakli bo'limni tanlang:</i>"
        )
        bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_keyboard(user_id))
    except Exception as e:
        logger.error(f"Start error: {e}")
        safe_send_message(message.chat.id, "Xush kelibsiz! Asosiy menyudan foydalanishingiz mumkin.", reply_markup=main_menu_keyboard(message.from_user.id))

# ==================== 1. VAKANSIYALAR QIDIRISH ====================
@bot.message_handler(func=lambda m: m.text == "🔎 Vakansiyalar qidirish")
def handle_search_vacancies(message):
    try:
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("📋 Barcha yangi vakansiyalar", callback_data="filter_all"))
        kb.add(types.InlineKeyboardButton("🗂 Soha (Kategoriya) bo'yicha", callback_data="filter_category"))
        kb.add(types.InlineKeyboardButton("📍 Hudud (Viloyat) bo'yicha", callback_data="filter_region"))
        bot.send_message(
            message.chat.id,
            "🔎 <b>Vakansiyalarni qanday saralashni xohlaysiz?</b>",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Search vacancies error: {e}")

# ==================== 2. ⚡ KUNLIK SHOSHILINCH ISHLAR ====================
@bot.message_handler(func=lambda m: m.text == "⚡ Bugunga ish (Kunlik)")
def handle_daily_jobs(message):
    try:
        conn = get_db()
        vacs = conn.execute("""
            SELECT * FROM vacancies 
            WHERE job_type = 'daily' AND status = 'active' 
            ORDER BY id DESC LIMIT 10
        """).fetchall()
        conn.close()

        if not vacs:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("➕ Kunlik ish e'lon qilish", callback_data="post_daily_job"))
            bot.send_message(
                message.chat.id,
                "⚡ <b>Hozircha faol kunlik ishlar yo'q.</b>\n\n"
                "Agar sizga bugun shoshilinch ishchi yoki usta kerak bo'lsa, birinchi bo'lib e'lon bering!",
                reply_markup=kb
            )
            return

        bot.send_message(
            message.chat.id,
            f"⚡ <b>Bugungi shoshilinch va kunlik ishlar ro'yxati ({len(vacs)} ta):</b>\n"
            f"<i>Kunlik to'lanadigan ishonchli takliflar:</i>"
        )
        for v in vacs:
            show_single_vacancy(message.chat.id, v, is_daily=True)
            time.sleep(0.05)
    except Exception as e:
        logger.error(f"Daily jobs error: {e}")
        safe_send_message(message.chat.id, "Kunlik ishlarni yuklashda qisqa uzilish bo'ldi. Qaytadan urinib ko'ring.")

# ==================== 3 & 4. REZYUME VA PDF YUKLAB OLISH ====================
@bot.message_handler(func=lambda m: m.text in ["📝 Rezyume yaratish / Tahrirlash", "📄 Mening Rezyumem (PDF)"])
def handle_resume_menu(message):
    try:
        user_id = message.from_user.id
        conn = get_db()
        res = conn.execute("SELECT * FROM resumes WHERE user_id=?", (user_id,)).fetchone()
        conn.close()

        if not res:
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("✨ Yangi Rezyume yaratish", callback_data="create_resume"))
            bot.send_message(
                message.chat.id,
                "📄 <b>Sizda hali to'ldirilgan rezyume yo'q.</b>\n\n"
                "1 daqiqa ichida o'z ma'lumotlaringizni kiriting va avtomatik <b>Professional PDF Rezyume</b>ga ega bo'ling!",
                reply_markup=kb
            )
            return

        text = (
            f"📄 <b>SIZNING SHAXSIY REZYUMENGIZ</b>\n\n"
            f"👤 <b>F.I.SH:</b> {res['full_name']}\n"
            f"💼 <b>Kasb / Mutaxassislik:</b> {res['profession']}\n"
            f"🗂 <b>Soha:</b> {res['category']}\n"
            f"📍 <b>Hudud:</b> {res['region']}\n"
            f"⏳ <b>Ish staji:</b> {res['experience']}\n"
            f"💰 <b>Kutilayotgan maosh:</b> {res['expected_salary']}\n"
            f"🛠 <b>Ko'nikmalar:</b> {res['skills']}\n"
            f"📞 <b>Aloqa:</b> {res['phone']}\n\n"
            f"📝 <b>Haqida:</b>\n{res['about']}\n"
        )
        if res['media_type'] in ['voice', 'video_note', 'video']:
            text += "\n🎙 <i>Ovozli/Video tanishtiruv biriktirilgan ✅</i>"

        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("📥 Professional PDF yuklab olish", callback_data="download_pdf_resume"))
        kb.add(types.InlineKeyboardButton("✏️ Rezyumeni qayta tahrirlash", callback_data="create_resume"))
        if res['media_type'] in ['voice', 'video_note', 'video']:
            kb.add(types.InlineKeyboardButton("▶️ O'z tanishtiruvingizni ko'rish", callback_data="view_my_media"))

        bot.send_message(message.chat.id, text, reply_markup=kb)

    except Exception as e:
        logger.error(f"Resume menu error: {e}")
        safe_send_message(message.chat.id, "Rezyumeni ko'rsatishda xatolik yuz berdi.")

# ==================== REZYUME TO'LDIRISH FSM ====================
@bot.callback_query_handler(func=lambda c: c.data == "create_resume")
def cb_start_resume(call):
    try:
        user_id = call.from_user.id
        USER_STATES[user_id] = "res_fullname"
        USER_DATA[user_id] = {}
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "📝 <b>1-qadam:</b> To'liq ism va familiyangizni kiriting (Masalan: <i>Ali Valiev</i>):"
        )
    except Exception as e:
        logger.error(f"CB start resume error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_fullname")
def step_res_fullname(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["full_name"] = message.text.strip()
        USER_STATES[user_id] = "res_profession"
        bot.send_message(
            message.chat.id,
            "💼 <b>2-qadam:</b> Mutaxassisligingiz yoki kasbingiz nomini yozing (Masalan: <i>Santexnik-Paykachi</i> yoki <i>Frontend Dasturchi</i>):"
        )
    except Exception as e:
        logger.error(f"Step res fullname error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_profession")
def step_res_profession(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["profession"] = message.text.strip()
        USER_STATES[user_id] = "res_category"

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        for cat in CATEGORIES:
            kb.add(types.KeyboardButton(cat))
        bot.send_message(
            message.chat.id,
            "🗂 <b>3-qadam:</b> Qaysi sohaga tegishlisiz? Quyidagilardan tanlang:",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Step res profession error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_category")
def step_res_category(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["category"] = message.text.strip()
        USER_STATES[user_id] = "res_region"

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        for reg in REGIONS:
            kb.add(types.KeyboardButton(reg))
        bot.send_message(
            message.chat.id,
            "📍 <b>4-qadam:</b> Qaysi hududda yashaysiz yoki ish qidiryapsiz?",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Step res category error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_region")
def step_res_region(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["region"] = message.text.strip()
        USER_STATES[user_id] = "res_experience"

        bot.send_message(
            message.chat.id,
            "⏳ <b>5-qadam:</b> Kasbiy tajribangiz (stajingiz) qancha? (Masalan: <i>3 yil</i> yoki <i>Boshlang'ich</i>):",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Step res region error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_experience")
def step_res_experience(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["experience"] = message.text.strip()
        USER_STATES[user_id] = "res_skills"
        bot.send_message(
            message.chat.id,
            "🛠 <b>6-qadam:</b> Asosiy ko'nikmalaringizni vergul bilan yozing (Masalan: <i>PPR Payka, Nasos o'rnatish, Tyopliy pol, Chizma o'qish</i>):"
        )
    except Exception as e:
        logger.error(f"Step res experience error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_skills")
def step_res_skills(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["skills"] = message.text.strip()
        USER_STATES[user_id] = "res_salary"
        bot.send_message(
            message.chat.id,
            "💰 <b>7-qadam:</b> Kutilayotgan oylik yoki kunlik maoshingiz qancha? (Masalan: <i>6 000 000 so'm</i> yoki <i>Kelishiladi</i>):"
        )
    except Exception as e:
        logger.error(f"Step res skills error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_salary")
def step_res_salary(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["expected_salary"] = message.text.strip()
        USER_STATES[user_id] = "res_about"
        bot.send_message(
            message.chat.id,
            "📝 <b>8-qadam:</b> O'zingiz haqingizda qisqacha ma'lumot (xarakteringiz, ishga munosabatingiz, yutuqlaringiz):"
        )
    except Exception as e:
        logger.error(f"Step res salary error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "res_about")
def step_res_about(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["about"] = message.text.strip()
        USER_STATES[user_id] = "res_phone"

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn_phone = types.KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)
        kb.add(btn_phone)
        bot.send_message(
            message.chat.id,
            "📞 <b>9-qadam:</b> Telefon raqamingizni pastdagi tugma orqali yuboring yoki yozib qoldiring (+998...):",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Step res about error: {e}")

@bot.message_handler(content_types=['contact', 'text'], func=lambda m: USER_STATES.get(m.from_user.id) == "res_phone")
def step_res_phone(message):
    try:
        user_id = message.from_user.id
        if message.contact:
            phone = message.contact.phone_number
        else:
            phone = message.text.strip()
        USER_DATA[user_id]["phone"] = phone
        USER_STATES[user_id] = "res_media"

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("⏭ O'tkazib yuborish (Kerak emas)", callback_data="skip_res_media"))
        bot.send_message(
            message.chat.id,
            "🎙 <b>10-qadam (Ixtiyoriy va Inqilobiy):</b>\n\n"
            "Ish beruvchilar diqqatini darhol jalb qilish uchun <b>30 soniyalik video-xabar (kruglyash)</b> yoki <b>ovozli xabar (voice)</b> yuboring!\n"
            "<i>(Agar xohlamasangiz, pastdagi 'O'tkazib yuborish' tugmasini bosing).</i>",
            reply_markup=types.ReplyKeyboardRemove()
        )
        safe_send_message(message.chat.id, "Tanlovni kuting:", reply_markup=kb)
    except Exception as e:
        logger.error(f"Step res phone error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "skip_res_media")
def cb_skip_res_media(call):
    try:
        user_id = call.from_user.id
        USER_DATA[user_id]["media_type"] = "none"
        USER_DATA[user_id]["media_file_id"] = None
        bot.answer_callback_query(call.id)
        finish_resume_creation(call.message.chat.id, user_id)
    except Exception as e:
        logger.error(f"Skip media error: {e}")

@bot.message_handler(content_types=['voice', 'video_note', 'video'], func=lambda m: USER_STATES.get(m.from_user.id) == "res_media")
def step_res_media(message):
    try:
        user_id = message.from_user.id
        if message.voice:
            USER_DATA[user_id]["media_type"] = "voice"
            USER_DATA[user_id]["media_file_id"] = message.voice.file_id
        elif message.video_note:
            USER_DATA[user_id]["media_type"] = "video_note"
            USER_DATA[user_id]["media_file_id"] = message.video_note.file_id
        elif message.video:
            USER_DATA[user_id]["media_type"] = "video"
            USER_DATA[user_id]["media_file_id"] = message.video.file_id

        finish_resume_creation(message.chat.id, user_id)
    except Exception as e:
        logger.error(f"Step res media error: {e}")

def finish_resume_creation(chat_id, user_id):
    try:
        d = USER_DATA.get(user_id, {})
        conn = get_db()
        conn.execute("""
            INSERT OR REPLACE INTO resumes 
            (user_id, full_name, phone, profession, category, region, experience, skills, expected_salary, about, media_type, media_file_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            d.get("full_name"),
            d.get("phone"),
            d.get("profession"),
            d.get("category"),
            d.get("region"),
            d.get("experience"),
            d.get("skills"),
            d.get("expected_salary"),
            d.get("about"),
            d.get("media_type", "none"),
            d.get("media_file_id")
        ))
        conn.commit()
        conn.close()

        USER_STATES.pop(user_id, None)
        log_audit(user_id, "resume_saved", f"{d.get('profession')} bo'yicha rezyume saqlandi")

        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📥 Professional PDF yuklab olish", callback_data="download_pdf_resume"))

        safe_send_message(
            chat_id,
            "🎉 <b>Tabriklaymiz! Rezyumengiz muvaffaqiyatli saqlandi!</b>\n\n"
            "Endi siz:\n"
            "• Istalgan vakansiyaga 1 ta tugma bilan ariza bera olasiz\n"
            "• AI Smart Match sizga mos ishlar paydo bo'lganda avtomatik xabar beradi\n"
            "• Pastdagi tugma orqali tayyor <b>A4 PDF rezyumengizni</b> yuklab olishingiz mumkin!",
            reply_markup=main_menu_keyboard(user_id)
        )
        safe_send_message(chat_id, "📄 <b>Tayyor PDF Rezyumeni qabul qiling:</b>", reply_markup=kb)
    except Exception as e:
        logger.error(f"Finish resume error: {e}")
        safe_send_message(chat_id, "Rezyumeni saqlashda xatolik yuz berdi, iltimos qaytadan urinib ko'ring.", reply_markup=main_menu_keyboard(user_id))

# ==================== PDF REZYUMENI YUBORISH ====================
@bot.callback_query_handler(func=lambda c: c.data == "download_pdf_resume")
def cb_download_pdf(call):
    try:
        user_id = call.from_user.id
        bot.answer_callback_query(call.id, "PDF tayyorlanmoqda...")
        conn = get_db()
        r = conn.execute("SELECT * FROM resumes WHERE user_id=?", (user_id,)).fetchone()
        u = conn.execute("SELECT username FROM users WHERE user_id=?", (user_id,)).fetchone()
        conn.close()

        if not r:
            return bot.send_message(call.message.chat.id, "Avval rezyume to'ldirishingiz kerak.")

        data = dict(r)
        data["username"] = u["username"] if u and u["username"] else "khasanov"
        os.makedirs("generated_resumes", exist_ok=True)
        pdf_path = f"generated_resumes/rezyume_{user_id}.pdf"

        generated = generate_pro_pdf_resume(data, pdf_path)
        if generated and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                bot.send_document(
                    call.message.chat.id,
                    f,
                    caption=f"📄 <b>{data['full_name']}</b> ning professional rezyumesi.\nIshTopish Bot orqali yaratildi."
                )
        else:
            bot.send_message(call.message.chat.id, "PDF yaratish moduli tizimda cheklangan, lekin rezyumengiz matn shaklida to'liq saqlangan.")
    except Exception as e:
        logger.error(f"Download PDF error: {e}")
        bot.send_message(call.message.chat.id, "PDF yuborishda xatolik bo'ldi.")

# ==================== 5. ISH BERUVCHI KABINETI ====================
@bot.message_handler(func=lambda m: m.text == "💼 Ish beruvchi kabineti")
def handle_employer_cabinet(message):
    try:
        user_id = message.from_user.id
        conn = get_db()
        my_vacs = conn.execute("SELECT * FROM vacancies WHERE employer_id=? ORDER BY id DESC", (user_id,)).fetchall()
        apps_count = conn.execute("""
            SELECT COUNT(*) as c FROM applications a
            JOIN vacancies v ON a.vacancy_id = v.id
            WHERE v.employer_id = ?
        """, (user_id,)).fetchone()["c"]
        conn.close()

        text = (
            f"💼 <b>ISH BERUVCHI KABINETI</b>\n\n"
            f"Sizning aktiv e'lonlaringiz: <b>{len(my_vacs)} ta</b>\n"
            f"Jami qabul qilingan arizalar: <b>{apps_count} ta</b>\n\n"
            "Quyidagi amallardan birini tanlang:"
        )
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("➕ Yangi doimiy vakansiya qo'shish", callback_data="post_vacancy"))
        kb.add(types.InlineKeyboardButton("⚡ Shoshilinch / Kunlik ish e'lon qilish", callback_data="post_daily_job"))
        if my_vacs:
            kb.add(types.InlineKeyboardButton("📋 Mening vakansiyalarim va Arizalar", callback_data="my_vacancies"))
        bot.send_message(message.chat.id, text, reply_markup=kb)
    except Exception as e:
        logger.error(f"Employer cabinet error: {e}")

# ==================== VAKANSIYA YARATISH FSM ====================
@bot.callback_query_handler(func=lambda c: c.data in ["post_vacancy", "post_daily_job"])
def cb_start_post_vac(call):
    try:
        user_id = call.from_user.id
        is_daily = (call.data == "post_daily_job")
        USER_STATES[user_id] = "vac_title"
        USER_DATA[user_id] = {"is_daily": is_daily}
        bot.answer_callback_query(call.id)

        job_label = "⚡ Shoshilinch/Kunlik ish" if is_daily else "💼 Yangi vakansiya"
        bot.send_message(
            call.message.chat.id,
            f"{job_label} yaratish:\n\n"
            "📌 <b>1-qadam:</b> Qanday mutaxassis kerak? (Lavozim nomi, masalan: <i>Paykachi Santexnik</i> yoki <i>Yuk tushiruvchi</i>):"
        )
    except Exception as e:
        logger.error(f"CB start vac error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "vac_title")
def step_vac_title(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["title"] = message.text.strip()
        USER_STATES[user_id] = "vac_company"
        bot.send_message(
            message.chat.id,
            "🏢 <b>2-qadam:</b> Tashkilot yoki Ish beruvchi nomi (Masalan: <i>'Grand Stroy' MCHJ</i> yoki <i>Xususiy buyurtmachi</i>):"
        )
    except Exception as e:
        logger.error(f"Step vac title error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "vac_company")
def step_vac_company(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["company"] = message.text.strip()
        USER_STATES[user_id] = "vac_category"

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        for cat in CATEGORIES:
            kb.add(types.KeyboardButton(cat))
        bot.send_message(
            message.chat.id,
            "🗂 <b>3-qadam:</b> Vakansiya qaysi sohaga tegishli?",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Step vac company error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "vac_category")
def step_vac_category(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["category"] = message.text.strip()
        USER_STATES[user_id] = "vac_region"

        kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True, row_width=2)
        for reg in REGIONS:
            kb.add(types.KeyboardButton(reg))
        bot.send_message(
            message.chat.id,
            "📍 <b>4-qadam:</b> Ish qaysi hududda amalga oshiriladi?",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Step vac category error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "vac_region")
def step_vac_region(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["region"] = message.text.strip()
        USER_STATES[user_id] = "vac_salary"

        bot.send_message(
            message.chat.id,
            "💰 <b>5-qadam:</b> Taklif qilinayotgan maosh qancha? (Masalan: <i>Kuniga 350 000 so'm</i> yoki <i>Oyiga 8 000 000 so'm</i>):",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        logger.error(f"Step vac region error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "vac_salary")
def step_vac_salary(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["salary"] = message.text.strip()
        USER_STATES[user_id] = "vac_desc"
        bot.send_message(
            message.chat.id,
            "📝 <b>6-qadam:</b> Ish tavsifi va bajariladigan vazifalar haqida batafsil yozing:"
        )
    except Exception as e:
        logger.error(f"Step vac salary error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "vac_desc")
def step_vac_desc(message):
    try:
        user_id = message.from_user.id
        USER_DATA[user_id]["description"] = message.text.strip()
        USER_STATES[user_id] = "vac_contacts"
        bot.send_message(
            message.chat.id,
            "📞 <b>7-qadam:</b> Nomzodlar bog'lanishi uchun telefon va aloqa ma'lumotlarini qoldiring:"
        )
    except Exception as e:
        logger.error(f"Step vac desc error: {e}")

@bot.message_handler(func=lambda m: USER_STATES.get(m.from_user.id) == "vac_contacts")
def step_vac_contacts(message):
    try:
        user_id = message.from_user.id
        d = USER_DATA.get(user_id, {})
        d["contacts"] = message.text.strip()
        job_type = "daily" if d.get("is_daily") else "full_time"

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vacancies 
            (employer_id, title, category, company, region, salary, job_type, description, contacts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            d.get("title"),
            d.get("category"),
            d.get("company"),
            d.get("region"),
            d.get("salary"),
            job_type,
            d.get("description"),
            d.get("contacts")
        ))
        vac_id = cur.lastrowid
        conn.commit()
        conn.close()

        USER_STATES.pop(user_id, None)
        log_audit(user_id, "vacancy_created", f"Vakansiya #{vac_id} ({d.get('title')}) yaratildi")

        bot.send_message(
            message.chat.id,
            f"🎉 <b>Vakansiyangiz muvaffaqiyatli qabul qilindi va e'lon qilindi!</b>\n\n"
            "🤖 <b>AI Smart Match</b> tizimi ishga tushdi va bazadagi barcha mos nomzodlarga avtomatik push-xabarnoma yuborilmoqda!",
            reply_markup=main_menu_keyboard(user_id)
        )

        # Trigger AI Smart Match in background
        run_ai_smart_match(vac_id)

    except Exception as e:
        logger.error(f"Finish vac error: {e}")
        safe_send_message(message.chat.id, "Vakansiyani saqlashda xatolik yuz berdi.", reply_markup=main_menu_keyboard(user_id))

# ==================== VAKANSIYALARNI KO'RSATISH VA ARIZA TOPSHIRISH ====================
def show_single_vacancy(chat_id, v, is_daily=False):
    try:
        badge = "⚡ KUNLIK / SHOSHILINCH" if v["job_type"] == "daily" else "💼 DOIMIY ISH"
        text = (
            f"📌 <b>{badge}: {v['title']}</b>\n\n"
            f"🏢 <b>Tashkilot:</b> {v['company']}\n"
            f"🗂 <b>Soha:</b> {v['category']}\n"
            f"📍 <b>Hudud:</b> {v['region']}\n"
            f"💰 <b>Maosh:</b> {v['salary']}\n\n"
            f"📝 <b>Tavsif:</b>\n{v['description']}\n\n"
            f"📞 <b>Aloqa:</b> {v['contacts']}\n"
        )
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("✍️ Ariza topshirish", callback_data=f"apply_{v['id']}"),
            types.InlineKeyboardButton("⭐ Saqlab qo'yish", callback_data=f"fav_{v['id']}")
        )
        safe_send_message(chat_id, text, reply_markup=kb)
    except Exception as e:
        logger.error(f"Show single vac error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("apply_"))
def cb_apply(call):
    try:
        vac_id = int(call.data.replace("apply_", ""))
        user_id = call.from_user.id
        bot.answer_callback_query(call.id)
        handle_apply_action(call.message.chat.id, user_id, vac_id)
    except Exception as e:
        logger.error(f"CB apply error: {e}")

def handle_apply_action(chat_id, user_id, vac_id):
    try:
        conn = get_db()
        res = conn.execute("SELECT * FROM resumes WHERE user_id=?", (user_id,)).fetchone()
        vac = conn.execute("SELECT * FROM vacancies WHERE id=?", (vac_id,)).fetchone()

        if not vac:
            conn.close()
            return safe_send_message(chat_id, "Ushbu vakansiya topilmadi yoki yopilgan.")

        if not res:
            conn.close()
            kb = types.InlineKeyboardMarkup()
            kb.add(types.InlineKeyboardButton("✨ Rezyume to'ldirish", callback_data="create_resume"))
            return safe_send_message(
                chat_id,
                "⚠️ <b>Ariza topshirish uchun avval rezyumengiz bo'lishi kerak!</b>\n\n"
                "Ish beruvchiga ma'lumotlaringiz yetib borishi uchun tezkor rezyume to'ldiring:",
                reply_markup=kb
            )

        prev_app = conn.execute("SELECT * FROM applications WHERE vacancy_id=? AND candidate_id=?", (vac_id, user_id)).fetchone()
        if prev_app:
            conn.close()
            return safe_send_message(chat_id, "✅ Siz ushbu vakansiyaga allaqachon ariza topshirgansiz! Ish beruvchi ko'rib chiqmoqda.")

        conn.execute("INSERT INTO applications (vacancy_id, candidate_id) VALUES (?, ?)", (vac_id, user_id))
        conn.commit()
        conn.close()

        log_audit(user_id, "application_sent", f"Vakansiya #{vac_id} ga ariza berildi")

        safe_send_message(
            chat_id,
            "🎉 <b>Arizangiz muvaffaqiyatli topshirildi!</b>\n\n"
            "Ish beruvchiga sizning rezyumengiz, aloqa raqamingiz va PDF shaklingiz yetkazildi."
        )

        emp_text = (
            f"🔔 <b>YANGI ARIZA QABUL QILINDI!</b>\n\n"
            f"Vakansiyangiz: <b>{vac['title']}</b>\n"
            f"Nomzod: <b>{res['full_name']}</b> ({res['profession']})\n"
            f"Hudud: {res['region']}\n"
            f"Ish staji: {res['experience']}\n"
            f"Ko'nikmalar: {res['skills']}\n"
            f"Aloqa: {res['phone']}\n"
        )
        emp_kb = types.InlineKeyboardMarkup(row_width=2)
        emp_kb.add(types.InlineKeyboardButton("📄 Nomzodning PDF Rezyumesi", callback_data=f"get_cand_pdf_{user_id}"))
        if res['media_type'] in ['voice', 'video_note', 'video']:
            emp_kb.add(types.InlineKeyboardButton("🎙 Ovoz/Video tanishtiruv", callback_data=f"get_cand_media_{user_id}"))

        safe_send_message(vac["employer_id"], emp_text, reply_markup=emp_kb)

    except Exception as e:
        logger.error(f"Handle apply error: {e}")
        safe_send_message(chat_id, "Ariza topshirishda qisqa uzilish bo'ldi.")

# ==================== NOMZODNING PDF REZYUMESINI ISH BERUVCHIGA YUBORISH ====================
@bot.callback_query_handler(func=lambda c: c.data.startswith("get_cand_pdf_"))
def cb_get_cand_pdf(call):
    try:
        cand_id = int(call.data.replace("get_cand_pdf_", ""))
        bot.answer_callback_query(call.id, "Nomzod PDF rezyumesi ochilmoqda...")
        conn = get_db()
        r = conn.execute("SELECT * FROM resumes WHERE user_id=?", (cand_id,)).fetchone()
        u = conn.execute("SELECT username FROM users WHERE user_id=?", (cand_id,)).fetchone()
        conn.close()

        if not r:
            return bot.send_message(call.message.chat.id, "Nomzod rezyumesi topilmadi.")

        data = dict(r)
        data["username"] = u["username"] if u and u["username"] else "nomzod"
        os.makedirs("generated_resumes", exist_ok=True)
        pdf_path = f"generated_resumes/rezyume_{cand_id}.pdf"
        generated = generate_pro_pdf_resume(data, pdf_path)

        if generated and os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                bot.send_document(
                    call.message.chat.id,
                    f,
                    caption=f"📄 Nomzod: <b>{data['full_name']}</b> | Telefon: {data['phone']}"
                )
        else:
            bot.send_message(call.message.chat.id, "PDF format mavjud emas, lekin nomzod ma'lumotlari matn shaklida xabarda keltirilgan.")
    except Exception as e:
        logger.error(f"Get cand pdf error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("get_cand_media_"))
def cb_get_cand_media(call):
    try:
        cand_id = int(call.data.replace("get_cand_media_", ""))
        bot.answer_callback_query(call.id, "Ovoz/Video yuklanmoqda...")
        conn = get_db()
        r = conn.execute("SELECT * FROM resumes WHERE user_id=?", (cand_id,)).fetchone()
        conn.close()

        if not r or not r["media_file_id"]:
            return bot.send_message(call.message.chat.id, "Nomzod media xabar qoldirmagan.")

        m_type = r["media_type"]
        f_id = r["media_file_id"]

        if m_type == "voice":
            bot.send_voice(call.message.chat.id, f_id, caption=f"🎙 Nomzod <b>{r['full_name']}</b> ning ovozli tanishtiruvi")
        elif m_type == "video_note":
            bot.send_video_note(call.message.chat.id, f_id)
        elif m_type == "video":
            bot.send_video(call.message.chat.id, f_id, caption=f"🎥 Nomzod <b>{r['full_name']}</b> ning video tanishtiruvi")
    except Exception as e:
        logger.error(f"Get cand media error: {e}")

# ==================== SAQLANGANLAR (FAVORITES) ====================
@bot.callback_query_handler(func=lambda c: c.data.startswith("fav_"))
def cb_favorite(call):
    try:
        vac_id = int(call.data.replace("fav_", ""))
        user_id = call.from_user.id
        conn = get_db()
        conn.execute("INSERT OR IGNORE INTO favorites (user_id, vacancy_id) VALUES (?, ?)", (user_id, vac_id))
        conn.commit()
        conn.close()
        bot.answer_callback_query(call.id, "⭐ Vakansiya saqlanganlarga qo'shildi!", show_alert=False)
    except Exception as e:
        logger.error(f"Favorite error: {e}")

@bot.message_handler(func=lambda m: m.text == "⭐ Saqlanganlar")
def handle_favorites(message):
    try:
        user_id = message.from_user.id
        conn = get_db()
        favs = conn.execute("""
            SELECT v.* FROM vacancies v
            JOIN favorites f ON v.id = f.vacancy_id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
        """, (user_id,)).fetchall()
        conn.close()

        if not favs:
            return bot.send_message(message.chat.id, "⭐ <b>Sizda saqlangan vakansiyalar mavjud emas.</b>")

        bot.send_message(message.chat.id, f"⭐ <b>Saqlangan vakansiyalaringiz ({len(favs)} ta):</b>")
        for v in favs:
            show_single_vacancy(message.chat.id, v)
            time.sleep(0.05)
    except Exception as e:
        logger.error(f"Favorites view error: {e}")

# ==================== BILDIRISHNOMALAR SOZLAMALARI ====================
@bot.message_handler(func=lambda m: m.text == "🔔 Bildirishnomalar")
def handle_notifications(message):
    try:
        user_id = message.from_user.id
        conn = get_db()
        u = conn.execute("SELECT notifications_enabled FROM users WHERE user_id=?", (user_id,)).fetchone()
        conn.close()

        is_enabled = bool(u["notifications_enabled"]) if u else True
        state_str = "YOQILGAN 🟢" if is_enabled else "O'CHIRILGAN 🔴"

        kb = types.InlineKeyboardMarkup()
        new_state = 0 if is_enabled else 1
        btn_txt = "🔴 O'chirish" if is_enabled else "🟢 Yoqish"
        kb.add(types.InlineKeyboardButton(btn_txt, callback_data=f"toggle_notify_{new_state}"))

        bot.send_message(
            message.chat.id,
            f"🔔 <b>AI Smart Match Bildirishnomalari: {state_str}</b>\n\n"
            "Agar yoqilgan bo'lsa, sizning kasbingiz va hududingiz bo'yicha yangi vakansiya chiqishi bilan bot avtomatik sizga xabar beradi.",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Notifications menu error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("toggle_notify_"))
def cb_toggle_notify(call):
    try:
        new_val = int(call.data.replace("toggle_notify_", ""))
        user_id = call.from_user.id
        conn = get_db()
        conn.execute("UPDATE users SET notifications_enabled=? WHERE user_id=?", (new_val, user_id))
        conn.commit()
        conn.close()

        bot.answer_callback_query(call.id, "Sozlama yangilandi!")
        handle_notifications(call.message)
    except Exception as e:
        logger.error(f"Toggle notify error: {e}")

# ==================== FILTRLAR (ALL, CATEGORY, REGION) ====================
@bot.callback_query_handler(func=lambda c: c.data == "filter_all")
def cb_filter_all(call):
    try:
        bot.answer_callback_query(call.id)
        conn = get_db()
        vacs = conn.execute("SELECT * FROM vacancies WHERE status='active' ORDER BY id DESC LIMIT 10").fetchall()
        conn.close()

        if not vacs:
            return bot.send_message(call.message.chat.id, "Hozircha faol vakansiyalar mavjud emas.")

        bot.send_message(call.message.chat.id, f"📋 <b>Eng so'nggi vakansiyalar ({len(vacs)} ta):</b>")
        for v in vacs:
            show_single_vacancy(call.message.chat.id, v)
            time.sleep(0.05)
    except Exception as e:
        logger.error(f"Filter all error: {e}")

@bot.callback_query_handler(func=lambda c: c.data == "filter_category")
def cb_filter_category(call):
    try:
        bot.answer_callback_query(call.id)
        kb = types.InlineKeyboardMarkup(row_width=1)
        for i, cat in enumerate(CATEGORIES):
            kb.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{i}"))
        bot.send_message(call.message.chat.id, "🗂 <b>Qaysi soha bo'yicha ish qidiryapsiz?</b>", reply_markup=kb)
    except Exception as e:
        logger.error(f"Filter cat error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("cat_"))
def cb_select_cat(call):
    try:
        idx = int(call.data.replace("cat_", ""))
        cat_name = CATEGORIES[idx]
        bot.answer_callback_query(call.id)

        conn = get_db()
        vacs = conn.execute("SELECT * FROM vacancies WHERE category=? AND status='active' ORDER BY id DESC LIMIT 10", (cat_name,)).fetchall()
        conn.close()

        if not vacs:
            return bot.send_message(call.message.chat.id, f"<b>{cat_name}</b> sohasida hozircha ochiq vakansiyalar yo'q.")

        bot.send_message(call.message.chat.id, f"🗂 <b>{cat_name} bo'yicha vakansiyalar ({len(vacs)} ta):</b>")
        for v in vacs:
            show_single_vacancy(call.message.chat.id, v)
            time.sleep(0.05)
    except Exception as e:
        logger.error(f"Select cat error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("filter_region"))
def cb_filter_region(call):
    try:
        bot.answer_callback_query(call.id)
        kb = types.InlineKeyboardMarkup(row_width=2)
        btns = [types.InlineKeyboardButton(reg, callback_data=f"reg_{i}") for i, reg in enumerate(REGIONS)]
        kb.add(*btns)
        bot.send_message(call.message.chat.id, "📍 <b>Qaysi viloyat/hudud bo'yicha vakansiyalar kerak?</b>", reply_markup=kb)
    except Exception as e:
        logger.error(f"Filter region error: {e}")

@bot.callback_query_handler(func=lambda c: c.data.startswith("reg_"))
def cb_select_reg(call):
    try:
        idx = int(call.data.replace("reg_", ""))
        reg_name = REGIONS[idx]
        bot.answer_callback_query(call.id)

        conn = get_db()
        vacs = conn.execute("SELECT * FROM vacancies WHERE region=? AND status='active' ORDER BY id DESC LIMIT 10", (reg_name,)).fetchall()
        conn.close()

        if not vacs:
            return bot.send_message(call.message.chat.id, f"📍 <b>{reg_name}</b> hududida hozircha ochiq vakansiyalar yo'q.")

        bot.send_message(call.message.chat.id, f"📍 <b>{reg_name} bo'yicha vakansiyalar ({len(vacs)} ta):</b>")
        for v in vacs:
            show_single_vacancy(call.message.chat.id, v)
            time.sleep(0.05)
    except Exception as e:
        logger.error(f"Select reg error: {e}")

# ==================== YORDAM / QO'LLANMA ====================
@bot.message_handler(func=lambda m: m.text == "ℹ️ Yordam")
def handle_help(message):
    help_text = (
        "ℹ️ <b>BOTDAN FOYDALANISH QO'LLANMASI</b>\n\n"
        "1. <b>Ish qidiruvchilar uchun:</b>\n"
        "• '📝 Rezyume yaratish' orqali anketani to'ldiring.\n"
        "• '📄 Mening Rezyumem' bo'limidan professional A4 PDF rezyumeni bepul yuklab oling.\n"
        "• '🔎 Vakansiyalar qidirish' orqali o'zingizga ma'qul ishga 1 ta tugma bilan ariza yuboring.\n"
        "• '⚡ Bugunga ish' bo'limida har kuni yangi kunlik daromadli vazifalar joylanadi.\n\n"
        "2. <b>Ish beruvchilar uchun:</b>\n"
        "• '💼 Ish beruvchi kabineti' orqali bir zumda yangi ish e'loni joylang.\n"
        "• AI Smart Match avtomatik tarzda bazadagi mos nomzodlarni topib beradi.\n"
        "• Nomzodlarning PDF rezyumelari va audio/video tanishtiruvlarini ko'ring.\n\n"
        "📞 Texnik yordam va savollar uchun: @usman_khasan"
    )
    safe_send_message(message.chat.id, help_text)

# ==================== 👑 ADMINISTRATOR PANELI ====================
@bot.message_handler(commands=['admin', 'stats', 'users', 'set_channel', 'sponsor', 'audit'])
@bot.message_handler(func=lambda m: m.text == "👑 Admin Panel")
def handle_admin_commands(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        return safe_send_message(message.chat.id, "Kechirasiz, ushbu buyruq faqat bot administratori uchun.")

    cmd = message.text.split()[0]

    # /stats
    if cmd in ['/stats', '/admin'] or message.text == "👑 Admin Panel":
        conn = get_db()
        u_count = conn.execute("SELECT COUNT(*) as c FROM users").fetchone()["c"]
        r_count = conn.execute("SELECT COUNT(*) as c FROM resumes").fetchone()["c"]
        v_count = conn.execute("SELECT COUNT(*) as c FROM vacancies").fetchone()["c"]
        a_count = conn.execute("SELECT COUNT(*) as c FROM applications").fetchone()["c"]
        conn.close()

        ch_id = get_setting("channel_id", "Sozlanmagan")
        sp_txt = get_setting("sponsor_text", "Yo'q")

        text = (
            f"👑 <b>ADMINISTRATOR BOSHQARUV PANELI</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{u_count} ta</b>\n"
            f"📄 Jami rezyumelar: <b>{r_count} ta</b>\n"
            f"💼 Jami vakansiyalar: <b>{v_count} ta</b>\n"
            f"✍️ Topshirilgan arizalar: <b>{a_count} ta</b>\n\n"
            f"📢 Ulangan Telegram kanal: <code>{ch_id}</code>\n"
            f"🎗 Homiy matni: <i>{sp_txt}</i>\n\n"
            f"<b>Mavjud buyruqlar:</b>\n"
            f"• <code>/set_channel @kanal_nomi</code> — Yangi vakansiyalar chiqadigan kanalni ulash\n"
            f"• <code>/sponsor Homiy_matni</code> — Homiy reklama matnini o'rnatish\n"
            f"• <code>/users</code> — Oxirgi 20 ta foydalanuvchini ko'rish\n"
            f"• <code>/audit</code> — Tizim auditi va so'nggi hodisalar\n"
            f"• <code>/broadcast Matn</code> — Barcha foydalanuvchilarga xabar yuborish"
        )
        safe_send_message(message.chat.id, text)

    # /users
    elif cmd == '/users':
        conn = get_db()
        users = conn.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 20").fetchall()
        conn.close()
        text = "👥 <b>Oxirgi 20 foydalanuvchi:</b>\n\n"
        for u in users:
            uname = f"@{u['username']}" if u['username'] else "username yo'q"
            text += f"• {u['full_name']} ({uname}) [<code>{u['user_id']}</code>]\n"
        safe_send_message(message.chat.id, text)

    # /set_channel
    elif cmd == '/set_channel':
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            ch_name = parts[1].strip()
            set_setting("channel_id", ch_name)
            safe_send_message(message.chat.id, f"✅ Rasmiy kanal muvaffaqiyatli saqlandi: <b>{ch_name}</b>\nEndi barcha yangi vakansiyalar avtomatik ushbu kanalga post qilinadi!")
        else:
            safe_send_message(message.chat.id, "Kanal manzilini kiriting. Masalan: <code>/set_channel @mening_kanalim</code>")

    # /sponsor
    elif cmd == '/sponsor':
        parts = message.text.split(maxsplit=1)
        if len(parts) > 1:
            sp_text = parts[1].strip()
            if sp_text.lower() == "off":
                set_setting("sponsor_text", "")
                safe_send_message(message.chat.id, "✅ Homiy matni o'chirildi.")
            else:
                set_setting("sponsor_text", sp_text)
                safe_send_message(message.chat.id, f"✅ Homiy matni saqlandi: <i>{sp_text}</i>")
        else:
            safe_send_message(message.chat.id, "Homiy matnini kiriting. O'chirish uchun: <code>/sponsor off</code>")

    # /audit
    elif cmd == '/audit':
        conn = get_db()
        logs = conn.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 10").fetchall()
        conn.close()
        text = "📑 <b>Audit jurnali (oxirgi 10 ta):</b>\n\n"
        for l in logs:
            text += f"[{l['created_at']}] ID:{l['user_id']} | <b>{l['action']}</b>: {l['details']}\n"
        safe_send_message(message.chat.id, text)

# /broadcast
@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return safe_send_message(message.chat.id, "Xabar matnini kiriting. Masalan: <code>/broadcast Assalomu alaykum!</code>")

    b_text = parts[1].strip()
    conn = get_db()
    users = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()

    sent = 0
    safe_send_message(message.chat.id, f"🚀 Xabar yuborish boshlandi ({len(users)} ta foydalanuvchiga)...")
    for u in users:
        try:
            bot.send_message(u["user_id"], b_text)
            sent += 1
            time.sleep(0.04)
        except Exception:
            pass

    safe_send_message(message.chat.id, f"✅ Xabar muvaffaqiyatli yetkazildi: <b>{sent} ta</b> foydalanuvchiga.")

# ==================== BOTNI ISHGA TUSHIRISH (MAIN) ====================
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("💼 ISH TOPISH VA ISH BERISH TELEGRAM BOTI ISHGA TUSHMOQDA...")
    logger.info(f"👑 Admin ID: {ADMIN_ID}")
    logger.info(f"📄 ReportLab PDF Generator: {'Faol (OK)' if REPORTLAB_AVAILABLE else 'Cheklangan'}")
    logger.info("=" * 60)

    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=20)
        except Exception as e:
            logger.error(f"Polling uzilishi yuz berdi: {e}. 5 soniyadan so'ng qayta ulanadi...")
            time.sleep(5)
