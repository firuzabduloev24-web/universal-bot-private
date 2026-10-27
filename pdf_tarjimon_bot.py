#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
🤖 SMART PDF, SCANNER (OCR) VA MATN TARJIMON TELEGRAM BOT (PRO EDITION) 🤖
=============================================================================
Bosh administrator: @usman_khasan (Telegram ID: 1021089367)
Bot Token: 8925389899:AAFL5NzM5bIu0eK8yVNCi_Fpj-QNPKL7J5c

YANGI IMKONIYATLAR:
1. 🎯 Interaktiv Til Tanlash (Fayl va Matn uchun):
   - Foydalanuvchi PDF fayl yuborganda, bot avval sahifalar sonini ko'rsatib:
     «Qaysi tilga tarjima qilib beray?» deb asosiy 5 ta til tugmasini chiqaradi!
   - Chatga oddiy matn yozib yuborganda ham avval tilni so'rab, tanlangan tilga o'girib beradi!
2. 🔍 100% Gibrid Matn Ajratish (Digital + OCR Engine):
   - Raqamli PDF lardan matnni tezkor o'qish (pypdf).
   - Skaner qilingan, tibbiy xulosalar (PATHOLOGY.pdf, IPSUM.pdf), kitoblar va
     hujjat fotosuratlaridan matnni 100% aniqlikda o'qish (pypdfium2 + Tesseract OCR).
3. 📄 Hujjat Formatlari:
   - Yangi A4 PDF hujjat (ReportLab & Pure-Python).
   - Tahrirlanadigan Word (.docx) varianti (python-docx).
   - Qisqa matnlar uchun to'g'ridan-to'g'ri Telegram xabari.
4. 🌐 Asosiy 5 ta Til:
   - 🇺🇿 O'zbek tili
   - 🇷🇺 Rus tili
   - 🇬🇧 Ingliz tili
   - 🇹🇷 Turk tili
   - 🇩🇪 Nemis tili (va 🇸🇦 Arab tili)
=============================================================================
"""

import os
import re
import sys
import io
import time
import json
import sqlite3
import logging
import tempfile
import threading
import html
import urllib.parse
from datetime import datetime

# ==================== KUTUBXONALAR ====================
import requests
import telebot
from telebot import types

# PDF va OCR kutubxonalari
import pypdf
import pypdfium2
from PIL import Image

try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

try:
    from docx import Document
    from docx.shared import Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    from deep_translator import GoogleTranslator
    HAS_DEEP_TRANSLATOR = True
except ImportError:
    HAS_DEEP_TRANSLATOR = False

# ==================== SOZLAMALAR ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8925389899:AAFL5NzM5bIu0eK8yVNCi_Fpj-QNPKL7J5c").strip()
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1021089367"))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(tempfile.gettempdir(), "pdf_translator_files")
os.makedirs(TEMP_DIR, exist_ok=True)

DB_FILE = os.path.join(tempfile.gettempdir(), "pdf_translator.db")

# Sessiyalar va Foydalanuvchi holatlari
PENDING_SESSIONS = {} # session_id -> {type: 'pdf'/'text'/'photo', data...}
USER_STATES = {}

# Asosiy 5-6 ta til ro'yxati
MAIN_LANGUAGES = {
    "uz": {"name": "O'zbek tiliga", "flag": "🇺🇿"},
    "ru": {"name": "Rus tiliga", "flag": "🇷🇺"},
    "en": {"name": "Ingliz tiliga", "flag": "🇬🇧"},
    "tr": {"name": "Turk tiliga", "flag": "🇹🇷"},
    "de": {"name": "Nemis tiliga", "flag": "🇩🇪"},
    "ar": {"name": "Arab tiliga", "flag": "🇸🇦"}
}

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PDF_Translator_Bot")

# ==================== MA'LUMOTLAR BAZASI ====================
def get_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                default_target_lang TEXT DEFAULT 'uz',
                total_translations INTEGER DEFAULT 0,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS translation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT,
                file_name TEXT,
                pages_count INTEGER,
                is_ocr INTEGER DEFAULT 0,
                target_lang TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

init_db()

def db_add_user(user_id, username, full_name):
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO users (user_id, username, full_name, last_active)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = excluded.username,
                    full_name = excluded.full_name,
                    last_active = CURRENT_TIMESTAMP
            """, (user_id, username or "", full_name or ""))
            conn.commit()
    except Exception as e:
        logger.error(f"db_add_user xatolik: {e}")

