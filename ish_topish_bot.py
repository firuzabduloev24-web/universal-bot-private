#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
💼 UNIVERSAL ISH TOPISH VA XODIM YOLOVCHI MEGA TELEGRAM BOT 💼
=============================================================================
Bot rasmiy manzili: https://t.me/universal_IshTop (@universal_IshTop)
Bosh Administrator & Muallif: @usman_khasan (Telegram ID: 1021089367)

Asosiy imkoniyatlar:
1. 🏢 Ish beruvchilar uchun:
   - Vakansiyalarni qulay bosqichma-bosqich wizard orqali kiritish.
   - KANALGA AVTOMATIK JOYLASHTIRISH: Har bir yangi vakansiya rasmiy Telegram
     kanaliga zamonaviy ko'rinishda, inline ariza topshirish tugmasi bilan e'lon qilinadi.
   - POST LINKINI TAQDIM ETISH: Vakansiya kanalga chiqqach, bot ish beruvchiga
     darhol "Kanalga joylandi" xabarini va kanal postiga to'g'ridan-to'g'ri havolani yuboradi.
   - Arizalarni boshqarish: kelgan rezyumelarni ko'rish, PDF yuklab olish, qabul qilish yoki rad etish.

2. 👨‍💻 Ish qidiruvchilar uchun:
   - 1 daqiqada professional rezyume yaratish va PDF formatda yuklab olish.
   - Kanaldagi e'lon ostidagi tugma orqali 1-bosishda rezyumeni ish beruvchiga yuborish (Deep Link: /start vac_{id}).
   - Sohalar va shaharlar bo'yicha vakansiyalarni qidirish va ko'rish.
   - SMART MATCH: Mutaxassislikka mos yangi ish chiqishi bilan avtomatik bildirishnoma.

3. 👑 Administrator uchun:
   - /set_channel <@kanal_yoki_id> orqali kanalni dinamik sozlash.
   - /channel orqali ulangan kanal holati va ruxsatlarini tekshirish.
   - /admin orqali to'liq statistika (foydalanuvchilar, rezyumelar, vakansiyalar, arizalar).
   - /broadcast orqali barcha foydalanuvchilarga xabar yuborish.
=============================================================================
"""

import os
import sys
import io
import re
import html
import sqlite3
import logging
import datetime
from typing import Optional, Tuple, Dict, Any

# Logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("UniversalIshTopBot")

# Telegram Bot API kutubxonasi
try:
    import telebot
    from telebot import types
    from telebot.apihelper import ApiTelegramException
except ImportError:
    print("❌ XATOLIK: pyTelegramBotAPI o'rnatilmagan!")
    print("Terminalda quyidagi buyruqni bering:")
    print("pip install pyTelegramBotAPI reportlab")
    sys.exit(1)

# PDF yaratish uchun ReportLab
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab kutubxonasi topilmadi. PDF rezyume matn ko'rinishida beriladi.")

# ==================== ASOSIY SOZLAMALAR ====================
DEFAULT_BOT_TOKEN = "8863390415:AAEj3E_H-Kv36OF9gb0pGJOXMvQd5KldSgQ"
BOT_TOKEN = os.environ.get("BOT_TOKEN", DEFAULT_BOT_TOKEN).strip()

# Bosh administrator Telegram ID (@usman_khasan)
DEFAULT_ADMIN_ID = 1021089367
ADMIN_USERNAME = "@usman_khasan"
ADMIN_FIRST_NAME = "khasanov"
try:
    ADMIN_ID = int(os.environ.get("ADMIN_ID", DEFAULT_ADMIN_ID))
except ValueError:
    ADMIN_ID = DEFAULT_ADMIN_ID

# Asosiy rasmiy bot username
PRIMARY_BOT_USERNAME = "universal_IshTop"

# Zaxira kanal username (agar bazada bo'lmasa)
DEFAULT_CHANNEL = os.environ.get("CHANNEL_USERNAME", "").strip()

# Ma'lumotlar bazasi fayli
DB_FILE = os.environ.get("DB_FILE", "job_bot.db")

# Bot obyektini ishga tushirish
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# Foydalanuvchi holatlari (Wizard state)
USER_STATES: Dict[int, Dict[str, Any]] = {}

# Soha / Kategoriyalar ro'yxati
CATEGORIES = [
    "💻 IT va Dasturlash",
    "📊 Savdo va Sotuv",
    "🏗 Qurilish va Loyihalash",
    "🏭 Ishlab chiqarish",
    "🚕 Xizmat ko'rsatish",
    "📚 Ta'lim va Repetitorlik",
    "🩺 Tibbiyot va Farmatsevtika",
    "📦 Logistika va Haydovchilik",
    "🎨 Dizayn va Multimedia",
    "🏢 Boshqaruv va HR",
    "🌐 Boshqa sohalar"
]

# Hududlar / Shaharlar
CITIES = [
    "Toshkent shahri", "Toshkent viloyati", "Samarqand", "Farg'ona",
    "Andijon", "Namangan", "Buxoro", "Xorazm", "Qashqadaryo",
    "Surxondaryo", "Jizzax", "Sirdaryo", "Navoiy", "Qoraqalpog'iston",
    "Masofaviy (Online)"
]


# ==================== BAZA (SQLite) BILAN ISHLASH ====================
def get_db_connection():
    """SQLite ulanishini qaytaradi."""
    conn = sqlite3.connect(DB_FILE, timeout=15)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Baza jadvallarini yaratadi."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Foydalanuvchilar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            role TEXT DEFAULT 'seeker',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Rezyumelar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            full_name TEXT,
            profession TEXT,
            skills TEXT,
            experience TEXT,
            salary TEXT,
            city TEXT,
            phone TEXT,
            telegram TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Vakansiyalar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER,
            title TEXT,
            company TEXT,
            category TEXT,
            salary TEXT,
            requirements TEXT,
            description TEXT,
            phone TEXT,
            city TEXT,
            telegram TEXT,
            status TEXT DEFAULT 'active',
            channel_post_id INTEGER DEFAULT NULL,
            channel_target TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Arizalar jadvali
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vacancy_id INTEGER,
            seeker_id INTEGER,
            resume_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(vacancy_id, seeker_id)
        )
    """)

    # Sozlamalar jadvali (Kanal username/id saqlash uchun)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS bot_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()
    logger.info("SQLite ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")

def get_setting(key: str, default: str = "") -> str:
    """Bazada saqlangan sozlama qiymatini oladi."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT value FROM bot_settings WHERE key = ?", (key,))
        row = cur.fetchone()
        conn.close()
        return row["value"] if row else default
    except Exception as e:
        logger.error(f"get_setting xatosi: {e}")
        return default

def set_setting(key: str, value: str):
    """Bazada sozlama qiymatini yangilaydi yoki yozadi."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

def get_channel_target() -> str:
    """Hozirgi ulangan kanal username yoki ID sini qaytaradi."""
    stored = get_setting("channel_username", "").strip()
    if stored:
        return stored
    if DEFAULT_CHANNEL:
        return DEFAULT_CHANNEL
    return ""

def get_bot_username() -> str:
    """Botning hozirgi Telegram username sini qaytaradi."""
    try:
        me = bot.get_me()
        if me and me.username:
            return me.username
    except Exception:
        pass
    return PRIMARY_BOT_USERNAME

