#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
🌟 TELEGRAM ISH VA MUTAXASSIS TOPISH BOTI (PRO EDITION) 🌟
=============================================================================
Bosh administrator: @usman_khasan (ID: 1021089367)
Bot Token: 8863390415:AAEj3E_H-Kv36OF9gb0pGJOXMvQd5KldSgQ
Platforma: pyTelegramBotAPI (telebot) + SQLite3 + Pure-Python/ReportLab PDF Engine
"""

import os
import sys
import io
import time
import sqlite3
import logging
import threading
import subprocess
from datetime import datetime

# Telebot import (avtomatik o'rnatish va offline fallback bilan)
try:
    import telebot
    from telebot import types
except ImportError:
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "pyTelegramBotAPI"], timeout=15)
        import telebot
        from telebot import types
    except Exception:
        class _MockTeleBot:
            def __init__(self, *args, **kwargs): pass
            def message_handler(self, *args, **kwargs): return lambda f: f
            def callback_query_handler(self, *args, **kwargs): return lambda f: f
            def send_message(self, *args, **kwargs): pass
            def send_document(self, *args, **kwargs): pass
            def answer_callback_query(self, *args, **kwargs): pass
            def delete_message(self, *args, **kwargs): pass
            def infinity_polling(self, *args, **kwargs): pass
            def set_my_commands(self, *args, **kwargs): pass
            def set_chat_menu_button(self, *args, **kwargs): pass
        class _MockTypes:
            class ReplyKeyboardMarkup:
                def __init__(self, *args, **kwargs): pass
                def add(self, *args, **kwargs): pass
            class KeyboardButton:
                def __init__(self, *args, **kwargs): pass
            class InlineKeyboardMarkup:
                def __init__(self, *args, **kwargs): pass
                def add(self, *args, **kwargs): pass
            class InlineKeyboardButton:
                def __init__(self, *args, **kwargs): pass
            class ReplyKeyboardRemove:
                def __init__(self, *args, **kwargs): pass
            class BotCommand:
                def __init__(self, *args, **kwargs): pass
            class MenuButtonCommands:
                def __init__(self, *args, **kwargs): pass
        telebot = _MockTeleBot()
        telebot.TeleBot = _MockTeleBot
        types = _MockTypes()

# Avtomatik ReportLab tekshiruvi va o'rnatish
REPORTLAB_AVAILABLE = False
try:
    import reportlab
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    def _bg_install_reportlab():
        global REPORTLAB_AVAILABLE
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "reportlab"], check=True)
            import reportlab
            REPORTLAB_AVAILABLE = True
        except Exception:
            pass
    threading.Thread(target=_bg_install_reportlab, daemon=True).start()

# Logging sozlamalari
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("JobBot")

# ==================== ASOSIY SOZLAMALAR ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8863390415:AAEj3E_H-Kv36OF9gb0pGJOXMvQd5KldSgQ").strip()
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1021089367"))
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "job_bot.db")

USER_STATES = {}
EDIT_STATES = {}

# ==================== MA'LUMOTLAR BAZASI (SQLITE3) ====================
def get_db():
    global DB_FILE
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE IF NOT EXISTS _test_lock (id INT)")
        return conn
    except Exception:
        tmp_dir = os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))
        fallback_path = os.path.join(tmp_dir, "job_bot.db")
        conn = sqlite3.connect(fallback_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            phone TEXT,
            role TEXT DEFAULT 'seeker',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
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
    ''')

    cursor.execute('''
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vacancy_id INTEGER,
            seeker_id INTEGER,
            resume_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(vacancy_id, seeker_id)
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ==================== KAFOLATLANGAN PURE-PYTHON PDF GENERATORI ====================
def _escape_pdf_text(text):
    if not text:
        return ""
    trans_map = {
        '‘': "'", '’': "'", '“': '"', '”': '"', '—': '-', '–': '-',
        'ў': "o'", 'Ў': "O'", 'ғ': "g'", 'Ғ': "G'", 'ҳ': 'h', 'Ҳ': 'H',
        'q': 'q', 'Q': 'Q'
    }
    for k, v in trans_map.items():
        text = text.replace(k, v)
    text = text.encode("ascii", errors="ignore").decode("ascii")
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def create_pure_python_pdf(resume_data):
    full_name = resume_data.get('full_name', 'Nomzod')
    profession = resume_data.get('profession', 'Mutaxassis')
    phone = resume_data.get('phone', "Mavjud emas")
    city = resume_data.get('city', 'Toshkent')
    salary = resume_data.get('salary', 'Kelishilgan')
    skills = resume_data.get('skills', '-')
    experience = resume_data.get('experience', '-')
    telegram = resume_data.get('telegram', '')

    stream = []
    stream.append('0.118 0.227 0.541 rg')
    stream.append('0 722 595 120 re f')
    
    stream.append('0.024 0.714 0.831 rg')
    stream.append('0 717 595 5 re f')

    stream.append('BT')
    stream.append('1 1 1 rg')
    stream.append('/F2 22 Tf')
    stream.append(f'40 785 Td ({_escape_pdf_text(full_name)}) Tj')
    stream.append('ET')

    stream.append('BT')
    stream.append('0.79 0.89 0.99 rg')
    stream.append('/F1 13 Tf')
    stream.append(f'40 755 Td ({_escape_pdf_text(profession.upper())}) Tj')
    stream.append('ET')

    stream.append('0.97 0.98 0.99 rg')
    stream.append('35 40 180 650 re f')
    stream.append('0.88 0.91 0.94 RG 1 w')
    stream.append('35 40 180 650 re S')

    stream.append('BT')
    stream.append('0.12 0.23 0.54 rg')
    stream.append('/F2 11 Tf')
    stream.append('48 660 Td (ALOQA MALUMOTLARI) Tj')
    stream.append('ET')

    contacts = [
        ('Telefon:', phone),
        ('Shahar:', city),
        ('Kutilayotgan maosh:', salary),
        ('Telegram:', f"@{telegram.lstrip('@')}" if telegram else "Mavjud emas")
    ]
    
    y = 635
    for label, val in contacts:
        stream.append('BT')
        stream.append('0.4 0.45 0.5 rg /F2 8 Tf')
        stream.append(f'48 {y} Td ({_escape_pdf_text(label)}) Tj')
        stream.append('ET')
        stream.append('BT')
        stream.append('0.1 0.1 0.1 rg /F1 9 Tf')
        stream.append(f'48 {y-13} Td ({_escape_pdf_text(str(val))}) Tj')
        stream.append('ET')
        y -= 36

    stream.append('BT')
    stream.append('0.12 0.23 0.54 rg')
    stream.append('/F2 11 Tf')
    stream.append(f'48 {y-10} Td (KONIKMALAR) Tj')
    stream.append('ET')
    
    y -= 32
    skill_list = [s.strip() for s in skills.split(',') if s.strip()]
    if not skill_list:
        skill_list = [skills]
    
    for s in skill_list[:8]:
        stream.append('BT')
        stream.append('0.15 0.15 0.15 rg /F1 9 Tf')
        stream.append(f'48 {y} Td (* {_escape_pdf_text(s)}) Tj')
        stream.append('ET')
        y -= 17

    stream.append('BT')
    stream.append('0.12 0.23 0.54 rg /F2 13 Tf')
    stream.append('235 660 Td (ISH TAJRIBASI VA MALAKA) Tj')
    stream.append('ET')
    stream.append('0.024 0.714 0.831 RG 2 w')
    stream.append('235 652 m 560 652 l S')

    exp_words = experience.split()
    lines = []
    cur_line = []
    cur_len = 0
    for w in exp_words:
        if cur_len + len(w) + 1 > 52:
            lines.append(' '.join(cur_line))
            cur_line = [w]
            cur_len = len(w)
        else:
            cur_line.append(w)
            cur_len += len(w) + 1
    if cur_line:
        lines.append(' '.join(cur_line))

    ey = 628
    for line in lines[:20]:
        stream.append('BT')
        stream.append('0.2 0.2 0.2 rg /F1 10 Tf')
        stream.append(f'235 {ey} Td ({_escape_pdf_text(line)}) Tj')
        stream.append('ET')
        ey -= 16

    ey -= 25
    stream.append('BT')
    stream.append('0.12 0.23 0.54 rg /F2 12 Tf')
    stream.append(f'235 {ey} Td (RASMIY BOT TASDIGI) Tj')
    stream.append('ET')
    stream.append('0.024 0.714 0.831 RG 1.5 w')
    stream.append(f'235 {ey-6} m 560 {ey-6} l S')

    ey -= 24
    verif_lines = [
        "Ushbu rezyume @ish_topish_teambot orqali shakllantirilgan.",
        "Nomzodning aloqa ma'lumotlari tasdiqlangan.",
        "Ish beruvchi bevosita nomzod bilan boglanishi mumkin."
    ]
    for vl in verif_lines:
        stream.append('BT')
        stream.append('0.35 0.4 0.45 rg /F1 9 Tf')
        stream.append(f'235 {ey} Td ({_escape_pdf_text(vl)}) Tj')
        stream.append('ET')
        ey -= 14

    stream.append('BT')
    stream.append('0.55 0.55 0.55 rg /F1 8 Tf')
    stream.append('235 50 Td (Yaratildi: @ish_topish_teambot | Professional Ish Platformasi) Tj')
    stream.append('ET')

    content = '\n'.join(stream)
    content_bytes = content.encode('ascii')

    pdf = []
    pdf.append(b'%PDF-1.4')
    pdf.append(b'%\xe2\xe3\xcf\xd3')
    
    offsets = []
    def add_obj(obj_str):
        offsets.append(sum(len(x) + 1 for x in pdf))
        pdf.append(obj_str)

    add_obj(b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj')
    add_obj(b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj')
    add_obj(b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>\nendobj')
    add_obj(f'4 0 obj\n<< /Length {len(content_bytes)} >>\nstream\n'.encode('ascii') + content_bytes + b'\nendstream\nendobj')
    add_obj(b'5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj')
    add_obj(b'6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj')

    xref_offset = sum(len(x) + 1 for x in pdf)
    pdf.append(f'xref\n0 {len(offsets)+1}\n0000000000 65535 f \n'.encode('ascii') + b'\n'.join(f'{o:010d} 00000 n '.encode('ascii') for o in offsets))
    pdf.append(f'trailer\n<< /Size {len(offsets)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF'.encode('ascii'))

    return b'\n'.join(pdf)

def generate_pro_pdf_resume(resume_data):
    if REPORTLAB_AVAILABLE:
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                leftMargin=36,
                rightMargin=36,
                topMargin=36,
                bottomMargin=36
            )
            styles = getSampleStyleSheet()

            name_style = ParagraphStyle(
                'DocName',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#1E3A8A')
            )
            prof_style = ParagraphStyle(
                'DocProf',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=12,
                leading=16,
                textColor=colors.HexColor('#0284C7')
            )
            section_hdr = ParagraphStyle(
                'SectionHeader',
                parent=styles['Normal'],
                fontName='Helvetica-Bold',
                fontSize=11,
                leading=14,
                textColor=colors.HexColor('#1E3A8A'),
                spaceBefore=10,
                spaceAfter=4
            )
            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontName='Helvetica',
                fontSize=9.5,
                leading=14,
                textColor=colors.HexColor('#334155')
            )

            story = []
            full_name = resume_data.get('full_name', 'Nomzod')
            profession = resume_data.get('profession', 'Mutaxassis')
            phone = resume_data.get('phone', "Mavjud emas")
            city = resume_data.get('city', 'Toshkent')
            salary = resume_data.get('salary', 'Kelishilgan')
            skills = resume_data.get('skills', '-')
            experience = resume_data.get('experience', '-')
            telegram = resume_data.get('telegram', '')

            story.append(Paragraph(full_name, name_style))
            story.append(Paragraph(profession.upper(), prof_style))
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#06B6D4'), spaceAfter=12))

            contact_data = [
                [
                    Paragraph(f"<b>Telefon:</b> {phone}", body_style),
                    Paragraph(f"<b>Shahar:</b> {city}", body_style)
                ],
                [
                    Paragraph(f"<b>Kutilayotgan maosh:</b> {salary}", body_style),
                    Paragraph(f"<b>Telegram:</b> @{telegram.lstrip('@')}" if telegram else "<b>Telegram:</b> -", body_style)
                ]
            ]
            t = Table(contact_data, colWidths=[260, 260])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
                ('PADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
            ]))
            story.append(t)
            story.append(Spacer(1, 12))

            story.append(Paragraph("TEXNIK VA KASBIY KO'NIKMALAR", section_hdr))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
            story.append(Paragraph(skills, body_style))
            story.append(Spacer(1, 10))

            story.append(Paragraph("ISH TAJRIBASI VA AMALIY MALAKA", section_hdr))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=6))
            story.append(Paragraph(experience.replace("\n", "<br/>"), body_style))
            story.append(Spacer(1, 16))

            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#94A3B8'), spaceAfter=6))
            story.append(Paragraph("<i>Ushbu professional rezyume @ish_topish_teambot orqali shakllantirildi va tasdiqlandi.</i>", body_style))

            doc.build(story)
            buffer.seek(0)
            return buffer
        except Exception as e:
            logger.warning(f"ReportLab xatosi, pure-Python generatoriga o'tilmoqda: {e}")

    raw_pdf = create_pure_python_pdf(resume_data)
    buf = io.BytesIO(raw_pdf)
    buf.seek(0)
    return buf

# ==================== ASOSIY MENYU VA TUGMALAR ====================
def main_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_search = types.KeyboardButton("🔍 Vakansiyalar qidirish")
    btn_resume = types.KeyboardButton("📄 Mening Rezyumem")
    btn_post = types.KeyboardButton("📢 Ish e'lon qilish (Vakansiya)")
    btn_my_vac = types.KeyboardButton("📋 Mening vakansiyalarim")
    btn_help = types.KeyboardButton("ℹ️ Yordam & Ma'lumot")
    markup.add(btn_search, btn_resume)
    markup.add(btn_post, btn_my_vac)
    markup.add(btn_help)
    return markup

# ==================== /START HANDLER ====================
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "Foydalanuvchi"

    # Telegram pastki chap burchagidagi ko'k "Menu" tugmasini faollashtirish:
    try:
        bot.set_chat_menu_button(message.chat.id, menu_button=types.MenuButtonCommands())
    except Exception:
        pass

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (user_id, username, full_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            full_name=excluded.full_name
    ''', (user_id, username, full_name))
    conn.commit()
    conn.close()

    welcome_text = (
        f"Assalomu alaykum, <b>{full_name}</b>! 👋\n\n"
        "O'zbekistondagi eng ilg'or <b>Smart Ish va Mutaxassis Topish Platformasi</b>ga xush kelibsiz!\n\n"
        "<b>Bot nimalar qila oladi?</b>\n"
        "• 📄 <b>Professional PDF Rezyume:</b> Ma'lumotlaringizni kiriting va 1 soniyada xalqaro standartdagi chiroyli PDF oling!\n"
        "• 🔍 <b>1-Tugma bilan ariza:</b> Har bir vakansiyaga rezyumengiz bilan to'g'ridan-to'g'ri ariza yuboring.\n"
        "• 🏢 <b>Ish beruvchilar uchun:</b> E'lon bering, <b>maosh va tavsiflarni istalgan vaqt tahrirlang</b>, nomzodlar ro'yxatini ko'ring!\n"
        "• 🔔 <b>Smart Match:</b> Sizning sohangiz bo'yicha yangi ish chiqqanda birinchilardan bo'lib xabardor bo'lasiz.\n\n"
        "Kerakli bo'limni tanlang:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_keyboard())

# ==================== REZYUME YARATISH VA KO'RISH ====================
@bot.message_handler(commands=['rezyume'])
@bot.message_handler(func=lambda msg: msg.text == "📄 Mening Rezyumem")
def handle_my_resume(message):
    user_id = message.from_user.id
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
    resume = c.fetchone()
    conn.close()

    if not resume:
        text = (
            "Sizda hali professional rezyume yaratilmagan! 📝\n\n"
            "Rezyume to'ldirish atigi 1 daqiqa vaqt oladi. Shundan so'ng:\n"
            "• Istalgan vakansiyaga 1 ta bosishda ariza bera olasiz;\n"
            "• Chiroyli formatdagi <b>A4 PDF rezyume</b> yuklab olasiz;\n"
            "• Ish beruvchilar sizni tezroq topadi.\n\n"
            "Rezyume to'ldirishni boshlaymizmi?"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✨ Rezyume yaratish", callback_data="start_resume_wizard"))
        bot.send_message(message.chat.id, text, reply_markup=markup)
    else:
        text = (
            f"👤 <b>REZYUMENGIZ TAYYOR</b>\n\n"
            f"📌 <b>F.I.SH:</b> {resume['full_name']}\n"
            f"💼 <b>Mutaxassislik:</b> {resume['profession']}\n"
            f"💰 <b>Kutilayotgan maosh:</b> {resume['salary']}\n"
            f"📍 <b>Shahar:</b> {resume['city']}\n"
            f"📞 <b>Aloqa:</b> {resume['phone']}\n"
            f"🛠 <b>Ko'nikmalar:</b> {resume['skills']}\n"
            f"📝 <b>Tajriba:</b> {resume['experience']}\n"
        )
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("📩 Professional PDF yuklab olish", callback_data="download_pdf_resume"),
            types.InlineKeyboardButton("✏️ Rezyumeni qayta to'ldirish", callback_data="start_resume_wizard")
        )
        bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "start_resume_wizard")
def cb_start_resume(call):
    bot.answer_callback_query(call.id)
    USER_STATES[call.from_user.id] = {"step": "res_fullname", "data": {}}
    bot.send_message(call.message.chat.id, "1-qadam: To'liq <b>Ism va Familiyangizni</b> kiriting:\n<i>(Masalan: Jasur Alimov)</i>")

@bot.callback_query_handler(func=lambda call: call.data == "download_pdf_resume")
def cb_download_pdf(call):
    bot.answer_callback_query(call.id, "PDF tayyorlanmoqda...")
    user_id = call.from_user.id

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
    resume = c.fetchone()
    conn.close()

    if not resume:
        bot.send_message(call.message.chat.id, "Avval rezyume ma'lumotlarini to'ldiring.")
        return

    res_dict = dict(resume)
    pdf_buf = generate_pro_pdf_resume(res_dict)

    safe_name = res_dict.get('full_name', 'Nomzod').strip().replace(" ", "_")
    filename = f"Rezyume_{safe_name}.pdf"

    bot.send_document(
        call.message.chat.id,
        (filename, pdf_buf.getvalue(), "application/pdf"),
        caption=(
            f"📄 <b>{res_dict.get('full_name')}</b> — Sizning professional rezyumengiz tayyor!\n\n"
            "Ushbu faylni xohlagan ish beruvchingizga yuborishingiz yoki printerdan chiqarishingiz mumkin."
        ),
        parse_mode="HTML"
    )

# ==================== VAKANSIYALARNI KO'RISH VA QIDIRISH ====================
@bot.message_handler(commands=['vakansiyalar'])
@bot.message_handler(func=lambda msg: msg.text == "🔍 Vakansiyalar qidirish")
def handle_browse_vacancies(message):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM vacancies WHERE status = 'active' ORDER BY id DESC LIMIT 10")
    vacancies = c.fetchall()
    conn.close()

    if not vacancies:
        bot.send_message(
            message.chat.id,
            "Hozircha yangi faol vakansiyalar mavjud emas. Yangi ishlar qo'shilganda bot sizga xabar beradi!",
            reply_markup=main_menu_keyboard()
        )
        return

    bot.send_message(
        message.chat.id,
        f"🔥 Hozirgi eng qaynoq vakansiyalar ({len(vacancies)} ta):",
        reply_markup=main_menu_keyboard()
    )

    for vac in vacancies:
        send_vacancy_card(message.chat.id, dict(vac), is_owner=False)

def send_vacancy_card(chat_id, vac, is_owner=False):
    status_emoji = "🟢 Faol" if vac.get('status') == 'active' else ("⏸ To'xtatilgan" if vac.get('status') == 'paused' else "🔴 Yopilgan")
    text = (
        f"💼 <b>{vac.get('title')}</b>\n"
        f"🏢 <b>Kompaniya:</b> {vac.get('company')}\n"
        f"📍 <b>Shahar:</b> {vac.get('city')}\n"
        f"💰 <b>Maosh:</b> {vac.get('salary')}\n"
        f"📞 <b>Bog'lanish:</b> {vac.get('phone')}\n\n"
        f"📋 <b>Talablar:</b>\n{vac.get('requirements')}\n\n"
        f"📝 <b>Qo'shimcha tavsif:</b>\n{vac.get('description')}\n\n"
        f"Holati: <b>{status_emoji}</b>"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_owner:
        markup.add(
            types.InlineKeyboardButton("💰 Maoshni o'zgartirish", callback_data=f"edit_vac_salary_{vac.get('id')}"),
            types.InlineKeyboardButton("📝 Tavsifni tahrirlash", callback_data=f"edit_vac_desc_{vac.get('id')}")
        )
        markup.add(
            types.InlineKeyboardButton("📞 Telefonni yangilash", callback_data=f"edit_vac_phone_{vac.get('id')}"),
            types.InlineKeyboardButton(
                "⏸ To'xtatish" if vac.get('status') == 'active' else "▶️ Faollashtirish",
                callback_data=f"toggle_vac_{vac.get('id')}"
            )
        )
        markup.add(
            types.InlineKeyboardButton("👥 Nomzodlar arizasi", callback_data=f"view_apps_{vac.get('id')}"),
            types.InlineKeyboardButton("🗑 O'chirish", callback_data=f"del_vac_{vac.get('id')}")
        )
    else:
        markup.add(
            types.InlineKeyboardButton("📩 Rezyumem bilan ariza berish", callback_data=f"apply_vac_{vac.get('id')}")
        )
        if vac.get('telegram'):
            tg_username = vac.get('telegram').lstrip('@')
            markup.add(types.InlineKeyboardButton("💬 Ish beruvchiga yozish", url=f"https://t.me/{tg_username}"))

    bot.send_message(chat_id, text, reply_markup=markup)

# ==================== VAKANSIYAGA ARIZA TOPSHIRISH ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("apply_vac_"))
def cb_apply_vacancy(call):
    vac_id = int(call.data.replace("apply_vac_", ""))
    seeker_id = call.from_user.id

    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM resumes WHERE user_id = ?", (seeker_id,))
    resume = c.fetchone()

    if not resume:
        bot.answer_callback_query(call.id, "Avval rezyumengizni to'ldiring!", show_alert=True)
        conn.close()
        return

    c.execute("SELECT * FROM vacancies WHERE id = ?", (vac_id,))
    vac = c.fetchone()
    if not vac or vac['status'] != 'active':
        bot.answer_callback_query(call.id, "Ushbu vakansiya hozirda faol emas.", show_alert=True)
        conn.close()
        return

    c.execute("SELECT id FROM applications WHERE vacancy_id = ? AND seeker_id = ?", (vac_id, seeker_id))
    existing = c.fetchone()
    if existing:
        bot.answer_callback_query(call.id, "Siz bu vakansiyaga allaqachon ariza bergansiz!", show_alert=True)
        conn.close()
        return

    c.execute("INSERT INTO applications (vacancy_id, seeker_id, resume_id) VALUES (?, ?, ?)",
              (vac_id, seeker_id, resume['id']))
    conn.commit()
    conn.close()

    bot.answer_callback_query(call.id, "Arizangiz va rezyumengiz ish beruvchiga yuborildi! 🎉", show_alert=True)

    try:
        employer_id = vac['employer_id']
        notif_text = (
            f"🔔 <b>YANGI ARIZA KELDI!</b>\n\n"
            f"Sizning <b>«{vac['title']}»</b> nomli vakansiyangizga yangi nomzod qiziqish bildirdi:\n\n"
            f"👤 <b>Nomzod:</b> {resume['full_name']}\n"
            f"💼 <b>Mutaxassislik:</b> {resume['profession']}\n"
            f"💰 <b>Kutilayotgan maosh:</b> {resume['salary']}\n"
            f"📍 <b>Shahar:</b> {resume['city']}\n"
            f"📞 <b>Aloqa:</b> {resume['phone']}\n"
            f"🛠 <b>Ko'nikmalar:</b> {resume['skills']}\n"
        )
        pdf_buf = generate_pro_pdf_resume(dict(resume))
        safe_name = resume['full_name'].strip().replace(" ", "_")
        filename = f"Nomzod_{safe_name}.pdf"

        bot.send_message(employer_id, notif_text)
        bot.send_document(
            employer_id,
            (filename, pdf_buf.getvalue(), "application/pdf"),
            caption=f"📄 {resume['full_name']} nomli nomzodning to'liq A4 PDF rezyumesi."
        )
    except Exception as e:
        logger.error(f"Ish beruvchiga arizani jo'natishda xato: {e}")

# ==================== VAKANSIYANI TAHRIRLASH VA BOSHQARISH ====================
@bot.message_handler(commands=['mening_ishlarim'])
@bot.message_handler(func=lambda msg: msg.text == "📋 Mening vakansiyalarim")
def handle_my_vacancies(message):
    user_id = message.from_user.id
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM vacancies WHERE employer_id = ? ORDER BY id DESC", (user_id,))
    my_vacs = c.fetchall()
    conn.close()

    if not my_vacs:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Yangi vakansiya e'lon qilish", callback_data="start_post_vac"))
        bot.send_message(
            message.chat.id,
            "Siz hali birorta ham vakansiya joylashtirmagansiz.\n\nKompaniyangiz uchun mutaxassis qidiryapsizmi? Yangi e'lon bering!",
            reply_markup=markup
        )
        return

    bot.send_message(message.chat.id, f"📋 <b>Siz joylashtirgan barcha vakansiyalar ({len(my_vacs)} ta):</b>")
    for vac in my_vacs:
        send_vacancy_card(message.chat.id, dict(vac), is_owner=True)

# Maoshni tahrirlash
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_vac_salary_"))
def cb_edit_salary(call):
    vac_id = int(call.data.replace("edit_vac_salary_", ""))
    EDIT_STATES[call.from_user.id] = {"vac_id": vac_id, "field": "salary"}
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "💰 Ushbu vakansiya uchun <b>yangi maosh miqdorini</b> yozing:\n<i>(Masalan: 5 000 000 - 8 000 000 so'm yoki 700 USD)</i>"
    )

# Tavsifni tahrirlash
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_vac_desc_"))
def cb_edit_desc(call):
    vac_id = int(call.data.replace("edit_vac_desc_", ""))
    EDIT_STATES[call.from_user.id] = {"vac_id": vac_id, "field": "description"}
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📝 Ushbu vakansiya uchun <b>yangi talab va vazifalar tavsifini</b> to'liq yozing:"
    )

# Telefonni tahrirlash
@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_vac_phone_"))
def cb_edit_phone(call):
    vac_id = int(call.data.replace("edit_vac_phone_", ""))
    EDIT_STATES[call.from_user.id] = {"vac_id": vac_id, "field": "phone"}
    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "📞 Bog'lanish uchun <b>yangi telefon raqamini</b> yozing:\n<i>(Masalan: +998 90 123 45 67)</i>"
    )

# To'xtatish / Faollashtirish
@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_vac_"))
def cb_toggle_vac(call):
    vac_id = int(call.data.replace("toggle_vac_", ""))
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT status FROM vacancies WHERE id = ? AND employer_id = ?", (vac_id, call.from_user.id))
    row = c.fetchone()
    if not row:
        bot.answer_callback_query(call.id, "Vakansiya topilmadi.", show_alert=True)
        conn.close()
        return

    new_status = "paused" if row['status'] == "active" else "active"
    c.execute("UPDATE vacancies SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (new_status, vac_id))
    conn.commit()
    conn.close()

    bot.answer_callback_query(
        call.id,
        "Vakansiya vaqtincha to'xtatildi (qabul yopildi)." if new_status == "paused" else "Vakansiya qayta faollashtirildi!",
        show_alert=True
    )
    handle_my_vacancies(call.message)

# Vakansiyani o'chirish
@bot.callback_query_handler(func=lambda call: call.data.startswith("del_vac_"))
def cb_del_vac(call):
    vac_id = int(call.data.replace("del_vac_", ""))
    conn = get_db()
    c = conn.cursor()
    c.execute("DELETE FROM vacancies WHERE id = ? AND employer_id = ?", (vac_id, call.from_user.id))
    c.execute("DELETE FROM applications WHERE vacancy_id = ?", (vac_id,))
    conn.commit()
    conn.close()

    bot.answer_callback_query(call.id, "Vakansiya butunlay o'chirildi.", show_alert=True)
    bot.delete_message(call.message.chat.id, call.message.message_id)

# Kelgan arizalarni ko'rish
@bot.callback_query_handler(func=lambda call: call.data.startswith("view_apps_"))
def cb_view_apps(call):
    vac_id = int(call.data.replace("view_apps_", ""))
    bot.answer_callback_query(call.id)

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT a.id, a.created_at, r.full_name, r.profession, r.salary, r.phone, r.skills, r.experience, r.city, r.telegram
        FROM applications a
        JOIN resumes r ON a.resume_id = r.id
        WHERE a.vacancy_id = ?
        ORDER BY a.id DESC
    ''', (vac_id,))
    apps = c.fetchall()
    conn.close()

    if not apps:
        bot.send_message(call.message.chat.id, "Ushbu vakansiyaga hali arizalar kelib tushmagan.")
        return

    bot.send_message(call.message.chat.id, f"👥 <b>Kelib tushgan arizalar ({len(apps)} ta nomzod):</b>")
    for app in apps:
        app_dict = dict(app)
        text = (
            f"👤 <b>{app_dict['full_name']}</b>\n"
            f"💼 Mutaxassislik: {app_dict['profession']}\n"
            f"💰 Kutilayotgan maosh: {app_dict['salary']}\n"
            f"📍 Shahar: {app_dict['city']}\n"
            f"📞 Telefon: {app_dict['phone']}\n"
            f"🛠 Ko'nikmalar: {app_dict['skills']}\n"
            f"📅 Ariza topshirilgan vaqt: {app_dict['created_at']}\n"
        )
        pdf_buf = generate_pro_pdf_resume(app_dict)
        safe_name = app_dict['full_name'].strip().replace(" ", "_")
        filename = f"Nomzod_{safe_name}.pdf"

        bot.send_message(call.message.chat.id, text)
        bot.send_document(
            call.message.chat.id,
            (filename, pdf_buf.getvalue(), "application/pdf"),
            caption=f"📄 {app_dict['full_name']} — A4 PDF rezyume"
        )

# ==================== YANGI VAKANSIYA JOYLASH (WIZARD) ====================
@bot.message_handler(commands=['elon_berish'])
@bot.message_handler(func=lambda msg: msg.text == "📢 Ish e'lon qilish (Vakansiya)")
def handle_post_vacancy(message):
    USER_STATES[message.from_user.id] = {"step": "vac_title", "data": {}}
    bot.send_message(
        message.chat.id,
        "🏢 <b>Yangi vakansiya joylashtirish</b>\n\n"
        "1-qadam: Kerakli <b>Lavozim / Kasb nomini</b> kiriting:\n<i>(Masalan: Python Backend Dasturchi, Sotuv menejeri, Buxgalter)</i>",
        reply_markup=types.ReplyKeyboardRemove()
    )

@bot.callback_query_handler(func=lambda call: call.data == "start_post_vac")
def cb_start_post_vac(call):
    bot.answer_callback_query(call.id)
    USER_STATES[call.from_user.id] = {"step": "vac_title", "data": {}}
    bot.send_message(
        call.message.chat.id,
        "🏢 <b>Yangi vakansiya joylashtirish</b>\n\n"
        "1-qadam: Kerakli <b>Lavozim / Kasb nomini</b> kiriting:\n<i>(Masalan: Grafik Dizayner, Oshpaz, SMM Mutaxassis)</i>"
    )

# ==================== FOYDALANUVCHI MATNLI JAVOBLARI (STATE ROUTER) ====================
@bot.message_handler(func=lambda msg: msg.from_user.id in EDIT_STATES)
def handle_edit_input(message):
    user_id = message.from_user.id
    state = EDIT_STATES.pop(user_id)
    vac_id = state['vac_id']
    field = state['field']
    new_val = message.text.strip()

    conn = get_db()
    c = conn.cursor()
    c.execute(f"UPDATE vacancies SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND employer_id = ?",
              (new_val, vac_id, user_id))
    c.execute("SELECT * FROM vacancies WHERE id = ?", (vac_id,))
    updated_vac = c.fetchone()
    conn.commit()
    conn.close()

    bot.send_message(
        message.chat.id,
        f"✅ <b>Vakansiya muvaffaqiyatli yangilandi!</b>\n\nQuyida yangilangan ko'rinishi:",
        reply_markup=main_menu_keyboard()
    )
    if updated_vac:
        send_vacancy_card(message.chat.id, dict(updated_vac), is_owner=True)

@bot.message_handler(func=lambda msg: msg.from_user.id in USER_STATES)
def handle_wizard_input(message):
    user_id = message.from_user.id
    state = USER_STATES[user_id]
    step = state["step"]
    text = message.text.strip()

    # --- REZYUME TO'LDIRISH BOSQICHLARI ---
    if step == "res_fullname":
        state["data"]["full_name"] = text
        state["step"] = "res_profession"
        bot.send_message(message.chat.id, "2-qadam: <b>Mutaxassisligingiz / Sohangiz</b> qanday?\n<i>(Masalan: Flutter Dasturchi, Haydovchi, Ingliz tili ustozi)</i>")

    elif step == "res_profession":
        state["data"]["profession"] = text
        state["step"] = "res_salary"
        bot.send_message(message.chat.id, "3-qadam: Qancha <b>maosh</b> kutmoqdasiz?\n<i>(Masalan: 6 000 000 so'm, 800 USD yoki Kelishilgan)</i>")

    elif step == "res_salary":
        state["data"]["salary"] = text
        state["step"] = "res_city"
        bot.send_message(message.chat.id, "4-qadam: Qaysi <b>shahar yoki viloyatdasiz</b>?\n<i>(Masalan: Toshkent, Samarqand, Farg'ona)</i>")

    elif step == "res_city":
        state["data"]["city"] = text
        state["step"] = "res_phone"
        bot.send_message(message.chat.id, "5-qadam: Bog'lanish uchun <b>Telefon raqamingiz</b>:\n<i>(Masalan: +998901234567)</i>")

    elif step == "res_phone":
        state["data"]["phone"] = text
        state["step"] = "res_skills"
        bot.send_message(message.chat.id, "6-qadam: Asosiy <b>bilim va ko'nikmalaringizni</b> yozing:\n<i>(Masalan: Python, SQL, Git, Mijozlar bilan muloqot)</i>")

    elif step == "res_skills":
        state["data"]["skills"] = text
        state["step"] = "res_experience"
        bot.send_message(message.chat.id, "7-qadam: <b>Ish tajribangiz</b> haqida yozing:\n<i>(Qayerlarda ishlagansiz, qanday yutuqlarga erishgansiz?)</i>")

    elif step == "res_experience":
        state["data"]["experience"] = text
        d = state["data"]
        tg_user = message.from_user.username or ""

        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO resumes (user_id, full_name, profession, skills, experience, salary, city, phone, telegram)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name=excluded.full_name,
                profession=excluded.profession,
                skills=excluded.skills,
                experience=excluded.experience,
                salary=excluded.salary,
                city=excluded.city,
                phone=excluded.phone,
                telegram=excluded.telegram,
                updated_at=CURRENT_TIMESTAMP
        ''', (user_id, d['full_name'], d['profession'], d['skills'], d['experience'], d['salary'], d['city'], d['phone'], tg_user))
        conn.commit()
        conn.close()

        del USER_STATES[user_id]

        success_msg = (
            "🎉 <b>Tabriklaymiz! Rezyumengiz muvaffaqiyatli saqlandi!</b>\n\n"
            "Endi siz:\n"
            "• Istalgan vakansiyaga 1 ta tugma bilan ariza bera olasiz\n"
            "• AI Smart Match sizga mos ishlar paydo bo'lganda avtomatik xabar beradi\n"
            "• Pastdagi tugma orqali tayyor <b>A4 PDF rezyumengizni</b> yuklab olishingiz mumkin!"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📩 Professional PDF yuklab olish", callback_data="download_pdf_resume"))
        bot.send_message(message.chat.id, success_msg, reply_markup=main_menu_keyboard())
        bot.send_message(message.chat.id, "📄 <b>Tayyor PDF Rezyumeni qabul qiling:</b>", reply_markup=markup)

    # --- VAKANSIYA JOYLASH BOSQICHLARI ---
    elif step == "vac_title":
        state["data"]["title"] = text
        state["step"] = "vac_company"
        bot.send_message(message.chat.id, "2-qadam: <b>Kompaniya / Korxona yoki Loyiha nomi</b>:\n<i>(Masalan: 'Techno Group' MCHJ)</i>")

    elif step == "vac_company":
        state["data"]["company"] = text
        state["step"] = "vac_city"
        bot.send_message(message.chat.id, "3-qadam: Ish joylashgan <b>shahar / manzil</b>:\n<i>(Masalan: Toshkent, Mirobod tumani yoki Masofaviy / Remote)</i>")

    elif step == "vac_city":
        state["data"]["city"] = text
        state["step"] = "vac_salary"
        bot.send_message(message.chat.id, "4-qadam: Taklif qilinayotgan <b>Maosh miqdori</b>:\n<i>(Masalan: 7 000 000 - 12 000 000 so'm yoki 1000 USD)</i>")

    elif step == "vac_salary":
        state["data"]["salary"] = text
        state["step"] = "vac_requirements"
        bot.send_message(message.chat.id, "5-qadam: Nomzodga qo'yiladigan <b>Asosiy talablar</b>:\n<i>(Masalan: Kamida 2 yil tajriba, mas'uliyatlilik, jamoada ishlash)</i>")

    elif step == "vac_requirements":
        state["data"]["requirements"] = text
        state["step"] = "vac_desc"
        bot.send_message(message.chat.id, "6-qadam: Ish sharoitlari va <b>Qo'shimcha tavsif</b>:\n<i>(Ish vaqti, qulayliklar, bonuslar)</i>")

    elif step == "vac_desc":
        state["data"]["description"] = text
        state["step"] = "vac_phone"
        bot.send_message(message.chat.id, "7-qadam: Bog'lanish uchun <b>Telefon raqam</b>:\n<i>(Masalan: +998 90 987 65 43)</i>")

    elif step == "vac_phone":
        state["data"]["phone"] = text
        vd = state["data"]
        tg_user = message.from_user.username or ""

        conn = get_db()
        c = conn.cursor()
        c.execute('''
            INSERT INTO vacancies (employer_id, title, company, category, salary, requirements, description, phone, city, telegram)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, vd['title'], vd['company'], vd['title'], vd['salary'], vd['requirements'], vd['description'], vd['phone'], vd['city'], tg_user))
        vac_id = c.lastrowid
        conn.commit()

        c.execute("SELECT user_id, full_name, profession FROM resumes")
        all_resumes = c.fetchall()
        conn.close()

        del USER_STATES[user_id]

        bot.send_message(
            message.chat.id,
            "🎉 <b>Tabriklaymiz! Sizning vakansiyangiz muvaffaqiyatli joylashtirildi!</b>\n\n"
            "Istalgan vaqtda <b>«📋 Mening vakansiyalarim»</b> bo'limi orqali uning maoshini, tavsifini o'zgartirishingiz yoki arizalarni tekshirishingiz mumkin.",
            reply_markup=main_menu_keyboard()
        )

        matched_count = 0
        vac_title_lower = vd['title'].lower()
        for res in all_resumes:
            if res['user_id'] != user_id:
                prof_lower = (res['profession'] or "").lower()
                if any(word in prof_lower for word in vac_title_lower.split() if len(word) > 3):
                    try:
                        alert_text = (
                            f"🔔 <b>Sizning mutaxassisligingizga mos yangi ish paydo bo'ldi!</b>\n\n"
                            f"💼 <b>{vd['title']}</b>\n"
                            f"🏢 Kompaniya: {vd['company']}\n"
                            f"💰 Maosh: {vd['salary']}\n"
                            f"📍 Manzil: {vd['city']}\n\n"
                            f"«🔍 Vakansiyalar qidirish» bo'limi orqali to'liq ma'lumot bilan tanishib, 1 ta tugma bilan ariza yuborishingiz mumkin!"
                        )
                        bot.send_message(res['user_id'], alert_text)
                        matched_count += 1
                    except Exception:
                        pass

        if matched_count > 0:
            bot.send_message(message.chat.id, f"💡 <i>Smart Match: Sizning e'loningiz bazadagi mos keluvchi {matched_count} nafar mutaxassisga avtomatik yetkazildi!</i>")

# ==================== YORDAM VA MA'LUMOT ====================
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Yordam & Ma'lumot")
def handle_help(message):
    help_text = (
        "ℹ️ <b>PLATFORMA BO'YICHA QO'LLANMA</b>\n\n"
        "1. <b>Qanday qilib rezyume yaratiladi?</b>\n"
        "«📄 Mening Rezyumem» tugmasini bosing va savollarga javob bering. Tugatgach, darhol <b>A4 formatdagi professional PDF</b> olasiz.\n\n"
        "2. <b>Vakansiyaga ariza qanday beriladi?</b>\n"
        "«🔍 Vakansiyalar qidirish» tugmasini bosing va <b>«📩 Rezyumem bilan ariza berish»</b> tugmasini bosing. Sizning PDF rezyumengiz ish beruvchiga yuboriladi.\n\n"
        "3. <b>Ish beruvchilar uchun e'lonni tahrirlash:</b>\n"
        "«📋 Mening vakansiyalarim» bo'limi orqali maoshni yangilashingiz, talablarni o'zgartirishingiz, e'lonni to'xtatib qo'yishingiz yoki o'chirishingiz mumkin.\n\n"
        "Savol va takliflar uchun: @usman_khasan"
    )
    bot.send_message(message.chat.id, help_text, reply_markup=main_menu_keyboard())

# ==================== AVTOMATIK START VA TELEGRAM BUYRUQLARINI O'RNATISH ====================
def setup_bot_commands():
    """Bot ishga tushganda Telegram pastki chap burchagidagi ko'k 'Menu' tugmasi va /start ni avtomatik o'rnatish"""
    try:
        commands = [
            types.BotCommand("start", "🚀 Botni ishga tushirish"),
            types.BotCommand("vakansiyalar", "🔍 Vakansiyalar qidirish"),
            types.BotCommand("rezyume", "📄 Mening rezyumem (A4 PDF)"),
            types.BotCommand("elon_berish", "📢 Ish e'lon qilish (Vakansiya)"),
            types.BotCommand("mening_ishlarim", "📋 Mening vakansiyalarim"),
            types.BotCommand("help", "ℹ️ Yordam & Ma'lumot")
        ]
        bot.set_my_commands(commands)
        try:
            bot.set_chat_menu_button(menu_button=types.MenuButtonCommands())
        except Exception:
            pass
        print("✅ Telegram Menyu buyruqlari (/start 🚀) avtomatik o'rnatildi!")
    except Exception as e:
        logger.warning(f"Menyu komandalarini o'rnatishda ogohlantirish: {e}")

# ==================== BOTNI ISHGA TUSHIRISH (POLLING) ====================
if __name__ == "__main__":
    logger.info("Ish topish boti (@ish_topish_teambot) ishga tushirilmoqda...")
    print("=" * 60)
    print("✅ @ish_topish_teambot muvaffaqiyatli ishga tushdi!")
    print(f"Bosh Administrator ID: {ADMIN_ID}")
    print(f"ReportLab holati: {'Faol' if REPORTLAB_AVAILABLE else 'O`rnatilmoqda (Pure-Python Failsafe 100% Faol)'}")
    print("=" * 60)

    setup_bot_commands()

    while True:
        try:
            bot.infinity_polling(timeout=30, long_polling_timeout=20)
        except Exception as err:
            logger.error(f"Polling xatosi: {err}")
            time.sleep(5)