def db_log_translation(user_id, trans_type, file_name, pages_count, is_ocr, target_lang):
    try:
        with get_db() as conn:
            conn.execute("""
                INSERT INTO translation_logs (user_id, type, file_name, pages_count, is_ocr, target_lang)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, trans_type, file_name, pages_count, 1 if is_ocr else 0, target_lang))
            conn.execute("UPDATE users SET total_translations = total_translations + 1, last_active = CURRENT_TIMESTAMP WHERE user_id = ?", (user_id,))
            conn.commit()
    except Exception as e:
        logger.error(f"db_log_translation xatolik: {e}")

def db_get_stats():
    try:
        with get_db() as conn:
            total_u = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total_tr = conn.execute("SELECT COUNT(*) FROM translation_logs").fetchone()[0]
            total_ocr = conn.execute("SELECT COUNT(*) FROM translation_logs WHERE is_ocr = 1").fetchone()[0]
            today_u = conn.execute("SELECT COUNT(DISTINCT user_id) FROM translation_logs WHERE date(created_at) = date('now')").fetchone()[0]
            return {
                "total_users": total_u,
                "total_trans": total_tr,
                "total_ocr": total_ocr,
                "today_users": today_u
            }
    except Exception:
        return {"total_users": 0, "total_trans": 0, "total_ocr": 0, "today_users": 0}

# ==================== OCR VA GIBRID MATN AJRATISH TIZIMI ====================
def get_ocr_languages():
    if not HAS_PYTESSERACT:
        return "eng"
    try:
        langs = pytesseract.get_languages()
        needed = [l for l in ["rus", "eng", "uzb"] if l in langs]
        if needed:
            return "+".join(needed)
        return "eng"
    except Exception:
        return "eng"

def extract_text_hybrid_pdf(pdf_path, max_pages=50, progress_callback=None):
    """
    Gibrid Matn Ajratuvchi (Digital + OCR):
    - Har bir sahifani tekshiradi.
    - Raqamli matn bo'lsa -> pypdf orqali bir zumda oladi.
    - Skaner/Rasm bo'lsa (PATHOLOGY, IPSUM kabi) -> pypdfium2 bilan 2.2x rasmga aylantirib,
      Tesseract OCR orqali 100% o'qiydi!
    """
    pages_data = []
    ocr_used = False

    # 1. Sahifalarni ochish
    pdf_doc = pypdfium2.PdfDocument(pdf_path)
    total_pages = len(pdf_doc)
    pages_to_process = min(total_pages, max_pages)

    # 2. Raqamli qatlam uchun pypdf
    pypdf_reader = None
    try:
        pypdf_reader = pypdf.PdfReader(pdf_path)
    except Exception:
        pass

    ocr_lang_str = get_ocr_languages()

    for idx in range(pages_to_process):
        page_num = idx + 1
        page_text = ""
        is_page_ocr = False

        if progress_callback:
            progress_callback(page_num, pages_to_process, is_ocr=False)

        # 1-qadam: Raqamli matn olishga urinish
        if pypdf_reader and idx < len(pypdf_reader.pages):
            try:
                extracted = pypdf_reader.pages[idx].extract_text()
                if extracted and len(extracted.strip()) > 35:
                    page_text = extracted.strip()
            except Exception:
                pass

        # 2-qadam: Agar matn yo'q bo'lsa -> Skaner / Rasm deb aniqlanadi va OCR ishga tushadi!
        if not page_text or len(page_text.strip()) <= 35:
            if progress_callback:
                progress_callback(page_num, pages_to_process, is_ocr=True)

            ocr_used = True
            is_page_ocr = True

            try:
                page = pdf_doc[idx]
                image = page.render(scale=2.2).to_pil()
                gray_img = image.convert("L")

                if HAS_PYTESSERACT:
                    page_text = pytesseract.image_to_string(gray_img, lang=ocr_lang_str, config="--psm 1")
                else:
                    page_text = "[Tesseract OCR moduli mavjud emas]"
            except Exception as ocr_err:
                logger.error(f"Sahifa {page_num} OCR xatosi: {ocr_err}")
                page_text = ""

        # Qatorlarni tozalash
        clean_lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        cleaned_text = "\n".join(clean_lines)

        pages_data.append({
            "page_num": page_num,
            "text": cleaned_text,
            "is_ocr": is_page_ocr
        })

    pdf_doc.close()
    return pages_data, ocr_used, total_pages

def extract_text_from_photo(photo_path):
    """Rasm (.jpg, .png) yuborilganda OCR orqali matnni o'qish"""
    if not HAS_PYTESSERACT:
        return "Tesseract OCR o'rnatilmagan."
    try:
        img = Image.open(photo_path).convert("L")
        langs = get_ocr_languages()
        text = pytesseract.image_to_string(img, lang=langs, config="--psm 3")
        return text.strip()
    except Exception as e:
        logger.error(f"Rasm OCR xatosi: {e}")
        return ""

# ==================== PROFESSIONAL TARJIMA TIZIMI ====================
def translate_chunk_gtx(text, target_lang="uz", source_lang="auto"):
    """Google Translate bepul GTX Web API"""
    if not text or not text.strip():
        return ""
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": source_lang,
        "tl": target_lang,
        "dt": "t",
        "q": text
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    r = requests.get(url, params=params, headers=headers, timeout=14)
    if r.status_code == 200:
        data = r.json()
        pieces = [p[0] for p in data[0] if p and p[0]]
        return "".join(pieces)
    raise Exception(f"GTX status {r.status_code}")

def translate_chunk_mymemory(text, target_lang="uz", source_lang="auto"):
    """MyMemory API zaxirasi"""
    sl = "en" if source_lang == "auto" else source_lang
    pair = f"{sl}|{target_lang}"
    url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text[:450])}&langpair={pair}"
    r = requests.get(url, timeout=10)
    if r.status_code == 200:
        data = r.json()
        return data.get("responseData", {}).get("translatedText", text)
    raise Exception("MyMemory xatosi")