def register_or_update_user(user: types.User, role: Optional[str] = None):
    """Foydalanuvchini bazaga kiritadi yoki yangilaydi."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, role FROM users WHERE user_id = ?", (user.id,))
    row = cur.fetchone()
    u_name = user.username or ""
    f_name = user.full_name or user.first_name or "Foydalanuvchi"

    if not row:
        assigned_role = role or "seeker"
        cur.execute(
            "INSERT INTO users (user_id, username, full_name, role) VALUES (?, ?, ?, ?)",
            (user.id, u_name, f_name, assigned_role)
        )
    else:
        new_role = role or row["role"]
        cur.execute(
            "UPDATE users SET username = ?, full_name = ?, role = ? WHERE user_id = ?",
            (u_name, f_name, new_role, user.id)
        )
    conn.commit()
    conn.close()


# ==================== KANALGA AVTO-POSTING VA LINK GENERATSIYASI ====================
def format_vacancy_channel_post(vac: sqlite3.Row, bot_username: str) -> Tuple[str, types.InlineKeyboardMarkup]:
    """Kanal uchun chiroyli, rasmiy va diqqat tortuvchi post matni va inline tugmani shakllantiradi."""
    vac_id = vac["id"]
    title = html.escape(str(vac["title"]))
    company = html.escape(str(vac["company"]))
    category = html.escape(str(vac["category"]))
    salary = html.escape(str(vac["salary"]))
    city = html.escape(str(vac["city"]))
    requirements = html.escape(str(vac["requirements"]))
    description = html.escape(str(vac["description"]))
    phone = html.escape(str(vac["phone"]))
    telegram = str(vac["telegram"] or "").strip().lstrip("@")
    tg_display = f"@{telegram}" if telegram else "Mavjud emas"

    post_text = (
        f"💼 <b>YANGI VAKANSIYA: {title.upper()}</b>\n\n"
        f"🏢 <b>Korxona / Kompaniya:</b> {company}\n"
        f"🏷 <b>Yo'nalish:</b> {category}\n"
        f"📍 <b>Shahar / Hudud:</b> {city}\n"
        f"💰 <b>Maosh:</b> <b>{salary}</b>\n\n"
        f"📋 <b>Talablar:</b>\n{requirements}\n\n"
        f"📝 <b>Vazifalar va sharoitlar:</b>\n{description}\n\n"
        f"📞 <b>Aloqa:</b> {phone}\n"
        f"👤 <b>Telegram:</b> {tg_display}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👇 <b>1 ta tugma orqali rezyumengiz bilan ariza yuboring:</b>"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    apply_url = f"https://t.me/{bot_username}?start=vac_{vac_id}"
    markup.add(
        types.InlineKeyboardButton("📩 Ariza topshirish (Rezyume yuborish)", url=apply_url),
        types.InlineKeyboardButton("🤖 Barcha vakansiyalar va Rezyume boti", url=f"https://t.me/{bot_username}")
    )
    return post_text, markup

def post_vacancy_to_channel(vac_id: int) -> Tuple[bool, str, str, str]:
    """Vakansiyani belgilangan Telegram kanalga chiqaradi va post linkini qaytaradi.
    Qaytaradi: (success: bool, post_url: str, channel_display: str, error_msg: str)"""
    channel_target = get_channel_target()
    if not channel_target:
        return False, "", "", "Kanal sozlanmagan (/set_channel orqali sozlang)"

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vacancies WHERE id = ?", (vac_id,))
    vac = cur.fetchone()
    if not vac:
        conn.close()
        return False, "", "", "Vakansiya topilmadi"

    bot_username = get_bot_username()
    post_text, markup = format_vacancy_channel_post(vac, bot_username)

    try:
        sent_msg = bot.send_message(
            chat_id=channel_target,
            text=post_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        post_id = sent_msg.message_id

        # Bazaga saqlab qo'yamiz
        cur.execute(
            "UPDATE vacancies SET channel_post_id = ?, channel_target = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (post_id, str(channel_target), vac_id)
        )
        conn.commit()
        conn.close()

        # Linkni shakllantirish
        clean_target = str(channel_target).strip()
        if clean_target.startswith("@"):
            clean_name = clean_target.lstrip("@")
            post_url = f"https://t.me/{clean_name}/{post_id}"
            channel_display = f"@{clean_name}"
        elif clean_target.startswith("-100"):
            internal_id = clean_target.replace("-100", "")
            post_url = f"https://t.me/c/{internal_id}/{post_id}"
            channel_display = f"Kanal ({channel_target})"
        else:
            post_url = f"https://t.me/{clean_target}/{post_id}"
            channel_display = clean_target

        logger.info(f"Vakansiya #{vac_id} muvaffaqiyatli kanalga joylandi: {post_url}")
        return True, post_url, channel_display, ""

    except ApiTelegramException as ex:
        conn.close()
        logger.error(f"Telegram API xatosi kanalga post qilishda: {ex}")
        err = f"API xatolik: {ex.description}"
        return False, "", str(channel_target), err
    except Exception as e:
        conn.close()
        logger.error(f"Kanalga post qilishda kutilmagan xatolik: {e}")
        return False, "", str(channel_target), str(e)


# ==================== SMART MATCH (MOS XODIMLARGA BILDIRISHNOMA) ====================
def notify_matched_seekers(vac_id: int):
    """Yangi vakansiyaga mos keladigan ish qidiruvchilarga bot ichida xabar beradi."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM vacancies WHERE id = ?", (vac_id,))
        vac = cur.fetchone()
        if not vac:
            conn.close()
            return

        title_words = [w.lower() for w in re.split(r"\W+", vac["title"]) if len(w) >= 3]
        category = vac["category"]

        cur.execute("SELECT user_id, profession, skills FROM resumes")
        candidates = cur.fetchall()
        conn.close()

        bot_username = get_bot_username()
        match_count = 0

        for cand in candidates:
            cand_text = f"{cand['profession']} {cand['skills']}".lower()
            matched = any(w in cand_text for w in title_words) or (category.lower() in cand_text)

            if matched:
                try:
                    markup = types.InlineKeyboardMarkup()
                    apply_url = f"https://t.me/{bot_username}?start=vac_{vac_id}"
                    markup.add(
                        types.InlineKeyboardButton("👁 Vakansiyani ko'rish va Ariza berish", url=apply_url)
                    )
                    text = (
                        f"🎯 <b>SIZNING SOHANGIZGA MOS YANGI ISH!</b>\n\n"
                        f"💼 <b>Lavozim:</b> {html.escape(vac['title'])}\n"
                        f"🏢 <b>Kompaniya:</b> {html.escape(vac['company'])}\n"
                        f"💰 <b>Maosh:</b> {html.escape(vac['salary'])}\n"
                        f"📍 <b>Hudud:</b> {html.escape(vac['city'])}\n\n"
                        f"<i>Rezyumengiz ushbu vakansiyaga mos kelgani uchun tizim sizga bildirishnoma yubordi.</i>"
                    )
                    bot.send_message(cand["user_id"], text, reply_markup=markup, parse_mode="HTML")
                    match_count += 1
                except Exception:
                    pass

        logger.info(f"Vakansiya #{vac_id} bo'yicha {match_count} ta nomzodga Smart Match xabarnomasi yuborildi.")
    except Exception as e:
        logger.error(f"Smart Match xatosi: {e}")


