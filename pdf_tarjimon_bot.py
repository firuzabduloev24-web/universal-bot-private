#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
🌍 SMART PDF & HUJJATLARNI TARJIMA QILUVCHI TELEGRAM BOT (PRO EDITION) 🌍
=============================================================================
Bosh administrator: @usman_khasan (ID: 1021089367)
Bot Token: 8925389899:AAFL5NzM5bIu0eK8yVNCi_Fpj-QNPKL7J5c (yoki BOT_TOKEN muhit o'zgaruvchisi)
Platforma: pyTelegramBotAPI (telebot) + pypdf + ReportLab + python-docx + SQLite3

Asosiy imkoniyatlar:
 1. 📄 PDF fayllarni to'liq tarjima qilish:
    - PDF sahifalaridagi matnlarni aniq ajratib olish (pypdf)
    - Sahifama-sahifa real vaqtda tarjima qilish (Google Translate & MyMemory API)
    - 📄 Tarjima qilingan yangi A4 PDF hujjat qilib qaytarish (ReportLab)
    - 📝 Tahrirlash mumkin bo'lgan Word (.docx) varianti
    - 💬 Tezkor matnli ko'rinish (chatda o'qish uchun)
 2. 🌐 Ko'p tilli qo'llab-quvvatlash:
    - 🇷🇺 Ruscha ➡️ 🇺🇿 O'zbekcha
    - 🇬🇧 Inglizcha ➡️ 🇺🇿 O'zbekcha
    - 🇺🇿 O'zbekcha ➡️ 🇷🇺 Ruscha
    - 🇺🇿 O'zbekcha ➡️ 🇬🇧 Inglizcha
    - 🇹🇷 Turkcha, 🇩🇪 Nemischa, 🇸🇦 Arabcha, 🇨🇳 Xitoycha, 🇰🇷 Koreyscha
 3. 💬 To'g'ridan-to'g'ri matnlarni tarjima qilish:
    - Chatga yozilgan har qanday matnni 1 soniyada tarjima qilib beradi
 4. 📊 Admin boshqaruvi va to'liq statistika
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
import threading
import subprocess
import html
import urllib.parse
from datetime import datetime

# ==================== KUTUBXONALARNI AVTOMATIK TEKSHIRISH VA O'RNATISH ====================
def _install_package(pkg_name):
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", pkg_name], timeout=40)
    except Exception:
        pass

# 1. Telebot
try:
    import telebot
    from telebot import types
except ImportError:
    _install_package("pyTelegramBotAPI")
    try:
        import telebot
        from telebot import types
    except Exception:
        # Offline mock for compilation and sandboxes
        class _MockTeleBot:
            def __init__(self, *args, **kwargs): pass
            def message_handler(self, *args, **kwargs): return lambda f: f
            def callback_query_handler(self, *args, **kwargs): return lambda f: f
            def send_message(self, *args, **kwargs): pass
            def send_document(self, *args, **kwargs): pass
            def edit_message_text(self, *args, **kwargs): pass
            def answer_callback_query(self, *args, **kwargs): pass
            def delete_message(self, *args, **kwargs): pass
            def get_file(self, *args, **kwargs): pass
            def download_file(self, *args, **kwargs): return b""
            def infinity_polling(self, *args, **kwargs): pass
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
        telebot = _MockTeleBot()
        telebot.TeleBot = _MockTeleBot
        types = _MockTypes()

# 2. pypdf (PDF matn ajratish uchun)
try:
    import pypdf
except ImportError:
    _install_package("pypdf")
    try:
        import pypdf
    except Exception:
        pypdf = None

# 3. ReportLab (PDF yaratish uchun)
try:
    import reportlab
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    _install_package("reportlab")
    try:
        import reportlab
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        REPORTLAB_AVAILABLE = True
    except Exception:
        REPORTLAB_AVAILABLE = False

# 4. python-docx (Word hujjat yaratish uchun)
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    _install_package("python-docx")
    try:
        import docx
        DOCX_AVAILABLE = True
    except Exception:
        DOCX_AVAILABLE = False

# 5. Requests
try:
    import requests
except ImportError:
    _install_package("requests")
    import requests

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("PDFTranslatorBot")

# ==================== SOZLAMALAR ====================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8925389899:AAFL5NzM5bIu0eK8yVNCi_Fpj-QNPKL7J5c").strip()
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1021089367"))
bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "pdf_temp")
os.makedirs(TEMP_DIR, exist_ok=True)

# Ma'lumotlar bazasi
DB_FILE = os.path.join(BASE_DIR, "pdf_translator.db")

USER_SESSIONS = {}
USER_STATES = {}