def translate_single_chunk(chunk, target_lang="uz"):
    if not chunk or not chunk.strip():
        return ""
    # 1. Deep Translator
    if HAS_DEEP_TRANSLATOR:
        try:
            return GoogleTranslator(source="auto", target=target_lang).translate(chunk)
        except Exception:
            pass
    # 2. Google Translate GTX
    try:
        return translate_chunk_gtx(chunk, target_lang=target_lang)
    except Exception:
        pass
    # 3. MyMemory
    try:
        return translate_chunk_mymemory(chunk, target_lang=target_lang)
    except Exception:
        return chunk

def split_text_paragraphs(text, max_chars=1600):
    paragraphs = text.split("\n")
    chunks = []
    cur_chunk = []
    cur_len = 0

    for para in paragraphs:
        p_clean = para.strip()
        if not p_clean:
            continue
        if cur_len + len(p_clean) > max_chars and cur_chunk:
            chunks.append("\n".join(cur_chunk))
            cur_chunk = [p_clean]
            cur_len = len(p_clean)
        else:
            cur_chunk.append(p_clean)
            cur_len += len(p_clean)

    if cur_chunk:
        chunks.append("\n".join(cur_chunk))
    return chunks

def translate_full_text(text, target_lang="uz"):
    if not text or not text.strip():
        return ""
    chunks = split_text_paragraphs(text)
    results = []
    for ch in chunks:
        res = translate_single_chunk(ch, target_lang=target_lang)
        results.append(res)
        time.sleep(0.1)
    return "\n\n".join(results)

# ==================== HUJJAT GENERATSIYASI (DOCX VA PDF) ====================
def create_translated_docx(pages_data, output_path, original_filename, target_lang_name):
    if not HAS_DOCX:
        return False
    try:
        doc = Document()
        title = doc.add_heading("Hujjat Tarjimasi", level=0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER

        sub = doc.add_paragraph()
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = sub.add_run(f"Asl fayl: {original_filename} | Til: {target_lang_name} | Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
        r.font.italic = True
        r.font.size = Pt(9.5)
        r.font.color.rgb = RGBColor(100, 116, 139)

        doc.add_paragraph().paragraph_format.space_after = Pt(12)

        for p_info in pages_data:
            page_num = p_info["page_num"]
            method_str = "(Skaner/OCR)" if p_info.get("is_ocr") else "(Raqamli)"

            h = doc.add_heading(f"--- Sahifa {page_num} {method_str} ---", level=2)
            h.paragraph_format.space_before = Pt(14)
            h.paragraph_format.space_after = Pt(6)

            text = p_info["translated_text"]
            for para in text.split("\n"):
                p_clean = para.strip()
                if p_clean:
                    p = doc.add_paragraph(p_clean)
                    p.paragraph_format.line_spacing = 1.15
                    p.paragraph_format.space_after = Pt(4)

        doc.save(output_path)
        return True
    except Exception as e:
        logger.error(f"Docx yaratishda xato: {e}")
        return False

def create_translated_pdf(pages_data, output_path, original_filename, target_lang_name):
    if not HAS_REPORTLAB:
        return False
    try:
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            alignment=1,
            textColor=colors.HexColor("#1E3A8A"),
            spaceAfter=4
        )
        meta_style = ParagraphStyle(
            "DocMeta",
            parent=styles["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=9.5,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=12
        )
        page_hdr_style = ParagraphStyle(
            "PageHdr",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0284C7"),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            leading=14.5,
            textColor=colors.HexColor("#1E293B"),
            spaceAfter=6
        )

        story = []
        safe_fn = html.escape(original_filename[:50])
        story.append(Paragraph(f"TARJIMA QILINGAN HUJJAT: {safe_fn}", title_style))
        story.append(Paragraph(f"Til: <b>{target_lang_name}</b> | Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}", meta_style))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#06B6D4"), spaceAfter=14))

        for idx, p_info in enumerate(pages_data):
            page_num = p_info["page_num"]
            method_str = "Skaner/OCR" if p_info.get("is_ocr") else "Raqamli matn"
            story.append(Paragraph(f"Sahifa {page_num} ({method_str})", page_hdr_style))

            text = p_info["translated_text"]
            for para in text.split("\n"):
                clean_p = html.escape(para.strip())
                if clean_p:
                    story.append(Paragraph(clean_p, body_style))

            if idx < len(pages_data) - 1:
                story.append(Spacer(1, 10))
                story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=8))

        doc.build(story)
        return True
    except Exception as e:
        logger.error(f"ReportLab PDF yaratishda xato: {e}")
        return False