# ==================== PDF REZYUME GENERATORI ====================
def generate_resume_pdf(resume: sqlite3.Row) -> Optional[io.BytesIO]:
    """Nomzod rezyumesi asosida professional A4 formatdagi PDF fayl shakllantiradi."""
    if not REPORTLAB_AVAILABLE:
        return None

    try:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=4
        )
        subtitle_style = ParagraphStyle(
            "SubTitleStyle",
            parent=styles["Normal"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#2B6CB0"),
            spaceAfter=12
        )
        heading_style = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#2D3748"),
            spaceBefore=10,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#1A202C")
        )

        elements = []

        # Sarlavha (Nomzod ismi va kasbi)
        f_name = resume["full_name"] or "Nomzod Rezyumesi"
        prof = resume["profession"] or "Mutaxassis"
        elements.append(Paragraph(f_name, title_style))
        elements.append(Paragraph(prof, subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3182CE"), spaceAfter=10))

        # Aloqa va shaxsiy ma'lumotlar jadvali
        contact_data = [
            [Paragraph("<b>Telefon:</b>", body_style), Paragraph(str(resume["phone"] or "-"), body_style)],
            [Paragraph("<b>Telegram:</b>", body_style), Paragraph(f"@{str(resume['telegram'] or '').lstrip('@')}", body_style)],
            [Paragraph("<b>Shahar / Hudud:</b>", body_style), Paragraph(str(resume["city"] or "-"), body_style)],
            [Paragraph("<b>Kutilayotgan maosh:</b>", body_style), Paragraph(str(resume["salary"] or "-"), body_style)],
        ]
        t = Table(contact_data, colWidths=[4 * cm, 13 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7FAFC")),
            ("PADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#EDF2F7")),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        # Tajriba
        elements.append(Paragraph("💼 Ish Tajribasi", heading_style))
        elements.append(Paragraph(html.escape(str(resume["experience"] or "Ko'rsatilmagan")).replace("\n", "<br/>"), body_style))
        elements.append(Spacer(1, 10))

        # Ko'nikmalar
        elements.append(Paragraph("🛠 Ko'nikmalar va Qobiliyatlar", heading_style))
        elements.append(Paragraph(html.escape(str(resume["skills"] or "Ko'rsatilmagan")).replace("\n", "<br/>"), body_style))
        elements.append(Spacer(1, 15))

        # Footer
        elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CBD5E0"), spaceAfter=6))
        footer_style = ParagraphStyle("Footer", parent=styles["Italic"], fontSize=8, textColor=colors.HexColor("#718096"))
        bot_uname = get_bot_username()
        footer_text = f"Hujjat https://t.me/{bot_uname} boti orqali shakllantirildi. Sana: {datetime.date.today()}"
        elements.append(Paragraph(footer_text, footer_style))

        doc.build(elements)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"PDF yaratishda xatolik: {e}")
        return None


# ==================== ASOSIY MENYU VA TUGMALAR ====================
def main_reply_keyboard(role: str = "seeker") -> types.ReplyKeyboardMarkup:
    """Asosiy pastki klaviatura."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    if role == "employer":
        markup.add("➕ Vakansiya joylash", "📋 Mening vakansiyalarim")
        markup.add("📥 Kelgan arizalar", "🔍 Ish qidiruvchi rejimiga o'tish")
        markup.add("ℹ️ Bot haqida", "📞 Yordam")
    else:
        markup.add("🔍 Ish izlash (Vakansiyalar)", "📄 Mening rezyumem")
        markup.add("📑 Mening arizalarim", "🏢 Ish beruvchi rejimiga o'tish")
        markup.add("ℹ️ Bot haqida", "📞 Yordam")
    return markup


# ==================== /start BUYRUG'I VA DEEP LINKING ====================
@bot.message_handler(commands=["start"])
def handle_start(message: types.Message):
    user = message.from_user
    args = message.text.split(maxsplit=1)
    payload = args[1].strip() if len(args) > 1 else ""

    register_or_update_user(user)

    # 1. DEEP LINK: Kanaldan ariza topshirish orqali kelgan foydalanuvchi (/start vac_123)
    if payload.startswith("vac_"):
        try:
            vac_id = int(payload.split("_")[1])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM vacancies WHERE id = ?", (vac_id,))
            vac = cur.fetchone()
            conn.close()

            if vac and vac["status"] == "active":
                show_vacancy_card(message.chat.id, vac, show_apply_btn=True)
                return
            else:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Kechirasiz, ushbu vakansiya topilmadi yoki uning muddati yakunlangan.",
                    reply_markup=main_reply_keyboard("seeker")
                )
                return
        except Exception as e:
            logger.error(f"Deep link tekshirishda xatolik: {e}")

    # Oddiy start xabari
    first_name = html.escape(user.first_name or "Do'stim")
    bot_uname = get_bot_username()
    welcome_text = (
        f"👋 <b>Assalomu alaykum, {first_name}!</b>\n\n"
        f"🤝 <b>«Universal Ish Topish & Xodimlar Markazi»</b> botiga xush kelibsiz!\n"
        f"🌐 <i>Bot manzili:</i> @{bot_uname}\n\n"
        f"🎯 <b>Bot sizga nimalarda yordam beradi?</b>\n"
        f"• <b>Ish qidiruvchilarga:</b> 1 daqiqada professional rezyume yaratish, A4 PDF yuklab olish, eng yangi vakansiyalarga 1 bosishda ariza topshirish.\n"
        f"• <b>Ish beruvchilarga:</b> Yangi vakansiyalarni joylashtirish, ularni rasmiy kanalga avtomatik e'lon qilish va nomzodlarning arizalarini tartibli qabul qilish.\n\n"
        f"👇 <b>Quyidagi bo'limlardan birini tanlang:</b>"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔍 Ish qidiruvchiman", callback_data="role_seeker"),
        types.InlineKeyboardButton("🏢 Ish beruvchiman", callback_data="role_employer")
    )
    ch = get_channel_target()
    if ch and ch.startswith("@"):
        markup.add(types.InlineKeyboardButton("📢 Vakansiyalar kanali", url=f"https://t.me/{ch.lstrip('@')}"))
    else:
        markup.add(types.InlineKeyboardButton("ℹ️ Yo'riqnoma", callback_data="btn_help"))

    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_reply_keyboard("seeker"),
        parse_mode="HTML"
    )


# ==================== VAKANSIYA KARTASINI KO'RSATISH ====================
def show_vacancy_card(chat_id: int, vac: sqlite3.Row, show_apply_btn: bool = True):
    """Bitta vakansiyaning to'liq ma'lumotlarini chiroyli karta shaklida yuboradi."""
    vac_id = vac["id"]
    title = html.escape(str(vac["title"]))
    company = html.escape(str(vac["company"]))
    category = html.escape(str(vac["category"]))
    salary = html.escape(str(vac["salary"]))
    city = html.escape(str(vac["city"]))
    requirements = html.escape(str(vac["requirements"]))
    description = html.escape(str(vac["description"]))
    phone = html.escape(str(vac["phone"]))
    telegram = str(vac["telegram"] or "").strip().lstrip("@")
    tg_display = f"@{telegram}" if telegram else "Mavjud emas"

    card_text = (
        f"💼 <b>VAKANSIYA №{vac_id}: {title.upper()}</b>\n\n"
        f"🏢 <b>Kompaniya:</b> {company}\n"
        f"🏷 <b>Yo'nalish:</b> {category}\n"
        f"📍 <b>Hudud:</b> {city}\n"
        f"💰 <b>Maosh:</b> <b>{salary}</b>\n\n"
        f"📋 <b>Talablar:</b>\n{requirements}\n\n"
        f"📝 <b>Sharoitlar va vazifalar:</b>\n{description}\n\n"
        f"📞 <b>Aloqa telefoni:</b> {phone}\n"
        f"👤 <b>Telegram:</b> {tg_display}\n"
    )

    # Agar kanalda e'lon qilingan bo'lsa, post linkini ko'rsatamiz
    channel_post_id = vac["channel_post_id"]
    channel_target = vac["channel_target"] or get_channel_target()
    if channel_post_id and channel_target:
        if str(channel_target).startswith("@"):
            ch_link = f"https://t.me/{str(channel_target).lstrip('@')}/{channel_post_id}"
            card_text += f"\n📢 <b>Kanal posti:</b> <a href=\"{ch_link}\">Kanalda ko'rish</a>\n"

    markup = types.InlineKeyboardMarkup(row_width=1)
    if show_apply_btn:
        markup.add(types.InlineKeyboardButton("📩 Ushbu ishga ariza topshirish", callback_data=f"apply_{vac_id}"))
    markup.add(types.InlineKeyboardButton("🔍 Boshqa vakansiyalarni ko'rish", callback_data="browse_vacancies"))

    bot.send_message(chat_id, card_text, reply_markup=markup, parse_mode="HTML")


# ==================== ADMIN BUYRUQLARI ====================
@bot.message_handler(commands=["admin"])
def handle_admin(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔️ Ushbu bo'lim faqat bosh administrator uchun.")
        return

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM users")
    users_cnt = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM resumes")
    res_cnt = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM vacancies WHERE status = 'active'")
    vac_active_cnt = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM vacancies")
    vac_total_cnt = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM applications")
    app_cnt = cur.fetchone()[0]
    conn.close()

    ch_target = get_channel_target() or "Sozlanmagan ⚠️"

    text = (
        f"👑 <b>BOSH ADMINISTRATOR PANELI (@usman_khasan)</b>\n\n"
        f"📊 <b>Bot Statistikasi:</b>\n"
        f"• 👥 Jami foydalanuvchilar: <b>{users_cnt} ta</b>\n"
        f"• 📄 Yaratilgan rezyumelar: <b>{res_cnt} ta</b>\n"
        f"• 💼 Faol vakansiyalar: <b>{vac_active_cnt} ta</b> (Jami: {vac_total_cnt} ta)\n"
        f"• 📥 Topshirilgan arizalar: <b>{app_cnt} ta</b>\n\n"
        f"📢 <b>Ulangan e'lonlar kanali:</b> <code>{ch_target}</code>\n\n"
        f"⚙️ <b>Admin buyruqlari:</b>\n"
        f"• <code>/set_channel @kanalingiz</code> — Vakansiyalar avtomatik joylanadigan kanalni sozlash.\n"
        f"• <code>/channel</code> — Kanal holati va bot ruxsatlarini tekshirish.\n"
        f"• <code>/broadcast &lt;matn&gt;</code> — Barcha foydalanuvchilarga xabar tarqatish."
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")


@bot.message_handler(commands=["set_channel"])
def handle_set_channel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "⛔️ Ushbu buyruq faqat bosh administrator uchun.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Kanal nomini ko'rsating!</b>\n\n"
            "Format:\n"
            "<code>/set_channel @sizning_kanalingiz</code>\n"
            "yoki ID orqali:\n"
            "<code>/set_channel -1001234567890</code>\n\n"
            "📌 <i>Eslatma: Kanalga botni administrator qilib qo'shing va unga «Post messages» (Xabarlarni yozish) ruxsatini bering!</i>",
            parse_mode="HTML"
        )
        return

    new_channel = args[1].strip()
    set_setting("channel_username", new_channel)

    # Kanal ruxsatini tekshirib ko'ramiz
    test_ok = False
    test_err = ""
    try:
        test_msg = bot.send_message(
            chat_id=new_channel,
            text=f"✅ <b>Universal Ish Topish Boti (@{get_bot_username()}) kanalga muvaffaqiyatli ulandi!</b>\n\nEndi bot orqali joylangan barcha yangi vakansiyalar ushbu kanalga avtomatik chiqadi.",
            parse_mode="HTML"
        )
        test_ok = True
    except Exception as e:
        test_err = str(e)

    if test_ok:
        bot.send_message(
            message.chat.id,
            f"🎉 <b>Kanal muvaffaqiyatli sozlandi va sinov xabari yuborildi!</b>\n\n"
            f"📢 <b>Kanal:</b> <code>{new_channel}</code>\n"
            f"✅ Bot administrator ekanligi tasdiqlandi. Endi vakansiyalar ushbu kanalga avtomatik joylanadi!",
            parse_mode="HTML"
        )
    else:
        bot.send_message(
            message.chat.id,
            f"⚠️ <b>Kanal bazaga saqlandi (<code>{new_channel}</code>), lekin sinov xabari yuborishda xatolik yuz berdi!</b>\n\n"
            f"Xatolik sababi: <i>{test_err}</i>\n\n"
            f"<b>Yechim:</b>\n"
            f"1. Telegramda <b>{new_channel}</b> kanaliga kiring.\n"
            f"2. Kanal boshqaruviga kirib, botni <b>Administrator</b> qilib qo'shing.\n"
            f"3. Botga <b>«Post messages» (Xabarlar yozish)</b> ruxsatini bering.\n"
            f"4. Keyin qaytadan <code>/channel</code> buyrug'ini yuborib tekshirib ko'ring.",
            parse_mode="HTML"
        )


@bot.message_handler(commands=["channel"])
def handle_check_channel(message: types.Message):
    """Kanal sozlamasini va ulanish holatini tekshirish."""
    ch = get_channel_target()
    if not ch:
        bot.send_message(
            message.chat.id,
            "⚠️ <b>Kanal hali ulanmagan!</b>\n\n"
            "Kanalni ulash uchun <code>/set_channel @kanalingiz</code> buyrug'ini bering.",
            parse_mode="HTML"
        )
        return

    # Holatni tekshirish
    try:
        chat_info = bot.get_chat(ch)
        title = chat_info.title or ch
        bot.send_message(
            message.chat.id,
            f"✅ <b>Kanal ulanishi faol!</b>\n\n"
            f"📢 <b>Kanal nomi:</b> {title}\n"
            f"🆔 <b>Kanal manzili:</b> <code>{ch}</code>\n\n"
            f"Yangi vakansiyalar avtomatik ushbu kanalga chiqadi va post linki ish beruvchiga taqdim etiladi.",
            parse_mode="HTML"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"⚠️ <b>Ulangan kanal:</b> <code>{ch}</code>\n\n"
            f"❌ <b>Kanalga ulanishda xatolik:</b> <i>{e}</i>\n"
            f"Iltimos, bot kanalda Administrator ekanligini va xabar yozish huquqi borligini tekshiring.",
            parse_mode="HTML"
        )


@bot.message_handler(commands=["broadcast"])
def handle_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Foydalanish: <code>/broadcast &lt;xabar matni&gt;</code>", parse_mode="HTML")
        return

    text = args[1]
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    conn.close()

    sent = 0
    for u in users:
        try:
            bot.send_message(u["user_id"], text, parse_mode="HTML")
            sent += 1
        except Exception:
            pass

    bot.send_message(message.chat.id, f"✅ Xabar {sent} ta foydalanuvchiga yuborildi.")


# ==================== ISH BERUVCHI: VAKANSIYA QO'SHISH WIZARD'I ====================
def start_vacancy_wizard(chat_id: int, user_id: int):
    """Vakansiya qo'shish so'rovnomasini boshlaydi."""
    USER_STATES[user_id] = {
        "flow": "vacancy",
        "step": "vac_title",
        "data": {}
    }
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Bekor qilish")
    bot.send_message(
        chat_id,
        "💼 <b>YANGI VAKANSIYA JOYLASH (1/8)</b>\n\n"
        "Qidirayotgan xodimingizning <b>lavozimi yoki kasb nomini</b> kiriting:\n"
        "<i>Masalan: Python Backend Dasturchi, Sotuv menejeri, Oshpaz, SMM mutaxassisi</i>",
        reply_markup=markup,
        parse_mode="HTML"
    )

def handle_vacancy_step(message: types.Message, state: Dict[str, Any]):
    user_id = message.from_user.id
    step = state.get("step")
    text = (message.text or "").strip()

    if text == "❌ Bekor qilish":
        USER_STATES.pop(user_id, None)
        bot.send_message(message.chat.id, "🚫 Vakansiya kiritish bekor qilindi.", reply_markup=main_reply_keyboard("employer"))
        return

    if step == "vac_title":
        state["data"]["title"] = text
        state["step"] = "vac_company"
        bot.send_message(
            message.chat.id,
            "🏢 <b>VAKANSIYA JOYLASH (2/8)</b>\n\n"
            "<b>Kompaniya, korxona yoki loyihangiz nomini</b> kiriting:\n"
            "<i>Masalan: «TechSoft MCHJ», «Savdo Olami» do'koni, Xususiy klinika</i>",
            parse_mode="HTML"
        )

    elif step == "vac_company":
        state["data"]["company"] = text
        state["step"] = "vac_category"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for cat in CATEGORIES:
            markup.add(cat)
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "🏷 <b>VAKANSIYA JOYLASH (3/8)</b>\n\n"
            "Vakansiya <b>qaysi sohaga</b> tegishli? Pastdagi ro'yxatdan tanlang yoki yozing:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "vac_category":
        state["data"]["category"] = text
        state["step"] = "vac_city"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for city in CITIES:
            markup.add(city)
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "📍 <b>VAKANSIYA JOYLASH (4/8)</b>\n\n"
            "Ish qaysi <b>shahar yoki hududda</b> joylashgan? Tanlang yoki yozing:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "vac_city":
        state["data"]["city"] = text
        state["step"] = "vac_salary"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("Kelishilgan holda", "Suhbat asosida")
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "💰 <b>VAKANSIYA JOYLASH (5/8)</b>\n\n"
            "Taklif qilinayotgan <b>maosh (oylik)</b> miqdorini kiriting:\n"
            "<i>Masalan: 5,000,000 - 8,000,000 so'm, 600$, Kelishilgan holda</i>",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "vac_salary":
        state["data"]["salary"] = text
        state["step"] = "vac_requirements"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "📋 <b>VAKANSIYA JOYLASH (6/8)</b>\n\n"
            "Nomzodga qo'yiladigan <b>asosiy talablarni</b> yozing:\n"
            "<i>Masalan: 1 yildan ortiq tajriba, rus tili bilishi, mas'uliyatlilik</i>",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "vac_requirements":
        state["data"]["requirements"] = text
        state["step"] = "vac_description"
        bot.send_message(
            message.chat.id,
            "📝 <b>VAKANSIYA JOYLASH (7/8)</b>\n\n"
            "Ish haqida <b>batafsil ma'lumot va vazifalarni</b> yozing:\n"
            "<i>Masalan: Ish vaqti 09:00 dan 18:00 gacha, tushlik kompaniya hisobidan, qulay ofis</i>",
            parse_mode="HTML"
        )

    elif step == "vac_description":
        state["data"]["description"] = text
        state["step"] = "vac_phone"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("📞 Telefon raqamimni yuborish", request_contact=True))
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "📞 <b>VAKANSIYA JOYLASH (8/8)</b>\n\n"
            "Nomzodlar bilan bog'lanish uchun <b>telefon raqamini</b> kiriting yoki pastdagi tugmani bosing:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "vac_phone":
        phone = ""
        if message.contact and message.contact.phone_number:
            phone = message.contact.phone_number
        else:
            phone = text

        state["data"]["phone"] = phone
        state["data"]["telegram"] = message.from_user.username or ""

        # Bazaga saqlaymiz
        conn = get_db_connection()
        cur = conn.cursor()
        d = state["data"]
        cur.execute("""
            INSERT INTO vacancies (
                employer_id, title, company, category, salary,
                requirements, description, phone, city, telegram
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, d["title"], d["company"], d["category"], d["salary"],
            d["requirements"], d["description"], d["phone"], d["city"], d["telegram"]
        ))
        vac_id = cur.lastrowid
        conn.commit()
        conn.close()

        # Wizardni tozalaymiz
        USER_STATES.pop(user_id, None)

        # 🚀 1. KANALGA AVTOMATIK JOYLASHTIRISH
        channel_success, post_url, channel_display, error_detail = post_vacancy_to_channel(vac_id)

        # 🚀 2. ISH BERUVCHIGA KANAL POSTI LINKI BILAN TASDIQ XABARINI YUBORISH
        if channel_success and post_url:
            employer_msg = (
                f"🎉 <b>TABRIKLAYMIZ! SIZNING VAKANSIYANGIZ QABUL QILINDI!</b>\n\n"
                f"💼 <b>Lavozim:</b> {html.escape(d['title'])}\n"
                f"🏢 <b>Kompaniya:</b> {html.escape(d['company'])}\n"
                f"🆔 <b>Vakansiya raqami:</b> №{vac_id}\n\n"
                f"📢 <b>KANALGA JOYLANDI:</b> Sizning e'loningiz <a href=\"{post_url}\">{channel_display}</a> kanaliga muvaffaqiyatli joylashtirildi!\n\n"
                f"🔗 <b>Kanal postiga havola:</b>\n"
                f"👉 <a href=\"{post_url}\"><b>E'LONNI KANALDA KO'RISH</b></a>\n\n"
                f"💡 <i>Nomzodlar kanal postidagi ariza tugmasi orqali rezyumelarini yuborganida, bot sizga darhol to'liq xabarnoma yetkazadi.</i>"
            )
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("📢 E'lonni kanalda ko'rish", url=post_url),
                types.InlineKeyboardButton("📋 Mening vakansiyalarim", callback_data="my_vacancies")
            )
        else:
            employer_msg = (
                f"✅ <b>Vakansiyangiz bot bazasiga saqlandi! (№{vac_id})</b>\n\n"
                f"💼 <b>Lavozim:</b> {html.escape(d['title'])}\n"
                f"🏢 <b>Kompaniya:</b> {html.escape(d['company'])}\n\n"
                f"⚠️ <b>Kanalga avtomatik chiqarish bo'yicha eslatma:</b>\n"
                f"<i>{error_detail or 'Kanal sozlanmagan'}</i>\n\n"
                f"📌 Kanalga avtomatik chiqishi uchun bosh admin <code>/set_channel @kanalingiz</code> buyrug'ini berishi va botni kanalda Administrator qilishi kerak."
            )
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("📋 Mening vakansiyalarim", callback_data="my_vacancies"))

        bot.send_message(
            message.chat.id,
            employer_msg,
            reply_markup=main_reply_keyboard("employer"),
            parse_mode="HTML"
        )

        # 🚀 3. SMART MATCH: Mos nomzodlarga bildirishnoma yuborish
        notify_matched_seekers(vac_id)