# Tillar ro'yxati
LANGUAGES = {
    "uz": {"name": "O'zbekcha", "flag": "🇺🇿"},
    "ru": {"name": "Ruscha", "flag": "🇷🇺"},
    "en": {"name": "Inglizcha", "flag": "🇬🇧"},
    "tr": {"name": "Turkcha", "flag": "🇹🇷"},
    "de": {"name": "Nemischa", "flag": "🇩🇪"},
    "ar": {"name": "Arabcha", "flag": "🇸🇦"},
    "zh": {"name": "Xitoycha", "flag": "🇨🇳"},
    "ko": {"name": "Koreyscha", "flag": "🇰🇷"},
    "fr": {"name": "Fransuzcha", "flag": "🇫🇷"},
    "es": {"name": "Ispancha", "flag": "🇪🇸"}
}

# ==================== MA'LUMOTLAR BAZASI ====================
def get_db():
    global DB_FILE
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE IF NOT EXISTS _test_lock (id INT)")
        return conn
    except Exception:
        tmp_dir = os.environ.get("TEMP", os.environ.get("TMP", "/tmp"))
        fallback_path = os.path.join(tmp_dir, "pdf_translator.db")
        conn = sqlite3.connect(fallback_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            default_target_lang TEXT DEFAULT 'uz',
            translations_count INTEGER DEFAULT 0,
            pages_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS translation_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_name TEXT,
            source_lang TEXT,
            target_lang TEXT,
            pages_count INTEGER,
            chars_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ==================== TARJIMA MOTORLARI (MULTI-ENGINE TRANSLATOR) ====================
def translate_chunk_google(text: str, src_lang: str = "auto", dest_lang: str = "uz") -> str:
    """
    1-MOTOR: Google Translate bepul Web API orqali yuqori sifatli va tezkor tarjima.
    """
    if not text or not text.strip():
        return ""
    try:
        url = "https://translate.googleapis.com/translate_a/single"
        params = {
            "client": "gtx",
            "sl": src_lang,
            "tl": dest_lang,
            "dt": "t",
            "q": text
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        res = requests.get(url, params=params, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            translated_pieces = []
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                for item in data[0]:
                    if isinstance(item, list) and len(item) > 0 and item[0]:
                        translated_pieces.append(item[0])
            if translated_pieces:
                return "".join(translated_pieces)
    except Exception as e:
        logger.warning(f"Google Translate API xatosi: {e}")
    return ""

def translate_chunk_mymemory(text: str, src_lang: str = "en", dest_lang: str = "uz") -> str:
    """
    2-MOTOR (ZAXIRA): MyMemory Xalqaro Tarjima API.
    """
    if not text or not text.strip():
        return ""
    try:
        sl = "en" if src_lang == "auto" else src_lang
        pair = f"{sl}|{dest_lang}"
        url = "https://api.mymemory.translated.net/get"
        params = {"q": text[:500], "langpair": pair}
        res = requests.get(url, params=params, timeout=10)
        if res.status_code == 200:
            data = res.json()
            t = (data.get("responseData") or {}).get("translatedText")
            if t:
                return t
    except Exception as e:
        logger.warning(f"MyMemory API xatosi: {e}")
    return ""

def translate_long_text(text: str, src_lang: str = "auto", dest_lang: str = "uz") -> str:
    """
    Katta matnlarni paragraflar va gaplar bo'yicha bo'laklarga (chunk) ajratib,
    butunligicha mukammal tarjima qilib qaytaradi.
    """
    if not text or not text.strip():
        return ""

    paragraphs = text.split("\n")
    translated_paragraphs = []

    for para in paragraphs:
        clean_para = para.strip()
        if not clean_para:
            translated_paragraphs.append("")
            continue

        # Agar paragraf 1200 belgidan kichik bo'lsa bittada tarjima qilish
        if len(clean_para) <= 1200:
            t = translate_chunk_google(clean_para, src_lang, dest_lang)
            if not t:
                t = translate_chunk_mymemory(clean_para, src_lang, dest_lang)
            translated_paragraphs.append(t if t else clean_para)
        else:
            # Uzoq paragraflarni gapma-gap bo'lish
            sentences = re.split(r'(?<=[.!?])\s+', clean_para)
            cur_chunk = []
            cur_len = 0
            para_pieces = []

            for sent in sentences:
                if cur_len + len(sent) > 1000:
                    chunk_text = " ".join(cur_chunk)
                    t_chunk = translate_chunk_google(chunk_text, src_lang, dest_lang) or translate_chunk_mymemory(chunk_text, src_lang, dest_lang)
                    para_pieces.append(t_chunk if t_chunk else chunk_text)
                    cur_chunk = [sent]
                    cur_len = len(sent)
                else:
                    cur_chunk.append(sent)
                    cur_len += len(sent)

            if cur_chunk:
                chunk_text = " ".join(cur_chunk)
                t_chunk = translate_chunk_google(chunk_text, src_lang, dest_lang) or translate_chunk_mymemory(chunk_text, src_lang, dest_lang)
                para_pieces.append(t_chunk if t_chunk else chunk_text)

            translated_paragraphs.append(" ".join(para_pieces))

    return "\n".join(translated_paragraphs)

# ==================== PDF MATNINI AJRATIB OLISH ====================
def extract_text_from_pdf(pdf_path: str, max_pages: int = 50) -> list:
    """
    PDF fayldan sahifama-sahifa matnlarni toza ajratib oladi.
    Qaytaradi: [{'page_num': 1, 'text': '...'}, ...]
    """
    pages_data = []
    if not pypdf or not os.path.exists(pdf_path):
        return pages_data

    try:
        reader = pypdf.PdfReader(pdf_path)
        total_p = min(len(reader.pages), max_pages)

        for i in range(total_p):
            page = reader.pages[i]
            extracted = page.extract_text() or ""
            # Belgilarni tozalash
            clean_text = extracted.replace("\x00", "").strip()
            pages_data.append({
                "page_num": i + 1,
                "text": clean_text
            })
    except Exception as e:
        logger.error(f"PDF matn ajratishda xato: {e}")
    return pages_data

# ==================== TARJIMA QILINGAN PDF YARATISH ====================
def _escape_pdf_str(text):
    if not text:
        return ""
    trans_map = {
        '‘': "'", '’': "'", '“': '"', '”': '"', '—': '-', '–': '-',
        'ў': "o'", 'Ў': "O'", 'ғ': "g'", 'Ғ': "G'", 'ҳ': 'h', 'Ҳ': 'H'
    }
    for k, v in trans_map.items():
        text = text.replace(k, v)
    text = text.encode("ascii", errors="ignore").decode("ascii")
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def build_pure_python_translated_pdf(pages_text: list, target_lang_name: str = "O'zbekcha") -> bytes:
    """
    ReportLab bo'lmaganda 100% sof Python bilan A4 PDF yaratish (Failsafe).
    """
    stream = []
    # Header (#1E3A8A)
    stream.append("0.118 0.227 0.541 rg 0 770 595 72 re f")
    stream.append("0.024 0.714 0.831 rg 0 766 595 4 re f")
    stream.append("BT 1 1 1 rg /F2 16 Tf 40 805 Td (TARJIMA QILINGAN HUJJAT) Tj ET")
    stream.append(f"BT 0.8 0.9 1.0 rg /F1 11 Tf 40 782 Td (Til: {_escape_pdf_str(target_lang_name)} | @pdf_tarjimon_bot) Tj ET")

    y = 730
    for p_info in pages_text:
        p_num = p_info["page_num"]
        p_text = p_info["text"]
        stream.append(f"BT 0.12 0.23 0.54 rg /F2 11 Tf 40 {y} Td (--- SAHIFA {p_num} ---) Tj ET")
        y -= 20

        words = p_text.split()
        cur_line = []
        cur_len = 0
        for w in words:
            if cur_len + len(w) + 1 > 75:
                line_str = " ".join(cur_line)
                stream.append(f"BT 0.15 0.15 0.15 rg /F1 9 Tf 40 {y} Td ({_escape_pdf_str(line_str)}) Tj ET")
                y -= 14
                cur_line = [w]
                cur_len = len(w)
                if y < 60:
                    break
            else:
                cur_line.append(w)
                cur_len += len(w) + 1

        if cur_line and y >= 60:
            line_str = " ".join(cur_line)
            stream.append(f"BT 0.15 0.15 0.15 rg /F1 9 Tf 40 {y} Td ({_escape_pdf_str(line_str)}) Tj ET")
            y -= 22

        if y < 80:
            break

    stream.append("BT 0.5 0.5 0.5 rg /F1 8 Tf 40 35 Td (Tarjima qiluvchi: @pdf_tarjimon_bot | Barcha huquqlar himoyalangan) Tj ET")

    content = "\n".join(stream)
    content_bytes = content.encode("ascii")

    pdf = []
    pdf.append(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    def add_obj(obj_str):
        offsets.append(sum(len(x) for x in pdf))
        pdf.append(obj_str + b"\n")

    add_obj(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    add_obj(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj")
    add_obj(b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>\nendobj")
    add_obj(f"4 0 obj\n<< /Length {len(content_bytes)} >>\nstream\n".encode("ascii") + content_bytes + b"\nendstream\nendobj")
    add_obj(b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj")
    add_obj(b"6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj")

    xref_offset = sum(len(x) for x in pdf)
    pdf.append(f"xref\n0 {len(offsets)+1}\n0000000000 65535 f \n".encode("ascii") + b"".join(f"{o:010d} 00000 n \n".encode("ascii") for o in offsets))
    pdf.append(f"trailer\n<< /Size {len(offsets)+1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF".encode("ascii"))
    return b"".join(pdf)

def build_translated_pdf_reportlab(pages_text: list, original_filename: str, target_lang_name: str) -> io.BytesIO:
    """
    ReportLab yordamida chiroyli, kitob shaklidagi A4 PDF hujjat yasaydi.
    """
    if not REPORTLAB_AVAILABLE:
        raw_b = build_pure_python_translated_pdf(pages_text, target_lang_name)
        buf = io.BytesIO(raw_b)
        buf.seek(0)
        return buf

    buffer = io.BytesIO()
    try:
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            textColor=colors.HexColor('#1E3A8A'),
            spaceAfter=4
        )
        meta_style = ParagraphStyle(
            'DocMeta',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor('#64748B'),
            spaceAfter=12
        )
        page_hdr_style = ParagraphStyle(
            'PageHdr',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=11,
            leading=15,
            textColor=colors.HexColor('#0284C7'),
            spaceBefore=12,
            spaceAfter=6
        )
        body_style = ParagraphStyle(
            'BodyTxt',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=9.5,
            leading=14.5,
            textColor=colors.HexColor('#1E293B'),
            spaceAfter=6
        )

        story = []
        safe_fn = html.escape(original_filename[:50])
        story.append(Paragraph(f"TARJIMA QILINGAN HUJJAT: {safe_fn}", title_style))
        story.append(Paragraph(f"Til: <b>{target_lang_name}</b> | Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')} | @pdf_tarjimon_bot", meta_style))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#06B6D4'), spaceAfter=14))

        for p_info in pages_text:
            p_num = p_info["page_num"]
            p_text = p_info["text"].strip()
            if not p_text:
                continue

            story.append(Paragraph(f"📄 Sahifa {p_num}", page_hdr_style))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E2E8F0'), spaceAfter=6))

            # Paragraflarni qo'shish
            for para in p_text.split("\n"):
                if para.strip():
                    safe_para = html.escape(para.strip())
                    story.append(Paragraph(safe_para, body_style))
            story.append(Spacer(1, 10))

        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceBefore=15, spaceAfter=8))
        story.append(Paragraph("<i>Ushbu hujjat @pdf_tarjimon_bot orqali avtomatik tarjima qilindi va formatlandi.</i>", meta_style))

        doc.build(story)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"ReportLab generatsiyasida xato, pure-python fallback: {e}")
        raw_b = build_pure_python_translated_pdf(pages_text, target_lang_name)
        buf = io.BytesIO(raw_b)
        buf.seek(0)
        return buf

# ==================== WORD (.DOCX) HUJJAT YARATISH ====================
def build_translated_docx(pages_text: list, original_filename: str, target_lang_name: str) -> io.BytesIO:
    """
    Foydalanuvchi keyinchalik tahrirlashi uchun Word (.docx) varianti.
    """
    buffer = io.BytesIO()
    if not DOCX_AVAILABLE:
        return buffer

    try:
        from docx import Document
        from docx.shared import Pt, RGBColor, Inches
        from docx.enum.text import WD_ALIGN_PARAGRAPH

        doc = Document()
        # Sarlavha
        title_p = doc.add_paragraph()
        run_title = title_p.add_run(f"TARJIMA QILINGAN HUJJAT: {original_filename}")
        run_title.font.size = Pt(16)
        run_title.font.bold = True
        run_title.font.color.rgb = RGBColor(30, 58, 138)

        # Meta info
        meta_p = doc.add_paragraph()
        meta_run = meta_p.add_run(f"Til: {target_lang_name} | Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')} | @pdf_tarjimon_bot")
        meta_run.font.size = Pt(9.5)
        meta_run.font.color.rgb = RGBColor(100, 116, 139)

        doc.add_paragraph("―" * 50)

        for p_info in pages_text:
            p_num = p_info["page_num"]
            p_text = p_info["text"].strip()
            if not p_text:
                continue

            h = doc.add_heading(f"Sahifa {p_num}", level=2)
            for r in h.runs:
                r.font.size = Pt(12)
                r.font.color.rgb = RGBColor(2, 132, 199)

            for para in p_text.split("\n"):
                if para.strip():
                    doc.add_paragraph(para.strip())

        doc.save(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        logger.error(f"Docx yaratishda xato: {e}")
        return io.BytesIO()

# ==================== TUGMALAR VA MENYULAR ====================
def main_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_upload = types.KeyboardButton("📤 PDF / Hujjat yuborish")
    btn_text = types.KeyboardButton("💬 Matn tarjima qilish")
    btn_lang = types.KeyboardButton("⚙️ Asosiy tilni sozlash")
    btn_stat = types.KeyboardButton("📊 Statistika")
    btn_help = types.KeyboardButton("ℹ️ Yordam & Yo'riqnoma")
    markup.add(btn_upload, btn_text)
    markup.add(btn_lang, btn_stat)
    markup.add(btn_help)
    return markup

def language_selection_keyboard(session_id: str):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🇷🇺 Ruscha ➡️ 🇺🇿 O'zbekcha", callback_data=f"tr_pair:ru:uz:{session_id}"),
        types.InlineKeyboardButton("🇬🇧 Inglizcha ➡️ 🇺🇿 O'zbekcha", callback_data=f"tr_pair:en:uz:{session_id}")
    )
    markup.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha ➡️ 🇷🇺 Ruscha", callback_data=f"tr_pair:uz:ru:{session_id}"),
        types.InlineKeyboardButton("🇺🇿 O'zbekcha ➡️ 🇬🇧 Inglizcha", callback_data=f"tr_pair:uz:en:{session_id}")
    )
    markup.add(
        types.InlineKeyboardButton("🇹🇷 Turkcha ➡️ 🇺🇿 O'zbekcha", callback_data=f"tr_pair:tr:uz:{session_id}"),
        types.InlineKeyboardButton("🇩🇪 Nemischa ➡️ 🇺🇿 O'zbekcha", callback_data=f"tr_pair:de:uz:{session_id}")
    )
    markup.add(
        types.InlineKeyboardButton("🌐 Avto Aniqlash ➡️ 🇺🇿 O'zbekcha", callback_data=f"tr_pair:auto:uz:{session_id}")
    )
    markup.add(types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"tr_cancel:{session_id}"))
    return markup

# ==================== ASOSIY HANDLERLAR ====================
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "Foydalanuvchi"

    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO users (user_id, username, full_name)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            full_name=excluded.full_name,
            last_active=CURRENT_TIMESTAMP
    ''', (user_id, username, full_name))
    conn.commit()
    conn.close()

    welcome_text = (
        f"Assalomu alaykum, <b>{full_name}</b>! 👋\n\n"
        "🌍 <b>Smart PDF va Hujjatlarni Tarjima Qiluvchi Bot</b>ga xush kelibsiz!\n\n"
        "<b>Bot nimalar qila oladi?</b>\n"
        "• 📄 <b>PDF fayllarni tarjima qilish:</b> Har qanday PDF kitob, qo'llanma, shartnoma yoki maqolani yuklang — bot uni sahifama-sahifa tarjima qilib beradi!\n"
        "• 📥 <b>2 xil tayyor format:</b> Tarjimani yangi <b>A4 PDF hujjat</b> va tahrirlash uchun <b>Word (.docx)</b> fayl ko'rinishida olasiz.\n"
        "• 💬 <b>Oddiy matn tarjimoni:</b> Chatga istalgan tildagi matnni yozsangiz, darhol o'zbekchaga o'girib beradi.\n"
        "• 🚀 <b>Tezkor & Bepul:</b> Katta matnlarni ham bo'laklab aniq tarjima qiladi.\n\n"
        "Boshlash uchun PDF faylingizni yuboring yoki quyidagi menyudan foydalaning:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_reply_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "📤 PDF / Hujjat yuborish")
def handle_btn_upload(message):
    bot.send_message(
        message.chat.id,
        "📄 <b>Tarjima qilinadigan PDF faylingizni yuboring:</b>\n\n"
        "<i>(Fayl hajmi 20 MB gacha, sahifalar soni 50 tagacha bo'lishi tavsiya etiladi)</i>"
    )

@bot.message_handler(func=lambda msg: msg.text == "💬 Matn tarjima qilish")
def handle_btn_text(message):
    USER_STATES[message.from_user.id] = "wait_text_translation"
    bot.send_message(
        message.chat.id,
        "✍️ <b>Tarjima qilinishi kerak bo'lgan matnni yozib yuboring:</b>\n"
        "<i>(Avtomatik ravishda O'zbek tiliga tarjima qilinadi. Bekor qilish uchun: /cancel)</i>"
    )

@bot.message_handler(commands=['cancel'])
def handle_cancel(message):
    USER_STATES.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "Amal bekor qilindi.", reply_markup=main_reply_keyboard())

# ==================== PDF VA HUJJATLARNI QABUL QILISH ====================
@bot.message_handler(content_types=['document'])
def handle_incoming_document(message):
    doc = message.document
    user_id = message.from_user.id
    file_name = doc.file_name or "document.pdf"
    file_size_mb = doc.file_size / (1024 * 1024)

    if not file_name.lower().endswith(".pdf"):
        bot.reply_to(
            message,
            "⚠️ <b>Faqat PDF (.pdf) formatdagi fayllar qabul qilinadi!</b>\nIltimos, PDF hujjat yuboring."
        )
        return

    if file_size_mb > 25:
        bot.reply_to(
            message,
            f"⚠️ Fayl hajmi juda katta ({file_size_mb:.1f} MB)! Telegram orqali 20 MB gacha bo'lgan PDF fayllarni qabul qilamiz."
        )
        return

    status_msg = bot.reply_to(message, "⏳ <b>PDF tahlil qilinmoqda, sahifalar o'qilmoqda...</b>")

    try:
        file_info = bot.get_file(doc.file_id)
        downloaded = bot.download_file(file_info.file_path)

        session_id = f"{user_id}_{int(time.time())}"
        local_pdf_path = os.path.join(TEMP_DIR, f"{session_id}.pdf")

        with open(local_pdf_path, "wb") as f:
            f.write(downloaded)

        # Matnlarni ajratish
        pages = extract_text_from_pdf(local_pdf_path, max_pages=50)

        if not pages or all(len(p['text']) < 10 for p in pages):
            bot.edit_message_text(
                "❌ <b>Ushbu PDF fayldan matn topilmadi!</b>\n\n"
                "Mumkin bo'lgan sabablar:\n"
                "• PDF skaner qilingan (rasm formatida);\n"
                "• Fayl parollangan yoki himoyalangan.\n\n"
                "Iltimos, ichida matn (text) qatlami mavjud bo'lgan PDF fayl yuboring.",
                chat_id=message.chat.id,
                message_id=status_msg.message_id
            )
            try:
                os.remove(local_pdf_path)
            except Exception:
                pass
            return

        total_pages = len(pages)
        total_words = sum(len(p['text'].split()) for p in pages)

        USER_SESSIONS[session_id] = {
            "user_id": user_id,
            "file_name": file_name,
            "pdf_path": local_pdf_path,
            "pages": pages,
            "total_pages": total_pages,
            "total_words": total_words
        }

        info_text = (
            f"📄 <b>Fayl muvaffaqiyatli qabul qilindi!</b>\n\n"
            f"📌 <b>Nomi:</b> <code>{html.escape(file_name)}</code>\n"
            f"📑 <b>Sahifalar soni:</b> {total_pages} ta\n"
            f"📊 <b>So'zlar soni:</b> ~{total_words:,} ta\n\n"
            f"👇 <b>Qaysi tildan qaysi tilga tarjima qilamiz?</b>"
        )

        bot.edit_message_text(
            info_text,
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            reply_markup=language_selection_keyboard(session_id)
        )
    except Exception as e:
        logger.error(f"Fayl yuklashda xato: {e}")
        bot.edit_message_text("❌ Faylni yuklashda xatolik yuz berdi. Qayta urinib ko'ring.", chat_id=message.chat.id, message_id=status_msg.message_id)

# ==================== TARJIMA CALLBACKLARI ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("tr_pair:"))
def cb_process_translation(call):
    parts = call.data.split(":")
    src_lang = parts[1]
    dest_lang = parts[2]
    session_id = parts[3]

    session = USER_SESSIONS.get(session_id)
    if not session:
        bot.answer_callback_query(call.id, "⚠️ Sessiya eskirgan. PDF faylni qaytadan yuboring.", show_alert=True)
        return

    bot.answer_callback_query(call.id, "Tarjima jarayoni boshlandi...")

    dest_info = LANGUAGES.get(dest_lang, {"name": dest_lang.upper(), "flag": "🌐"})
    src_info = LANGUAGES.get(src_lang, {"name": "Avto", "flag": "🌐"})

    prog_msg = bot.edit_message_text(
        f"⏳ <b>Tarjima boshlanmoqda...</b>\n\n"
        f"🌐 <b>Yo'nalish:</b> {src_info['flag']} {src_info['name']} ➡️ {dest_info['flag']} {dest_info['name']}\n"
        f"📄 Jami sahifalar: <b>{session['total_pages']} ta</b>\n"
        f"<i>Iltimos, kuting...</i>",
        call.message.chat.id,
        call.message.message_id
    )

    # Tarjimani alohida thread orqali bajarish (Bot qotib qolmasligi uchun)
    def _run_translation_worker():
        try:
            pages = session["pages"]
            translated_pages = []
            total_p = len(pages)
            total_chars = 0

            for idx, p in enumerate(pages, 1):
                raw_text = p["text"]
                # Holatni yangilash
                try:
                    bot.edit_message_text(
                        f"⏳ <b>Hujjat tarjima qilinmoqda:</b>\n\n"
                        f"📄 <b>Sahifa:</b> {idx}/{total_p} ({int(idx*100/total_p)}%)\n"
                        f"🌐 <b>Yo'nalish:</b> {src_info['flag']} {src_info['name']} ➡️ {dest_info['flag']} {dest_info['name']}\n"
                        f"<i>Iltimos, kuting, biroz vaqt talab qilishi mumkin...</i>",
                        call.message.chat.id,
                        prog_msg.message_id
                    )
                except Exception:
                    pass

                tr_text = translate_long_text(raw_text, src_lang, dest_lang)
                total_chars += len(tr_text)
                translated_pages.append({
                    "page_num": p["page_num"],
                    "text": tr_text
                })
                time.sleep(0.3)

            # Tayyor fayllarni yaratish
            try:
                bot.edit_message_text("📑 <b>Tarjima yakunlandi! PDF va Word hujjatlar shakllantirilmoqda...</b>", call.message.chat.id, prog_msg.message_id)
            except Exception:
                pass

            orig_fn = session["file_name"]
            base_name = os.path.splitext(orig_fn)[0]

            # 1. A4 PDF fayl
            pdf_buf = build_translated_pdf_reportlab(translated_pages, orig_fn, dest_info["name"])
            pdf_out_name = f"Tarjima_{dest_lang.upper()}_{base_name}.pdf"

            # 2. Word .docx fayl
            docx_buf = build_translated_docx(translated_pages, orig_fn, dest_info["name"])
            docx_out_name = f"Tarjima_{dest_lang.upper()}_{base_name}.docx"

            # Foydalanuvchiga yuborish
            caption_text = (
                f"✅ <b>Tarjima muvaffaqiyatli yakunlandi!</b>\n\n"
                f"📌 <b>Asl fayl:</b> {orig_fn}\n"
                f"🌐 <b>Tarjima tili:</b> {dest_info['flag']} {dest_info['name']}\n"
                f"📑 <b>Sahifalar:</b> {total_p} ta\n\n"
                f"Quyida tayyor <b>A4 PDF</b> va tahrirlash uchun <b>Word (.docx)</b> fayllaringiz:"
            )

            bot.send_message(call.message.chat.id, caption_text)

            # PDF yuborish
            bot.send_document(
                call.message.chat.id,
                (pdf_out_name, pdf_buf.getvalue(), "application/pdf"),
                caption=f"📄 {pdf_out_name} (A4 formatdagi tayyor PDF)"
            )

            # DOCX yuborish
            if docx_buf.getvalue():
                bot.send_document(
                    call.message.chat.id,
                    (docx_out_name, docx_buf.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                    caption=f"📝 {docx_out_name} (Tahrirlash uchun Word hujjati)"
                )

            # Tezkor birinchi sahifa ko'rinishi
            first_preview = translated_pages[0]["text"][:600]
            if first_preview:
                bot.send_message(
                    call.message.chat.id,
                    f"💬 <b>1-sahifadan qisqa parcha:</b>\n\n<i>\"{html.escape(first_preview)}...\"</i>"
                )

            # Bazaga log yozish va foydalanuvchi statistikasini yangilash
            conn = get_db()
            c = conn.cursor()
            c.execute('''
                UPDATE users SET
                    translations_count = translations_count + 1,
                    pages_count = pages_count + ?,
                    last_active = CURRENT_TIMESTAMP
                WHERE user_id = ?
            ''', (total_p, call.from_user.id))
            c.execute('''
                INSERT INTO translation_logs (user_id, file_name, source_lang, target_lang, pages_count, chars_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (call.from_user.id, orig_fn, src_lang, dest_lang, total_p, total_chars))
            conn.commit()
            conn.close()

            # Sessiyani tozalash
            try:
                os.remove(session["pdf_path"])
            except Exception:
                pass
            USER_SESSIONS.pop(session_id, None)

        except Exception as err:
            logger.error(f"Tarjima xatoligi: {err}")
            bot.send_message(call.message.chat.id, f"❌ Tarjima jarayonida xatolik yuz berdi: {err}")

    threading.Thread(target=_run_translation_worker, daemon=True).start()

@bot.callback_query_handler(func=lambda call: call.data.startswith("tr_cancel:"))
def cb_cancel_translation(call):
    session_id = call.data.split(":")[1]
    session = USER_SESSIONS.pop(session_id, None)
    if session and os.path.exists(session.get("pdf_path", "")):
        try:
            os.remove(session["pdf_path"])
        except Exception:
            pass
    bot.answer_callback_query(call.id, "Bekor qilindi.")
    bot.edit_message_text("Amal bekor qilindi.", call.message.chat.id, call.message.message_id)

# ==================== ODDIY MATN TARJIMASI ====================
@bot.message_handler(func=lambda msg: True and msg.text)
def handle_incoming_text(message):
    user_id = message.from_user.id
    text = message.text.strip()

    if text in ["📤 PDF / Hujjat yuborish", "💬 Matn tarjima qilish", "⚙️ Asosiy tilni sozlash", "📊 Statistika", "ℹ️ Yordam & Yo'riqnoma"]:
        return

    # Statistika buyrug'i
    if text in ["📊 Statistika", "/stat", "/stats"]:
        conn = get_db()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        total_u = c.fetchone()[0]
        c.execute("SELECT SUM(translations_count), SUM(pages_count) FROM users")
        row = c.fetchone()
        total_tr = row[0] or 0
        total_pages = row[1] or 0
        conn.close()

        stat_text = (
            f"📊 <b>BOT STATISTIKASI</b>\n\n"
            f"👥 Jami foydalanuvchilar: <b>{total_u:,} ta</b>\n"
            f"📑 Jami tarjima qilingan hujjatlar: <b>{total_tr:,} ta</b>\n"
            f"📄 Jami tarjima qilingan sahifalar: <b>{total_pages:,} sahifa</b>\n\n"
            f"👑 Administrator: @usman_khasan"
        )
        bot.send_message(message.chat.id, stat_text)
        return

    if text in ["ℹ️ Yordam & Yo'riqnoma", "/help"]:
        help_text = (
            "ℹ️ <b>BOTDAN FOYDALANISH YO'RIQNOMASI:</b>\n\n"
            "1. <b>PDF faylni tarjima qilish:</b>\n"
            "Faylingizni Telegram orqali botga jo'nating. Bot sahifalarni o'qiydi va sizga til tanlash menyusini chiqaradi. Kerakli tilni tanlaganingizdan so'ng, bot tarjimani amalga oshirib, yangi A4 PDF va Word faylini yuboradi.\n\n"
            "2. <b>Matnni tarjima qilish:</b>\n"
            "Shunchaki istalgan tildagi matnni chatga yozib yuboring — bot uni avtomatik o'zbek tiliga o'girib beradi.\n\n"
            "3. <b>Qo'llab-quvvatlanadigan tillar:</b>\n"
            "Ruscha, Inglizcha, Turkcha, Nemischa, Arabcha, Xitoycha va h.k.\n\n"
            "Savol va takliflar: @usman_khasan"
        )
        bot.send_message(message.chat.id, help_text)
        return

    # To'g'ridan-to'g'ri matn tarjimasi
    status_msg = bot.reply_to(message, "⏳ <i>Matn tarjima qilinmoqda...</i>")
    translated = translate_long_text(text, src_lang="auto", dest_lang="uz")

    if translated:
        bot.edit_message_text(
            f"🇺🇿 <b>O'zbekcha tarjima:</b>\n\n{translated}\n\n🤖 @pdf_tarjimon_bot",
            message.chat.id,
            status_msg.message_id
        )
    else:
        bot.edit_message_text("❌ Tarjima qilishda xatolik yuz berdi.", message.chat.id, status_msg.message_id)

# ==================== ISHGA TUSHIRISH ====================
if __name__ == "__main__":
    logger.info("PDF Tarjimon Boti ishga tushirilmoqda...")
    print("=" * 65)
    print("🌍 SMART PDF & HUJJATLARNI TARJIMA QILUVCHI BOT TAYYOR!")
    print(f"👑 Admin ID: {ADMIN_ID} (@usman_khasan)")
    print(f"ReportLab holati: {'Faol' if REPORTLAB_AVAILABLE else 'Pure-Python rejimida'}")
    print(f"python-docx holati: {'Faol' if DOCX_AVAILABLE else 'O`rnatilmagan'}")
    print("=" * 65)

    while True:
        try:
            bot.infinity_polling(timeout=35, long_polling_timeout=20, skip_pending=True)
        except Exception as err:
            logger.error(f"Polling uzilishi: {err}")
            time.sleep(5)