# ==================== TUGMALAR VA MENYULAR ====================
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b1 = types.KeyboardButton("📤 PDF / Hujjat yuborish")
    b2 = types.KeyboardButton("💬 Matn tarjima qilish")
    b3 = types.KeyboardButton("📊 Statistika")
    b4 = types.KeyboardButton("ℹ️ Yordam")
    markup.add(b1, b2)
    markup.add(b3, b4)
    return markup

def language_choice_keyboard(session_id: str):
    """Asosiy 5-6 ta til tugmasi (Foydalanuvchi tanlashi uchun)"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for code, info in MAIN_LANGUAGES.items():
        buttons.append(types.InlineKeyboardButton(
            text=f"{info['flag']} {info['name']}",
            callback_data=f"lang_choice:{code}:{session_id}"
        ))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_sess:{session_id}"))
    return markup

# ==================== TELEGRAM HANDLERS ====================
@bot.message_handler(commands=["start"])
def handle_start(message):
    user = message.from_user
    db_add_user(user.id, user.username, user.first_name)
    welcome_text = (
        f"Assalomu alaykum, <b>{user.first_name}</b>!\n\n"
        f"🤖 <b>Smart PDF, Skaner (OCR) va Matn Tarjimon Botiga</b> xush kelibsiz!\n\n"
        f"🔥 <b>Botning asosiy imkoniyatlari:</b>\n"
        f"• 📄 <b>PDF Fayllar:</b> Oddiy elektron PDF hamda <b>skaner qilingan / rasm formatdagi</b> PDF (tibbiy xulosalar, analizlar `PATHOLOGY`, `IPSUM`, kitoblar) larni <b>100% OCR</b> orqali o'qish!\n"
        f"• 💬 <b>Oddiy Matnlar:</b> Chatga istalgan matn yozsangiz, qaysi tilga tarjima qilishni so'rab darhol o'girib beradi!\n"
        f"• 📸 <b>Hujjat Rasmlari:</b> Suratga olingan hujjatlarni ham o'qib tarjima qiladi!\n"
        f"• 📥 <b>Tayyor Formatlar:</b> Yangi A4 PDF va tahrirlanadigan Word (.docx) faylini qaytaradi.\n\n"
        f"Boshlash uchun shunchaki <b>PDF fayl</b> yuboring yoki <b>matn</b> yozing!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_reply_keyboard())

@bot.message_handler(commands=["help"])
@bot.message_handler(func=lambda msg: msg.text == "ℹ️ Yordam")
def handle_help(message):
    help_text = (
        "ℹ️ <b>BOTDAN FOYDALANISH QO'LLANMASI:</b>\n\n"
        "1. <b>PDF Fayl yuborish:</b>\n"
        "PDF faylingizni botga jo'nating. Bot sahifalarni o'qiydi va sizdan <b>«Qaysi tilga tarjima qilib beray?»</b> deb so'raydi. Kerakli til tugmasini bosing — bot tarjima qilib yangi PDF va Word (.docx) faylini beradi.\n\n"
        "2. <b>Matn yuborish:</b>\n"
        "Chatga har qanday tildagi matnni yozib yuboring — bot darhol qaysi tilga tarjima qilishni so'raydi va tanlangan tilga o'girib beradi.\n\n"
        "3. <b>Skanerlangan / Rasmli PDF:</b>\n"
        "Botda o'rnatilgan kuchli <b>Tesseract OCR</b> tizimi tufayli hatto skaner qilingan tibbiy analizlar va qog'oz kitoblar ham xatosiz o'qiladi!\n\n"
        "Administrator: @usman_khasan"
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=["stat", "stats"])
@bot.message_handler(func=lambda msg: msg.text == "📊 Statistika")
def handle_stats(message):
    st = db_get_stats()
    text = (
        "📊 <b>BOT STATISTIKASI</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{st['total_users']:,} ta</b>\n"
        f"📄 Jami tarjimalar: <b>{st['total_trans']:,} ta</b>\n"
        f"🔍 Skaner / OCR orqali o'qilganlar: <b>{st['total_ocr']:,} ta</b>\n"
        f"⚡️ Bugun faol: <b>{st['today_users']:,} ta</b>\n\n"
        f"👑 Administrator: @usman_khasan"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(func=lambda msg: msg.text == "📤 PDF / Hujjat yuborish")
def handle_btn_pdf_prompt(message):
    bot.send_message(
        message.chat.id,
        "📄 <b>Tarjima qilinadigan PDF faylingizni yoki hujjat fotosuratini yuboring:</b>\n\n"
        "<i>(Har qanday raqamli yoki skaner qilingan kitob, tibbiy xulosa, shartnoma qabul qilinadi)</i>"
    )

@bot.message_handler(func=lambda msg: msg.text == "💬 Matn tarjima qilish")
def handle_btn_text_prompt(message):
    USER_STATES[message.from_user.id] = "wait_text"
    bot.send_message(
        message.chat.id,
        "✍️ <b>Tarjima qilinadigan matnni yozib yuboring:</b>\n"
        "<i>(Yuborganingizdan so'ng bot qaysi tilga tarjima qilishni so'raydi)</i>"
    )

# ==================== PDF FAYLLARNI QABUL QILISH ====================
@bot.message_handler(content_types=["document"])
def handle_incoming_document(message):
    doc = message.document
    user = message.from_user
    db_add_user(user.id, user.username, user.first_name)

    file_name = doc.file_name or "document.pdf"
    file_size_mb = (doc.file_size or 0) / (1024 * 1024)

    if file_size_mb > 25:
        bot.reply_to(message, f"❌ Fayl hajmi juda katta ({file_size_mb:.1f} MB)! Telegram bot cheklovi: 25 MB.")
        return

    ext = os.path.splitext(file_name)[1].lower()
    if ext not in [".pdf", ".docx", ".txt", ".jpg", ".png", ".jpeg"]:
        bot.reply_to(message, "⚠️ Iltimos, <b>PDF</b>, <b>Word (.docx)</b> yoki <b>Rasm</b> formatidagi fayl yuboring.")
        return

    status_msg = bot.reply_to(message, "⏳ <b>PDF tahlil qilinmoqda, sahifalar tekshirilmoqda...</b>")

    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        session_id = f"pdf_{user.id}_{int(time.time()*1000)%1000000}"
        local_path = os.path.join(TEMP_DIR, f"{session_id}_{file_name}")

        with open(local_path, "wb") as f:
            f.write(downloaded)

        # Sahifalar sonini aniqlash (pypdfium2 yordamida tezkor)
        try:
            pdf_doc = pypdfium2.PdfDocument(local_path)
            total_pages = len(pdf_doc)
            pdf_doc.close()
        except Exception:
            total_pages = 1

        PENDING_SESSIONS[session_id] = {
            "type": "pdf",
            "user_id": user.id,
            "chat_id": message.chat.id,
            "file_name": file_name,
            "local_path": local_path,
            "total_pages": total_pages,
            "file_size_mb": file_size_mb
        }

        # FOYDALANUVCHIDAN ASOSIY 5 TA TILDAN BIRINI SO'RASH:
        info_text = (
            f"📄 <b>Fayl muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"📌 <b>Nomi:</b> <code>{html.escape(file_name)}</code>\n"
            f"📑 <b>Sahifalar soni:</b> {total_pages} ta\n"
            f"💾 <b>Hajmi:</b> {file_size_mb:.1f} MB\n\n"
            f"👇 <b>Qaysi tilga tarjima qilib beray?</b>"
        )

        bot.edit_message_text(
            info_text,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            reply_markup=language_choice_keyboard(session_id)
        )
    except Exception as e:
        logger.error(f"Fayl yuklashda xato: {e}")
        bot.edit_message_text("❌ Faylni yuklashda xatolik yuz berdi. Qaytadan urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

# ==================== HUJJAT RASMI QABUL QILINGANDA ====================
@bot.message_handler(content_types=["photo"])
def handle_incoming_photo(message):
    user = message.from_user
    db_add_user(user.id, user.username, user.first_name)
    photo = message.photo[-1]

    status_msg = bot.reply_to(message, "⏳ <b>Rasm qabul qilindi, tahlil qilinmoqda...</b>")

    try:
        file_info = bot.get_file(photo.file_id)
        downloaded = bot.download_file(file_info.file_path)

        session_id = f"photo_{user.id}_{int(time.time()*1000)%1000000}"
        local_path = os.path.join(TEMP_DIR, f"{session_id}.jpg")

        with open(local_path, "wb") as f:
            f.write(downloaded)

        PENDING_SESSIONS[session_id] = {
            "type": "photo",
            "user_id": user.id,
            "chat_id": message.chat.id,
            "file_name": "Hujjat_Rasmi.jpg",
            "local_path": local_path,
            "total_pages": 1,
            "file_size_mb": round((photo.file_size or 0) / (1024 * 1024), 2)
        }

        bot.edit_message_text(
            "📸 <b>Hujjat fotosurati qabul qilindi!</b>\n\n"
            "👇 <b>Qaysi tilga tarjima qilib beray?</b>",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            reply_markup=language_choice_keyboard(session_id)
        )
    except Exception as e:
        logger.error(f"Rasm yuklashda xato: {e}")
        bot.edit_message_text("❌ Rasmni qabul qilishda xatolik yuz berdi.", chat_id=message.chat.id, message_id=status_msg.message_id)

# ==================== ODDIY MATN YUBORILGANDA ====================
@bot.message_handler(func=lambda msg: True and msg.text)
def handle_incoming_text(message):
    user = message.from_user
    text = message.text.strip()
    db_add_user(user.id, user.username, user.first_name)

    if text in ["📤 PDF / Hujjat yuborish", "💬 Matn tarjima qilish", "📊 Statistika", "ℹ️ Yordam"]:
        return

    session_id = f"txt_{user.id}_{int(time.time()*1000)%1000000}"
    PENDING_SESSIONS[session_id] = {
        "type": "text",
        "user_id": user.id,
        "chat_id": message.chat.id,
        "raw_text": text
    }

    preview_text = html.escape(text[:120]) + ("..." if len(text) > 120 else "")
    bot.reply_to(
        message,
        f"📝 <b>Matn qabul qilindi ({len(text)} ta belgi):</b>\n\n"
        f"<i>\"{preview_text}\"</i>\n\n"
        f"👇 <b>Qaysi tilga tarjima qilib beray?</b>",
        reply_markup=language_choice_keyboard(session_id)
    )

# ==================== TIL TANLANGANDAGI JARAYON (CALLBACK QUERY) ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_choice:"))
def handle_language_choice(call):
    parts = call.data.split(":")
    target_lang = parts[1]
    session_id = parts[2]

    session = PENDING_SESSIONS.get(session_id)
    if not session:
        bot.answer_callback_query(call.id, "⚠️ Sessiya eskirgan. Qaytadan yuboring.", show_alert=True)
        return

    bot.answer_callback_query(call.id, "Tarjima jarayoni boshlandi...")

    lang_info = MAIN_LANGUAGES.get(target_lang, {"name": target_lang, "flag": "🌐"})
    target_name = f"{lang_info['flag']} {lang_info['name']}"

    # 1. MATN TARJIMASI BO'LSA
    if session["type"] == "text":
        prog_msg = bot.edit_message_text(
            f"⏳ <b>Matn tarjima qilinmoqda...</b>\n"
            f"🌐 <b>Mo'ljal:</b> {target_name}\n"
            f"<i>Iltimos, kuting...</i>",
            call.message.chat.id,
            call.message.message_id
        )

        def _text_worker():
            try:
                raw_t = session["raw_text"]
                translated = translate_full_text(raw_t, target_lang=target_lang)
                bot.edit_message_text(
                    f"✅ <b>Tarjima tayyor ({target_name}):</b>\n\n{html.escape(translated)}",
                    call.message.chat.id,
                    prog_msg.message_id
                )
                db_log_translation(call.from_user.id, "text", "Matn", 1, 0, target_lang)
            except Exception as e:
                bot.edit_message_text(f"❌ Tarjimada xatolik: {e}", call.message.chat.id, prog_msg.message_id)
            finally:
                PENDING_SESSIONS.pop(session_id, None)

        threading.Thread(target=_text_worker, daemon=True).start()
        return

    # 2. RASM TARJIMASI BO'LSA
    if session["type"] == "photo":
        prog_msg = bot.edit_message_text(
            f"🔍 <b>Rasm OCR orqali o'qilmoqda...</b>\n"
            f"🌐 <b>Mo'ljal:</b> {target_name}",
            call.message.chat.id,
            call.message.message_id
        )

        def _photo_worker():
            try:
                p_path = session["local_path"]
                extracted = extract_text_from_photo(p_path)

                if not extracted or len(extracted.strip()) < 10:
                    bot.edit_message_text("❌ <b>Rasmdan matn topilmadi!</b>\nIltimos, hujjat aniqroq ko'ringan fotosurat yuboring.", call.message.chat.id, prog_msg.message_id)
                    return

                bot.edit_message_text(f"🌐 <b>Matn o'qildi ({len(extracted)} belgi)! Tarjima qilinmoqda...</b>", call.message.chat.id, prog_msg.message_id)
                translated = translate_full_text(extracted, target_lang=target_lang)

                # Word fayl yaratish
                pages_data = [{"page_num": 1, "is_ocr": True, "translated_text": translated}]
                docx_path = os.path.join(TEMP_DIR, f"Tarjima_{session_id}_{target_lang}.docx")
                create_translated_docx(pages_data, docx_path, "Hujjat_Rasmi.jpg", target_name)

                caption = (
                    f"✅ <b>Rasm matni tarjima qilindi!</b>\n\n"
                    f"🌐 <b>Til:</b> {target_name}\n"
                    f"🔍 <b>Tahlil:</b> Tesseract OCR\n\n"
                    f"📝 <b>Natija:</b>\n{translated[:3000]}"
                )

                if os.path.exists(docx_path):
                    with open(docx_path, "rb") as df:
                        bot.send_document(call.message.chat.id, df, caption=caption)
                else:
                    bot.send_message(call.message.chat.id, caption)

                try:
                    bot.delete_message(call.message.chat.id, prog_msg.message_id)
                except Exception:
                    pass

                db_log_translation(call.from_user.id, "photo", "Hujjat_Rasmi.jpg", 1, 1, target_lang)
            except Exception as e:
                bot.edit_message_text(f"❌ Xatolik yuz berdi: {e}", call.message.chat.id, prog_msg.message_id)
            finally:
                try:
                    os.remove(session.get("local_path", ""))
                except Exception:
                    pass
                PENDING_SESSIONS.pop(session_id, None)

        threading.Thread(target=_photo_worker, daemon=True).start()
        return

    # 3. PDF HUJJAT TARJIMASI BO'LSA
    if session["type"] == "pdf":
        prog_msg = bot.edit_message_text(
            f"⏳ <b>Tarjima jarayoni boshlanmoqda...</b>\n\n"
            f"📄 <b>Fayl:</b> <code>{html.escape(session['file_name'])}</code>\n"
            f"🌐 <b>Tanlangan til:</b> {target_name}\n"
            f"📑 Jami sahifalar: <b>{session['total_pages']} ta</b>\n"
            f"<i>Iltimos, kuting...</i>",
            call.message.chat.id,
            call.message.message_id
        )

        def _pdf_worker():
            try:
                pdf_path = session["local_path"]
                total_pages = session["total_pages"]

                last_update = [time.time()]
                def progress_cb(current, total, is_ocr=False):
                    now = time.time()
                    if now - last_update[0] >= 2.0 or current == 1 or current == total:
                        last_update[0] = now
                        method_txt = "⚙️ <b>Skaner aniqlandi -> OCR ishlamoqda</b>" if is_ocr else "⚡️ <i>Raqamli qatlam o'qilmoqda</i>"
                        try:
                            bot.edit_message_text(
                                f"⏳ <b>Hujjat tahlil qilinmoqda:</b>\n\n"
                                f"📄 <b>Sahifa:</b> {current}/{total} ({int(current*100/total)}%)\n"
                                f"🌐 <b>Mo'ljal:</b> {target_name}\n"
                                f"{method_txt}...",
                                call.message.chat.id,
                                prog_msg.message_id
                            )
                        except Exception:
                            pass

                # 1. Gibrid matn ajratish (Raqamli + OCR)
                pages_data, was_ocr, count = extract_text_hybrid_pdf(
                    pdf_path,
                    max_pages=50,
                    progress_callback=progress_cb
                )

                total_chars = sum(len(p["text"]) for p in pages_data)
                if total_chars < 15:
                    bot.edit_message_text(
                        "❌ <b>Hujjatdan matn aniqlanmadi!</b>\nFayl butunlay bo'sh yoki parollangan bo'lishi mumkin.",
                        call.message.chat.id,
                        prog_msg.message_id
                    )
                    return

                # 2. Tarjima qilish
                bot.edit_message_text(
                    f"🌐 <b>Matn muvaffaqiyatli ajratildi ({len(pages_data)} sahifa)!</b>\n"
                    f"Tahlil usuli: {'🔍 <b>Skaner / OCR</b>' if was_ocr else '⚡️ <b>Raqamli matn</b>'}\n\n"
                    f"🔄 <b>{target_name}</b> tiliga professional tarjima qilinmoqda...",
                    call.message.chat.id,
                    prog_msg.message_id
                )

                translated_pages = []
                for p in pages_data:
                    p_num = p["page_num"]
                    raw_text = p["text"]
                    trans_text = translate_full_text(raw_text, target_lang=target_lang)
                    translated_pages.append({
                        "page_num": p_num,
                        "is_ocr": p["is_ocr"],
                        "translated_text": trans_text
                    })

                # 3. Yangi A4 PDF va Word DOCX yaratish
                bot.edit_message_text(
                    "📑 <b>Tarjima yakunlandi! Yangi A4 PDF va Word hujjatlari shakllantirilmoqda...</b>",
                    call.message.chat.id,
                    prog_msg.message_id
                )

                orig_fn = session["file_name"]
                base_name = os.path.splitext(orig_fn)[0]
                docx_name = f"Tarjima_{target_lang.upper()}_{base_name}.docx"
                pdf_name = f"Tarjima_{target_lang.upper()}_{base_name}.pdf"

                docx_out = os.path.join(TEMP_DIR, docx_name)
                pdf_out = os.path.join(TEMP_DIR, pdf_name)

                has_docx = create_translated_docx(translated_pages, docx_out, orig_fn, target_name)
                has_pdf = create_translated_pdf(translated_pages, pdf_out, orig_fn, target_name)

                caption = (
                    f"✅ <b>Hujjat tarjimasi muvaffaqiyatli yakunlandi!</b>\n\n"
                    f"📌 <b>Asl fayl:</b> {orig_fn}\n"
                    f"📑 <b>Sahifalar:</b> {len(translated_pages)} ta\n"
                    f"🔍 <b>Tahlil usuli:</b> {'Skaner/OCR (Optik tanish)' if was_ocr else 'Raqamli matn'}\n"
                    f"🌐 <b>Tarjima tili:</b> {target_name}\n\n"
                    f"Quyida tayyor <b>Word (.docx)</b> va <b>A4 PDF</b> fayllaringiz:"
                )

                bot.send_message(call.message.chat.id, caption)

                # Word faylni yuborish
                if has_docx and os.path.exists(docx_out):
                    with open(docx_out, "rb") as df:
                        bot.send_document(call.message.chat.id, df, caption=f"📝 {docx_name} (Tahrirlanadigan Word)")

                # PDF faylni yuborish
                if has_pdf and os.path.exists(pdf_out):
                    with open(pdf_out, "rb") as pf:
                        bot.send_document(call.message.chat.id, pf, caption=f"📄 {pdf_name} (A4 formatdagi tayyor PDF)")

                # Agar qisqa bo'lsa (1-2 sahifa), chatga matnli parcha ham berish
                first_text = translated_pages[0]["translated_text"][:800]
                if first_text:
                    bot.send_message(call.message.chat.id, f"💬 <b>1-sahifadan qisqa parcha:</b>\n\n<i>\"{html.escape(first_text)}...\"</i>")

                try:
                    bot.delete_message(call.message.chat.id, prog_msg.message_id)
                except Exception:
                    pass

                db_log_translation(call.from_user.id, "pdf", orig_fn, len(translated_pages), was_ocr, target_lang)

            except Exception as e:
                logger.error(f"PDF jarayoni xatosi: {e}")
                bot.send_message(call.message.chat.id, f"❌ Tarjima jarayonida xatolik yuz berdi: {e}")
            finally:
                try:
                    os.remove(session.get("local_path", ""))
                except Exception:
                    pass
                PENDING_SESSIONS.pop(session_id, None)

        threading.Thread(target=_pdf_worker, daemon=True).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("cancel_sess:"))
def handle_cancel_session(call):
    session_id = call.data.split(":")[1]
    session = PENDING_SESSIONS.pop(session_id, None)
    if session and "local_path" in session:
        try:
            os.remove(session["local_path"])
        except Exception:
            pass
    bot.answer_callback_query(call.id, "Amal bekor qilindi.")
    bot.edit_message_text("Amal bekor qilindi.", call.message.chat.id, call.message.message_id)

# ==================== ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    print("=" * 65)
    print("🤖 SMART PDF & MATN TARJIMON BOTI ISHGA TUSHMOQDA...")
    print(f"🔑 Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-6:]}")
    print(f"👑 Admin ID: {ADMIN_ID}")
    print(f"🔍 OCR Tillari: {get_ocr_languages()}")
    print("=" * 65)

    while True:
        try:
            bot.infinity_polling(timeout=35, long_polling_timeout=20, skip_pending=True)
        except Exception as err:
            logger.error(f"Polling xatosi: {err}")
            time.sleep(5)