# ==================== ISH QIDIRUVCHI: REZYUME YARATISH WIZARD'I ====================
def start_resume_wizard(chat_id: int, user_id: int, pending_vac_id: Optional[int] = None):
    """Rezyume to'ldirish wizard'ini boshlaydi."""
    USER_STATES[user_id] = {
        "flow": "resume",
        "step": "res_name",
        "pending_vac_id": pending_vac_id,
        "data": {}
    }
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Bekor qilish")
    bot.send_message(
        chat_id,
        "📄 <b>PROFESSIONAL REZYUME YARATISH (1/7)</b>\n\n"
        "To'liq <b>Ism, Familiyangizni</b> kiriting:\n"
        "<i>Masalan: Jasur Aliyev</i>",
        reply_markup=markup,
        parse_mode="HTML"
    )

def handle_resume_step(message: types.Message, state: Dict[str, Any]):
    user_id = message.from_user.id
    step = state.get("step")
    text = (message.text or "").strip()

    if text == "❌ Bekor qilish":
        USER_STATES.pop(user_id, None)
        bot.send_message(message.chat.id, "🚫 Rezyume to'ldirish bekor qilindi.", reply_markup=main_reply_keyboard("seeker"))
        return

    if step == "res_name":
        state["data"]["full_name"] = text
        state["step"] = "res_profession"
        bot.send_message(
            message.chat.id,
            "💼 <b>REZYUME YARATISH (2/7)</b>\n\n"
            "<b>Mutaxassisligingiz yoki kasbingizni</b> kiriting:\n"
            "<i>Masalan: Python Dasturchi, Sotuv Menejeri, Hisobchi, Grafik Dizayner</i>",
            parse_mode="HTML"
        )

    elif step == "res_profession":
        state["data"]["profession"] = text
        state["step"] = "res_experience"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("Tajribasiz (Boshlang'ich)", "1 yilgacha", "1 yildan 3 yilgacha", "3 yildan ortiq")
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "⏳ <b>REZYUME YARATISH (3/7)</b>\n\n"
            "Ushbu sohada <b>ish tajribangiz</b> qancha? Tanlang yoki batafsil yozing:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "res_experience":
        state["data"]["experience"] = text
        state["step"] = "res_skills"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "🛠 <b>REZYUME YARATISH (4/7)</b>\n\n"
            "Asosiy <b>ko'nikmalaringiz va bilgan dasturlaringizni</b> yozing:\n"
            "<i>Masalan: Python, Django, PostgreSQL, Git, Rus tili, Muzokaralar olib borish</i>",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "res_skills":
        state["data"]["skills"] = text
        state["step"] = "res_salary"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add("Kelishilgan holda", "Suhbatda aytiladi")
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "💰 <b>REZYUME YARATISH (5/7)</b>\n\n"
            "Sizni qoniqtiradigan <b>kutilayotgan maosh</b> miqdorini kiriting:\n"
            "<i>Masalan: 6,000,000 so'm, 700$, Kelishilgan holda</i>",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "res_salary":
        state["data"]["salary"] = text
        state["step"] = "res_city"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        for city in CITIES:
            markup.add(city)
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "📍 <b>REZYUME YARATISH (6/7)</b>\n\n"
            "Yashash <b>shahringiz yoki viloyatingizni</b> tanlang:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "res_city":
        state["data"]["city"] = text
        state["step"] = "res_phone"
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("📞 Raqamimni yuborish", request_contact=True))
        markup.add("❌ Bekor qilish")
        bot.send_message(
            message.chat.id,
            "📞 <b>REZYUME YARATISH (7/7)</b>\n\n"
            "Ish beruvchilar siz bilan bog'lanishi uchun <b>telefon raqamingizni</b> yuboring:",
            reply_markup=markup,
            parse_mode="HTML"
        )

    elif step == "res_phone":
        phone = ""
        if message.contact and message.contact.phone_number:
            phone = message.contact.phone_number
        else:
            phone = text

        state["data"]["phone"] = phone
        state["data"]["telegram"] = message.from_user.username or ""

        # Bazaga saqlaymiz
        conn = get_db_connection()
        cur = conn.cursor()
        d = state["data"]
        cur.execute("""
            INSERT INTO resumes (
                user_id, full_name, profession, skills, experience,
                salary, city, phone, telegram, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name = excluded.full_name,
                profession = excluded.profession,
                skills = excluded.skills,
                experience = excluded.experience,
                salary = excluded.salary,
                city = excluded.city,
                phone = excluded.phone,
                telegram = excluded.telegram,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user_id, d["full_name"], d["profession"], d["skills"], d["experience"],
            d["salary"], d["city"], d["phone"], d["telegram"]
        ))
        conn.commit()
        conn.close()

        pending_vac_id = state.get("pending_vac_id")
        USER_STATES.pop(user_id, None)

        bot.send_message(
            message.chat.id,
            "🎉 <b>Rezyumengiz muvaffaqiyatli saqlandi!</b>\n\nEndi siz vakansiyalarga bir bosishda ariza topshira olasiz va rezyumengizni PDF formatda yuklab olishingiz mumkin.",
            reply_markup=main_reply_keyboard("seeker"),
            parse_mode="HTML"
        )

        # Agar foydalanuvchi ma'lum bir vakansiyaga topshirish uchun rezyume yaratgan bo'lsa
        if pending_vac_id:
            process_application(message.chat.id, user_id, pending_vac_id)


# ==================== ARIZA TOPSHIRISHNI BOSHQARISH ====================
def process_application(chat_id: int, seeker_id: int, vac_id: int):
    """Vakansiyaga ariza yuborish jarayoni."""
    conn = get_db_connection()
    cur = conn.cursor()

    # Rezyumeni tekshiramiz
    cur.execute("SELECT * FROM resumes WHERE user_id = ?", (seeker_id,))
    res = cur.fetchone()
    if not res:
        conn.close()
        bot.send_message(
            chat_id,
            "⚠️ Ushbu vakansiyaga ariza topshirish uchun avval 1 daqiqada rezyumengizni to'ldirishingiz kerak.",
            parse_mode="HTML"
        )
        start_resume_wizard(chat_id, seeker_id, pending_vac_id=vac_id)
        return

    # Vakansiyani tekshiramiz
    cur.execute("SELECT * FROM vacancies WHERE id = ?", (vac_id,))
    vac = cur.fetchone()
    if not vac or vac["status"] != "active":
        conn.close()
        bot.send_message(chat_id, "⚠️ Kechirasiz, ushbu vakansiya endi faol emas.", parse_mode="HTML")
        return

    # Avval topshirganmi?
    cur.execute("SELECT * FROM applications WHERE vacancy_id = ? AND seeker_id = ?", (vac_id, seeker_id))
    existing_app = cur.fetchone()
    if existing_app:
        conn.close()
        bot.send_message(
            chat_id,
            "ℹ️ <b>Siz ushbu vakansiyaga allaqachon ariza topshirgansiz!</b>\n\nIsh beruvchi arizangizni ko'rib chiqqanida sizga xabar yetkaziladi.",
            parse_mode="HTML"
        )
        return

    # Arizani bazaga yozamiz
    cur.execute(
        "INSERT INTO applications (vacancy_id, seeker_id, resume_id) VALUES (?, ?, ?)",
        (vac_id, seeker_id, res["id"])
    )
    app_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Nomzodga tasdiq
    bot.send_message(
        chat_id,
        f"✅ <b>ARIZANGIZ ISH BERUVCHIGA YUBORILDI!</b>\n\n"
        f"💼 <b>Vakansiya:</b> {html.escape(vac['title'])}\n"
        f"🏢 <b>Kompaniya:</b> {html.escape(vac['company'])}\n\n"
        f"Ish beruvchi arizangizni ko'rib chiqqanida sizga bot orqali xabar yetkaziladi.",
        parse_mode="HTML"
    )

    # Ish beruvchiga bildirishnoma yuborish
    employer_id = vac["employer_id"]
    try:
        emp_text = (
            f"🔔 <b>YANGI ARIZA QABUL QILINDI!</b>\n\n"
            f"💼 <b>Vakansiyangiz:</b> {html.escape(vac['title'])}\n\n"
            f"👤 <b>Nomzod:</b> {html.escape(res['full_name'])}\n"
            f"🎯 <b>Mutaxassisligi:</b> {html.escape(res['profession'])}\n"
            f"⏳ <b>Tajribasi:</b> {html.escape(res['experience'])}\n"
            f"🛠 <b>Ko'nikmalari:</b> {html.escape(res['skills'])}\n"
            f"💰 <b>Kutilayotgan maosh:</b> {html.escape(res['salary'])}\n"
            f"📍 <b>Hudud:</b> {html.escape(res['city'])}\n"
            f"📞 <b>Telefon:</b> {html.escape(res['phone'])}\n"
            f"👤 <b>Telegram:</b> @{html.escape(str(res['telegram'] or '').lstrip('@'))}\n"
        )

        emp_markup = types.InlineKeyboardMarkup(row_width=2)
        emp_markup.add(
            types.InlineKeyboardButton("✅ Qabul qilish", callback_data=f"app_accept_{app_id}"),
            types.InlineKeyboardButton("❌ Rad etish", callback_data=f"app_reject_{app_id}")
        )
        emp_markup.add(
            types.InlineKeyboardButton("📄 PDF Rezyumeni yuklash", callback_data=f"app_pdf_{res['id']}")
        )

        bot.send_message(employer_id, emp_text, reply_markup=emp_markup, parse_mode="HTML")
    except Exception as e:
        logger.error(f"Ish beruvchiga arizani yetkazishda xatolik: {e}")


# ==================== MATNLI XABARLARNI QABUL QILISH ====================
@bot.message_handler(func=lambda msg: True, content_types=["text", "contact"])
def handle_all_messages(message: types.Message):
    user_id = message.from_user.id
    text = (message.text or "").strip()

    # Agar foydalanuvchi biror wizard jarayonida bo'lsa
    if user_id in USER_STATES:
        state = USER_STATES[user_id]
        if state.get("flow") == "vacancy":
            handle_vacancy_step(message, state)
            return
        elif state.get("flow") == "resume":
            handle_resume_step(message, state)
            return

    # Reply klaviatura tugmalari
    if text == "➕ Vakansiya joylash":
        register_or_update_user(message.from_user, "employer")
        start_vacancy_wizard(message.chat.id, user_id)

    elif text == "📋 Mening vakansiyalarim":
        show_my_vacancies(message.chat.id, user_id)

    elif text == "📥 Kelgan arizalar":
        show_employer_applications(message.chat.id, user_id)

    elif text == "🔍 Ish izlash (Vakansiyalar)":
        show_vacancies_list(message.chat.id)

    elif text == "📄 Mening rezyumem":
        show_my_resume(message.chat.id, user_id)

    elif text == "📑 Mening arizalarim":
        show_my_applications(message.chat.id, user_id)

    elif text == "🏢 Ish beruvchi rejimiga o'tish":
        register_or_update_user(message.from_user, "employer")
        bot.send_message(
            message.chat.id,
            "🏢 <b>Siz «Ish beruvchi» rejimiga o'tdingiz.</b>\nEndi vakansiya joylashtirishingiz va xodimlardan arizalar qabul qilishingiz mumkin.",
            reply_markup=main_reply_keyboard("employer"),
            parse_mode="HTML"
        )

    elif text == "🔍 Ish qidiruvchi rejimiga o'tish":
        register_or_update_user(message.from_user, "seeker")
        bot.send_message(
            message.chat.id,
            "🔍 <b>Siz «Ish qidiruvchi» rejimiga o'tdingiz.</b>\nRezyumengizni yarating va yangi vakansiyalarga ariza topshiring.",
            reply_markup=main_reply_keyboard("seeker"),
            parse_mode="HTML"
        )

    elif text == "ℹ️ Bot haqida":
        bot_uname = get_bot_username()
        ch_target = get_channel_target() or "Mavjud emas"
        bot.send_message(
            message.chat.id,
            f"🌟 <b>UNIVERSAL ISH TOPISH BOTI</b>\n\n"
            f"🤖 <b>Bot:</b> @{bot_uname}\n"
            f"📢 <b>Rasmiy kanal:</b> <code>{ch_target}</code>\n"
            f"👑 <b>Muallif:</b> @usman_khasan\n\n"
            f"Ushbu bot O'zbekistonda ish beruvchilar va ish qidiruvchilarni eng qulay, tezkor va avtomatlashtirilgan tarzda birlashtiradi.",
            parse_mode="HTML"
        )

    elif text == "📞 Yordam":
        bot.send_message(
            message.chat.id,
            "📞 <b>QO'LLAB-QUVVATLASH VA SAVOLLAR:</b>\n\n"
            "Botdan foydalanishda savollaringiz yoki takliflaringiz bo'lsa, ma'muriyat bilan bog'laning:\n"
            "👤 <b>Administrator:</b> @usman_khasan\n\n"
            "Bosh menyuga qaytish uchun /start buyrug'ini bering.",
            parse_mode="HTML"
        )


# ==================== FOYDALANUVCHI BO'LIMLARI ====================
def show_my_vacancies(chat_id: int, employer_id: int):
    """Ish beruvchining o'z vakansiyalari ro'yxatini ko'rsatadi."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vacancies WHERE employer_id = ? ORDER BY id DESC", (employer_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Birinchi vakansiyani joylash", callback_data="btn_add_vac"))
        bot.send_message(
            chat_id,
            "📭 <b>Siz hali hech qanday vakansiya joylamagansiz.</b>\n\nYangi ish o'rni e'lon qilish uchun pastdagi tugmani bosing:",
            reply_markup=markup,
            parse_mode="HTML"
        )
        return

    text = f"📋 <b>SIZNING VAKANSIYALARINGIZ ({len(rows)} ta):</b>\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)

    for vac in rows[:10]:
        status_icon = "🟢 Faol" if vac["status"] == "active" else "🔴 Yopilgan"
        btn_text = f"{vac['title']} ({vac['company']}) — {status_icon}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"view_my_vac_{vac['id']}"))

    markup.add(types.InlineKeyboardButton("➕ Yangi vakansiya qo'shish", callback_data="btn_add_vac"))
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


def show_vacancies_list(chat_id: int):
    """Ish qidiruvchilar uchun oxirgi faol vakansiyalar."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM vacancies WHERE status = 'active' ORDER BY id DESC LIMIT 8")
    rows = cur.fetchall()
    conn.close()

    if not rows:
        bot.send_message(chat_id, "📭 Hozircha faol vakansiyalar mavjud emas. Tez orada yangilari qo'shiladi!")
        return

    text = "💼 <b>ENG SO'NGGI FAOL VAKANSIYALAR:</b>\nBatafsil ma'lumot olish uchun tanlang:\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for vac in rows:
        btn_text = f"💼 {vac['title']} — {vac['company']} ({vac['city']})"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"vac_details_{vac['id']}"))

    ch = get_channel_target()
    if ch and ch.startswith("@"):
        markup.add(types.InlineKeyboardButton("📢 Barcha vakansiyalar kanali", url=f"https://t.me/{ch.lstrip('@')}"))

    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


def show_my_resume(chat_id: int, user_id: int):
    """Foydalanuvchining o'z rezyumesini ko'rsatish va PDF yuklab olish."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
    res = cur.fetchone()
    conn.close()

    if not res:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📝 Rezyume yaratish", callback_data="btn_create_resume"))
        bot.send_message(
            chat_id,
            "📭 <b>Siz hali rezyume yaratmagansiz.</b>\n\n1 daqiqada rezyume to'ldirib, orzuingizdagi ishga 1 bosishda ariza topshiring!",
            reply_markup=markup,
            parse_mode="HTML"
        )
        return

    text = (
        f"📄 <b>SIZNING REZYUMENGIZ:</b>\n\n"
        f"👤 <b>F.I.Sh:</b> {html.escape(res['full_name'])}\n"
        f"💼 <b>Mutaxassislik:</b> {html.escape(res['profession'])}\n"
        f"⏳ <b>Tajriba:</b> {html.escape(res['experience'])}\n"
        f"🛠 <b>Ko'nikmalar:</b> {html.escape(res['skills'])}\n"
        f"💰 <b>Kutilayotgan maosh:</b> {html.escape(res['salary'])}\n"
        f"📍 <b>Hudud:</b> {html.escape(res['city'])}\n"
        f"📞 <b>Telefon:</b> {html.escape(res['phone'])}\n"
        f"👤 <b>Telegram:</b> @{html.escape(str(res['telegram'] or '').lstrip('@'))}\n"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📥 PDF Yuklab olish", callback_data=f"download_pdf_{res['id']}"),
        types.InlineKeyboardButton("✏️ Tahrirlash", callback_data="btn_create_resume")
    )
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


def show_my_applications(chat_id: int, user_id: int):
    """Ish qidiruvchining topshirgan arizalari ro'yxati."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, a.status, a.created_at, v.title, v.company
        FROM applications a
        JOIN vacancies v ON a.vacancy_id = v.id
        WHERE a.seeker_id = ?
        ORDER BY a.id DESC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        bot.send_message(chat_id, "📭 Siz hali hech qaysi vakansiyaga ariza topshirmagansiz.")
        return

    text = f"📑 <b>TOPShIRILGAN ARIZALARINGIZ ({len(rows)} ta):</b>\n\n"
    for r in rows:
        st = r["status"]
        if st == "accepted":
            st_badge = "✅ Qabul qilindi"
        elif st == "rejected":
            st_badge = "❌ Rad etildi"
        else:
            st_badge = "⏳ Ko'rib chiqilmoqda"

        text += f"• <b>{html.escape(r['title'])}</b> ({html.escape(r['company'])})\n  Holati: <b>{st_badge}</b>\n\n"

    bot.send_message(chat_id, text, parse_mode="HTML")


def show_employer_applications(chat_id: int, employer_id: int):
    """Ish beruvchining vakansiyalariga kelgan nomzodlar ro'yxati."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id as app_id, a.status, v.title, r.full_name, r.profession, r.phone, r.id as res_id
        FROM applications a
        JOIN vacancies v ON a.vacancy_id = v.id
        JOIN resumes r ON a.resume_id = r.id
        WHERE v.employer_id = ?
        ORDER BY a.id DESC
        LIMIT 10
    """, (employer_id,))
    rows = cur.fetchall()
    conn.close()

    if not rows:
        bot.send_message(chat_id, "📭 Hozircha vakansiyalaringizga arizalar kelib tushmagan.")
        return

    text = f"📥 <b>KELGAN ARIZALAR ({len(rows)} ta):</b>\n\n"
    markup = types.InlineKeyboardMarkup(row_width=1)
    for r in rows:
        st_icon = "🟢" if r["status"] == "accepted" else ("🔴" if r["status"] == "rejected" else "🟡")
        btn_text = f"{st_icon} {r['full_name']} — {r['title']}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"app_detail_{r['app_id']}"))

    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


# ==================== CALLBACK QUERY (INLINE TUGMALAR) ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call: types.CallbackQuery):
    data = call.data
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    try:
        # Rol tanlash
        if data == "role_seeker":
            register_or_update_user(call.from_user, "seeker")
            bot.answer_callback_query(call.id, "Siz «Ish qidiruvchi» rejimidasiz")
            bot.send_message(
                chat_id,
                "🔍 <b>«Ish qidiruvchi» rejimi faollashdi.</b>\n\nRezyumengizni yarating yoki mavjud vakansiyalarni ko'ring:",
                reply_markup=main_reply_keyboard("seeker"),
                parse_mode="HTML"
            )

        elif data == "role_employer":
            register_or_update_user(call.from_user, "employer")
            bot.answer_callback_query(call.id, "Siz «Ish beruvchi» rejimidasiz")
            bot.send_message(
                chat_id,
                "🏢 <b>«Ish beruvchi» rejimi faollashdi.</b>\n\nYangi vakansiya joylashtiring va xodimlardan arizalar qabul qiling:",
                reply_markup=main_reply_keyboard("employer"),
                parse_mode="HTML"
            )

        elif data == "btn_add_vac":
            bot.answer_callback_query(call.id)
            start_vacancy_wizard(chat_id, user_id)

        elif data == "btn_create_resume":
            bot.answer_callback_query(call.id)
            start_resume_wizard(chat_id, user_id)

        elif data == "browse_vacancies":
            bot.answer_callback_query(call.id)
            show_vacancies_list(chat_id)

        elif data == "my_vacancies":
            bot.answer_callback_query(call.id)
            show_my_vacancies(chat_id, user_id)

        # Vakansiya tafsilotlarini ko'rish
        elif data.startswith("vac_details_"):
            vac_id = int(data.split("_")[2])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM vacancies WHERE id = ?", (vac_id,))
            vac = cur.fetchone()
            conn.close()
            if vac:
                bot.answer_callback_query(call.id)
                show_vacancy_card(chat_id, vac, show_apply_btn=True)
            else:
                bot.answer_callback_query(call.id, "Vakansiya topilmadi!", show_alert=True)

        # Ariza topshirish (apply_{id})
        elif data.startswith("apply_"):
            vac_id = int(data.split("_")[1])
            bot.answer_callback_query(call.id)
            process_application(chat_id, user_id, vac_id)

        # PDF yuklab olish
        elif data.startswith("download_pdf_") or data.startswith("app_pdf_"):
            res_id = int(data.split("_")[-1])
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT * FROM resumes WHERE id = ?", (res_id,))
            res = cur.fetchone()
            conn.close()

            if not res:
                bot.answer_callback_query(call.id, "Rezyume topilmadi", show_alert=True)
                return

            bot.answer_callback_query(call.id, "PDF tayyorlanmoqda...")
            pdf_buf = generate_resume_pdf(res)
            if pdf_buf:
                clean_name = re.sub(r"\W+", "_", res["full_name"] or "Rezyume")
                pdf_buf.name = f"Rezyume_{clean_name}.pdf"
                bot.send_document(
                    chat_id,
                    pdf_buf,
                    caption=f"📄 <b>{html.escape(res['full_name'])} — Professional Rezyume (PDF)</b>",
                    parse_mode="HTML"
                )
            else:
                bot.send_message(
                    chat_id,
                    f"📄 <b>{html.escape(res['full_name'])} — Rezyume:</b>\n\n"
                    f"Mutaxassislik: {html.escape(res['profession'])}\n"
                    f"Tajriba: {html.escape(res['experience'])}\n"
                    f"Ko'nikmalar: {html.escape(res['skills'])}\n"
                    f"Telefon: {html.escape(res['phone'])}\n"
                    f"Telegram: @{html.escape(str(res['telegram'] or '').lstrip('@'))}",
                    parse_mode="HTML"
                )

        # Arizani qabul qilish / rad etish
        elif data.startswith("app_accept_") or data.startswith("app_reject_"):
            is_accept = data.startswith("app_accept_")
            app_id = int(data.split("_")[-1])
            new_status = "accepted" if is_accept else "rejected"

            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT a.seeker_id, v.title, v.company, r.full_name
                FROM applications a
                JOIN vacancies v ON a.vacancy_id = v.id
                JOIN resumes r ON a.resume_id = r.id
                WHERE a.id = ?
            """, (app_id,))
            app_info = cur.fetchone()

            if app_info:
                cur.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
                conn.commit()
                conn.close()

                bot.answer_callback_query(call.id, f"Holat yangilandi: {new_status}")
                status_word = "Qabul qilindi ✅" if is_accept else "Rad etildi ❌"
                bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
                bot.send_message(chat_id, f"Ariza holati: <b>{status_word}</b>", parse_mode="HTML")

                # Nomzodga xabar yetkazish
                try:
                    if is_accept:
                        seeker_msg = (
                            f"🎉 <b>TABRIKLAYMIZ! ARIZANGIZ QABUL QILINDI!</b>\n\n"
                            f"💼 <b>Vakansiya:</b> {html.escape(app_info['title'])}\n"
                            f"🏢 <b>Kompaniya:</b> {html.escape(app_info['company'])}\n\n"
                            f"Ish beruvchi nomzodingizni ma'qulladi. Tez orada ular siz bilan bog'lanishadi!"
                        )
                    else:
                        seeker_msg = (
                            f"ℹ️ <b>Ariza holati:</b>\n\n"
                            f"«{html.escape(app_info['title'])}» ({html.escape(app_info['company'])}) vakansiyasi bo'yicha arizangiz ko'rib chiqildi va rad etildi.\n"
                            f"Kanalimizdagi boshqa ochiq vakansiyalarga ariza topshirishingiz mumkin."
                        )
                    bot.send_message(app_info["seeker_id"], seeker_msg, parse_mode="HTML")
                except Exception:
                    pass
            else:
                conn.close()
                bot.answer_callback_query(call.id, "Ariza topilmadi")

    except Exception as e:
        logger.error(f"Callback xatosi: {e}")
        try:
            bot.answer_callback_query(call.id, "Xatolik yuz berdi")
        except Exception:
            pass


# ==================== DASTURNI ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    init_db()

    print("=" * 65)
    print(f"🚀 Universal Ish Topish Boti ishga tushmoqda...")
    print(f"👤 Rasmiy Username: @{PRIMARY_BOT_USERNAME}")
    print(f"👑 Bosh Admin ID: {ADMIN_ID} (@usman_khasan)")
    print(f"📢 Kanal: {get_channel_target() or 'Hali belgilanmagan (/set_channel)'}")
    print("=" * 65)

    try:
        me = bot.get_me()
        print(f"✅ Telegram API ga muvaffaqiyatli ulandi: @{me.username} ({me.first_name})")
    except Exception as e:
        print(f"⚠️ Telegramga ulanish ogohlantirishi: {e}")

    # Polling orqali botni 24/7 uzluksiz yurgizish (auto-reconnect)
    print("🤖 Bot 24/7 uzluksiz polling rejimida ishga tushdi...")
    import time
    while True:
        try:
            bot.infinity_polling(timeout=35, long_polling_timeout=20, skip_pending=True)
        except (KeyboardInterrupt, SystemExit):
            print("\n🛑 Bot toxtatildi.")
            break
        except Exception as e:
            logger.error(f"Polling xatosi (5 soniyada qayta ulanadi): {e}")
            time.sleep(5)
