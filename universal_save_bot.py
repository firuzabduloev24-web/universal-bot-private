#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
🌟 UNIVERSAL SUPER SAVER & MULTIMEDIA AI TELEGRAM BOT (#1 EDITION) 🌟
=============================================================================
Muallif & Bosh Administrator: @usman_khasan (Telegram ID: 1021089367)
Arxitektura: pyTelegramBotAPI (telebot) + yt-dlp + Multi-Engine Mobile API + FFmpeg + SQLite3

Noyob imkoniyatlar (100% Sof Universal Media & AI Bot):
 1. 🎬 12-Bosqichli Xatosiz Mobil & Desktop Video Yuklagich (VIDEO-FIRST):
    - Instagram (Reels, Post video, Karusel albomlar, Stories — ?cplk=, ?obrf=, ?igsh=, /p/, /reel/ mobil linklar bilan 100% VIDEO yuklaydi, videoni rasm qilib yubormaydi!)
    - TikTok (Suv belgisiz, toza HD video — vt.tiktok.com, vm.tiktok.com mobil linklar bilan)
    - YouTube & Shorts (Video va MP3 audio — Android/iOS client bypass bilan)
    - Pinterest (pin.it mobil linklar), Twitter/X (vxTwitter API bilan), Facebook, Likee, Threads, Reddit.
 2. ✂️ 50 MB+ Video Auto-Splitter (Part 1, Part 2...):
    - Telegram botlarining 50 MB cheklovini stream-copy (-c copy) orqali yengish!
    - Katta videolarni soniyalar ichida 45 MB lik bo'laklarga ajratib jo'natadi.
 3. 🎵 Shazam / Musiqani Aniqlash:
    - Videodagi qo'shiq nomi, ijrochisi va albomini aniqlash.
 4. 🧠 Bepul Sun'iy Intellekt (DeepSeek & ChatGPT):
    - Har qanday savollarga aqlli va tezkor javoblar (/ai yoki chat orqali).
 5. 🖼 AI Rasm Chizish (NanoBanana / Flux Art):
    - Matnli tavsif bo'yicha yuqori sifatli fotosuratlar yaratish (/image).
 6. 🌐 Ko'p Tilli Interfeys (Multi-Language):
    - 🇺🇿 O'zbekcha | 🇷🇺 Русский | 🇬🇧 English (/lang orqali o'zgartirish).
 7. ✂️ Videoni Qirqish / Kesish (Video Trimmer):
    - Videodan kerakli vaqt oralig'ini qirqib olish (masalan: 00:10 - 00:35).
 8. 📝 AI Subtitr va Transkripsiya (Speech-to-Text):
    - Videodagi nutqni matnga aylantirish (.SRT subtitr fayli va xabar matni).
 9. 🎬 Subtitrli Video (Hardcode Subtitles):
    - Subtitrlarni video kadrlariga chiroyli dizaynda yopishtirib berish.
10. 🔵 Telegram Kruglyash (Video Note) 1:1 formatda yaratish (480x480).
11. 🎧 Audio (MP3 320kbps) ajratish va 🎙 Ovozli Xabar (Voice Note .ogg).
12. ⚡ 1.5x Tezlashtirilgan video va 🎞 GIF looper animatsiya.
13. 🎧 8D Surround Audio & 🔊 Bass Boost Konverter.
14. 🎤 Karaoke / Minusovka Ajratgich (Vocal Remover).
15. ⏪ Videoni Teskari Aylantirish (Reverse Video).
16. 🖼 Video Oblojkasini (HD Thumbnail) Yuklash.
17. 🌍 AI Professional Tarjimon (/tr), 💱 4-Manbali Markaziy Bank Valyuta Kurslari (/kurs) va 📱 QR-Kod (/qr).
18. 🎬 PRO REKLAMA MONTAJ STUDIYASI (/montaj, /set_outro — Har qanday davomiylikdagi videolarni, masalan 10s, 19s, 45s, 1 daqiqa va undan uzun videolarni 4 xil professional audio-vizual rejimda 1080x1920 Full HD Reels formatda ulash!)
19. 🧹 Avtomatik Xotira Tozalagich + Eski python.exe jarayonlarini avto-yopish!
=============================================================================
"""

import os
import re
import sys
import time
import json
import math
import html
import uuid
import zlib
import struct
import random
import shutil
import sqlite3
import threading
import subprocess
import urllib.request
import urllib.parse
from datetime import datetime
import telebot
from telebot import types
import yt_dlp
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==================== ESKI BOT JARAYONLARINI AVTOMATIK TO'XTATISH ====================
def kill_other_bot_instances():
    """Windowsda orqa fonda qolib ketgan eski python.exe (eski bot) jarayonlarini avtomatik to'xtatish"""
    if os.name == "nt":
        my_pid = os.getpid()
        try:
            subprocess.run(
                f'taskkill /F /FI "PID ne {my_pid}" /IM python.exe',
                shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception:
            pass

# ==================== WINDOWS FFMPEG AVTO-SOZLASH ====================
FFMPEG_DIR = None

def ensure_ffmpeg_in_path():
    """Windows WinGet orqali o'rnatilgan FFmpeg ni avtomatik topish va PATH ga qo'shish"""
    global FFMPEG_DIR
    existing = shutil.which("ffmpeg")
    if existing and shutil.which("ffprobe"):
        FFMPEG_DIR = os.path.dirname(os.path.abspath(existing))
        return True
    search_dirs = []
    local_app_data = os.environ.get("LOCALAPPDATA", "")
    if local_app_data:
        winget_links = os.path.join(local_app_data, "Microsoft", "WinGet", "Links")
        if os.path.isdir(winget_links):
            search_dirs.append(winget_links)
        winget_pkgs = os.path.join(local_app_data, "Microsoft", "WinGet", "Packages")
        if os.path.isdir(winget_pkgs):
            for root, dirs, files in os.walk(winget_pkgs):
                if "ffmpeg.exe" in [f.lower() for f in files]:
                    search_dirs.append(root)
    for extra in [r"C:\ffmpeg\bin", r"C:\Program Files\ffmpeg\bin"]:
        if os.path.isdir(extra):
            search_dirs.append(extra)
    for d in search_dirs:
        if os.path.exists(os.path.join(d, "ffmpeg.exe")):
            os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
            FFMPEG_DIR = d
            return True
    return False

FFMPEG_READY = ensure_ffmpeg_in_path()

# ==================== SOZLAMALAR (KONFIGURATSIYA) ====================
# Maxfiy kalitlar .env faylidan o'qiladi (GitHub'ga chiqmaydi, qarang: .env.example)
def load_env_file(path):
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as ef:
        for line in ef:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

load_env_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN topilmadi. .env faylini tekshiring.")
ADMIN_ID = 1021089367
ADMIN_USERNAME = "@usman_khasan"
ADMIN_FIRST_NAME = "khasanov"

TOKEN_FILE = "bot_token.txt"
try:
    with open(TOKEN_FILE, "w", encoding="utf-8") as tf:
        tf.write(BOT_TOKEN.strip())
except Exception:
    pass

# Majburiy obuna bo'linadigan kanallar ro'yxati (ixtiyoriy, masalan: ["@kanal_username"]):
SPONSOR_CHANNELS = []

REQUIRED_REFERRALS_FOR_VIP = 3
MAX_TELEGRAM_FILE_MB = 49.5
GROQ_API_KEY = ""  # Ixtiyoriy: console.groq.com (Bo'sh bo'lsa, bepul Google Speech ishlaydi)
GOOGLE_SPEECH_KEY = os.environ.get("GOOGLE_SPEECH_KEY", "")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Doimiy reklama/outro shablonlari saqlanadigan papka (Avto-tozalagich bu papkani hech qachon o'chirmaydi!)
PROMO_DIR = "promo_assets"
os.makedirs(PROMO_DIR, exist_ok=True)

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML", threaded=True, num_threads=8)
USER_STATES = {}
TRIM_CACHE = {}
MONTAGE_CACHE = {}

# ==================== XOTIRANI AVTOMATIK TOZALASH TIZIMI ====================
def safe_remove(*file_paths):
    """Berilgan fayllarni kompyuter xotirasidan darhol va xavfsiz o'chirib tashlash"""
    for fp in file_paths:
        if fp and isinstance(fp, str) and os.path.exists(fp):
            try:
                os.remove(fp)
            except Exception:
                pass

def cleanup_old_files(max_age_seconds: int = 120):
    """downloads papkasidagi vaqtinchalik fayllarni avtomatik o'chirish (xotira to'lmasligi uchun)"""
    now = time.time()
    removed_count = 0
    freed_bytes = 0
    try:
        for fname in os.listdir(DOWNLOAD_DIR):
            fpath = os.path.join(DOWNLOAD_DIR, fname)
            if os.path.isfile(fpath):
                age = now - os.path.getmtime(fpath)
                if age > max_age_seconds or fname.endswith(".part") or fname.endswith(".ytdl"):
                    try:
                        fsize = os.path.getsize(fpath)
                        os.remove(fpath)
                        removed_count += 1
                        freed_bytes += fsize
                    except Exception:
                        pass
        for fname in os.listdir("."):
            if fname.startswith("_tmp_sub_") and fname.endswith(".srt"):
                try:
                    if (now - os.path.getmtime(fname)) > 120:
                        os.remove(fname)
                except Exception:
                    pass
    except Exception:
        pass
    return removed_count, freed_bytes / (1024 * 1024)

def start_auto_cleaner_daemon():
    """Orqa fonda har 45 soniyada kompyuter xotirasini tozalab turuvchi avto-tizim"""
    def _cleaner_loop():
        while True:
            try:
                cleanup_old_files(max_age_seconds=120)
            except Exception:
                pass
            time.sleep(45)
    t = threading.Thread(target=_cleaner_loop, daemon=True)
    t.start()

start_auto_cleaner_daemon()

# ==================== KO'P TILLI INTERFEYS (LOCALIZATION) ====================
TEXTS = {
    "uz": {
        "welcome": (
            "👋 <b>Assalomu alaykum, {name}!</b>\n\n"
            "⚡ <b>Universal Super Saver & Multimedia AI Bot (#1 Edition)</b>ga xush kelibsiz!\n\n"
            "📥 <b>Universal Media Yuklovchi (Telefon va Kompyuterdan 100% Xatosiz):</b>\n"
            "• 📸 <b>Instagram:</b> Reels, Post video, Karusel albomlar, Stories\n"
            "• 🎵 <b>TikTok:</b> Toza, suv belgisiz HD video\n"
            "• ▶️ <b>YouTube & Shorts:</b> Video, MP3 musiqa va HD Oblojka\n"
            "• 📌 <b>Pinterest, Twitter / X, Facebook, Likee, Reddit</b>\n\n"
            "🧠 <b>Sun'iy Intellekt (AI) & Universal Vositalar:</b>\n"
            "• 🤖 <b>DeepSeek & ChatGPT:</b> Istalgan savolga aqlli javoblar (/ai)\n"
            "• 🖼 <b>NanoBanana / AI Image:</b> Matndan ajoyib rasm chizish (/image)\n"
            "• 🌍 <b>AI Tarjimon:</b> Matnlarni istalgan tilga tarjima qilish (/tr)\n"
            "• 📱 <b>QR-Kod Generator:</b> Ssilka va matndan QR-kod yasash (/qr)\n"
            "• 💱 <b>Valyuta Kurslari:</b> Markaziy bank jonli kurslari (/kurs)\n\n"
            "💎 <b>12 ta Super Multimedia Studiyasi:</b>\n"
            "✂️ <b>50 MB+ Splitter:</b> Katta videolarni bo'laklarga ajratish\n"
            "🎵 <b>Shazam:</b> Videodagi musiqani topish va MP3 yuklash\n"
            "🎧 <b>8D Audio & 🔊 Bass Boost:</b> Qo'shiqni 8D va Bass qilish\n"
            "🎤 <b>Karaoke Minusovka:</b> Qo'shiqdan ovozni pasaytirish\n"
            "🎬 <b>AI Subtitr:</b> Nutqni videoga yozish va .SRT olish\n"
            "✂️ <b>Qirqish (Trim), 🔵 Kruglyash, ⏪ Teskari video, ⚡ 1.5x, 🎞 GIF</b>\n\n"
            "⭐️ <b>VIP Tizim:</b> 3 ta do'stni taklif qilib, umrbod VIP maqomiga ega bo'ling!\n\n"
            "📥 <i>Video havolasini yuboring, fayl tashlang yoki AI ga savol yozing!</i>"
        ),
        "btn_profile": "👤 Profilim",
        "btn_stat": "📊 Statistika",
        "btn_kurs": "💱 Valyuta Kurslari",
        "btn_ref": "👥 VIP & Do'stlar",
        "btn_ai": "🧠 AI Savol-Javob",
        "btn_image": "🖼 AI Rasm Chizish",
        "btn_montaj": "🎬 Reklama Montaj",
        "btn_tools": "🛠 Universal Vositalar",
        "btn_help": "📖 Qo'llanma",
        "btn_lang": "🌐 Til",
        "sub_required": (
            "⚠️ <b>Botdan to'liq foydalanish uchun rasmiy kanalimizga a'zo bo'ling:</b>\n"
            "<i>(Yoki 3 ta do'stingizni taklif qilib, umrbod obunalarsiz VIP bo'ling!)</i>"
        ),
        "btn_sub_check": "✅ A'zo bo'ldim / Tekshirish",
        "btn_sub_invite": "⭐️ 3 ta do'stni chaqirib, VIP olish",
        "sub_success": "✅ Rahmat! Barcha kanallarga a'zo bo'lgansiz.",
        "sub_failed": "❌ Hali hamma kanallarga a'zo bo'lmadingiz!",
        "lang_changed": "✅ Til muvaffaqiyatli o'zgartirildi: 🇺🇿 O'zbek tili",
        "analyzing": "⏳ <b>{platform}</b> havolasi tahlil qilinmoqda. Yuklanmoqda...",
        "not_found": "❌ Video topilmadi yoki havola yopiq (private) profilga tegishli.",
        "err_generic": "❌ Xatolik yuz berdi. Qayta urinib ko'ring.",
        "large_file_split_prompt": (
            "⚠️ <b>Diqqat: Video hajmi Telegram limitidan katta ({size:.1f} MB)!</b>\n\n"
            "Quyidagi qulay variantlardan birini tanlang:"
        ),
        "btn_split_parts": "✂️ Qismlarga (Part 1, 2...) bo'lib yuklash",
        "btn_audio_only": "🎧 Faqat MP3 musiqasini yuklash",
        "splitting_progress": "⏳ Video bo'laklarga ajratilmoqda, kuting...",
        "part_caption": "🎬 <b>{title}</b>\n📦 <b>Qism:</b> {current}/{total}\n🤖 @{bot}",
        "trim_prompt": "✂️ <b>Videoni qirqish (Trim):</b>\nBoshlanish va tugash vaqtini yozing (Masalan: <code>00:10 - 00:35</code>):",
        "trim_invalid": "⚠️ Vaqt formati noto'g'ri. Masalan: <code>00:10 - 00:35</code> shaklida yozing.",
        "trimming_progress": "⏳ Video qirqilmoqda...",
        "music_searching": "🔍 Videodagi musiqa aniqlanmoqda (Shazam)...",
        "music_found": (
            "🎵 <b>Musiqa aniqlandi!</b>\n\n"
            "🎼 <b>Nomi:</b> <b>{title}</b>\n"
            "👤 <b>Ijrochi:</b> <b>{artist}</b>\n"
            "{album_line}"
            "🤖 @{bot}"
        ),
        "music_not_found": "ℹ️ Musiqa aniqlanmadi yoki videoda faqat nutq mavjud.",
        "sub_video_generating": "🎬 AI Subtitr tayyorlanmoqda (nutq kadrga yozilmoqda)...",
        "sub_text_generating": "📝 Nutq tahlil qilinmoqda (Speech-to-Text)...",
        "sub_not_found": "ℹ️ Nutq aniqlanmadi. Inson ovozi yo'q yoki fon shovqini baland.",
        "circle_generating": "🔄 Dumaloq video (kruglyash) tayyorlanmoqda...",
        "audio_generating": "🎵 Musiqa (MP3) ajratib olinmoqda...",
        "voice_generating": "🎙 Ovozli xabar (Voice) tayyorlanmoqda...",
        "speed_generating": "⚡ Video 1.5x tezlashtirilmoqda...",
        "gif_generating": "🎞 GIF animatsiya tayyorlanmoqda...",
        "bass_generating": "🔊 Kuchli Bass Boost audio tayyorlanmoqda...",
        "audio8d_generating": "🎧 8D Surround aylanma audio tayyorlanmoqda...",
        "karaoke_generating": "🎤 Karaoke minusovka tayyorlanmoqda...",
        "reverse_generating": "⏪ Video teskari (Reverse) aylantirilmoqda...",
        "ai_thinking": "🧠 <b>AI o'ylamoqda...</b>",
        "ai_image_generating": "🎨 <b>AI rasm chizmoqda, bir oz kuting...</b>",
        "ai_prompt_ask": "🧠 <b>Sun'iy Intellektga savolingizni yozing:</b>\n(DeepSeek va ChatGPT javob beradi)",
        "image_prompt_ask": "🖼 <b>Qanday rasm chizmoqchisiz?</b>\nTavsifni batafsil yozing (Masalan: <code>Toshkent shahrida futuristik uchuvchi mashinalar</code>):"
    },
    "ru": {
        "welcome": (
            "👋 <b>Здравствуйте, {name}!</b>\n\n"
            "⚡ Добро пожаловать в <b>Universal Super Saver & Multimedia AI Bot (#1 Edition)</b>!\n\n"
            "📥 <b>Скачивание медиа без водяных знаков:</b>\n"
            "• Instagram, TikTok, YouTube & Shorts, Pinterest, Twitter/X, FB\n\n"
            "🧠 <b>Искусственный Интеллект и Инструменты:</b>\n"
            "• DeepSeek & ChatGPT (/ai) | Генерация картинок NanoBanana (/image)\n"
            "• AI Переводчик (/tr) | Генератор QR-кодов (/qr) | Курсы валют (/kurs)\n\n"
            "💎 <b>Мультимедиа студия (12 функций):</b>\n"
            "✂️ 50MB+ Splitter, Shazam, 8D Аудио, Bass Boost, Караоке Минусовка,\n"
            "🎬 AI Субтитры, Обрезка, Кругляш, Реверс видео, MP3, 1.5x, GIF\n\n"
            "📥 <i>Отправьте ссылку на видео, медиафайл или задайте вопрос AI!</i>"
        ),
        "btn_profile": "👤 Мой профиль",
        "btn_stat": "📊 Статистика",
        "btn_kurs": "💱 Курсы валют",
        "btn_ref": "👥 VIP & Рефералы",
        "btn_ai": "🧠 Задать вопрос AI",
        "btn_image": "🖼 Создать картинку AI",
        "btn_montaj": "🎬 Видео Монтаж",
        "btn_tools": "🛠 Инструменты",
        "btn_help": "📖 Инструкция",
        "btn_lang": "🌐 Сменить язык",
        "sub_required": "⚠️ <b>Для использования бота подпишитесь на наш канал:</b>",
        "btn_sub_check": "✅ Я подписался / Проверить",
        "btn_sub_invite": "⭐️ Пригласить 3 друзей и получить VIP",
        "sub_success": "✅ Спасибо! Вы подписаны на все каналы.",
        "sub_failed": "❌ Вы ещё не подписались на все каналы!",
        "lang_changed": "✅ Язык успешно изменен: 🇷🇺 Русский",
        "analyzing": "⏳ Анализирую ссылку <b>{platform}</b>...",
        "not_found": "❌ Видео не найдено или аккаунт приватный.",
        "err_generic": "❌ Произошла ошибка. Попробуйте еще раз.",
        "large_file_split_prompt": "⚠️ <b>Размер видео превышает 50 МБ!</b> Выберите вариант:",
        "btn_split_parts": "✂️ Разбить на части (Part 1, 2...)",
        "btn_audio_only": "🎧 Скачать только MP3 аудио",
        "splitting_progress": "⏳ Видео нарезается на части...",
        "part_caption": "🎬 <b>{title}</b>\n📦 <b>Часть:</b> {current}/{total}\n🤖 @{bot}",
        "trim_prompt": "✂️ <b>Обрезка видео (Trim):</b>\nУкажите таймкод (Например: <code>00:10 - 00:35</code>):",
        "trim_invalid": "⚠️ Неверный формат времени. Пример: <code>00:10 - 00:35</code>.",
        "trimming_progress": "⏳ Видео нарезается...",
        "music_searching": "🔍 Распознавание музыки (Shazam)...",
        "music_found": "🎵 <b>Трек найден!</b>\n\n🎼 <b>Название:</b> <b>{title}</b>\n👤 <b>Исполнитель:</b> <b>{artist}</b>\n{album_line}🤖 @{bot}",
        "music_not_found": "ℹ️ Музыка не распознана.",
        "sub_video_generating": "🎬 Создание видео с субтитрами...",
        "sub_text_generating": "📝 Распознавание речи в текст...",
        "sub_not_found": "ℹ️ Речь не распознана.",
        "circle_generating": "🔄 Создание видеосообщения 1:1...",
        "audio_generating": "🎵 Извлечение MP3 музыки...",
        "voice_generating": "🎙 Создание голосового сообщения...",
        "speed_generating": "⚡ Ускорение видео в 1.5x...",
        "gif_generating": "🎞 Создание GIF анимации...",
        "bass_generating": "🔊 Создание Bass Boost аудио...",
        "audio8d_generating": "🎧 Создание 8D Surround аудио...",
        "karaoke_generating": "🎤 Создание караоке минусовки...",
        "reverse_generating": "⏪ Обратная перемотка видео (Reverse)...",
        "ai_thinking": "🧠 <b>AI думает...</b>",
        "ai_image_generating": "🎨 <b>AI генерирует изображение...</b>",
        "ai_prompt_ask": "🧠 <b>Задайте любой вопрос AI:</b>",
        "image_prompt_ask": "🖼 <b>Какое изображение вы хотите создать?</b>"
    },
    "en": {
        "welcome": (
            "👋 <b>Hello, {name}!</b>\n\n"
            "⚡ Welcome to <b>Universal Super Saver & Multimedia AI Bot (#1 Edition)</b>!\n\n"
            "📥 <b>Universal Media Downloader:</b>\n"
            "• Instagram, TikTok, YouTube & Shorts, Pinterest, Twitter/X, FB\n\n"
            "🧠 <b>AI & Smart Utilities:</b>\n"
            "• DeepSeek & ChatGPT (/ai) | NanoBanana Flux Image Generator (/image)\n"
            "• AI Translator (/tr) | QR Code Maker (/qr) | Exchange Rates (/kurs)\n\n"
            "💎 <b>Multimedia Studio (12 Tools):</b>\n"
            "✂️ 50MB+ Splitter, Shazam, 8D Audio, Bass Boost, Karaoke Vocal Remover,\n"
            "🎬 AI Subtitles, Trimmer, Video Note, Reverse Video, MP3, 1.5x, GIF\n\n"
            "📥 <i>Send a video link, upload a media file, or ask AI anything!</i>"
        ),
        "btn_profile": "👤 Profile",
        "btn_stat": "📊 Statistics",
        "btn_kurs": "💱 Exchange Rates",
        "btn_ref": "👥 VIP & Referral",
        "btn_ai": "🧠 Ask AI",
        "btn_image": "🖼 AI Image",
        "btn_montaj": "🎬 Video Montage",
        "btn_tools": "🛠 Smart Tools",
        "btn_help": "📖 Help",
        "btn_lang": "🌐 Language",
        "sub_required": "⚠️ <b>Please subscribe to our channel to use the bot:</b>",
        "btn_sub_check": "✅ Joined / Check",
        "btn_sub_invite": "⭐️ Invite 3 Friends for VIP",
        "sub_success": "✅ Thank you! Joined all channels.",
        "sub_failed": "❌ Please join the channels first!",
        "lang_changed": "✅ Language changed to: 🇬🇧 English",
        "analyzing": "⏳ Analyzing link <b>{platform}</b>...",
        "not_found": "❌ Video not found or account is private.",
        "err_generic": "❌ An error occurred. Please try again.",
        "large_file_split_prompt": "⚠️ <b>Video size exceeds 50 MB!</b> Choose option:",
        "btn_split_parts": "✂️ Split into Parts (Part 1, 2...)",
        "btn_audio_only": "🎧 Extract MP3 Audio only",
        "splitting_progress": "⏳ Splitting video into parts...",
        "part_caption": "🎬 <b>{title}</b>\n📦 <b>Part:</b> {current}/{total}\n🤖 @{bot}",
        "trim_prompt": "✂️ <b>Trim Video:</b> Enter timestamps (e.g. <code>00:10 - 00:35</code>):",
        "trim_invalid": "⚠️ Invalid format. Example: <code>00:10 - 00:35</code>.",
        "trimming_progress": "⏳ Trimming video clip...",
        "music_searching": "🔍 Identifying music (Shazam)...",
        "music_found": "🎵 <b>Music Identified!</b>\n\n🎼 <b>Title:</b> <b>{title}</b>\n👤 <b>Artist:</b> <b>{artist}</b>\n{album_line}🤖 @{bot}",
        "music_not_found": "ℹ️ Music not identified.",
        "sub_video_generating": "🎬 Burning subtitles onto video...",
        "sub_text_generating": "📝 Transcribing speech to text...",
        "sub_not_found": "ℹ️ No speech detected.",
        "circle_generating": "🔄 Converting to video note...",
        "audio_generating": "🎵 Extracting MP3 audio...",
        "voice_generating": "🎙 Converting to voice note...",
        "speed_generating": "⚡ Speeding up video to 1.5x...",
        "gif_generating": "🎞 Converting to GIF animation...",
        "bass_generating": "🔊 Generating Bass Boosted audio...",
        "audio8d_generating": "🎧 Generating 8D Surround audio...",
        "karaoke_generating": "🎤 Removing vocals (Karaoke)...",
        "reverse_generating": "⏪ Reversing video clip...",
        "ai_thinking": "🧠 <b>AI is thinking...</b>",
        "ai_image_generating": "🎨 <b>AI is generating image...</b>",
        "ai_prompt_ask": "🧠 <b>Ask anything to AI:</b>",
        "image_prompt_ask": "🖼 <b>Describe the image you want to generate:</b>"
    }
}

def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    selected_lang = lang if lang in TEXTS else "uz"
    template = TEXTS[selected_lang].get(key, TEXTS["uz"].get(key, ""))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template

# ==================== MA'LUMOTLAR BAZASI (SQLite) ====================
DB_PATH = "save_bot_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'uz',
            referrer_id INTEGER DEFAULT NULL,
            referral_count INTEGER DEFAULT 0,
            is_vip INTEGER DEFAULT 0,
            downloads_count INTEGER DEFAULT 0,
            first_seen TIMESTAMP,
            last_seen TIMESTAMP
        )
    """)
    cols = [c[1] for c in cursor.execute("PRAGMA table_info(users)").fetchall()]
    if "language" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'uz'")
    if "referrer_id" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN referrer_id INTEGER DEFAULT NULL")
    if "referral_count" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN referral_count INTEGER DEFAULT 0")
    if "is_vip" not in cols:
        cursor.execute("ALTER TABLE users ADD COLUMN is_vip INTEGER DEFAULT 0")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS downloads_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            url TEXT,
            platform TEXT,
            download_type TEXT,
            created_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def register_user(user: types.User, referrer_id: int | None = None) -> tuple[bool, bool]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("SELECT user_id, is_vip, language FROM users WHERE user_id = ?", (user.id,))
    row = cursor.fetchone()

    is_new = False
    ref_became_vip = False

    if not row:
        is_new = True
        actual_referrer = None
        if referrer_id and referrer_id != user.id:
            cursor.execute("SELECT user_id, referral_count, is_vip FROM users WHERE user_id = ?", (referrer_id,))
            ref_row = cursor.fetchone()
            if ref_row:
                actual_referrer = referrer_id
                new_count = (ref_row[1] or 0) + 1
                became_vip = 1 if new_count >= REQUIRED_REFERRALS_FOR_VIP else ref_row[2]
                if became_vip == 1 and ref_row[2] == 0:
                    ref_became_vip = True
                cursor.execute(
                    "UPDATE users SET referral_count = ?, is_vip = ? WHERE user_id = ?",
                    (new_count, became_vip, referrer_id)
                )

        default_lang = "uz"
        if user.language_code:
            if user.language_code.startswith("ru"):
                default_lang = "ru"
            elif user.language_code.startswith("en"):
                default_lang = "en"

        cursor.execute("""
            INSERT INTO users (user_id, username, full_name, language, referrer_id, referral_count, is_vip, downloads_count, first_seen, last_seen)
            VALUES (?, ?, ?, ?, ?, 0, 0, 0, ?, ?)
        """, (user.id, user.username or "", f"{user.first_name or ''} {user.last_name or ''}".strip(), default_lang, actual_referrer, now, now))
    else:
        cursor.execute("""
            UPDATE users SET username = ?, full_name = ?, last_seen = ? WHERE user_id = ?
        """, (user.username or "", f"{user.first_name or ''} {user.last_name or ''}".strip(), now, user.id))

    conn.commit()
    conn.close()
    return is_new, ref_became_vip

def get_user_lang(user_id: int) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] in TEXTS else "uz"

def set_user_lang(user_id: int, lang: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET language = ? WHERE user_id = ?", (lang, user_id))
    conn.commit()
    conn.close()

def is_user_vip(user_id: int) -> bool:
    if user_id == ADMIN_ID:
        return True
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_vip FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return bool(row and row[0] == 1)

def get_user_profile(user_id: int) -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT referral_count, is_vip, downloads_count, language, first_seen, username, full_name FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if row:
        return {
            "referrals": row[0] or 0,
            "is_vip": bool(row[1] == 1 or user_id == ADMIN_ID),
            "downloads": row[2] or 0,
            "language": row[3] or "uz",
            "registered": (row[4] or now_str)[:16],
            "username": row[5] or "",
            "full_name": row[6] or ""
        }
    return {
        "referrals": 0,
        "is_vip": (user_id == ADMIN_ID),
        "downloads": 0,
        "language": "uz",
        "registered": now_str,
        "username": "",
        "full_name": ""
    }

def increment_download_count(user_id: int, url: str, platform: str, download_type: str = "video"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET downloads_count = downloads_count + 1, last_seen = ? WHERE user_id = ?", (now, user_id))
    cursor.execute("""
        INSERT INTO downloads_history (user_id, url, platform, download_type, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, url, platform, download_type, now))
    conn.commit()
    conn.close()

def is_admin_user(user: types.User) -> bool:
    if not user:
        return False
    if user.id == ADMIN_ID:
        return True
    if user.username and user.username.lower() == ADMIN_USERNAME.lstrip("@").lower():
        return True
    return False

def get_stats() -> dict:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM users WHERE last_seen LIKE ?", (f"{today_str}%",))
    active_today = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE first_seen LIKE ?", (f"{today_str}%",))
    new_today = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM users WHERE is_vip = 1")
    total_vips = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM downloads_history")
    total_downloads = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM downloads_history WHERE created_at LIKE ?", (f"{today_str}%",))
    downloads_today = cursor.fetchone()[0]
    cursor.execute("SELECT platform, COUNT(*) FROM downloads_history GROUP BY platform ORDER BY COUNT(*) DESC LIMIT 6")
    top_platforms = cursor.fetchall()
    cursor.execute("SELECT user_id, username, full_name, downloads_count FROM users ORDER BY last_seen DESC LIMIT 5")
    recent_users = cursor.fetchall()
    conn.close()
    return {
        "total_users": total_users,
        "active_today": active_today,
        "new_today": new_today,
        "total_vips": total_vips,
        "total_downloads": total_downloads,
        "downloads_today": downloads_today,
        "top_platforms": top_platforms,
        "recent_users": recent_users
    }

def build_stats_message(user: types.User) -> tuple[str, types.InlineKeyboardMarkup]:
    register_user(user)
    st = get_stats()
    prof = get_user_profile(user.id)
    uname = f"@{user.username}" if user.username else (ADMIN_USERNAME if user.id == ADMIN_ID else f"user_{user.id}")
    fname = user.first_name or (ADMIN_FIRST_NAME if user.id == ADMIN_ID else "User")

    platform_lines = "\n".join([f"  • <b>{p[0]}:</b> {p[1]:,} ta" for p in st["top_platforms"]]) or "  • Hozircha yuklamalar yo'q"

    disk_files = 0
    disk_mb = 0.0
    try:
        for fn in os.listdir(DOWNLOAD_DIR):
            fp = os.path.join(DOWNLOAD_DIR, fn)
            if os.path.isfile(fp):
                disk_files += 1
                disk_mb += os.path.getsize(fp) / (1024 * 1024)
    except Exception:
        pass

    recent_block = ""
    if is_admin_user(user) and st.get("recent_users"):
        r_lines = []
        for ru in st["recent_users"]:
            r_uname = f"@{ru[1]}" if ru[1] else (ru[2] or str(ru[0]))
            r_lines.append(f"  • {r_uname} (<code>{ru[0]}</code>) — {ru[3] or 0} yuklama")
        recent_block = "\n\n👑 <b>Oxirgi faol foydalanuvchilar:</b>\n" + "\n".join(r_lines)

    text = (
        f"📊 <b>BOT VA FOYDALANUVCHI STATISTIKASI</b>\n\n"
        f"👤 <b>Sizning profilingiz:</b> {uname} ({fname})\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code> | 🌐 <b>Til:</b> {prof.get('language', 'uz')}\n"
        f"📥 <b>Sizning yuklamalaringiz:</b> <b>{prof['downloads']} ta</b>\n"
        f"👥 <b>Taklif qilgan do'stlaringiz:</b> <b>{prof['referrals']} ta</b>\n"
        f"📅 <b>Ro'yxatdan o'tgan:</b> {prof.get('registered', 'Bugun')}\n\n"
        f"🌐 <b>UMUMIY BOT KO'RSATKICHLARI:</b>\n"
        f"👥 <b>Jami foydalanuvchilar:</b> <b>{st['total_users']:,} ta</b>\n"
        f"🆕 <b>Bugun qo'shilganlar:</b> <b>{st['new_today']:,} ta</b>\n"
        f"⚡ <b>Bugun faol:</b> <b>{st['active_today']:,} ta</b>\n"
        f"⭐️ <b>VIP foydalanuvchilar:</b> <b>{st['total_vips']:,} ta</b>\n"
        f"📥 <b>Jami yuklab olingan media:</b> <b>{st['total_downloads']:,} ta</b>\n"
        f"🔥 <b>Bugungi yuklashlar:</b> <b>{st['downloads_today']:,} ta</b>\n"
        f"💾 <b>Kompyuter xotirasi (Downloads):</b> <b>{disk_mb:.2f} MB</b> ({disk_files} ta fayl)\n\n"
        f"📈 <b>Top platformalar bo'yicha:</b>\n{platform_lines}"
        f"{recent_block}"
    )

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔄 Yangilash", callback_data="open_stats"),
        types.InlineKeyboardButton("🧹 Xotirani tozalash", callback_data="clean_storage_cb")
    )
    markup.add(
        types.InlineKeyboardButton("💱 Markaziy Bank Kurslari", callback_data="tool_cmd:kurs"),
        types.InlineKeyboardButton("📱 QR-Kod Yasash", callback_data="tool_cmd:qr")
    )
    markup.add(
        types.InlineKeyboardButton("🧠 Free AI → DeepSeek & ChatGPT", callback_data="tool_cmd:ai"),
        types.InlineKeyboardButton("🖼 Make Image → NanoBanana", callback_data="tool_cmd:image")
    )
    return text, markup

# ==================== KANAL OBUNA & MENYULAR ====================
def check_channel_subscription(user_id: int) -> tuple[bool, list]:
    if is_user_vip(user_id) or not SPONSOR_CHANNELS:
        return True, []
    unsubscribed = []
    for channel in SPONSOR_CHANNELS:
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status in ["left", "kicked"]:
                unsubscribed.append(channel)
        except Exception as e:
            print(f"Kanal tekshirishda xatolik ({channel}): {e}")
    return len(unsubscribed) == 0, unsubscribed

def get_sub_keyboard(unsubscribed: list, lang: str = "uz") -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=1)
    for channel in unsubscribed:
        clean_name = channel.replace("@", "")
        markup.add(types.InlineKeyboardButton(text=f"➕ {channel}", url=f"https://t.me/{clean_name}"))
    markup.add(types.InlineKeyboardButton(text=get_text("btn_sub_check", lang), callback_data="check_subscription"))
    markup.add(types.InlineKeyboardButton(text=get_text("btn_sub_invite", lang), callback_data="open_referral"))
    return markup

def get_main_reply_keyboard(lang: str = "uz") -> types.ReplyKeyboardMarkup:
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    b_montaj = types.KeyboardButton(get_text("btn_montaj", lang))
    b1 = types.KeyboardButton(get_text("btn_profile", lang))
    b_stat = types.KeyboardButton(get_text("btn_stat", lang))
    b_kurs = types.KeyboardButton(get_text("btn_kurs", lang))
    b2 = types.KeyboardButton(get_text("btn_ref", lang))
    b3 = types.KeyboardButton(get_text("btn_ai", lang))
    b4 = types.KeyboardButton(get_text("btn_image", lang))
    b5 = types.KeyboardButton(get_text("btn_tools", lang))
    b6 = types.KeyboardButton(get_text("btn_help", lang))
    b7 = types.KeyboardButton(get_text("btn_lang", lang))
    markup.add(b_montaj, b_stat)
    markup.add(b1, b_kurs)
    markup.add(b3, b4)
    markup.add(b5, b2)
    markup.add(b6, b7)
    return markup

def get_language_inline_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=3)
    b_uz = types.InlineKeyboardButton("🇺🇿 O'zbek", callback_data="set_lang:uz")
    b_ru = types.InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang:ru")
    b_en = types.InlineKeyboardButton("🇬🇧 English", callback_data="set_lang:en")
    markup.add(b_uz, b_ru, b_en)
    return markup

# ==================== SUN'IY INTELLEKT (AI DEEPSEEK & CHATGPT & IMAGE) ====================
def query_free_ai(prompt: str, model_type: str = "deepseek") -> str:
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}?model={model_type}&system=You+are+an+intelligent+helpful+AI+assistant.+Answer+politely+in+the+user's+language."
        resp = requests.get(url, timeout=30, verify=False)
        if resp.status_code == 200 and resp.text.strip():
            return resp.text.strip()
    except Exception as e:
        print(f"AI so'rov xatoligi: {e}")

    try:
        url2 = f"https://text.pollinations.ai/{urllib.parse.quote(prompt)}"
        resp2 = requests.get(url2, timeout=20, verify=False)
        if resp2.status_code == 200 and resp2.text.strip():
            return resp2.text.strip()
    except Exception:
        pass

    return "Kechirasiz, sun'iy intellekt serveri bilan bog'lanishda vaqtinchalik xatolik yuz berdi. Birozdan so'ng qayta urinib ko'ring."

def generate_ai_image_bytes(prompt: str) -> bytes | None:
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
        resp = requests.get(image_url, timeout=45, verify=False)
        if resp.status_code == 200 and len(resp.content) > 5000:
            return resp.content
    except Exception as e:
        print(f"AI Image xatoligi: {e}")
    return None

def generate_qr_code_bytes(data_text: str) -> bytes | None:
    try:
        encoded = urllib.parse.quote(data_text)
        url = f"https://api.qrserver.com/v1/create-qr-code/?size=600x600&margin=15&data={encoded}"
        resp = requests.get(url, timeout=15, verify=False)
        if resp.status_code == 200 and len(resp.content) > 500:
            return resp.content
    except Exception as e:
        print(f"QR xatoligi: {e}")
    return None

# ==================== 4-MANBALI MARKAZIY BANK VALYUTA KURSLARI (/kurs) ====================
def fetch_cbu_exchange_rates(amount: float = 1.0) -> str:
    """
    O'zbekiston Respublikasi Markaziy Banki valyuta kurslarini 4 ta mustaqil manbadan
    SSL va WAF bloklarisiz (verify=False + Browser User-Agent) 100% xatosiz olib kelish!
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
    }
    wanted = [
        ("USD", "🇺🇸 AQSH Dollari"),
        ("EUR", "🇪🇺 Yevro"),
        ("RUB", "🇷🇺 Rossiya Rubli"),
        ("GBP", "🇬🇧 Angliya Funti"),
        ("CNY", "🇨🇳 Xitoy Yuani"),
        ("KZT", "🇰🇿 Qozog'iston Tengesi"),
        ("TRY", "🇹🇷 Turkiya Lirasi"),
    ]

    # 1-MANBA: O'zbekiston Markaziy Banki rasmiy JSON API (3 xil til endpointi, SSL verify=False bilan)
    cbu_urls = [
        "https://cbu.uz/oz/arkhiv-kursov-valyut/json/",
        "https://cbu.uz/uz/arkhiv-kursov-valyut/json/",
        "https://cbu.uz/ru/arkhiv-kursov-valyut/json/",
        "http://cbu.uz/oz/arkhiv-kursov-valyut/json/",
    ]
    for cbu_url in cbu_urls:
        try:
            resp = requests.get(cbu_url, headers=headers, timeout=10, verify=False)
            if resp.status_code == 200 and resp.text.strip():
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    by_ccy = {item.get("Ccy"): item for item in data if isinstance(item, dict)}
                    lines = ["🏦 <b>O'zbekiston Markaziy Banki Valyuta Kurslari:</b>\n"]
                    for code, label in wanted:
                        item = by_ccy.get(code)
                        if not item:
                            continue
                        rate_val = float(str(item.get("Rate", "0")).replace(",", "."))
                        nominal = float(str(item.get("Nominal", "1")).replace(",", ".")) or 1.0
                        unit_rate = rate_val / nominal
                        diff_str = str(item.get("Diff", "0"))
                        try:
                            diff_val = float(diff_str.replace(",", "."))
                        except ValueError:
                            diff_val = 0.0
                        sign = f"📈 +{diff_str}" if diff_val > 0 else (f"📉 {diff_str}" if diff_val < 0 else "➖ 0")
                        if amount != 1.0:
                            calc_sum = unit_rate * amount
                            lines.append(f"{label} (<b>{amount:g} {code}</b>): <b>{calc_sum:,.2f} so'm</b> <i>(1 {code} = {unit_rate:,.2f})</i>")
                        else:
                            lines.append(f"{label} (<b>1 {code}</b>): <b>{unit_rate:,.2f} so'm</b> ({sign})")

                    date_str = data[0].get("Date") or datetime.now().strftime("%d.%m.%Y")
                    lines.append(f"\n📅 <i>Sana: {date_str} | Manba: cbu.uz</i>")
                    lines.append("💡 <i>Hisoblash uchun:</i> <code>/kurs 100</code>")
                    return "\n".join(lines)
        except Exception as e:
            print(f"CBU API urinish xatosi ({cbu_url}): {e}")

    # 2-MANBA va 3-MANBA: Xalqaro Zaxira Bank API (open.er-api.com & exchangerate-api.com)
    backup_apis = [
        "https://open.er-api.com/v6/latest/USD",
        "https://api.exchangerate-api.com/v4/latest/USD",
    ]
    for b_url in backup_apis:
        try:
            r = requests.get(b_url, headers=headers, timeout=10, verify=False)
            if r.status_code == 200:
                j = r.json()
                rates = j.get("rates", {})
                uzs_per_usd = float(rates.get("UZS", 0))
                if uzs_per_usd > 1000:
                    lines = ["🏦 <b>Markaziy Bank & Xalqaro Valyuta Kurslari:</b>\n"]
                    for code, label in wanted:
                        c_rate = float(rates.get(code, 0))
                        if c_rate > 0:
                            uzs_val = (uzs_per_usd / c_rate) * amount
                            unit_val = uzs_per_usd / c_rate
                            if amount != 1.0:
                                lines.append(f"{label} (<b>{amount:g} {code}</b>): <b>{uzs_val:,.2f} so'm</b> <i>(1 {code} = {unit_val:,.2f})</i>")
                            else:
                                lines.append(f"{label} (<b>1 {code}</b>): <b>{unit_val:,.2f} so'm</b>")
                    lines.append(f"\n📅 <i>Sana: {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>")
                    lines.append("💡 <i>Hisoblash uchun:</i> <code>/kurs 100</code>")
                    return "\n".join(lines)
        except Exception as e:
            print(f"Backup Currency API xatosi ({b_url}): {e}")

    # 4-MANBA: JsDelivr Global Currency CDN
    try:
        cdn_url = "https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/usd.json"
        r = requests.get(cdn_url, headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            usd_map = r.json().get("usd", {})
            uzs_per_usd = float(usd_map.get("uzs", 0))
            if uzs_per_usd > 1000:
                lines = ["🏦 <b>Joriy Valyuta Kurslari:</b>\n"]
                for code, label in wanted:
                    c_rate = float(usd_map.get(code.lower(), 0))
                    if c_rate > 0:
                        unit_val = uzs_per_usd / c_rate
                        uzs_val = unit_val * amount
                        lines.append(f"{label} (<b>{amount:g} {code}</b>): <b>{uzs_val:,.2f} so'm</b>")
                lines.append(f"\n📅 <i>Sana: {datetime.now().strftime('%d.%m.%Y')}</i>")
                return "\n".join(lines)
    except Exception:
        pass

    return "❌ Valyuta serveri bilan bog'lanishda xatolik. Internet aloqasini tekshirib qayta urinib ko'ring."

# ==================== PLATFORMA ANIQLAGICH VA LINK AJRATGICH ====================
def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "instagram.com" in url_lower or "instagr.am" in url_lower:
        return "Instagram"
    elif "tiktok.com" in url_lower or "douyin.com" in url_lower:
        return "TikTok"
    elif "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "YouTube"
    elif "pin.it" in url_lower or "pinterest.com" in url_lower:
        return "Pinterest"
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return "Twitter / X"
    elif "facebook.com" in url_lower or "fb.watch" in url_lower or "fb.com" in url_lower:
        return "Facebook"
    elif "likee.video" in url_lower or "likee.com" in url_lower:
        return "Likee"
    elif "threads.net" in url_lower or "threads.com" in url_lower:
        return "Threads"
    elif "reddit.com" in url_lower or "redd.it" in url_lower:
        return "Reddit"
    return "Web"

def extract_url(text: str) -> str | None:
    if not text:
        return None
    cleaned = re.sub(r'[\u200b\u200c\u200d\u200e\u200f\ufeff]', '', text)
    match = re.search(r'(https?://[^\s<>"\']+)', cleaned)
    if match:
        return match.group(1).rstrip(".,;!?)'\">]")
    match2 = re.search(
        r'((?:www\.|m\.|vt\.|vm\.)?(?:instagram\.com|instagr\.am|tiktok\.com|youtube\.com|youtu\.be|pin\.it|pinterest\.com|x\.com|twitter\.com|facebook\.com|fb\.watch)/[^\s<>"\']+)',
        cleaned, re.IGNORECASE
    )
    if match2:
        return "https://" + match2.group(1).rstrip(".,;!?)'\">]")
    return None

# ==================== FFMPEG VIDEO/AUDIO TRANZITSIYALARI ====================
def get_media_duration(file_path: str) -> float:
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        return float(res.stdout.strip())
    except Exception:
        return 30.0

def convert_to_circle_note(input_video_path: str, output_note_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-t", "59",
            "-vf", "crop='min(iw,ih)':'min(iw,ih)',scale=480:480",
            "-c:v", "libx264", "-profile:v", "baseline", "-level", "3.0",
            "-pix_fmt", "yuv420p", "-preset", "fast",
            "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-movflags", "+faststart",
            output_note_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
        return res.returncode == 0 and os.path.exists(output_note_path) and os.path.getsize(output_note_path) > 1000
    except Exception as e:
        print(f"Kruglyash xatoligi: {e}")
        return False

def extract_audio_mp3(input_video_path: str, output_mp3_path: str, title: str = "Audio", artist: str = "") -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vn", "-c:a", "libmp3lame", "-b:a", "320k",
            "-metadata", f"title={title}",
            "-metadata", f"artist={artist or 'Universal Bot'}",
            output_mp3_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return res.returncode == 0 and os.path.exists(output_mp3_path)
    except Exception as e:
        print(f"Audio ajratish xatoligi: {e}")
        return False

def convert_to_bass_boost(input_video_path: str, output_mp3_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vn", "-af", "bass=g=12:f=110:w=0.6",
            "-c:a", "libmp3lame", "-b:a", "320k",
            output_mp3_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return res.returncode == 0 and os.path.exists(output_mp3_path)
    except Exception as e:
        print(f"Bass Boost xatoligi: {e}")
        return False

def convert_to_8d_audio(input_video_path: str, output_mp3_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vn", "-af", "apulsator=hz=0.125,aecho=0.8:0.88:60:0.4",
            "-c:a", "libmp3lame", "-b:a", "320k",
            output_mp3_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return res.returncode == 0 and os.path.exists(output_mp3_path)
    except Exception as e:
        print(f"8D Audio xatoligi: {e}")
        return False

def convert_to_karaoke_minus(input_video_path: str, output_mp3_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vn", "-af", "pan=stereo|c0=c0-0.5*c1|c1=c1-0.5*c0",
            "-c:a", "libmp3lame", "-b:a", "320k",
            output_mp3_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return res.returncode == 0 and os.path.exists(output_mp3_path)
    except Exception as e:
        print(f"Karaoke xatoligi: {e}")
        return False

def convert_to_reverse_video(input_video_path: str, output_video_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-t", "45",
            "-vf", "reverse", "-af", "areverse",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac",
            output_video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        return res.returncode == 0 and os.path.exists(output_video_path)
    except Exception as e:
        print(f"Reverse xatoligi: {e}")
        return False

def extract_hd_thumbnail(input_video_path: str, output_jpg_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-ss", "00:00:01",
            "-i", input_video_path,
            "-frames:v", "1", "-q:v", "2",
            output_jpg_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
        return res.returncode == 0 and os.path.exists(output_jpg_path)
    except Exception as e:
        print(f"Thumbnail xatoligi: {e}")
        return False

def convert_to_voice_ogg(input_video_path: str, output_voice_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vn", "-c:a", "libopus", "-b:a", "64k", "-vbr", "on",
            output_voice_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return res.returncode == 0 and os.path.exists(output_voice_path)
    except Exception as e:
        print(f"Voice note xatoligi: {e}")
        return False

def convert_to_fast_speed(input_video_path: str, output_video_path: str, speed: float = 1.5) -> bool:
    try:
        pts_factor = 1.0 / speed
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vf", f"setpts={pts_factor}*PTS",
            "-af", f"atempo={speed}",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac",
            output_video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
        return res.returncode == 0 and os.path.exists(output_video_path)
    except Exception as e:
        print(f"Tezlik xatoligi: {e}")
        return False

def convert_to_gif_animation(input_video_path: str, output_gif_path: str) -> bool:
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-t", "6",
            "-vf", "scale=480:-2",
            "-c:v", "libx264", "-preset", "fast",
            "-an", "-movflags", "+faststart",
            output_gif_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)
        return res.returncode == 0 and os.path.exists(output_gif_path)
    except Exception as e:
        print(f"GIF xatoligi: {e}")
        return False

# ==================== 50 MB+ VIDEO AUTO-SPLITTER ====================
def split_large_video(input_video_path: str, target_dir: str, max_chunk_mb: float = 46.0) -> list:
    total_size_mb = os.path.getsize(input_video_path) / (1024 * 1024)
    if total_size_mb <= max_chunk_mb:
        return [input_video_path]

    duration = get_media_duration(input_video_path)
    parts_count = math.ceil(total_size_mb / max_chunk_mb)
    chunk_duration = duration / parts_count

    output_files = []
    base_name = os.path.splitext(os.path.basename(input_video_path))[0]

    current_start = 0.0
    for part_idx in range(1, parts_count + 1):
        chunk_file = os.path.join(target_dir, f"{base_name}_part{part_idx}.mp4")
        dur_to_take = min(chunk_duration, duration - current_start)

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(current_start),
            "-i", input_video_path,
            "-t", str(dur_to_take),
            "-c", "copy",
            "-avoid_negative_ts", "make_zero",
            chunk_file
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if res.returncode != 0 or not os.path.exists(chunk_file) or os.path.getsize(chunk_file) < 500:
            cmd_reencode = [
                "ffmpeg", "-y",
                "-ss", str(current_start),
                "-i", input_video_path,
                "-t", str(dur_to_take),
                "-c:v", "libx264", "-preset", "ultrafast", "-crf", "26",
                "-c:a", "aac", "-b:a", "128k",
                chunk_file
            ]
            subprocess.run(cmd_reencode, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.exists(chunk_file) and os.path.getsize(chunk_file) > 1000:
            output_files.append(chunk_file)

        current_start += dur_to_take
        if current_start >= duration:
            break

    return output_files

# ==================== VIDEO TRIMMER ====================
def parse_time_to_seconds(time_str: str):
    try:
        clean = time_str.strip()
        if ":" in clean:
            parts = [float(p) for p in clean.split(":")]
            if len(parts) == 2:
                return parts[0] * 60 + parts[1]
            elif len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
        return float(clean)
    except Exception:
        return None

def trim_video(input_video_path: str, output_path: str, start_sec: float, end_sec: float) -> bool:
    try:
        duration = end_sec - start_sec
        if duration <= 0:
            return False
        cmd = [
            "ffmpeg", "-y",
            "-ss", str(start_sec),
            "-i", input_video_path,
            "-t", str(duration),
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "aac",
            "-movflags", "+faststart",
            output_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"Trim xatoligi: {e}")
        return False

# ==================== PRO REKLAMA MONTAJ STUDIYASI + 10-BOSQICHLI ANTI-DUPLIKAT + SUZUVCHI WATERMARK ====================
WATERMARK_CONFIG_FILE = os.path.join(PROMO_DIR, "watermark_config.json")
_BOT_USERNAME_CACHE = None

def get_cached_bot_username() -> str:
    global _BOT_USERNAME_CACHE
    if _BOT_USERNAME_CACHE:
        return _BOT_USERNAME_CACHE
    try:
        me = bot.get_me()
        if me and me.username:
            _BOT_USERNAME_CACHE = me.username
            return _BOT_USERNAME_CACHE
    except Exception:
        pass
    return ADMIN_USERNAME.lstrip("@") or "usman_khasan"

def get_watermark_settings() -> dict:
    """
    Har bir videoda tepadan pastga suzib yuruvchi shaffof (prazrachniy) Telegram ikonka + @handle sozlamalari.
    Standart holatda: enabled=True, opacity=0.24 (24% ko'rinar-ko'rinmas, videoga xalaqit bermaydi).
    """
    default_cfg = {
        "enabled": True,
        "text": "",
        "opacity": 0.24
    }
    if os.path.exists(WATERMARK_CONFIG_FILE):
        try:
            with open(WATERMARK_CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    if not default_cfg.get("text"):
        default_cfg["text"] = f"@{get_cached_bot_username().upper()}"
    return default_cfg

def save_watermark_settings(enabled: bool = True, text: str = "", opacity: float = 0.24):
    clean_t = text.strip()
    if clean_t and not clean_t.startswith("@"):
        clean_t = "@" + clean_t
    cfg = {
        "enabled": bool(enabled),
        "text": clean_t.upper() if clean_t else f"@{get_cached_bot_username().upper()}",
        "opacity": max(0.12, min(0.55, float(opacity)))
    }
    try:
        with open(WATERMARK_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Watermark config saqlash xatosi: {e}")
    return cfg

# Pure-Python 5x7 Bitmap Font (agar foydalanuvchi kompyuterida Pillow o'rnatilmagan bo'lsa ham 100% ishlashi uchun!)
_BITMAP_FONT_5X7 = {
    '@': ["01110", "10001", "10111", "10101", "10111", "10000", "01110"],
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11100", "10010", "10001", "10001", "10001", "10010", "11100"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01110"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '_': ["00000", "00000", "00000", "00000", "00000", "00000", "11111"],
    '-': ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    '6': ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
}

def _point_in_poly(x: float, y: float, poly: list) -> bool:
    inside = False
    n = len(poly)
    p1x, p1y = poly[0]
    for i in range(1, n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def _generate_watermark_png_pure_python(text: str, out_png_path: str, opacity: float = 0.24) -> bool:
    """
    Agar kompyuterda Pillow (PIL) yo'q bo'lsa ham, standart Python (zlib+struct) yordamida
    Dumaloq Telegram Samolyot Ikonkasi + @HANDLE yozuvli shaffof (RGBA) PNG yaratish!
    """
    try:
        clean_text = (text or "@USMAN_KHASAN").upper().strip()
        if not clean_text.startswith("@"):
            clean_text = "@" + clean_text
        scale = 4  # 5x7 font -> 20x28 px harf
        char_w = 6 * scale
        h = 76
        w = max(260, 88 + len(clean_text) * char_w + 20)

        alpha_main = max(25, min(160, int(255 * opacity)))
        alpha_icon_bg = max(20, min(140, int(255 * (opacity * 0.85))))

        # RGBA buffer
        buf = bytearray(w * h * 4)

        cx, cy, r_outer = 40.0, 38.0, 28.0
        # Telegram paper plane uchburchaklari (cx, cy atrofida)
        plane_poly = [
            (22, 38),  # chap uch
            (54, 24),  # tepa o'ng uch
            (46, 53),  # past o'ng uch
            (36, 44),  # o'rta past
        ]
        wing_cut = [
            (34, 41),
            (52, 26),
            (38, 45),
        ]

        for py in range(h):
            row_off = py * w * 4
            for px in range(w):
                dx = px - cx
                dy = py - cy
                dist = math.hypot(dx, dy)
                if dist <= r_outer:
                    idx = row_off + px * 4
                    if _point_in_poly(px, py, plane_poly) and not _point_in_poly(px, py, wing_cut):
                        # Samolyotcha (oq-oltin tusda)
                        buf[idx] = 255
                        buf[idx + 1] = 252
                        buf[idx + 2] = 235
                        buf[idx + 3] = min(255, int(alpha_main * 1.15))
                    elif dist >= r_outer - 3.2:
                        # Aylana hoshiyasi
                        buf[idx] = 245
                        buf[idx + 1] = 225
                        buf[idx + 2] = 120
                        buf[idx + 3] = alpha_main
                    else:
                        # Aylana ichi (yarim shaffof)
                        buf[idx] = 40
                        buf[idx + 1] = 45
                        buf[idx + 2] = 55
                        buf[idx + 3] = int(alpha_icon_bg * 0.55)

        # Matnni chizish
        start_x = 80
        start_y = (h - 7 * scale) // 2
        for ch_idx, ch in enumerate(clean_text[:26]):
            glyph = _BITMAP_FONT_5X7.get(ch, _BITMAP_FONT_5X7[' '])
            gx0 = start_x + ch_idx * char_w
            for gy in range(7):
                line_bits = glyph[gy]
                for gx in range(5):
                    if line_bits[gx] == '1':
                        for sy in range(scale):
                            for sx in range(scale):
                                px = gx0 + gx * scale + sx
                                py = start_y + gy * scale + sy
                                if 0 <= px < w and 0 <= py < h:
                                    idx = (py * w + px) * 4
                                    buf[idx] = 255
                                    buf[idx + 1] = 255
                                    buf[idx + 2] = 255
                                    buf[idx + 3] = alpha_main

        # PNG fayl sifatida yig'ish (standart zlib + struct)
        raw_rows = bytearray()
        stride = w * 4
        for y in range(h):
            raw_rows.append(0)  # filter type 0
            raw_rows.extend(buf[y * stride:(y + 1) * stride])

        def _png_chunk(chunk_type: bytes, data: bytes) -> bytes:
            crc = zlib.crc32(chunk_type + data) & 0xffffffff
            return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

        ihdr = struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)
        png_bytes = (
            bytes([137, 80, 78, 71, 13, 10, 26, 10])
            + _png_chunk(b"IHDR", ihdr)
            + _png_chunk(b"IDAT", zlib.compress(bytes(raw_rows), 6))
            + _png_chunk(b"IEND", b"")
        )
        with open(out_png_path, "wb") as f:
            f.write(png_bytes)
        return os.path.exists(out_png_path) and os.path.getsize(out_png_path) > 200
    except Exception as e:
        print(f"Pure-Python PNG watermark xatosi: {e}")
        return False

def generate_telegram_watermark_png(text: str = "", out_png_path: str = "", opacity: float = 0.24) -> str | None:
    """
    Foydalanuvchi yuborgan namuna (`@TELEGRAM_YULDUZLARI`) kabi:
    Chap tomonda dumaloq Telegram qog'oz samolyot ikonkasi + O'ng tomonda qalin @USERNAME yozuvi!
    Ko'rinar-ko'rinmas (shaffof ~24% alpha) bo'lib, videoga umuman xalaqit bermaydi.
    """
    cfg = get_watermark_settings()
    wm_text = (text or cfg.get("text") or f"@{get_cached_bot_username()}").upper().strip()
    if not wm_text.startswith("@"):
        wm_text = "@" + wm_text
    use_opacity = opacity if opacity else cfg.get("opacity", 0.24)

    if not out_png_path:
        safe_tag = re.sub(r"[^A-Z0-9_]", "", wm_text) or "BOT"
        out_png_path = os.path.join(PROMO_DIR, f"wm_badge_{safe_tag}_{int(use_opacity*100)}.png")

    if os.path.exists(out_png_path) and os.path.getsize(out_png_path) > 300:
        return out_png_path

    # 1-Usul: Pillow (PIL) orqali yuqori aniqlikda anti-aliased chizish
    try:
        from PIL import Image, ImageDraw, ImageFont
        font_size = 34
        font = None
        font_candidates = [
            r"C:\Windows\Fonts\arialbd.ttf",
            r"C:\Windows\Fonts\segoeuib.ttf",
            r"C:\Windows\Fonts\calibrib.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        for fc in font_candidates:
            if os.path.exists(fc):
                try:
                    font = ImageFont.truetype(fc, font_size)
                    break
                except Exception:
                    pass
        if font is None:
            font = ImageFont.load_default()

        dummy = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
        d_dummy = ImageDraw.Draw(dummy)
        try:
            bbox = d_dummy.textbbox((0, 0), wm_text, font=font)
            tw = bbox[2] - bbox[0]
            th = bbox[3] - bbox[1]
        except Exception:
            tw = len(wm_text) * 20
            th = 30

        h = 84
        w = max(280, 96 + tw + 28)
        img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        alpha_main = max(28, min(165, int(255 * use_opacity)))
        alpha_shadow = max(16, min(110, int(255 * (use_opacity * 0.55))))
        alpha_circle_fill = max(18, min(115, int(255 * (use_opacity * 0.65))))

        # 1) Dumaloq Telegram nishoni (chapda)
        cx, cy, r = 44, 42, 30
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(30, 35, 45, alpha_circle_fill),
            outline=(250, 225, 115, alpha_main),
            width=3
        )
        # Telegram qog'oz samolyotchasi (vektor koordinatalari)
        plane_outer = [
            (25, 42),  # chap tumshuq
            (58, 27),  # tepa-o'ng qanot uchi
            (50, 57),  # past-o'ng qanot
            (39, 48),  # o'rta burilish
            (33, 53),  # dum qismi
            (34, 44),  # ichki burchak
        ]
        draw.polygon(plane_outer, fill=(255, 252, 235, min(255, int(alpha_main * 1.15))))
        # Samolyotcha o'rta chizig'i (qanot soyasi)
        draw.line([(34, 44), (56, 29)], fill=(40, 45, 55, alpha_main), width=2)

        # 2) @HANDLE matni (o'ng tomonda, yumshoq soya bilan)
        tx = 88
        ty = (h - th) // 2 - 3
        draw.text((tx + 2, ty + 2), wm_text, font=font, fill=(0, 0, 0, alpha_shadow))
        draw.text((tx, ty), wm_text, font=font, fill=(255, 255, 255, alpha_main))

        img.save(out_png_path, "PNG")
        if os.path.exists(out_png_path) and os.path.getsize(out_png_path) > 300:
            return out_png_path
    except Exception as e:
        print(f"Pillow watermark fallbackga o'tilmoqda: {e}")

    # 2-Usul: Pure-Python RGBA PNG generator (Pillow bo'lmasa ham 100% ishlaydi!)
    if _generate_watermark_png_pure_python(wm_text, out_png_path, opacity=use_opacity):
        return out_png_path
    return None

def apply_floating_watermark_to_video(input_path: str, output_path: str, custom_text: str = "") -> bool:
    """
    Har bitta videoda shaffof (prazrachniy, ko'rinar-ko'rinmas) Telegram ikonka + @HANDLE ni
    tepadan pastga silliq suzib yuradigan qilib tushirish! Videoga xalaqit bermaydi.
    """
    ensure_ffmpeg_in_path()
    cfg = get_watermark_settings()
    if not cfg.get("enabled", True) and not custom_text:
        return False

    wm_png = generate_telegram_watermark_png(text=custom_text or cfg.get("text", ""), opacity=cfg.get("opacity", 0.24))
    if not wm_png or not os.path.exists(wm_png):
        return False

    vinfo = get_video_stream_info(input_path)
    vid_w = max(360, vinfo.get("width", 720))
    # Watermark kengligi video enining ~42% qismiga moslanadi (katta ham emas, juda kichik ham emas)
    wm_target_w = max(180, min(460, int(vid_w * 0.44)))

    # Tepadan pastga silliq harakat: y = 55 + mod(t*85, H-h-110), x esa o'rtada ohista suzadi
    filter_complex = (
        f"[1:v]scale={wm_target_w}:-1[wm];"
        f"[0:v][wm]overlay="
        f"x='(W-w)/2+(W*0.14)*sin(t*0.75)':"
        f"y='55+mod(t*85,max(60,H-h-110))':"
        f"format=auto,format=yuv420p[vout]"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-i", wm_png,
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "0:a?",
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_path
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"Floating watermark xatosi: {e}")
        return False

def make_video_100_original(
    input_path: str,
    output_path: str,
    custom_watermark: str = "",
    force_9_16: bool = False
) -> tuple[bool, dict]:
    """
    🛡 10-BOSQICHLI PRO ANTI-DUPLIKAT (100% ORIGINAL VIDEO) ALGORITMI!
    Instagram Reels, TikTok va YouTube Shorts algoritmlari (pHash, dHash, MD5/SHA256,
    Audio Chromaprint, Histogram, GOP Keyframe va Metadata) videoni 100% YANGI ORIGINAL
    deb qabul qilishi va Rekomendatsiya / Topga chiqarishi uchun 10 ta qatlamli ishlov beradi:
      1) Sub-piksel Dinamik Mikro-Zoom (1.022x - 1.034x) va assimetrik kadr siljishi
      2) Burchak pHash himoyasi uchun sezilmas mikro-vignette (PI/22)
      3) Kinematik Rang Matritsasi (Contrast/Saturation/Gamma RGB mikro-siljishi)
      4) Ultra-HD Detalizatsiya (Unsharp mask — DCT koeffitsientlarini yangilaydi)
      5) Ko'zga ko'rinmas 1-bit Temporal Mikro-Grain (har bir kadrning pHash imzosini 100% yangilaydi)
      6) Tepadan-pastga suzib yuruvchi shaffof (ko'rinar-ko'rinmas) Telegram Icon + @Handle
      7) Mikro-Tezlik & PTS vaqt siljishi (0.988x yoki 1.012x)
      8) Nostandart Keyframe GOP strukturasi (-g 29 -keyint_min 15)
      9) Audio Chromaprint / Shazam-Bypass (Spectral Pitch +1.2% mikro-shift + EBU R128 -14 LUFS Loudnorm)
     10) Eski metama'lumotlarni 100% tozalash (-map_metadata -1) va yangi Apple iPhone 16 Pro Max kamerasi imzosini yozish!
    """
    ensure_ffmpeg_in_path()
    try:
        vinfo = get_video_stream_info(input_path)
        orig_w = max(360, vinfo.get("width", 720))
        orig_h = max(360, vinfo.get("height", 1280))
        target_w = 1080 if force_9_16 else (orig_w if orig_w % 2 == 0 else orig_w + 1)
        target_h = 1920 if force_9_16 else (orig_h if orig_h % 2 == 0 else orig_h + 1)

        # Randomizatsiya parametrlari (har safar 100% betakror natija chiqishi uchun!)
        zoom_factor = round(random.uniform(1.022, 1.034), 4)
        speed_factor = round(random.choice([random.uniform(0.986, 0.993), random.uniform(1.007, 1.015)]), 4)
        pts_mult = round(1.0 / speed_factor, 5)
        contrast_val = round(random.uniform(1.020, 1.032), 3)
        sat_val = round(random.uniform(1.025, 1.045), 3)
        bright_val = round(random.uniform(0.004, 0.009), 4)
        gamma_r = round(random.uniform(1.008, 1.018), 3)
        gamma_b = round(random.uniform(0.985, 0.994), 3)
        audio_pitch = round(random.uniform(1.011, 1.016), 4)
        audio_tempo = round(speed_factor / audio_pitch, 4)
        audio_tempo = max(0.5, min(2.0, audio_tempo))

        scaled_w = int(target_w * zoom_factor)
        scaled_h = int(target_h * zoom_factor)
        scaled_w = scaled_w if scaled_w % 2 == 0 else scaled_w + 1
        scaled_h = scaled_h if scaled_h % 2 == 0 else scaled_h + 1
        crop_x = max(1, (scaled_w - target_w) // 2 + random.choice([-2, -1, 1, 2]))
        crop_y = max(1, (scaled_h - target_h) // 2 + random.choice([-2, -1, 1, 2]))

        cfg = get_watermark_settings()
        wm_png = generate_telegram_watermark_png(
            text=custom_watermark or cfg.get("text", ""),
            opacity=cfg.get("opacity", 0.24)
        )
        wm_w = max(180, min(460, int(target_w * 0.44)))

        # Video filter zanjiri:
        base_v_chain = (
            f"scale={scaled_w}:{scaled_h}:flags=lanczos,"
            f"crop={target_w}:{target_h}:{crop_x}:{crop_y},"
            f"eq=contrast={contrast_val}:brightness={bright_val}:saturation={sat_val}:gamma_r={gamma_r}:gamma_b={gamma_b},"
            f"unsharp=3:3:0.35:3:3:0.0,"
            f"vignette=angle=PI/22,"
            f"noise=alls=1:allf=t,"
            f"setpts={pts_mult}*PTS,"
            f"fps=30,setsar=1"
        )

        now_iso = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        unique_id = str(uuid.uuid4()).upper()
        audio_exists = has_audio_stream(input_path)

        cmd = ["ffmpeg", "-y", "-i", input_path]
        if wm_png and os.path.exists(wm_png):
            cmd += ["-i", wm_png]
            filter_complex = (
                f"[0:v]{base_v_chain}[v_clean];"
                f"[1:v]scale={wm_w}:-1[wm];"
                f"[v_clean][wm]overlay="
                f"x='(W-w)/2+(W*0.15)*sin(t*0.8)':"
                f"y='60+mod(t*92,max(65,H-h-120))':"
                f"format=auto,format=yuv420p[vout]"
            )
            cmd += ["-filter_complex", filter_complex, "-map", "[vout]"]
        else:
            cmd += ["-vf", f"{base_v_chain},format=yuv420p", "-map", "0:v:0"]

        if audio_exists:
            af_chain = (
                f"asetrate=44100*{audio_pitch},aresample=44100,"
                f"atempo={audio_tempo},"
                f"highpass=f=22,lowpass=f=18600,"
                f"loudnorm=I=-14:TP=-1.5:LRA=11"
            )
            cmd += ["-map", "0:a:0", "-af", af_chain, "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2"]
        else:
            cmd += ["-an"]

        # 10-Bosqich: Eski metadatalarni to'liq o'chirib, yangi iPhone 16 Pro Max kamerasi metadatasini yozish
        cmd += [
            "-map_metadata", "-1",
            "-map_chapters", "-1",
            "-metadata", f"creation_time={now_iso}",
            "-metadata", "make=Apple",
            "-metadata", "model=iPhone 16 Pro Max",
            "-metadata", "software=18.2",
            "-metadata", "com.apple.quicktime.make=Apple",
            "-metadata", "com.apple.quicktime.model=iPhone 16 Pro Max",
            "-metadata", "com.apple.quicktime.software=18.2",
            "-metadata", f"comment=Original_Capture_{unique_id}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-g", "29", "-keyint_min", "15",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path
        ]

        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
        ok = res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
        return ok, {
            "zoom": f"{zoom_factor*100 - 100:.1f}%",
            "speed": f"{speed_factor:.3f}x",
            "pitch": f"+{(audio_pitch-1)*100:.1f}%",
            "device": "Apple iPhone 16 Pro Max (iOS 18.2)",
            "uuid": unique_id[:8]
        }
    except Exception as e:
        print(f"Anti-duplikat xatoligi: {e}")
        return False, {}

def has_audio_stream(file_path: str) -> bool:
    """Videoda audio oqimi bor-yo'qligini ffprobe orqali tekshirish (ovozsiz videolarda xato chiqmasligi uchun)"""
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_type",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        return "audio" in (res.stdout or "").lower()
    except Exception:
        return False

def get_saved_outro_path(user_id: int) -> str | None:
    """Foydalanuvchi yoki Admin saqlab qo'ygan reklama/outro videosini topish"""
    user_outro = os.path.join(PROMO_DIR, f"outro_{user_id}.mp4")
    if os.path.exists(user_outro) and os.path.getsize(user_outro) > 1000:
        return user_outro
    admin_outro = os.path.join(PROMO_DIR, f"outro_{ADMIN_ID}.mp4")
    if os.path.exists(admin_outro) and os.path.getsize(admin_outro) > 1000:
        return admin_outro
    default_outro = os.path.join(PROMO_DIR, "default_outro.mp4")
    if os.path.exists(default_outro) and os.path.getsize(default_outro) > 1000:
        return default_outro
    return None

def normalize_clip_for_montage(
    input_path: str,
    output_path: str,
    target_w: int = 1080,
    target_h: int = 1920,
    max_duration: float = 0.0,
    keep_audio: bool = True,
    use_blur_bg: bool = True,
    fade_out_video: bool = False,
    fade_in_video: bool = False
) -> bool:
    """
    Har qanday o'lcham, FPS va davomiylikdagi (10s, 19s, 45s, 1 daqiqa va h.k.) videoni
    Instagram Reels / TikTok 1080x1920 Full HD (30 fps, yuv420p, 44.1kHz stereo) standartiga keltirish!
    YANGILIKLAR:
      - Qora hoshiya o'rniga Xiralashtirilgan Orqa Fon (Blurred Background `boxblur=25:4`)!
      - Kinematik silliq o'tish (fade-in / fade-out) va EBU R128 (`loudnorm`) ovoz tenglashtirish!
    """
    ensure_ffmpeg_in_path()
    dur = get_media_duration(input_path)
    if dur <= 0.2:
        dur = 15.0
    use_dur = min(dur, max_duration) if (max_duration and max_duration > 0.5 and dur > max_duration) else dur
    audio_exists = has_audio_stream(input_path)
    vinfo = get_video_stream_info(input_path)
    in_w = max(100, vinfo.get("width", 720))
    in_h = max(100, vinfo.get("height", 1280))
    aspect_ratio = in_w / float(in_h)
    target_aspect = target_w / float(target_h)  # 0.5625 (9:16)

    fade_filters = []
    if fade_in_video and use_dur > 0.8:
        fade_filters.append("fade=t=in:st=0:d=0.35")
    if fade_out_video and use_dur > 0.8:
        fade_filters.append(f"fade=t=out:st={max(0.1, use_dur - 0.35):.2f}:d=0.35")
    fade_suffix = ("," + ",".join(fade_filters)) if fade_filters else ""

    # Agar video 9:16 bo'lmasa (gorizontal yoki kvadrat bo'lsa) -> Qora fon o'rniga Blurred Background!
    if use_blur_bg and abs(aspect_ratio - target_aspect) > 0.08:
        v_filter_complex = (
            f"[0:v]split=2[vbg][vfg];"
            f"[vbg]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
            f"crop={target_w}:{target_h},boxblur=24:4,eq=brightness=-0.08:saturation=1.15[bg];"
            f"[vfg]scale={target_w}:{target_h}:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30{fade_suffix},format=yuv420p[vout]"
        )
        use_complex = True
    else:
        v_filter_simple = (
            f"scale={target_w}:{target_h}:force_original_aspect_ratio=decrease,"
            f"pad={target_w}:{target_h}:(ow-iw)/2:(oh-ih)/2:black,"
            f"setsar=1,fps=30{fade_suffix},format=yuv420p"
        )
        use_complex = False

    cmd = ["ffmpeg", "-y", "-i", input_path]
    if keep_audio and not audio_exists:
        cmd += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100"]

    cmd += ["-t", f"{use_dur:.3f}"]
    if use_complex:
        cmd += ["-filter_complex", v_filter_complex, "-map", "[vout]"]
    else:
        cmd += ["-vf", v_filter_simple, "-map", "0:v:0"]

    if keep_audio and not audio_exists:
        cmd += [
            "-map", "1:a:0",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-shortest", "-movflags", "+faststart",
            output_path
        ]
    elif keep_audio and audio_exists:
        cmd += [
            "-map", "0:a:0",
            "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=44100,aformat=sample_fmts=fltp:channel_layouts=stereo",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-movflags", "+faststart",
            output_path
        ]
    else:
        cmd += [
            "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
            "-movflags", "+faststart",
            output_path
        ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
        return res.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 1000
    except Exception as e:
        print(f"Normalize clip xatoligi: {e}")
        return False

def _generate_transition_whoosh_sfx(out_wav: str, duration: float = 0.65) -> bool:
    """1-videodan 2-videoga o'tish nuqtasi uchun kinematik Sub-Bass Whoosh ovoz effekti yaratish"""
    try:
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"aevalsrc='0.32*sin(2*PI*(150-105*t/{duration:.2f})*t)*exp(-3.5*t)':s=44100:d={duration:.2f}",
            "-af", "pan=stereo|c0=c0|c1=c0,afade=t=in:st=0:d=0.06,afade=t=out:st=0.25:d=0.40",
            out_wav
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)
        return res.returncode == 0 and os.path.exists(out_wav) and os.path.getsize(out_wav) > 200
    except Exception:
        return False

def montage_two_videos(
    video1_path: str,
    video2_path: str,
    output_path: str,
    mode: str = "audio1_bridge",
    apply_anti_duplicate: bool = True
) -> tuple[bool, dict]:
    """
    2 ta har qanday uzunlikdagi (masalan: 10s, 19s, 35s, 60s+ — 1 daqiqa va undan ko'p) videoni
    7 ta Pro Studiya funksiyasi + 10-Bosqichli Anti-Duplikat + Tepadan-Pastga Suzuvchi Watermark bilan montaj qilish!

    5 Xil Smart Rejim (mode):
      1. "audio1_bridge" (🔥 Tavsiya — 1-Video Audiosi Uzluksiz 2-Videoga O'tadi, 2-Video Muted)
      2. "lcut_split" (🎬 True L-Cut — 1-Video kadri ertaroq almashib, o'zining original audiosi 2-videoda tugaydi)
      3. "pip_outro" (🖼 PiP Reklama — 1-video oxirida 2-video burchakda Picture-in-Picture chiqib, so'ng to'liq ekranga o'tadi!)
      4. "both_original" (🔊 Original Ovozlar — 1-Video o'z ovozi bilan + Whoosh Transition + 2-Video o'z ovozi bilan)
      5. "audio_ducking" (🔉 Fon Musiqa Mix — 2-Video boshlanganda 1-Video audiosi 25% fonda + 2-Video ovozi 100%)
    """
    ensure_ffmpeg_in_path()
    ts = int(time.time() * 1000) % 1000000
    norm1 = os.path.join(DOWNLOAD_DIR, f"_m_norm1_{ts}.mp4")
    norm2 = os.path.join(DOWNLOAD_DIR, f"_m_norm2_{ts}.mp4")
    concat_vid = os.path.join(DOWNLOAD_DIR, f"_m_concat_v_{ts}.mp4")
    raw_montaj = os.path.join(DOWNLOAD_DIR, f"_m_raw_out_{ts}.mp4")
    audio1_aac = os.path.join(DOWNLOAD_DIR, f"_m_aud1_{ts}.m4a")
    whoosh_wav = os.path.join(DOWNLOAD_DIR, f"_m_whoosh_{ts}.wav")
    concat_list = os.path.join(DOWNLOAD_DIR, f"_m_list_{ts}.txt")

    try:
        dur1_raw = max(get_media_duration(video1_path), 1.0)
        dur2_raw = max(get_media_duration(video2_path), 1.0)
        target_stage = raw_montaj if apply_anti_duplicate else output_path
        mode_label = ""
        final_d1 = dur1_raw
        final_d2 = dur2_raw
        total_d = dur1_raw + dur2_raw

        # ---------------- REJIM 5: PICTURE-IN-PICTURE (PiP Preview + Fullscreen Outro) ----------------
        if mode == "pip_outro":
            if not normalize_clip_for_montage(video1_path, norm1, keep_audio=False, fade_out_video=True):
                return False, {}
            if not normalize_clip_for_montage(video2_path, norm2, keep_audio=False, fade_in_video=True):
                return False, {}

            d1 = get_media_duration(norm1)
            d2 = get_media_duration(norm2)
            pip_lead = min(3.0, max(1.5, d1 * 0.25), max(1.5, d2 * 0.5))
            pip_start = max(0.5, d1 - pip_lead)

            with open(concat_list, "w", encoding="utf-8") as lf:
                lf.write(f"file '{os.path.abspath(norm1)}'\n")
                lf.write(f"file '{os.path.abspath(norm2)}'\n")

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", concat_vid
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)

            total_d = get_media_duration(concat_vid) or (d1 + d2)

            if has_audio_stream(video1_path):
                subprocess.run([
                    "ffmpeg", "-y", "-i", video1_path, "-vn",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", audio1_aac
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            else:
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-t", f"{total_d:.3f}", "-c:a", "aac", audio1_aac
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

            fade_start = max(total_d - 1.2, 0.5)
            # 1-video oxirgi soniyalarida o'ng pastki burchakda 2-videoning PiP preview oynasi chiqadi!
            pip_filter = (
                f"[1:v]scale=340:604,drawbox=x=0:y=0:w=iw:h=ih:color=gold@0.9:t=6,"
                f"setpts=PTS+{pip_start:.2f}/TB[pip];"
                f"[0:v][pip]overlay=x=W-w-36:y=H-h-190:enable='between(t,{pip_start:.2f},{d1:.2f})'[v_pip]"
            )
            cmd_pip = [
                "ffmpeg", "-y",
                "-i", concat_vid,
                "-i", norm2,
                "-stream_loop", "-1", "-i", audio1_aac,
                "-filter_complex", pip_filter,
                "-map", "[v_pip]", "-map", "2:a:0",
                "-t", f"{total_d:.3f}",
                "-af", f"afade=t=out:st={fade_start:.2f}:d=1.2",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-movflags", "+faststart",
                target_stage
            ]
            res = subprocess.run(cmd_pip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
            if res.returncode != 0 or not os.path.exists(target_stage):
                return False, {}
            final_d1, final_d2 = d1, d2
            mode_label = "🖼 PiP Reklama (Burchakda Preview + To'liq Ekran)"

        # ---------------- REJIM 3: ORIGINAL OVOZLAR (1-Video + Whoosh FX + 2-Video o'z ovozi bilan) ----------------
        elif mode == "both_original":
            if not normalize_clip_for_montage(video1_path, norm1, keep_audio=True, fade_out_video=True):
                return False, {}
            if not normalize_clip_for_montage(video2_path, norm2, keep_audio=True, fade_in_video=True):
                return False, {}

            with open(concat_list, "w", encoding="utf-8") as lf:
                lf.write(f"file '{os.path.abspath(norm1)}'\n")
                lf.write(f"file '{os.path.abspath(norm2)}'\n")

            cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", concat_list,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-movflags", "+faststart",
                target_stage
            ]
            res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=300)
            if res.returncode != 0 or not os.path.exists(target_stage):
                return False, {}
            total_d = get_media_duration(target_stage) or (dur1_raw + dur2_raw)
            mode_label = "🔊 Original Ovozlar (1+2 + Kinematik O'tish)"

        # ---------------- REJIM 2: TRUE L-CUT (1-Video tasviri ertaroq almashib, audiosi 2-video ustida tugaydi) ----------------
        elif mode == "lcut_split":
            if dur1_raw > dur2_raw + 3.0:
                v1_visual_dur = dur1_raw - dur2_raw
            else:
                v1_visual_dur = max(dur1_raw * 0.65, 2.0)

            if not normalize_clip_for_montage(video1_path, norm1, max_duration=v1_visual_dur, keep_audio=False, fade_out_video=True):
                return False, {}
            if not normalize_clip_for_montage(video2_path, norm2, keep_audio=False, fade_in_video=True):
                return False, {}

            with open(concat_list, "w", encoding="utf-8") as lf:
                lf.write(f"file '{os.path.abspath(norm1)}'\n")
                lf.write(f"file '{os.path.abspath(norm2)}'\n")

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", concat_vid
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)

            total_d = get_media_duration(concat_vid)
            if total_d <= 0.5:
                total_d = v1_visual_dur + dur2_raw

            if has_audio_stream(video1_path):
                subprocess.run([
                    "ffmpeg", "-y", "-i", video1_path, "-vn",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", audio1_aac
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            else:
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-t", f"{total_d:.3f}", "-c:a", "aac", audio1_aac
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

            fade_start = max(total_d - 1.2, 0.5)
            cmd_mux = [
                "ffmpeg", "-y",
                "-i", concat_vid,
                "-stream_loop", "-1", "-i", audio1_aac,
                "-map", "0:v:0", "-map", "1:a:0",
                "-t", f"{total_d:.3f}",
                "-af", f"afade=t=out:st={fade_start:.2f}:d=1.2",
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-movflags", "+faststart",
                target_stage
            ]
            res = subprocess.run(cmd_mux, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
            if res.returncode != 0 or not os.path.exists(target_stage):
                return False, {}
            final_d1 = v1_visual_dur
            mode_label = "🎬 L-Cut Overlap (Kadr almashib, 1-Audio davom etadi)"

        # ---------------- REJIM 4: FON MUSIQA MIX (Audio Ducking: 1-Video Audiosi 25% + 2-Video Ovozi 100%) ----------------
        elif mode == "audio_ducking":
            if not normalize_clip_for_montage(video1_path, norm1, keep_audio=True, fade_out_video=True):
                return False, {}
            if not normalize_clip_for_montage(video2_path, norm2, keep_audio=True, fade_in_video=True):
                return False, {}

            d1 = get_media_duration(norm1)
            d2 = get_media_duration(norm2)
            total_d = d1 + d2

            with open(concat_list, "w", encoding="utf-8") as lf:
                lf.write(f"file '{os.path.abspath(norm1)}'\n")
                lf.write(f"file '{os.path.abspath(norm2)}'\n")

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list,
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                "-c:a", "aac", "-b:a", "192k", concat_vid
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)

            subprocess.run([
                "ffmpeg", "-y", "-i", norm1, "-vn", "-c:a", "aac", "-b:a", "192k", audio1_aac
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

            fade_start = max(total_d - 1.2, 0.5)
            filter_complex = (
                f"[0:a]volume=1.0[a_main];"
                f"[1:a]volume=0.25,afade=t=out:st={fade_start:.2f}:d=1.2[a_bg];"
                f"[a_main][a_bg]amix=inputs=2:duration=first:dropout_transition=2[a_out]"
            )
            cmd_mix = [
                "ffmpeg", "-y",
                "-i", concat_vid,
                "-stream_loop", "-1", "-i", audio1_aac,
                "-filter_complex", filter_complex,
                "-map", "0:v:0", "-map", "[a_out]",
                "-t", f"{total_d:.3f}",
                "-c:v", "copy",
                "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                "-movflags", "+faststart",
                target_stage
            ]
            res = subprocess.run(cmd_mix, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
            if res.returncode != 0 or not os.path.exists(target_stage):
                return False, {}
            final_d1, final_d2 = d1, d2
            mode_label = "🔉 Fon Mix (1-Audio 25% fonda + 2-Video ovozi 100%)"

        # ---------------- REJIM 1 (DEFAULT): 1-VIDEO AUDIOSI UZLUKSIZ 2-VIDEOGA ULANADI (2-VIDEO MUTE) ----------------
        else:
            if not normalize_clip_for_montage(video1_path, norm1, keep_audio=False, fade_out_video=True):
                return False, {}
            if not normalize_clip_for_montage(video2_path, norm2, keep_audio=False, fade_in_video=True):
                return False, {}

            with open(concat_list, "w", encoding="utf-8") as lf:
                lf.write(f"file '{os.path.abspath(norm1)}'\n")
                lf.write(f"file '{os.path.abspath(norm2)}'\n")

            subprocess.run([
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", concat_vid
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)

            total_d = get_media_duration(concat_vid)
            if total_d <= 0.5:
                total_d = dur1_raw + dur2_raw

            if has_audio_stream(video1_path):
                subprocess.run([
                    "ffmpeg", "-y", "-i", video1_path, "-vn",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2", audio1_aac
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
            else:
                subprocess.run([
                    "ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
                    "-t", f"{total_d:.3f}", "-c:a", "aac", audio1_aac
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)

            fade_start = max(total_d - 1.2, 0.5)
            # Kinematik Whoosh Sub-Bass ovozini 1-video tugab 2-video boshlanish nuqtasiga qo'shamiz!
            delay_ms = max(100, int((dur1_raw - 0.25) * 1000))
            if _generate_transition_whoosh_sfx(whoosh_wav, 0.65):
                af_complex = (
                    f"[1:a]afade=t=out:st={fade_start:.2f}:d=1.2[a_main];"
                    f"[2:a]adelay={delay_ms}|{delay_ms},volume=0.45[a_sfx];"
                    f"[a_main][a_sfx]amix=inputs=2:duration=first:dropout_transition=1[a_final]"
                )
                cmd_bridge = [
                    "ffmpeg", "-y",
                    "-i", concat_vid,
                    "-stream_loop", "-1", "-i", audio1_aac,
                    "-i", whoosh_wav,
                    "-filter_complex", af_complex,
                    "-map", "0:v:0", "-map", "[a_final]",
                    "-t", f"{total_d:.3f}",
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                    "-movflags", "+faststart",
                    target_stage
                ]
            else:
                cmd_bridge = [
                    "ffmpeg", "-y",
                    "-i", concat_vid,
                    "-stream_loop", "-1", "-i", audio1_aac,
                    "-map", "0:v:0", "-map", "1:a:0",
                    "-t", f"{total_d:.3f}",
                    "-af", f"afade=t=out:st={fade_start:.2f}:d=1.2",
                    "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
                    "-movflags", "+faststart",
                    target_stage
                ]
            res = subprocess.run(cmd_bridge, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=240)
            if res.returncode != 0 or not os.path.exists(target_stage):
                return False, {}
            mode_label = "🔥 Audio Uzluksiz (1-Video Audiosi 2-ga Ulanadi + Transition FX)"

        # ---------------- YAKUNIY BOSQICH: 10-QATLAMLI ANTI-DUPLIKAT + TEPADAN PASTGA SUZUVCHI SHAFFOF WATERMARK ----------------
        anti_dup_info = {}
        if apply_anti_duplicate:
            ok_ad, anti_dup_info = make_video_100_original(target_stage, output_path, force_9_16=False)
            if not ok_ad or not os.path.exists(output_path):
                shutil.copyfile(target_stage, output_path)
            total_d = get_media_duration(output_path) or total_d

        return (os.path.exists(output_path) and os.path.getsize(output_path) > 1000), {
            "dur1": final_d1,
            "dur2": final_d2,
            "total": total_d,
            "mode_name": mode_label,
            "anti_dup": anti_dup_info
        }
    except Exception as e:
        print(f"Montaj xatoligi ({mode}): {e}")
        return False, {}
    finally:
        safe_remove(norm1, norm2, concat_vid, raw_montaj, audio1_aac, whoosh_wav, concat_list)


# ==================== SHAZAM / MUSIQANI ANIQLASH ====================
def identify_music_from_video(video_path: str, metadata_info: dict = None):
    if metadata_info:
        track = metadata_info.get('track') or metadata_info.get('music_title')
        artist = metadata_info.get('artist') or metadata_info.get('creator') or metadata_info.get('channel')
        album = metadata_info.get('album')
        if track and artist:
            return {"title": track, "artist": artist, "album": album or ""}

    temp_sample = f"{video_path}_sample.mp3"
    try:
        subprocess.run([
            "ffmpeg", "-y", "-ss", "5", "-t", "12",
            "-i", video_path, "-vn", "-c:a", "libmp3lame", "-b:a", "128k",
            temp_sample
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=20)

        if os.path.exists(temp_sample):
            with open(temp_sample, "rb") as af:
                files = {"file": af}
                resp = requests.post("https://api.audd.io/", files=files, data={"api_token": "test"}, timeout=15)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("status") == "success" and data.get("result"):
                        res = data["result"]
                        return {
                            "title": res.get("title", "Noma'lum qo'shiq"),
                            "artist": res.get("artist", "Noma'lum ijrochi"),
                            "album": res.get("album", "")
                        }
    except Exception as e:
        print(f"Musiqa qidirish xatosi: {e}")
    finally:
        safe_remove(temp_sample)
    return None

# ==================== AI SUBTITR VA NUTQNI MATNGA O'GIRISH ====================
def format_srt_timestamp(seconds: float) -> str:
    millis = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def _call_google_speech_single(flac_bytes: bytes, api_lang: str) -> str:
    if not flac_bytes or len(flac_bytes) < 200:
        return ""
    params = urllib.parse.urlencode({
        "client": "chromium",
        "lang": api_lang,
        "key": GOOGLE_SPEECH_KEY,
        "output": "json",
        "maxresults": "1",
        "pfilter": "0"
    })
    url = f"https://www.google.com/speech-api/v2/recognize?{params}"
    headers = {
        "Content-Type": "audio/x-flac; rate=16000",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    req = urllib.request.Request(url, data=flac_bytes, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                results = data.get("result", [])
                if results and "alternative" in results[0] and len(results[0]["alternative"]) > 0:
                    transcript = results[0]["alternative"][0].get("transcript", "").strip()
                    if transcript:
                        return transcript
    except Exception as e:
        print(f"Google Speech API ({api_lang}) xatosi: {e}")
    return ""

def recognize_google_flac(flac_bytes: bytes, lang: str = "uz-UZ") -> str:
    if lang == "auto":
        lang_order = ["uz-UZ", "ru-RU", "en-US"]
    else:
        fallbacks = [l for l in ["uz-UZ", "ru-RU", "en-US"] if l != lang]
        lang_order = [lang] + fallbacks[:1]

    for candidate_lang in lang_order:
        text = _call_google_speech_single(flac_bytes, candidate_lang)
        if text:
            return text
    return ""

def transcribe_audio_to_srt(audio_path: str, srt_path: str, lang: str = "uz-UZ") -> tuple:
    ensure_ffmpeg_in_path()
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) < 500:
        return False, ""

    total_dur = min(get_media_duration(audio_path), 360.0)
    if total_dur <= 0.5:
        total_dur = 15.0
    segments = []

    if GROQ_API_KEY:
        try:
            headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
            with open(audio_path, "rb") as af:
                files = {"file": (os.path.basename(audio_path), af, "audio/wav")}
                data = {"model": "whisper-large-v3-turbo", "response_format": "verbose_json"}
                if lang != "auto":
                    data["language"] = lang.split("-")[0]
                resp = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=headers, files=files, data=data, timeout=45)
                if resp.status_code == 200:
                    result_json = resp.json()
                    for s in result_json.get("segments", []):
                        segments.append({
                            "start": float(s.get("start", 0)),
                            "end": float(s.get("end", 0)),
                            "text": s.get("text", "").strip()
                        })
        except Exception as e:
            print(f"Groq Whisper xatoligi: {e}")

    for filter_mode in ["voice_boost", "raw"]:
        if segments:
            break
        chunk_duration = 5.0 if total_dur <= 30.0 else 7.0
        current = 0.0
        idx = 0
        while current < total_dur:
            end = min(current + chunk_duration, total_dur)
            if (end - current) < 0.6:
                break
            chunk_flac = f"{audio_path}_chk_{idx}.flac"
            cmd = ["ffmpeg", "-y", "-ss", str(current), "-t", str(end - current), "-i", audio_path]
            if filter_mode == "voice_boost":
                cmd += ["-af", "highpass=f=150,lowpass=f=3800,volume=1.8"]
            cmd += ["-ar", "16000", "-ac", "1", "-c:a", "flac", chunk_flac]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(chunk_flac):
                with open(chunk_flac, "rb") as cf:
                    flac_bytes = cf.read()
                safe_remove(chunk_flac)

                check_lang = "auto" if filter_mode == "raw" else lang
                text = recognize_google_flac(flac_bytes, lang=check_lang)
                if text:
                    segments.append({"start": current, "end": end, "text": text.strip()})
            current = end
            idx += 1

    if not segments:
        return False, ""

    full_text_list = []
    with open(srt_path, "w", encoding="utf-8") as srt_file:
        for i, seg in enumerate(segments, 1):
            s_str = format_srt_timestamp(seg["start"])
            e_str = format_srt_timestamp(seg["end"])
            txt = seg["text"]
            full_text_list.append(txt)
            srt_file.write(f"{i}\n{s_str} --> {e_str}\n{txt}\n\n")

    return True, " ".join(full_text_list)

def burn_subtitles_to_video(input_video_path: str, srt_path: str, output_video_path: str) -> bool:
    ensure_ffmpeg_in_path()
    local_temp_srt = f"_tmp_sub_{int(time.time() * 1000) % 100000}.srt"
    try:
        shutil.copyfile(srt_path, local_temp_srt)
        style = "FontSize=16,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=30"
        cmd = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vf", f"subtitles={local_temp_srt}:force_style='{style}'",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "copy", "-movflags", "+faststart",
            output_video_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        if res.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 1000:
            return True

        cmd_fallback = [
            "ffmpeg", "-y", "-i", input_video_path,
            "-vf", f"subtitles={local_temp_srt}",
            "-c:v", "libx264", "-preset", "fast",
            "-c:a", "copy", "-movflags", "+faststart",
            output_video_path
        ]
        res2 = subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180)
        return res2.returncode == 0 and os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 1000
    except Exception as e:
        print(f"Subtitr qadash xatoligi: {e}")
        return False
    finally:
        safe_remove(local_temp_srt)

# ==================== 12-BOSQICHLI XATOSIZ VIDEO-FIRST YUKLAGICH ====================
def extract_ig_shortcode(url: str) -> str | None:
    """Instagram URL dan shortcode ni aniq ajratib olish (reel, reels, p, tv, stories)"""
    m = re.search(r"instagram\.com/(?:[A-Za-z0-9_.-]+/)?(?:reel|reels|p|tv)/([A-Za-z0-9_-]+)", url, re.IGNORECASE)
    if m:
        return m.group(1)
    m2 = re.search(r"instagr\.am/(?:p|reel)/([A-Za-z0-9_-]+)", url, re.IGNORECASE)
    if m2:
        return m2.group(1)
    return None

def clean_and_resolve_url(raw_url: str) -> str:
    """
    Telefondan yuborilgan har qanday ssilkani (?cplk=..., ?obrf=..., ?igsh=..., /share/reel/..., vt.tiktok.com, pin.it)
    tozalash va asl manzilga yechish!
    """
    url = raw_url.strip().rstrip(".,;!?)'\">]")
    url = url.replace("instagram.com/reels/", "instagram.com/reel/")
    lower = url.lower()

    # 1. Qisqa mobil ssilkalarni redirect orqali ochish
    if any(k in lower for k in [
        "vt.tiktok.com", "vm.tiktok.com", "tiktok.com/t/",
        "/share/reel/", "/share/p/", "/share/v/", "instagram.com/share/",
        "pin.it/", "fb.watch/", "redd.it/", "bit.ly/", "tinyurl.com/"
    ]):
        for ua in [
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
            "curl/8.4.0",
            "TelegramBot (like TwitterBot)"
        ]:
            try:
                resp = requests.get(url, headers={"User-Agent": ua}, allow_redirects=True, stream=True, timeout=12, verify=False)
                resolved = resp.url
                resp.close()
                if resolved and resolved.startswith("http"):
                    if "accounts/login" in resolved.lower():
                        parsed_q = urllib.parse.parse_qs(urllib.parse.urlparse(resolved).query)
                        if "next" in parsed_q and parsed_q["next"]:
                            next_url = urllib.parse.unquote(parsed_q["next"][0])
                            if next_url.startswith("/"):
                                next_url = "https://www.instagram.com" + next_url
                            url = next_url
                            break
                    else:
                        url = resolved
                        break
            except Exception:
                pass

    # 2. Instagram linkidan ?cplk=..., ?obrf=..., ?igsh=..., ?utm_source=... kabi kuzatuv parametrlarini olib tashlash
    if "instagram.com" in url.lower() or "instagr.am" in url.lower():
        shortcode = extract_ig_shortcode(url)
        if shortcode:
            kind = "p" if "/p/" in url.lower() else "reel"
            url = f"https://www.instagram.com/{kind}/{shortcode}/"

    # 3. Pinterest redirect parametrlarini tozalash
    if "pinterest.com" in url.lower() and "/sent/" in url.lower():
        url = url.split("/sent/")[0] + "/"

    return url

def _download_binary_stream(file_url: str, target_path: str, referer: str = "") -> bool:
    """Berilgan to'g'ridan-to'g'ri media URL dan faylni xavfsiz yuklab olish"""
    if not file_url or not file_url.startswith("http"):
        return False
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "*/*",
    }
    if referer:
        headers["Referer"] = referer
    try:
        with requests.get(file_url, headers=headers, stream=True, timeout=45, verify=False) as r:
            if r.status_code in (200, 206):
                ctype = (r.headers.get("Content-Type") or "").lower()
                if "text/html" in ctype:
                    return False
                with open(target_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                if os.path.exists(target_path) and os.path.getsize(target_path) > 3000:
                    return True
    except Exception as e:
        print(f"Binary stream yuklash xatosi: {e}")
    safe_remove(target_path)
    return False

def _unescape_ig_text(raw_str: str) -> str:
    """Instagram HTML va contextJSON ichidagi ko'p qavatli escaped belgilarni toza holatga keltirish"""
    s = raw_str
    for _ in range(3):
        s = s.replace('\\\\"', '"').replace('\\"', '"')
        s = s.replace("\\\\/", "/").replace("\\/", "/")
        s = s.replace("\\\\u0026", "&").replace("\\u0026", "&")
        s = s.replace("\\\\u0025", "%").replace("\\u0025", "%")
        s = s.replace("\\\\u003C", "<").replace("\\u003C", "<")
    return html.unescape(s)

def _download_instagram_video_engines(url: str, user_id: int, timestamp: int) -> tuple[list, str, bool]:
    """
    Instagram VIDEO-FIRST 6-Bosqichli Maxsus Yuklagich!
    Qaytaradi: (fayllar_royxati, sarlavha, is_definitely_video)
    MUHIM: Agar post video bo'lsa, HECH QACHON oblojka rasmni (.jpg) video o'rniga yubormaydi!
    """
    shortcode = extract_ig_shortcode(url)
    target_mp4 = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_00001.mp4")

    if not shortcode:
        return [], "", False

    is_definitely_video = ("/reel/" in url.lower() or "/reels/" in url.lower() or "/tv/" in url.lower())
    embed_bodies = []

    # ---------------- 1-MOTOR: Deep Unescaped Embed Captioned Video Extractor ----------------
    embed_urls = [
        f"https://www.instagram.com/reel/{shortcode}/embed/captioned/",
        f"https://www.instagram.com/p/{shortcode}/embed/captioned/",
        f"https://www.instagram.com/p/{shortcode}/embed/",
    ]
    embed_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    for emb_url in embed_urls:
        try:
            er = requests.get(emb_url, headers=embed_headers, timeout=14, verify=False)
            if er.status_code == 200 and er.text:
                raw_body = er.text
                embed_bodies.append(raw_body)
                clean_body = _unescape_ig_text(raw_body)

                # Post video ekanligini bildiruvchi belgilar (hatto video_url yashirilgan bo'lsa ham!):
                if any(ind in clean_body for ind in [
                    '"is_video":true', '"is_video": true',
                    'EmbeddedMediaVideo', 'WatchOnInstagram', 'Watch on Instagram',
                    'glyphsSpritePlay', 'video_versions', '"media_type":2'
                ]):
                    is_definitely_video = True

                # Tozalangan HTML/JSON ichidan barcha video URL larni qidirish
                vid_patterns = [
                    r'"video_url"\s*:\s*"(https?://[^"]+)"',
                    r'"contentUrl"\s*:\s*"(https?://[^"]+)"',
                    r'"video_versions"\s*:\s*\[\s*\{[^}]*"url"\s*:\s*"(https?://[^"]+)"',
                    r'<video[^>]+src="(https?://[^"]+)"',
                    r'property="og:video(?::secure_url)?"\s+content="(https?://[^"]+)"',
                ]
                for pat in vid_patterns:
                    for vurl in re.findall(pat, clean_body):
                        vurl_clean = _unescape_ig_text(vurl)
                        if vurl_clean.startswith("http") and any(k in vurl_clean for k in [".mp4", "cdninstagram", "fbcdn.net"]):
                            if _download_binary_stream(vurl_clean, target_mp4, referer="https://www.instagram.com/"):
                                print(f"[OK] Instagram 1-Motor (Unescaped Embed Video) orqali yuklandi: {shortcode}")
                                return [target_mp4], f"Instagram Video ({shortcode})", True
        except Exception as e:
            print(f"IG 1-Motor xatosi ({emb_url}): {e}")

    # ---------------- 2-MOTOR: Live-Session GraphQL API (Avto-LSD + CSRF token bilan) ----------------
    try:
        sess = requests.Session()
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        lsd_token = "AVqbxe3J_YA"
        csrf_token = "missing"

        # Jonli LSD va cookie olish
        try:
            init_r = sess.get(f"https://www.instagram.com/reel/{shortcode}/", headers={"User-Agent": ua}, timeout=12, verify=False)
            if init_r.status_code == 200 and init_r.text:
                m_lsd = re.search(r'"LSD",\s*\[\],\s*\{\s*"token"\s*:\s*"([^"]+)"', init_r.text) or re.search(r'"lsd"\s*:\s*"([^"]+)"', init_r.text)
                if m_lsd:
                    lsd_token = m_lsd.group(1)
                # Shu sahifaning o'zida video_versions bor-yo'qligini ham tekshiramiz!
                clean_init = _unescape_ig_text(init_r.text)
                if '"is_video":true' in clean_init or '"media_type":2' in clean_init:
                    is_definitely_video = True
                for vurl in re.findall(r'"video_versions"\s*:\s*\[\s*\{[^}]*"url"\s*:\s*"(https?://[^"]+)"', clean_init) + re.findall(r'"video_url"\s*:\s*"(https?://[^"]+)"', clean_init):
                    if _download_binary_stream(_unescape_ig_text(vurl), target_mp4, referer="https://www.instagram.com/"):
                        print(f"[OK] Instagram 2A-Motor (Direct Page JSON) orqali yuklandi: {shortcode}")
                        return [target_mp4], f"Instagram Video ({shortcode})", True
            csrf_token = sess.cookies.get("csrftoken") or "missing"
        except Exception:
            pass

        gql_headers = {
            "User-Agent": ua,
            "Content-Type": "application/x-www-form-urlencoded",
            "X-IG-App-ID": "936619743392459",
            "X-FB-LSD": lsd_token,
            "X-CSRFToken": csrf_token,
            "X-ASBD-ID": "129477",
            "X-IG-WWW-Claim": "0",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.instagram.com",
            "Referer": f"https://www.instagram.com/reel/{shortcode}/",
            "Sec-Fetch-Site": "same-origin",
        }
        graphql_doc_ids = ["8845758582119845", "7341532402634560", "10015901848480474", "25811509981800768", "7153035638091937"]
        for doc_id in graphql_doc_ids:
            try:
                payload = {
                    "av": "0",
                    "__d": "www",
                    "__user": "0",
                    "__a": "1",
                    "__req": "1",
                    "dpr": "1",
                    "__ccg": "EXCELLENT",
                    "lsd": lsd_token,
                    "fb_api_caller_class": "RelayModern",
                    "fb_api_req_friendly_name": "PolarisPostActionLoadPostQueryQuery",
                    "variables": json.dumps({
                        "shortcode": shortcode,
                        "fetch_comment_count": 0,
                        "fetch_related_profile_media_count": 0,
                        "parent_comment_count": 0,
                        "child_comment_count": 0,
                        "fetch_like_count": 10,
                        "fetch_tagged_user_count": None,
                        "fetch_preview_comment_count": 2,
                        "has_threaded_comments": True,
                        "hoisted_comment_id": None,
                        "hoisted_reply_id": None,
                    }),
                    "server_timestamps": "true",
                    "doc_id": doc_id,
                }
                for gql_endpoint in ["https://www.instagram.com/api/graphql", "https://www.instagram.com/graphql/query"]:
                    gr = sess.post(gql_endpoint, headers=gql_headers, data=payload, timeout=12, verify=False)
                    if gr.status_code == 200 and gr.text:
                        clean_json_str = gr.text.lstrip("for (;;);").strip()
                        gdata = json.loads(clean_json_str)
                        media = (
                            gdata.get("data", {}).get("xdt_shortcode_media")
                            or gdata.get("data", {}).get("shortcode_media")
                            or gdata.get("graphql", {}).get("shortcode_media")
                        )
                        if not media:
                            continue

                        if media.get("is_video") or media.get("video_url") or media.get("video_versions"):
                            is_definitely_video = True

                        caption_edges = media.get("edge_media_to_caption", {}).get("edges", [])
                        title = caption_edges[0]["node"]["text"][:80] if caption_edges else f"Instagram ({shortcode})"

                        # Karusel (Sidecar) bo'lsa
                        sidecar = media.get("edge_sidecar_to_children", {}).get("edges", []) or media.get("carousel_media", [])
                        if sidecar:
                            collected = []
                            for idx, item in enumerate(sidecar[:10], 1):
                                node = item.get("node", item) if isinstance(item, dict) else {}
                                vurl_node = node.get("video_url") or (node.get("video_versions", [{}])[0].get("url") if node.get("video_versions") else None)
                                if node.get("is_video") or vurl_node:
                                    fp = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_{idx:05d}.mp4")
                                    if vurl_node and _download_binary_stream(vurl_node, fp, referer="https://www.instagram.com/"):
                                        collected.append(fp)
                                else:
                                    durl_node = node.get("display_url") or (node.get("image_versions2", {}).get("candidates", [{}])[0].get("url"))
                                    fp = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_{idx:05d}.jpg")
                                    if durl_node and _download_binary_stream(durl_node, fp, referer="https://www.instagram.com/"):
                                        collected.append(fp)
                            if collected:
                                print(f"[OK] Instagram 2-Motor (GraphQL Karusel) orqali yuklandi: {shortcode}")
                                return collected, title, is_definitely_video

                        # Bitta video bo'lsa
                        vurl = media.get("video_url") or (media.get("video_versions", [{}])[0].get("url") if media.get("video_versions") else None)
                        if vurl and _download_binary_stream(vurl, target_mp4, referer="https://www.instagram.com/"):
                            print(f"[OK] Instagram 2-Motor (GraphQL Video) orqali yuklandi: {shortcode}")
                            return [target_mp4], title, True

                        # Agar GraphQL aniq is_video == False desa (haqiqiy bitta rasm post bo'lsa):
                        if media.get("is_video") is False and not sidecar:
                            durl = media.get("display_url")
                            target_jpg = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_00001.jpg")
                            if durl and _download_binary_stream(durl, target_jpg, referer="https://www.instagram.com/"):
                                print(f"[OK] Instagram 2-Motor (Confirmed Photo Post) orqali yuklandi: {shortcode}")
                                return [target_jpg], title, False
            except Exception:
                pass
    except Exception as e:
        print(f"IG 2-Motor session xatosi: {e}")

    # ---------------- 3-MOTOR: Multi-Proxy OpenGraph Video Scrapers ----------------
    proxy_domains = [
        "https://kkinstagram.com",
        "https://www.vxinstagram.com",
        "https://eeinstagram.com",
        "https://www.ddinstagram.com",
        "https://instagramez.com",
    ]
    bot_uas = [
        "TelegramBot (like TwitterBot)",
        "Mozilla/5.0 (compatible; Discordbot/2.0; +https://discordapp.com)",
        "Twitterbot/1.0"
    ]
    for domain in proxy_domains:
        for bua in bot_uas:
            try:
                purl = f"{domain}/reel/{shortcode}"
                pr = requests.get(purl, headers={"User-Agent": bua}, timeout=12, allow_redirects=True, verify=False)
                if pr.status_code == 200:
                    ctype = (pr.headers.get("Content-Type") or "").lower()
                    if "video/" in ctype and len(pr.content) > 10000:
                        with open(target_mp4, "wb") as f:
                            f.write(pr.content)
                        print(f"[OK] Instagram 3-Motor ({domain} direct stream) orqali yuklandi: {shortcode}")
                        return [target_mp4], f"Instagram Video ({shortcode})", True

                    html_text = _unescape_ig_text(pr.text)
                    og_matches = (
                        re.findall(r'(?:property="og:video(?::secure_url|:url)?"|name="twitter:player:stream")\s+content="([^"]+)"', html_text)
                        + re.findall(r'content="([^"]+)"\s+(?:property="og:video(?::secure_url|:url)?"|name="twitter:player:stream")', html_text)
                    )
                    for og_url in og_matches:
                        clean_og = _unescape_ig_text(og_url)
                        if clean_og.startswith("/"):
                            clean_og = domain + clean_og
                        if _download_binary_stream(clean_og, target_mp4, referer=domain):
                            print(f"[OK] Instagram 3-Motor ({domain} og:video) orqali yuklandi: {shortcode}")
                            return [target_mp4], f"Instagram Video ({shortcode})", True
            except Exception:
                pass

    # ---------------- 4-MOTOR: External IG Video Downloader APIs (RyzenDesu / VKR / SaveIG) ----------------
    ig_page_url = f"https://www.instagram.com/reel/{shortcode}/"
    external_apis = [
        f"https://api.ryzendesu.vip/api/downloader/igdl?url={urllib.parse.quote(ig_page_url)}",
        f"https://vkrdownloader.xyz/server?vkr={urllib.parse.quote(ig_page_url)}",
    ]
    for api_u in external_apis:
        try:
            ar = requests.get(api_u, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, verify=False)
            if ar.status_code == 200 and ar.text:
                clean_api = _unescape_ig_text(ar.text)
                mp4_urls = re.findall(r'(https?://[^\s"\'<>\\]+(?:\.mp4|cdninstagram\.com|fbcdn\.net)[^\s"\'<>\\]*)', clean_api)
                for m_url in mp4_urls:
                    if any(bad in m_url.lower() for bad in [".jpg", ".png", ".webp", "t51.2885-15"]):
                        continue
                    if _download_binary_stream(m_url, target_mp4, referer="https://www.instagram.com/"):
                        print(f"[OK] Instagram 4-Motor (External API) orqali yuklandi: {shortcode}")
                        return [target_mp4], f"Instagram Video ({shortcode})", True
        except Exception:
            pass

    return [], "", is_definitely_video

def _download_instagram_photo_if_not_video(shortcode: str, user_id: int, timestamp: int, is_definitely_video: bool) -> tuple[list, str]:
    """
    FAQAT barcha video motorlar va yt-dlp tekshirilgandan keyin,
    agar post VIDEO EMASLIGI aniq bo'lsa (haqiqiy rasm post bo'lsa), rasmni yuklaydi!
    """
    if is_definitely_video or not shortcode:
        return [], ""

    target_jpg = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_00001.jpg")
    embed_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    }
    try:
        er = requests.get(f"https://www.instagram.com/p/{shortcode}/embed/captioned/", headers=embed_headers, timeout=12, verify=False)
        if er.status_code == 200 and er.text:
            clean_body = _unescape_ig_text(er.text)
            # Agar sahifada video belgisi bo'lsa, rasm yuklamaymiz!
            if any(ind in clean_body for ind in [
                '"is_video":true', '"is_video": true',
                'EmbeddedMediaVideo', 'WatchOnInstagram', 'Watch on Instagram',
                'glyphsSpritePlay', 'video_versions', '"media_type":2'
            ]):
                return [], ""

            img_m = re.findall(r'class="EmbeddedMediaImage"[^>]+src="([^"]+)"', clean_body) or re.findall(r'"display_url"\s*:\s*"(https?://[^"]+)"', clean_body)
            for im in img_m:
                iurl = _unescape_ig_text(im)
                if _download_binary_stream(iurl, target_jpg, referer="https://www.instagram.com/"):
                    print(f"[OK] Instagram Haqiqiy Rasm Post yuklandi: {shortcode}")
                    return [target_jpg], f"Instagram Post ({shortcode})"
    except Exception:
        pass
    return [], ""

def _download_tiktok_multi_engine(url: str, user_id: int, timestamp: int) -> tuple[list, str]:
    """TikTok uchun 3-Bosqichli Suv Belgisiz HD Yuklagich (Video + Slayd-shou rasmlar)"""
    target_mp4 = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_00001.mp4")

    # 1-Motor: TikWM API (HD No-Watermark + Slideshow Images)
    try:
        resp = requests.post(
            "https://www.tikwm.com/api/",
            data={"url": url, "hd": 1},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=20,
            verify=False
        )
        if resp.status_code == 200:
            j = resp.json()
            if j.get("code") == 0 and j.get("data"):
                d = j["data"]
                title = d.get("title") or "TikTok Video"
                images = d.get("images")
                if images and isinstance(images, list):
                    collected = []
                    for idx, img_url in enumerate(images[:10], 1):
                        fp = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_{idx:05d}.jpg")
                        if _download_binary_stream(img_url, fp):
                            collected.append(fp)
                    if collected:
                        print("[OK] TikTok TikWM Karusel orqali yuklandi")
                        return collected, title

                play_url = d.get("hdplay") or d.get("play") or d.get("wmplay")
                if play_url:
                    if play_url.startswith("/"):
                        play_url = "https://www.tikwm.com" + play_url
                    if _download_binary_stream(play_url, target_mp4, referer="https://www.tikwm.com/"):
                        print("[OK] TikTok TikWM HD orqali yuklandi")
                        return [target_mp4], title
    except Exception as e:
        print(f"TikWM xatosi: {e}")

    # 2-Motor: vxTikTok / tnktok Proxy OpenGraph
    parsed = urllib.parse.urlparse(url)
    for tk_domain in ["https://www.vxtiktok.com", "https://tnktok.com"]:
        try:
            tk_url = f"{tk_domain}{parsed.path}"
            r = requests.get(tk_url, headers={"User-Agent": "TelegramBot (like TwitterBot)"}, timeout=15, verify=False)
            if r.status_code == 200:
                m = re.search(r'property="og:video(?::secure_url)?"\s+content="([^"]+)"', r.text)
                if m:
                    vurl = _unescape_ig_text(m.group(1))
                    if _download_binary_stream(vurl, target_mp4):
                        print(f"[OK] TikTok {tk_domain} orqali yuklandi")
                        return [target_mp4], "TikTok Video"
        except Exception:
            pass

    return [], ""

def _download_twitter_fallback(url: str, user_id: int, timestamp: int) -> tuple[list, str]:
    """Twitter / X uchun vxTwitter JSON API zaxirasi"""
    m = re.search(r"(?:twitter\.com|x\.com)/([^/]+)/status/(\d+)", url, re.IGNORECASE)
    if not m:
        return [], ""
    user_handle, status_id = m.group(1), m.group(2)
    try:
        api_url = f"https://api.vxtwitter.com/{user_handle}/status/{status_id}"
        r = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15, verify=False)
        if r.status_code == 200:
            data = r.json()
            title = data.get("text") or "X / Twitter Video"
            media_list = data.get("media_extended", [])
            collected = []
            for idx, mitem in enumerate(media_list[:10], 1):
                murl = mitem.get("url")
                mtype = mitem.get("type", "video")
                ext = "mp4" if mtype in ("video", "gif") else "jpg"
                fp = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_{idx:05d}.{ext}")
                if murl and _download_binary_stream(murl, fp):
                    collected.append(fp)
            if collected:
                print("[OK] Twitter/X vxTwitter API orqali yuklandi")
                return collected, title
    except Exception as e:
        print(f"vxTwitter xatosi: {e}")
    return [], ""

def _download_pinterest_fallback(url: str, user_id: int, timestamp: int) -> tuple[list, str]:
    """Pinterest uchun to'g'ridan-to'g'ri pinimg.com video/rasm qidiruv zaxirasi"""
    target_mp4 = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_00001.mp4")
    target_jpg = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_00001.jpg")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
        }
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        if r.status_code == 200 and r.text:
            mp4_matches = re.findall(r'(https://v\d*\.pinimg\.com/videos/[^\s"\\]+\.mp4)', r.text)
            for vurl in mp4_matches:
                clean_v = _unescape_ig_text(vurl)
                if _download_binary_stream(clean_v, target_mp4):
                    print("[OK] Pinterest direct MP4 yuklandi")
                    return [target_mp4], "Pinterest Video"
            img_matches = re.findall(r'(https://i\.pinimg\.com/originals/[^\s"\\]+\.(?:jpg|png|webp))', r.text)
            for iurl in img_matches:
                clean_i = _unescape_ig_text(iurl)
                if _download_binary_stream(clean_i, target_jpg):
                    print("[OK] Pinterest direct Image yuklandi")
                    return [target_jpg], "Pinterest Image"
    except Exception as e:
        print(f"Pinterest fallback xatosi: {e}")
    return [], ""

def get_video_stream_info(file_path: str) -> dict:
    """ffprobe yordamida video kodek, o'lcham (width, height) va davomiylikni aniqlash"""
    ensure_ffmpeg_in_path()
    info = {"codec": "h264", "width": 720, "height": 1280, "duration": 15}
    try:
        cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,width,height:format=duration",
            "-of", "json",
            file_path
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=15)
        if res.returncode == 0 and res.stdout.strip():
            data = json.loads(res.stdout)
            streams = data.get("streams", [])
            if streams:
                st = streams[0]
                info["codec"] = (st.get("codec_name") or "h264").lower()
                info["width"] = int(st.get("width") or 720)
                info["height"] = int(st.get("height") or 1280)
            fmt = data.get("format", {})
            if fmt.get("duration"):
                info["duration"] = max(1, int(float(fmt["duration"])))
    except Exception:
        pass
    return info

def ensure_phone_playable_mp4(input_path: str, force_reencode: bool = False, apply_watermark: bool = True) -> tuple[str, dict]:
    """
    Telefonda (iPhone va Android) bittada ochiladigan H.264 (yuv420p) + faststart MP4 ga keltirish
    HAMDA har bitta videoga tepadan-pastga suzib yuruvchi ko'rinar-ko'rinmas (prazrachniy)
    Telegram ikonka + @handle watermark tushirish!
    """
    ensure_ffmpeg_in_path()
    vinfo = get_video_stream_info(input_path)
    ext = os.path.splitext(input_path)[1].lower()
    codec = vinfo.get("codec", "h264")
    cfg = get_watermark_settings()
    already_watermarked = os.path.basename(input_path).startswith(("reklama_reel_", "orig_"))

    if apply_watermark and cfg.get("enabled", True) and not already_watermarked:
        wm_out = os.path.splitext(input_path)[0] + "_wm.mp4"
        if apply_floating_watermark_to_video(input_path, wm_out):
            safe_remove(input_path)
            vinfo = get_video_stream_info(wm_out)
            return wm_out, vinfo

    if force_reencode or codec not in ("h264", "avc1") or ext != ".mp4":
        fixed_path = os.path.splitext(input_path)[0] + "_phone.mp4"
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            "-c:a", "aac", "-b:a", "128k",
            "-movflags", "+faststart",
            fixed_path
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=150)
            if res.returncode == 0 and os.path.exists(fixed_path) and os.path.getsize(fixed_path) > 1000:
                safe_remove(input_path)
                vinfo = get_video_stream_info(fixed_path)
                return fixed_path, vinfo
        except Exception:
            safe_remove(fixed_path)
    return input_path, vinfo

def download_media_bulletproof(raw_url: str, user_id: int, timestamp: int) -> tuple[list, str]:
    """
    12-Bosqichli VIDEO-FIRST Media Yuklagich:
    1) Mobil qisqa link va tracking parametrlarni (?cplk=, ?obrf=, ?igsh=, vt.tiktok, pin.it) tozalaydi.
    2) Instagram uchun avval VIDEO motorlarini (Unescaped Embed Video + Live-LSD GraphQL + Proxy Video + API) ishga tushiradi.
    3) Agar ular topolmasa, yt-dlp ni (/reel/ va /p/ variantlarda) ishlatadi.
    4) FAQAT video emasligi 100% tasdiqlangandagina rasm post (.jpg) sifatida yuklaydi!
    """
    ensure_ffmpeg_in_path()
    url = clean_and_resolve_url(raw_url)
    lower_url = url.lower()
    out_template = os.path.join(DOWNLOAD_DIR, f"{user_id}_{timestamp}_%(autonumber)s.%(ext)s")

    def _collect_files():
        return sorted([
            os.path.join(DOWNLOAD_DIR, fname)
            for fname in os.listdir(DOWNLOAD_DIR)
            if fname.startswith(f"{user_id}_{timestamp}_")
            and not fname.endswith(".part")
            and not fname.endswith(".ytdl")
            and os.path.getsize(os.path.join(DOWNLOAD_DIR, fname)) > 1000
        ])

    ig_shortcode = extract_ig_shortcode(url) if ("instagram.com" in lower_url or "instagr.am" in lower_url) else None
    is_definitely_video = False

    # A) INSTAGRAM MAXSUS VIDEO MOTORLARI (Video-First!)
    if ig_shortcode:
        ig_files, ig_title, is_definitely_video = _download_instagram_video_engines(url, user_id, timestamp)
        if ig_files:
            return ig_files, ig_title

    # B) TIKTOK MAXSUS HD MOTORI
    if "tiktok.com" in lower_url:
        tk_files, tk_title = _download_tiktok_multi_engine(url, user_id, timestamp)
        if tk_files:
            return tk_files, tk_title

    # C) YT-DLP UNIVERSAL VIDEO YUKLAGICH (Instagram uchun ham /reel/, ham /p/ URL ni sinaydi!)
    format_candidates = [
        "best[ext=mp4][vcodec^=avc1]/bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "bestvideo+bestaudio/best"
    ]
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1"
    ]

    urls_to_try = [url]
    if ig_shortcode:
        reel_variant = f"https://www.instagram.com/reel/{ig_shortcode}/"
        post_variant = f"https://www.instagram.com/p/{ig_shortcode}/"
        urls_to_try = [reel_variant, post_variant]

    title = "Video"
    for candidate_u in urls_to_try:
        for attempt_idx in range(2):
            ydl_opts = {
                "outtmpl": out_template,
                "format": format_candidates[attempt_idx],
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "nocheckcertificate": True,
                "geo_bypass": True,
                "retries": 4,
                "fragment_retries": 4,
                "extractor_retries": 3,
                "socket_timeout": 30,
                "extractor_args": {
                    "youtube": {"player_client": ["android", "ios", "web"]}
                },
                "http_headers": {
                    "User-Agent": user_agents[attempt_idx],
                    "Accept-Language": "en-US,en;q=0.9,ru;q=0.8,uz;q=0.7"
                }
            }
            if FFMPEG_DIR:
                ydl_opts["ffmpeg_location"] = FFMPEG_DIR
            if os.path.exists("cookies.txt"):
                ydl_opts["cookiefile"] = "cookies.txt"

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(candidate_u, download=True)
                    if info:
                        title = info.get("title") or info.get("description") or "Video"
                files = _collect_files()
                if files:
                    print(f"[OK] yt-dlp orqali yuklandi: {candidate_u}")
                    return files, str(title).strip() or "Video"
            except Exception as e:
                print(f"yt-dlp urinish xatosi ({candidate_u}): {e}")

    # D) QO'SHIMCHA PLATFORM ZAXIRALARI (Twitter/X, Pinterest, va Instagram Haqiqiy Rasm Post)
    if "twitter.com" in lower_url or "x.com" in lower_url:
        tw_files, tw_title = _download_twitter_fallback(url, user_id, timestamp)
        if tw_files:
            return tw_files, tw_title

    if "pinterest.com" in lower_url or "pin.it" in lower_url:
        pin_files, pin_title = _download_pinterest_fallback(url, user_id, timestamp)
        if pin_files:
            return pin_files, pin_title

    # E) AGAR INSTAGRAM POST HAQIQATDAN RASM BO'LSA (video emasligi tasdiqlangan bo'lsa):
    if ig_shortcode:
        photo_files, photo_title = _download_instagram_photo_if_not_video(ig_shortcode, user_id, timestamp, is_definitely_video)
        if photo_files:
            return photo_files, photo_title

    return _collect_files(), title

def ensure_video_from_telegram(message_obj: types.Message, local_video_path: str) -> bool:
    """Agar video xotiradan avto-o'chirilgan bo'lsa, Telegram serveridan (file_id orqali) soniyada qayta tiklash"""
    if os.path.exists(local_video_path) and os.path.getsize(local_video_path) > 500:
        return True
    if not message_obj:
        return False
    media_obj = message_obj.video or message_obj.audio or message_obj.voice or message_obj.video_note or message_obj.document
    if not media_obj and message_obj.reply_to_message:
        r = message_obj.reply_to_message
        media_obj = r.video or r.audio or r.voice or r.video_note or r.document
    if not media_obj:
        return False
    try:
        file_info = bot.get_file(media_obj.file_id)
        downloaded_bytes = bot.download_file(file_info.file_path)
        with open(local_video_path, "wb") as f:
            f.write(downloaded_bytes)
        return os.path.exists(local_video_path) and os.path.getsize(local_video_path) > 500
    except Exception as e:
        print(f"Telegram file_id dan qayta yuklash xatosi: {e}")
        return False

# ==================== TUGMALARNI SHAKLLANTIRISH ====================
def make_video_action_keyboard(base_fname: str, lang: str = "uz") -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    labels = {
        "uz": {
            "sub_vid": "🎬 Subtitrli video", "sub_txt": "📝 Subtitr matni (.srt)",
            "circle": "🔵 Kruglyash", "audio": "🎧 MP3 Audio",
            "bass": "🔊 Bass Boost", "audio8d": "🎧 8D Audio",
            "karaoke": "🎤 Karaoke Minus", "thumb": "🖼 HD Oblojka",
            "voice": "🎙 Ovozli xabar", "trim": "✂️ Qirqish (Trim)",
            "shazam": "🎵 Musiqani topish", "speed": "⚡ 1.5x Tezlik",
            "reverse": "⏪ Teskari video", "gif": "🎞 GIF qilish"
        },
        "ru": {
            "sub_vid": "🎬 С субтитрами", "sub_txt": "📝 Текст (.srt)",
            "circle": "🔵 Кругляш", "audio": "🎧 MP3 Аудио",
            "bass": "🔊 Bass Boost", "audio8d": "🎧 8D Аудио",
            "karaoke": "🎤 Караоке Минус", "thumb": "🖼 HD Обложка",
            "voice": "🎙 Голосовое", "trim": "✂️ Обрезать (Trim)",
            "shazam": "🎵 Найти музыку", "speed": "⚡ 1.5x Скорость",
            "reverse": "⏪ Реверс видео", "gif": "🎞 В GIF"
        },
        "en": {
            "sub_vid": "🎬 Subtitled Video", "sub_txt": "📝 Subtitle (.srt)",
            "circle": "🔵 Video Note", "audio": "🎧 MP3 Audio",
            "bass": "🔊 Bass Boost", "audio8d": "🎧 8D Audio",
            "karaoke": "🎤 Karaoke Minus", "thumb": "🖼 HD Thumbnail",
            "voice": "🎙 Voice Note", "trim": "✂️ Trim Video",
            "shazam": "🎵 Identify Music", "speed": "⚡ 1.5x Speed",
            "reverse": "⏪ Reverse Video", "gif": "🎞 To GIF"
        }
    }
    lbl = labels.get(lang, labels["uz"])

    markup.add(
        types.InlineKeyboardButton(lbl["sub_vid"], callback_data=f"sub_vid:{base_fname}"),
        types.InlineKeyboardButton(lbl["sub_txt"], callback_data=f"sub_txt:{base_fname}")
    )
    markup.add(
        types.InlineKeyboardButton(lbl["circle"], callback_data=f"circle:{base_fname}"),
        types.InlineKeyboardButton(lbl["audio"], callback_data=f"audio:{base_fname}"),
    )
    markup.add(
        types.InlineKeyboardButton(lbl["bass"], callback_data=f"bass:{base_fname}"),
        types.InlineKeyboardButton(lbl["audio8d"], callback_data=f"audio8d:{base_fname}")
    )
    markup.add(
        types.InlineKeyboardButton(lbl["karaoke"], callback_data=f"karaoke:{base_fname}"),
        types.InlineKeyboardButton(lbl["thumb"], callback_data=f"thumb:{base_fname}")
    )
    markup.add(
        types.InlineKeyboardButton(lbl["voice"], callback_data=f"voice:{base_fname}"),
        types.InlineKeyboardButton(lbl["trim"], callback_data=f"trim:{base_fname}")
    )
    markup.add(
        types.InlineKeyboardButton(lbl["shazam"], callback_data=f"shazam:{base_fname}"),
        types.InlineKeyboardButton(lbl["speed"], callback_data=f"speed:{base_fname}")
    )
    markup.add(
        types.InlineKeyboardButton(lbl["reverse"], callback_data=f"reverse:{base_fname}"),
        types.InlineKeyboardButton(lbl["gif"], callback_data=f"gif:{base_fname}")
    )
    antidup_lbl = {
        "uz": "🛡 Anti-Duplikat (100% Original — Top/Rekomendatsiya)",
        "ru": "🛡 Анти-Дубликат (100% Оригинал для Reels/TikTok)",
        "en": "🛡 Anti-Duplicate (100% Original for Reels/TikTok)"
    }.get(lang, "🛡 Anti-Duplikat (100% Original — Top/Rekomendatsiya)")
    montaj_lbl = {
        "uz": "🎯 Pro Reklama Montaj (2-Video / Outro Ulash)",
        "ru": "🎯 Про Видео Монтаж (Склеить с Outro / 2-м видео)",
        "en": "🎯 Pro Promo Montage (Merge with Outro / 2nd Video)"
    }.get(lang, "🎯 Pro Reklama Montaj (2-Video / Outro Ulash)")
    markup.add(types.InlineKeyboardButton(antidup_lbl, callback_data=f"antidup_vid:{base_fname}"))
    markup.add(types.InlineKeyboardButton(montaj_lbl, callback_data=f"montaj_from_vid:{base_fname}"))
    return markup

def make_sub_lang_keyboard(action_type: str, base_fname: str) -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    b_uz = types.InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data=f"{action_type}:uz-UZ:{base_fname}")
    b_ru = types.InlineKeyboardButton("🇷🇺 Rus tili", callback_data=f"{action_type}:ru-RU:{base_fname}")
    b_en = types.InlineKeyboardButton("🇬🇧 Ingliz tili", callback_data=f"{action_type}:en-US:{base_fname}")
    b_auto = types.InlineKeyboardButton("🌐 Avto aniqlash", callback_data=f"{action_type}:auto:{base_fname}")
    b_back = types.InlineKeyboardButton("🔙 Orqaga", callback_data=f"back_video:{base_fname}")
    markup.add(b_uz, b_ru)
    markup.add(b_en, b_auto)
    markup.add(b_back)
    return markup

def get_universal_tools_keyboard() -> types.InlineKeyboardMarkup:
    markup = types.InlineKeyboardMarkup(row_width=2)
    b_montaj = types.InlineKeyboardButton("🎬 Pro Reklama Montaj (/montaj)", callback_data="tool_cmd:montaj")
    b_outro = types.InlineKeyboardButton("📌 Reklama Outro Saqlash (/set_outro)", callback_data="tool_cmd:set_outro")
    b_tr = types.InlineKeyboardButton("🌍 AI Tarjimon (/tr)", callback_data="tool_cmd:tr")
    b_qr = types.InlineKeyboardButton("📱 QR-Kod Yasash (/qr)", callback_data="tool_cmd:qr")
    b_kurs = types.InlineKeyboardButton("💱 Valyuta Kursi (/kurs)", callback_data="tool_cmd:kurs")
    b_ai = types.InlineKeyboardButton("🧠 DeepSeek AI (/ai)", callback_data="tool_cmd:ai")
    b_img = types.InlineKeyboardButton("🖼 Rasm Chizish (/image)", callback_data="tool_cmd:image")
    markup.add(b_montaj)
    markup.add(b_outro)
    markup.add(b_kurs, b_qr)
    markup.add(b_tr, b_ai)
    markup.add(b_img)
    return markup

def make_montage_mode_keyboard(session_key: str) -> types.InlineKeyboardMarkup:
    """5 xil professional montaj rejimini tanlash tugmalari (Blurred BG + Anti-Duplikat + Suzuvchi Watermark bilan!)"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "🔥 1. Audio Uzluksiz + Whoosh FX (1-Audio 2-ga o'tadi, 2-Mute) [Tavsiya]",
            callback_data=f"do_montaj:audio1_bridge:{session_key}"
        ),
        types.InlineKeyboardButton(
            "🎬 2. L-Cut Overlap (1-Video kadri almashib, audiosi 2-da tugaydi)",
            callback_data=f"do_montaj:lcut_split:{session_key}"
        ),
        types.InlineKeyboardButton(
            "🖼 3. PiP Reklama (Burchakda 3s Preview + To'liq Ekran Outro)",
            callback_data=f"do_montaj:pip_outro:{session_key}"
        ),
        types.InlineKeyboardButton(
            "🔊 4. Original Ovozlar (1-Video ovozi + 2-Video o'z ovozi)",
            callback_data=f"do_montaj:both_original:{session_key}"
        ),
        types.InlineKeyboardButton(
            "🔉 5. Fon Musiqa Mix (1-Audio 25% fonda + 2-Video ovozi 100%)",
            callback_data=f"do_montaj:audio_ducking:{session_key}"
        ),
        types.InlineKeyboardButton("❌ Bekor qilish", callback_data=f"cancel_montaj:{session_key}")
    )
    return markup

# ==================== ASOSIY BUYRUQLAR (COMMANDS) ====================
@bot.message_handler(commands=['start'])
def handle_start(message: types.Message):
    cleanup_old_files()
    user = message.from_user
    referrer_id = None
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        try:
            referrer_id = int(args[1].replace("ref_", ""))
        except ValueError:
            referrer_id = None

    is_new, ref_became_vip = register_user(user, referrer_id)
    lang = get_user_lang(user.id)

    if ref_became_vip and referrer_id:
        try:
            ref_lang = get_user_lang(referrer_id)
            vip_notif = {
                "uz": f"🎉 <b>Ajoyib yangilik!</b> Siz {REQUIRED_REFERRALS_FOR_VIP} ta do'stingizni taklif qildingiz!\n\n⭐️ <b>Sizga umrbod VIP maqomi berildi!</b>",
                "ru": f"🎉 <b>Отличные новости!</b> Вы пригласили {REQUIRED_REFERRALS_FOR_VIP} друзей!\n\n⭐️ <b>Вам присвоен вечный статус VIP!</b>",
                "en": f"🎉 <b>Great news!</b> You have invited {REQUIRED_REFERRALS_FOR_VIP} friends!\n\n⭐️ <b>You are granted lifetime VIP status!</b>"
            }
            bot.send_message(referrer_id, vip_notif.get(ref_lang, vip_notif["uz"]))
        except Exception:
            pass

    is_subbed, unsubscribed = check_channel_subscription(user.id)
    if not is_subbed:
        bot.send_message(
            message.chat.id,
            get_text("sub_required", lang),
            reply_markup=get_sub_keyboard(unsubscribed, lang)
        )
        return

    text = get_text("welcome", lang, name=user.first_name)
    bot.send_message(message.chat.id, text, reply_markup=get_main_reply_keyboard(lang))

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda msg: msg.text in ["📖 Qo'llanma", "📖 Инструкция", "📖 Help"])
def handle_help(message: types.Message):
    help_text = (
        "📖 <b>Universal Super Saver & AI Bot Qo'llanmasi:</b>\n\n"
        "1️⃣ <b>Video va musiqa yuklash:</b> Instagram, TikTok, YouTube, Pinterest, X havolasini yuboring.\n"
        "2️⃣ <b>12 ta Multimedia studiyasi:</b> Video yuklangach, uning ostidagi tugmalar orqali:\n"
        "   • 🎬 AI Subtitr yozish va .SRT olish\n"
        "   • 🔊 Bass Boost va 🎧 8D Audio qilish\n"
        "   • 🎤 Karaoke Minusovka tayyorlash\n"
        "   • 🔵 Kruglyash, ✂️ Qirqish (Trim), ⏪ Teskari video, 🖼 HD Oblojka olish mumkin!\n"
        "3️⃣ <b>Sun'iy Intellekt (DeepSeek & ChatGPT):</b> <code>/ai savolingiz</code> deb yozing.\n"
        "4️⃣ <b>AI Rasm chizish (NanoBanana):</b> <code>/image rasm tavsifi</code> deb yozing.\n"
        "5️⃣ <b>AI Tarjimon:</b> <code>/tr matn</code> — har qanday matnni tarjima qilish.\n"
        "6️⃣ <b>QR-Kod yasash:</b> <code>/qr ssilka yoki matn</code>.\n"
        "7️⃣ <b>Valyuta kurslari:</b> <code>/kurs</code> yoki <code>/kurs 100</code> — Markaziy bank real kurslari."
    )
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(commands=['tools'])
@bot.message_handler(func=lambda msg: msg.text in ["🛠 Universal Vositalar", "🛠 Инструменты", "🛠 Smart Tools"])
def handle_tools_menu(message: types.Message):
    text = (
        "🛠 <b>Universal Foydali Vositalar Markazi:</b>\n\n"
        "• 💱 <b>Valyuta Kurslari:</b> <code>/kurs</code> yoki <code>/kurs 100</code>\n"
        "• 🌍 <b>AI Tarjimon:</b> <code>/tr Hello world</code>\n"
        "• 📱 <b>QR-Kod Generator:</b> <code>/qr https://t.me/usman_khasan</code>\n"
        "• 🧠 <b>DeepSeek AI:</b> <code>/ai savolingiz</code>\n"
        "• 🖼 <b>AI Rasm Chizish:</b> <code>/image manzara</code>\n\n"
        "Quyidagi tugmalardan birini bosing:"
    )
    bot.send_message(message.chat.id, text, reply_markup=get_universal_tools_keyboard())

@bot.message_handler(commands=['kurs', 'valyuta'])
@bot.message_handler(func=lambda msg: msg.text and msg.text.strip() in [
    "💱 Valyuta Kurslari", "💱 Курсы валют", "💱 Exchange Rates",
    "kurs", "Kurs", "valyuta", "Valyuta"
])
def handle_kurs_cmd(message: types.Message):
    amount = 1.0
    if message.text:
        parts = message.text.strip().split()
        if len(parts) > 1:
            try:
                amount = float(parts[1].replace(",", "."))
            except ValueError:
                amount = 1.0
    markup = types.InlineKeyboardMarkup(row_width=3)
    markup.add(
        types.InlineKeyboardButton("💵 100$", callback_data="kurs_amt:100"),
        types.InlineKeyboardButton("💵 500$", callback_data="kurs_amt:500"),
        types.InlineKeyboardButton("💵 1000$", callback_data="kurs_amt:1000"),
    )
    markup.add(types.InlineKeyboardButton("🔄 Kursni yangilash", callback_data="kurs_amt:1"))
    bot.reply_to(message, fetch_cbu_exchange_rates(amount), reply_markup=markup)

@bot.message_handler(commands=['qr'])
def handle_qr_cmd(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        msg = bot.reply_to(message, "📱 <b>QR-Kod yasash uchun matn yoki ssilka yuboring:</b>")
        USER_STATES[message.from_user.id] = {"action": "qr_make"}
        bot.register_next_step_handler(msg, process_qr_step)
        return
    send_qr_result(message, args[1])

def process_qr_step(message: types.Message):
    uid = message.from_user.id
    if uid in USER_STATES and USER_STATES[uid].get("action") == "qr_make":
        del USER_STATES[uid]
        if message.text:
            send_qr_result(message, message.text)

def send_qr_result(message: types.Message, data_text: str):
    qr_bytes = generate_qr_code_bytes(data_text)
    if qr_bytes:
        bot.send_photo(
            message.chat.id,
            photo=qr_bytes,
            caption=f"📱 <b>QR-Kod tayyor!</b>\n🔗 <code>{data_text[:100]}</code>\n\n🤖 @{(bot.get_me()).username}"
        )
    else:
        bot.reply_to(message, "❌ QR-kod yaratishda xatolik yuz berdi.")

@bot.message_handler(commands=['tr', 'translate'])
def handle_translate_cmd(message: types.Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        msg = bot.reply_to(message, "🌍 <b>Tarjima qilish uchun matnni yuboring:</b>\n(O'zbek, Rus va Ingliz tillariga professional tarjima qilinadi)")
        USER_STATES[message.from_user.id] = {"action": "tr_text"}
        bot.register_next_step_handler(msg, process_tr_step)
        return
    send_translation_result(message, args[1])

def process_tr_step(message: types.Message):
    uid = message.from_user.id
    if uid in USER_STATES and USER_STATES[uid].get("action") == "tr_text":
        del USER_STATES[uid]
        if message.text:
            send_translation_result(message, message.text)

def send_translation_result(message: types.Message, text_to_tr: str):
    prog = bot.reply_to(message, "🌍 <b>AI tarjima qilmoqda...</b>")
    prompt = (
        f"Translate the following text accurately into 1) Uzbek, 2) Russian, and 3) English. "
        f"Format cleanly with flags:\n\nText: {text_to_tr}"
    )
    ans = query_free_ai(prompt, model_type="deepseek")
    bot.delete_message(message.chat.id, prog.message_id)
    bot.reply_to(message, f"🌍 <b>AI Professional Tarjima:</b>\n\n{ans}")

@bot.message_handler(commands=['lang', 'language'])
@bot.message_handler(func=lambda msg: msg.text in ["🌐 Til", "🌐 Сменить язык", "🌐 Language"])
def handle_lang_command(message: types.Message):
    bot.send_message(
        message.chat.id,
        "🌐 <b>Tilni tanlang / Выберите язык / Select language:</b>",
        reply_markup=get_language_inline_keyboard()
    )

@bot.message_handler(commands=['referral', 'ref'])
@bot.message_handler(func=lambda msg: msg.text in ["👥 VIP & Do'stlar", "👥 VIP & Рефералы", "👥 VIP & Referral"])
def handle_referral(message: types.Message):
    user = message.from_user
    register_user(user)
    prof = get_user_profile(user.id)
    bot_info = bot.get_me()

    ref_link = f"https://t.me/{bot_info.username}?start=ref_{user.id}"
    vip_status = "⭐️ VIP (Faol)" if prof['is_vip'] else f"{prof['referrals']} / {REQUIRED_REFERRALS_FOR_VIP}"

    share_text = f"🔥 Instagram, TikTok, YouTube dan suv belgisiz video yuklovchi, 8D Audio, Bass Boost va AI bot!\n\n{ref_link}"
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(share_text)}"

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🚀 Telegramda ulashish", url=share_url))

    ref_msg = (
        "👥 <b>VIP & Referal Dasturi</b>\n\n"
        f"🔗 <b>Sizning taklif havolangiz:</b>\n<code>{ref_link}</code>\n\n"
        f"📊 <b>Chaqirilgan do'stlar:</b> {prof['referrals']} ta\n"
        f"🏆 <b>VIP holati:</b> {vip_status}\n\n"
        f"🎁 <b>Qoida:</b> {REQUIRED_REFERRALS_FOR_VIP} ta do'stingizni taklif qiling va botdan umrbod erkin, reklamasiz foydalaning!"
    )
    bot.send_message(message.chat.id, ref_msg, reply_markup=markup)

@bot.message_handler(commands=['profile'])
@bot.message_handler(func=lambda msg: msg.text in ["👤 Profilim", "👤 Мой профиль", "👤 Profile"])
def handle_profile(message: types.Message):
    user = message.from_user
    register_user(user)
    prof = get_user_profile(user.id)
    uname = f"@{user.username}" if user.username else (ADMIN_USERNAME if user.id == ADMIN_ID else f"user_{user.id}")
    fname = user.first_name or (ADMIN_FIRST_NAME if user.id == ADMIN_ID else "User")
    status_str = "⭐️ VIP (Umrbod)" if prof['is_vip'] else "Standard"
    text = (
        f"👤 <b>{uname}</b>\n"
        f"🆔 <b>Id:</b> <code>{user.id}</code>\n"
        f"👤 <b>First:</b> {fname}\n"
        f"🌐 <b>Lang:</b> {prof.get('language', 'uz')}\n"
        f"📅 <b>Registered:</b> {prof.get('registered', 'Bugun')}\n"
        f"🏆 <b>Status:</b> {status_str} | 📥 <b>Yuklamalar:</b> {prof['downloads']} ta\n\n"
        f"🧠 <b>Explanations and answers</b>\n"
        f"Free AI → <b>DeepSeek & ChatGPT</b>\n\n"
        f"🖼 <b>Visualize your ideas</b>\n"
        f"Make Image → <b>NanoBanana</b>"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📊 Bot Statistikasi (/stat)", callback_data="open_stats"),
        types.InlineKeyboardButton("💱 Valyuta Kurslari (/kurs)", callback_data="tool_cmd:kurs")
    )
    markup.add(
        types.InlineKeyboardButton("🧠 Free AI → DeepSeek & ChatGPT", callback_data="tool_cmd:ai"),
        types.InlineKeyboardButton("🖼 Make Image → NanoBanana", callback_data="tool_cmd:image")
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['clean', 'clear'])
def handle_clean_storage(message: types.Message):
    removed, freed_mb = cleanup_old_files(max_age_seconds=0)
    bot.reply_to(
        message,
        f"🧹 <b>Xotira 100% tozalandi!</b>\n"
        f"🗑 O'chirilgan vaqtinchalik fayllar: <b>{removed} ta</b>\n"
        f"💾 Bo'shatilgan joy: <b>{freed_mb:.2f} MB</b>\n"
        f"<i>(Bot har bir videoni yuborgach, kompyuter xotirasidan avtomatik o'chiradi!)</i>"
    )

# ==================== SUN'IY INTELLEKT (AI) BUYRUQLARI ====================
@bot.message_handler(commands=['ai'])
@bot.message_handler(func=lambda msg: msg.text in ["🧠 AI Savol-Javob", "🧠 Задать вопрос AI", "🧠 Ask AI"])
def handle_ai_entry(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    args = message.text.split(maxsplit=1)

    if len(args) > 1 and not message.text.startswith("🧠"):
        process_ai_query(message, args[1], lang)
    else:
        msg = bot.send_message(message.chat.id, get_text("ai_prompt_ask", lang))
        USER_STATES[message.from_user.id] = {"action": "ai_query", "lang": lang}
        bot.register_next_step_handler(msg, process_ai_step)

def process_ai_step(message: types.Message):
    user_id = message.from_user.id
    if user_id in USER_STATES and USER_STATES[user_id].get("action") == "ai_query":
        lang = USER_STATES[user_id].get("lang", "uz")
        del USER_STATES[user_id]
        if message.text:
            process_ai_query(message, message.text, lang)

def process_ai_query(message: types.Message, query: str, lang: str):
    prog = bot.send_message(message.chat.id, get_text("ai_thinking", lang))
    ai_answer = query_free_ai(query, model_type="deepseek")
    bot.delete_message(message.chat.id, prog.message_id)
    bot.reply_to(message, f"🤖 <b>AI (DeepSeek / ChatGPT):</b>\n\n{ai_answer}")

@bot.message_handler(commands=['image'])
@bot.message_handler(func=lambda msg: msg.text in ["🖼 AI Rasm Chizish", "🖼 Создать картинку AI", "🖼 AI Image"])
def handle_image_entry(message: types.Message):
    lang = get_user_lang(message.from_user.id)
    args = message.text.split(maxsplit=1)

    if len(args) > 1 and not message.text.startswith("🖼"):
        process_image_generation(message, args[1], lang)
    else:
        msg = bot.send_message(message.chat.id, get_text("image_prompt_ask", lang))
        USER_STATES[message.from_user.id] = {"action": "image_prompt", "lang": lang}
        bot.register_next_step_handler(msg, process_image_step)

def process_image_step(message: types.Message):
    user_id = message.from_user.id
    if user_id in USER_STATES and USER_STATES[user_id].get("action") == "image_prompt":
        lang = USER_STATES[user_id].get("lang", "uz")
        del USER_STATES[user_id]
        if message.text:
            process_image_generation(message, message.text, lang)

def process_image_generation(message: types.Message, prompt: str, lang: str):
    prog = bot.send_message(message.chat.id, get_text("ai_image_generating", lang))
    img_bytes = generate_ai_image_bytes(prompt)
    bot.delete_message(message.chat.id, prog.message_id)
    if img_bytes:
        bot.send_photo(
            message.chat.id,
            photo=img_bytes,
            caption=f"🎨 <b>AI Chizgan Rasm (NanoBanana / Flux):</b>\n<i>\"{prompt[:100]}\"</i>\n\n🤖 @{(bot.get_me()).username}"
        )
    else:
        bot.reply_to(message, "❌ Rasm chizishda xatolik yuz berdi. Qayta urinib ko'ring.")

# ==================== STATISTIKA VA ADMIN BUYRUQLARI ====================
@bot.message_handler(commands=['stat', 'stats', 'statistika', 'admin'])
@bot.message_handler(func=lambda msg: msg.text and msg.text.strip() in [
    "📊 Statistika", "📊 Статистика", "📊 Statistics",
    "statistika", "Statistika", "stat", "Stat"
])
def handle_stats(message: types.Message):
    text, markup = build_stats_message(message.from_user)
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['vip'])
def handle_give_vip(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Foydalanish: <code>/vip USER_ID</code>")
        return
    try:
        target_id = int(args[1])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_vip = 1 WHERE user_id = ?", (target_id,))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ Foydalanuvchi {target_id} ga VIP berildi!")
        try:
            bot.send_message(target_id, "🎉 <b>Administrator tomonidan sizga umrbod VIP maqomi berildi!</b>")
        except Exception:
            pass
    except Exception as e:
        bot.reply_to(message, f"Xatolik: {e}")

@bot.message_handler(commands=['delvip'])
def handle_del_vip(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Foydalanish: <code>/delvip USER_ID</code>")
        return
    try:
        target_id = int(args[1])
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_vip = 0 WHERE user_id = ?", (target_id,))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ Foydalanuvchi {target_id} dan VIP olib tashlandi!")
    except Exception as e:
        bot.reply_to(message, f"Xatolik: {e}")

@bot.message_handler(commands=['send'])
def handle_broadcast(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    reply = message.reply_to_message
    if not reply:
        bot.send_message(message.chat.id, "⚠️ Xabar tarqatish uchun biror postga javob (reply) qilib <code>/send</code> yozing.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    status_msg = bot.send_message(message.chat.id, f"📤 Xabar tarqatish boshlandi... Jami: {len(users)} ta")
    success_count = 0
    blocked_count = 0

    for u in users:
        try:
            bot.copy_message(chat_id=u[0], from_chat_id=reply.chat.id, message_id=reply.message_id)
            success_count += 1
            time.sleep(0.04)
        except Exception:
            blocked_count += 1

    bot.edit_message_text(
        f"✅ <b>Tugatildi!</b>\n\n🟢 Yetkazildi: {success_count} ta\n🔴 Bloklaganlar: {blocked_count} ta",
        chat_id=message.chat.id,
        message_id=status_msg.message_id
    )

# ==================== PRO REKLAMA MONTAJ STUDIYASI BUYRUQLARI (/montaj, /set_outro) ====================
def _extract_or_download_video_from_message(message: types.Message, target_prefix: str) -> tuple[str | None, str]:
    """
    Foydalanuvchi yuborgan xabardan (Video fayl, Document MP4 yoki Instagram/TikTok/YouTube linkidan)
    videoni yuklab olish va yo'lini qaytarish! Har qanday davomiylikni (10s, 19s, 1 daqiqa+) qo'llab-quvvatlaydi!
    """
    uid = message.from_user.id
    ts = int(time.time() * 1000)

    # A) Agar bevosita video yoki video_note yoki document yuborilgan bo'lsa:
    media_obj = message.video or message.video_note or (
        message.document if (message.document and (message.document.mime_type or "").startswith("video")) else None
    )
    if media_obj:
        local_path = os.path.join(DOWNLOAD_DIR, f"{target_prefix}_{uid}_{ts}.mp4")
        try:
            finfo = bot.get_file(media_obj.file_id)
            fbytes = bot.download_file(finfo.file_path)
            with open(local_path, "wb") as vf:
                vf.write(fbytes)
            if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
                dur = get_media_duration(local_path)
                return local_path, f"Yuklangan video ({dur:.1f} sek)"
        except Exception as e:
            print(f"Montaj video fayl yuklash xatosi: {e}")
            safe_remove(local_path)
            return None, "Faylni yuklab bo'lmadi (hajmi 20 MB dan kichik fayl yoki link yuboring)."

    # B) Agar link (Instagram, TikTok, YouTube va h.k.) yuborilgan bo'lsa:
    if message.text:
        url = extract_url(message.text)
        if url:
            files, title = download_media_bulletproof(url, uid, ts)
            for fpath in files:
                ext = os.path.splitext(fpath)[1].lower()
                if ext in [".mp4", ".mov", ".mkv", ".webm"]:
                    dur = get_media_duration(fpath)
                    return fpath, f"{title[:40]} ({dur:.1f} sek)"
            safe_remove(*files)
            return None, "Ushbu havoladan video topilmadi."

    return None, "Iltimos, video fayl yuboring yoki Instagram/TikTok/YouTube video linkini tashlang!"

@bot.message_handler(commands=['montaj', 'merge', 'reklama'])
@bot.message_handler(func=lambda msg: msg.text and msg.text.strip() in [
    "🎬 Reklama Montaj", "🎬 Видео Монтаж", "🎬 Video Montage",
    "montaj", "Montaj"
])
def handle_montage_menu(message: types.Message):
    uid = message.from_user.id
    outro_path = get_saved_outro_path(uid)
    if outro_path:
        outro_dur = get_media_duration(outro_path)
        outro_size = os.path.getsize(outro_path) / (1024 * 1024)
        outro_status = f"✅ <b>Saqlangan ({outro_dur:.1f} sek | {outro_size:.1f} MB)</b>"
    else:
        outro_status = "⚠️ <b>Hali saqlanmagan</b> (<code>/set_outro</code> orqali saqlang)"

    wm_cfg = get_watermark_settings()
    wm_state = f"✅ <b>Faol:</b> <code>{wm_cfg.get('text')}</code> ({int(wm_cfg.get('opacity', 0.24)*100)}% shaffof, tepadan-pastga suzuvchi)" if wm_cfg.get("enabled", True) else "🔴 O'chirilgan"

    text = (
        "🎬 <b>TOP-1 PRO REKLAMA MONTAJ & ANTI-DUPLIKAT STUDIYASI</b>\n\n"
        "Har qanday davomiylikdagi (10s, 19s, 45s, 1 daqiqa+) videolarni <b>7 ta Pro Studiya funksiyasi</b> "
        "va <b>10-Bosqichli Anti-Duplikat (100% Original)</b> algoritmi bilan tayyorlaydi!\n\n"
        f"📌 <b>Doimiy Reklama Outro:</b> {outro_status}\n"
        f"💧 <b>Shaffof Telegram Watermark:</b> {wm_state}\n\n"
        "✨ <b>Avtomatik qo'llanadigan 7 ta Pro Imkoniyat:</b>\n"
        "1️⃣ <b>Blurred 9:16 Fon:</b> Qora hoshiya o'rniga xiralashtirilgan zamonaviy fon\n"
        "2️⃣ <b>Kinematik O'tish (Smooth Fade):</b> 1-videodan 2-videoga silliq o'tish\n"
        "3️⃣ <b>Tepadan-Pastga Suzuvchi Shaffof Ikonka:</b> Telegram samolyotcha + @Handle\n"
        "4️⃣ <b>5 xil Rejim (shu jumladan 🖼 PiP Burchakda Preview!)</b>\n"
        "5️⃣ <b>Auto-Ovoz Balansi:</b> EBU R128 (-14 LUFS) studiya ovozi\n"
        "6️⃣ <b>Whoosh Sub-Bass Sound FX:</b> Reklamaga o'tishda kinematik ovoz effekti\n"
        "7️⃣ <b>10-Qatlamli Anti-Duplikat + iPhone 16 Pro Max Metadata</b> (Reels/TikTok Top uchun!)\n\n"
        "👇 <b>Kerakli bo'limni tanlang:</b>"
    )
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎬 2 ta Videoni Ulash (1-Video + 2-Video)", callback_data="montaj_start_two"),
        types.InlineKeyboardButton("🛡 1 ta Videoni 100% Original Qilish (Anti-Duplikat)", callback_data="antidup_start_single"),
        types.InlineKeyboardButton("📌 Doimiy Reklama Outro Videoni Saqlash (/set_outro)", callback_data="montaj_set_outro"),
        types.InlineKeyboardButton("💧 Shaffof Watermark Matnini O'zgartirish (/set_watermark)", callback_data="montaj_set_wm")
    )
    if outro_path:
        markup.add(
            types.InlineKeyboardButton("⚡ Saqlangan Outroni Videoga Ulash (1-Click)", callback_data="montaj_use_saved_outro"),
            types.InlineKeyboardButton("🗑 Saqlangan Outroni O'chirish (/del_outro)", callback_data="montaj_del_outro")
        )
    bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.message_handler(commands=['set_watermark', 'watermark'])
def handle_set_watermark_cmd(message: types.Message):
    args = message.text.split(maxsplit=1) if message.text else []
    if len(args) > 1:
        val = args[1].strip()
        if val.lower() in ("off", "0", "yoq", "ochirish"):
            save_watermark_settings(enabled=False)
            bot.reply_to(message, "🔴 <b>Suzuvchi shaffof watermark o'chirildi.</b> Yoqish uchun: <code>/set_watermark @kanal_nomi</code>")
            return
        cfg = save_watermark_settings(enabled=True, text=val, opacity=0.24)
        # Eski kesh PNG larni tozalaymiz
        for fn in os.listdir(PROMO_DIR):
            if fn.startswith("wm_badge_") and fn.endswith(".png"):
                safe_remove(os.path.join(PROMO_DIR, fn))
        bot.reply_to(
            message,
            f"✅ <b>Shaffof Telegram Watermark yangilandi!</b>\n\n"
            f"💧 <b>Yozuv:</b> <code>{cfg['text']}</code> (Telegram samolyotcha ikonkasi bilan)\n"
            f"👁 <b>Shaffoflik:</b> 24% (ko'rinar-ko'rinmas, videoga xalaqit bermaydi)\n"
            f"↕️ <b>Harakat:</b> Tepadan pastga silliq suzib yuradi!"
        )
        return

    cfg = get_watermark_settings()
    msg = bot.reply_to(
        message,
        f"💧 <b>Tepadan-Pastga Suzuvchi Shaffof Watermark Sozlamasi</b>\n\n"
        f"Hozirgi yozuv: <code>{cfg.get('text')}</code>\n\n"
        f"✍️ <b>Yangi kanal yoki bot nikini yuboring</b> (Masalan: <code>@TELEGRAM_YULDUZLARI</code> yoki <code>@usman_khasan</code>):\n"
        f"<i>(O'chirib qo'yish uchun <code>off</code> deb yozing, bekor qilish uchun /cancel)</i>"
    )
    USER_STATES[message.from_user.id] = {"action": "set_watermark_step"}
    bot.register_next_step_handler(msg, process_set_watermark_step)

def process_set_watermark_step(message: types.Message):
    uid = message.from_user.id
    state = USER_STATES.get(uid)
    if not state or state.get("action") != "set_watermark_step":
        return
    del USER_STATES[uid]
    if not message.text or message.text.strip().lower() in ("/cancel", "bekor"):
        bot.reply_to(message, "❌ Bekor qilindi.")
        return
    val = message.text.strip()
    if val.lower() in ("off", "0", "yoq"):
        save_watermark_settings(enabled=False)
        bot.reply_to(message, "🔴 <b>Suzuvchi shaffof watermark o'chirildi.</b>")
        return
    cfg = save_watermark_settings(enabled=True, text=val, opacity=0.24)
    for fn in os.listdir(PROMO_DIR):
        if fn.startswith("wm_badge_") and fn.endswith(".png"):
            safe_remove(os.path.join(PROMO_DIR, fn))
    bot.reply_to(
        message,
        f"✅ <b>Shaffof Telegram Watermark saqlandi!</b>\n\n"
        f"💧 <b>Yozuv:</b> <code>{cfg['text']}</code>\n"
        f"↕️ Endi har bir videoda tepadan pastga ko'rinar-ko'rinmas bo'lib suzib yuradi!"
    )

@bot.message_handler(commands=['original', 'antiduplikat', 'unique'])
def handle_original_cmd(message: types.Message):
    msg = bot.reply_to(
        message,
        "🛡 <b>10-BOSQICHLI ANTI-DUPLIKAT (100% ORIGINAL VIDEO) STUDIYASI</b>\n\n"
        "Videoni Instagram Reels, TikTok va YouTube Shorts algoritmlari uchun <b>100% yangi original</b> qilib "
        "(Rekomendatsiya / Topga chiqadigan qilib) tayyorlash uchun:\n\n"
        "📥 <b>Video fayl yuboring yoki Instagram/TikTok/YouTube linkini tashlang:</b>"
    )
    USER_STATES[message.from_user.id] = {"action": "antidup_wait_video"}
    bot.register_next_step_handler(msg, process_antidup_step)

def process_antidup_step(message: types.Message):
    uid = message.from_user.id
    state = USER_STATES.get(uid)
    if not state or state.get("action") != "antidup_wait_video":
        return
    del USER_STATES[uid]

    if message.text and message.text.strip().lower() in ("/cancel", "bekor"):
        bot.reply_to(message, "❌ Bekor qilindi.")
        return

    prog = bot.reply_to(
        message,
        "🛡 <b>10-Bosqichli Anti-Duplikat + Suzuvchi Watermark ishga tushdi...</b>\n"
        "• pHash, Audio Spektr, GOP va iPhone 16 Pro Max metama'lumotlari yangilanmoqda..."
    )
    src_path, label = _extract_or_download_video_from_message(message, "antidup_src")
    if not src_path:
        bot.edit_message_text(f"❌ {label}", message.chat.id, prog.message_id)
        return

    out_orig = os.path.join(DOWNLOAD_DIR, f"orig_{uid}_{int(time.time())}.mp4")
    try:
        ok, ad_info = make_video_100_original(src_path, out_orig)
        if ok and os.path.exists(out_orig):
            vinfo = get_video_stream_info(out_orig)
            fsize_mb = os.path.getsize(out_orig) / (1024 * 1024)
            bot_uname = get_cached_bot_username()
            cap = (
                f"🛡 <b>100% ORIGINAL VIDEO TAYYOR (Top / Rekomendatsiya Uchun)!</b>\n\n"
                f"🔍 <b>Vizual pHash siljishi:</b> +{ad_info.get('zoom', '2.5%')} (Sub-piksel + Micro-Grain)\n"
                f"🎵 <b>Audio Fingerprint:</b> {ad_info.get('pitch', '+1.3%')} + Loudnorm (-14 LUFS)\n"
                f"⏱ <b>Kadr & PTS Tezligi:</b> {ad_info.get('speed', '1.01x')} (GOP -g 29)\n"
                f"📱 <b>Kamera Imzosi:</b> <code>{ad_info.get('device', 'iPhone 16 Pro Max')}</code>\n"
                f"💧 <b>Watermark:</b> Tepadan-pastga suzuvchi shaffof ikona\n"
                f"💾 <b>Hajmi:</b> {fsize_mb:.1f} MB\n\n"
                f"🤖 @{bot_uname}"
            )
            with open(out_orig, "rb") as vf:
                bot.send_video(
                    message.chat.id,
                    video=vf,
                    caption=cap,
                    width=vinfo.get("width", 720),
                    height=vinfo.get("height", 1280),
                    duration=vinfo.get("duration", 15),
                    supports_streaming=True
                )
            increment_download_count(uid, "anti_duplicate", "Anti-Duplicate Studio", "original")
            try:
                bot.delete_message(message.chat.id, prog.message_id)
            except Exception:
                pass
        else:
            bot.edit_message_text("❌ Videoni qayta ishlashda xatolik yuz berdi.", message.chat.id, prog.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, prog.message_id)
    finally:
        safe_remove(src_path, out_orig)

@bot.message_handler(commands=['set_outro'])
def handle_set_outro_cmd(message: types.Message):
    msg = bot.reply_to(
        message,
        "📌 <b>Doimiy Reklama (Outro) videosini yuboring:</b>\n\n"
        "• Video davomiyligi <b>ixtiyoriy</b> bo'lishi mumkin (masalan: 10 sek, 19 sek, 30 sek yoki 1 daqiqagacha!).\n"
        "• Videoni fayl sifatida tashlang yoki Instagram/TikTok/YouTube linkini yuboring.\n"
        "• Bir marta saqlab qo'ysangiz, botda yuklangan har bir videoning tagidagi <b>«🎯 Reklama Montaj»</b> tugmasi orqali 1 bosishda ulab ketaverasiz!"
    )
    USER_STATES[message.from_user.id] = {"action": "save_outro"}
    bot.register_next_step_handler(msg, process_save_outro_step)

def process_save_outro_step(message: types.Message):
    uid = message.from_user.id
    state = USER_STATES.get(uid)
    if not state or state.get("action") != "save_outro":
        return
    del USER_STATES[uid]

    if message.text and message.text.strip().lower() in ["/cancel", "bekor", "отмена"]:
        bot.reply_to(message, "❌ Bekor qilindi.")
        return

    prog = bot.reply_to(message, "⏳ <b>Reklama (Outro) video qabul qilinib, 1080x1920 HD formatga moslanmoqda...</b>")
    temp_path, info_label = _extract_or_download_video_from_message(message, "raw_outro")
    if not temp_path:
        bot.edit_message_text(f"❌ {info_label}", message.chat.id, prog.message_id)
        return

    target_outro = os.path.join(PROMO_DIR, f"outro_{uid}.mp4")
    try:
        # Outroni oldindan 1080x1920 30fps qilib saqlab qo'yamiz (shunda keyingi montajlar 2 baravar tez bitadi!)
        ok = normalize_clip_for_montage(temp_path, target_outro, keep_audio=True)
        if not ok:
            shutil.copyfile(temp_path, target_outro)
        dur = get_media_duration(target_outro)
        size_mb = os.path.getsize(target_outro) / (1024 * 1024)
        bot.edit_message_text(
            f"✅ <b>Reklama Outro muvaffaqiyatli saqlandi!</b>\n\n"
            f"⏱ <b>Davomiyligi:</b> {dur:.1f} soniya\n"
            f"💾 <b>Hajmi:</b> {size_mb:.1f} MB\n"
            f"📐 <b>Format:</b> 1080x1920 Full HD (Reels)\n\n"
            f"🚀 Endi botga istalgan Instagram/TikTok linkini tashlab, video ostidagi <b>«🎯 Reklama Montaj»</b> tugmasini bossangiz, "
            f"ushbu reklama videongiz avtomatik ulanadi!",
            message.chat.id,
            prog.message_id
        )
    except Exception as e:
        bot.edit_message_text(f"❌ Saqlashda xatolik: {e}", message.chat.id, prog.message_id)
    finally:
        safe_remove(temp_path)

@bot.message_handler(commands=['del_outro'])
def handle_del_outro_cmd(message: types.Message):
    uid = message.from_user.id
    user_outro = os.path.join(PROMO_DIR, f"outro_{uid}.mp4")
    if os.path.exists(user_outro):
        safe_remove(user_outro)
        bot.reply_to(message, "🗑 <b>Saqlangan reklama (Outro) videongiz o'chirildi.</b> Yangisini saqlash uchun: <code>/set_outro</code>")
    else:
        bot.reply_to(message, "ℹ️ Sizda saqlangan Outro video yo'q.")

def process_montage_step1(message: types.Message):
    """1-videoni qabul qilish (Link yoki Video fayl — har qanday davomiylikda)"""
    uid = message.from_user.id
    state = USER_STATES.get(uid)
    if not state or state.get("action") not in ("montaj_wait_v1", "montaj_wait_v1_with_saved"):
        return

    if message.text and message.text.strip().lower() in ["/cancel", "bekor", "отмена"]:
        del USER_STATES[uid]
        bot.reply_to(message, "❌ Montaj bekor qilindi.")
        return

    use_saved_outro = (state.get("action") == "montaj_wait_v1_with_saved")
    del USER_STATES[uid]

    prog = bot.reply_to(message, "⏳ <b>1-video yuklanmoqda va tekshirilmoqda...</b>")
    v1_path, v1_label = _extract_or_download_video_from_message(message, "montaj_v1")
    if not v1_path:
        bot.edit_message_text(f"❌ {v1_label}", message.chat.id, prog.message_id)
        return

    dur1 = get_media_duration(v1_path)
    session_key = f"{uid}_{int(time.time())}"

    # Agar foydalanuvchi "Saqlangan Outroni ulash" ni tanlagan bo'lsa, darhol rejim tanlashga o'tamiz!
    outro_path = get_saved_outro_path(uid) if use_saved_outro else None
    if use_saved_outro and outro_path:
        v2_copy = os.path.join(DOWNLOAD_DIR, f"montaj_v2_{session_key}.mp4")
        shutil.copyfile(outro_path, v2_copy)
        dur2 = get_media_duration(v2_copy)
        MONTAGE_CACHE[session_key] = {
            "user_id": uid,
            "v1": v1_path,
            "v2": v2_copy,
            "dur1": dur1,
            "dur2": dur2,
            "created": time.time()
        }
        bot.edit_message_text(
            f"✅ <b>Har ikkala video tayyor!</b>\n\n"
            f"🎬 <b>1-Video (Asosiy):</b> {dur1:.1f} soniya\n"
            f"🎯 <b>2-Video (Saqlangan Reklama):</b> {dur2:.1f} soniya\n"
            f"⏱ <b>Umumiy davomiylik:</b> ~{dur1 + dur2:.1f} soniya\n\n"
            f"👇 <b>Qaysi rejimda montaj qilamiz?</b>",
            message.chat.id,
            prog.message_id,
            reply_markup=make_montage_mode_keyboard(session_key)
        )
        return

    # Aks holda 2-videoni so'raymiz
    MONTAGE_CACHE[session_key] = {
        "user_id": uid,
        "v1": v1_path,
        "v2": None,
        "dur1": dur1,
        "dur2": 0.0,
        "created": time.time()
    }
    USER_STATES[uid] = {"action": "montaj_wait_v2", "session_key": session_key}
    bot.edit_message_text(
        f"✅ <b>1-Video qabul qilindi!</b> ({v1_label})\n\n"
        f"📥 <b>Endi 2-Videoni (Reklama / Outro videoni) yuboring:</b>\n"
        f"• Davomiyligi <b>ixtiyoriy</b> (10s, 19s, 30s, 1 daqiqa va h.k.) bo'lishi mumkin.\n"
        f"• Video fayl tashlang yoki link yuboring:",
        message.chat.id,
        prog.message_id
    )
    bot.register_next_step_handler(message, process_montage_step2)

def process_montage_step2(message: types.Message):
    """2-videoni qabul qilish va 4 ta montaj rejimini chiqarish"""
    uid = message.from_user.id
    state = USER_STATES.get(uid)
    if not state or state.get("action") != "montaj_wait_v2":
        return

    session_key = state.get("session_key")
    del USER_STATES[uid]
    session = MONTAGE_CACHE.get(session_key)
    if not session:
        bot.reply_to(message, "⚠️ Montaj sessiyasi eskirgan. Qaytadan <code>/montaj</code> bosing.")
        return

    if message.text and message.text.strip().lower() in ["/cancel", "bekor", "отмена"]:
        safe_remove(session.get("v1"))
        MONTAGE_CACHE.pop(session_key, None)
        bot.reply_to(message, "❌ Montaj bekor qilindi.")
        return

    prog = bot.reply_to(message, "⏳ <b>2-video yuklanmoqda va tekshirilmoqda...</b>")
    v2_path, v2_label = _extract_or_download_video_from_message(message, "montaj_v2")
    if not v2_path:
        bot.edit_message_text(f"❌ {v2_label}", message.chat.id, prog.message_id)
        safe_remove(session.get("v1"))
        MONTAGE_CACHE.pop(session_key, None)
        return

    dur2 = get_media_duration(v2_path)
    session["v2"] = v2_path
    session["dur2"] = dur2

    # Shuningdek, foydalanuvchiga qulay bo'lishi uchun agar saqlangan outro yo'q bo'lsa, shu 2-videoni avto-shablon sifatida ham saqlab qo'yamiz
    user_outro = os.path.join(PROMO_DIR, f"outro_{uid}.mp4")
    if not os.path.exists(user_outro):
        try:
            shutil.copyfile(v2_path, user_outro)
        except Exception:
            pass

    dur1 = session.get("dur1", 15.0)
    bot.edit_message_text(
        f"🎬 <b>Har ikkala video montajga tayyor!</b>\n\n"
        f"1️⃣ <b>1-Video:</b> {dur1:.1f} soniya\n"
        f"2️⃣ <b>2-Video (Reklama):</b> {dur2:.1f} soniya ({v2_label})\n"
        f"⏱ <b>Jami davomiylik:</b> ~{dur1 + dur2:.1f} soniya\n\n"
        f"👇 <b>Qaysi audio-vizual rejimda birlashtiramiz?</b>",
        message.chat.id,
        prog.message_id,
        reply_markup=make_montage_mode_keyboard(session_key)
    )

# ==================== FOYDALANUVCHI FAYL YUBORGANIDA (DIRECT UPLOAD) ====================
@bot.message_handler(content_types=['video', 'video_note', 'voice', 'audio'])
def handle_uploaded_media(message: types.Message):
    user = message.from_user
    register_user(user)
    lang = get_user_lang(user.id)
    cleanup_old_files()

    is_subbed, unsubscribed = check_channel_subscription(user.id)
    if not is_subbed:
        bot.send_message(message.chat.id, get_text("sub_required", lang), reply_markup=get_sub_keyboard(unsubscribed, lang))
        return

    file_obj = message.video or message.video_note or message.voice or message.audio
    if not file_obj:
        return

    status_msg = bot.reply_to(message, "⏳ Fayl qabul qilinmoqda...")
    try:
        ext = "mp4"
        if message.voice:
            ext = "ogg"
        elif message.audio:
            ext = "mp3"

        timestamp = int(time.time() * 1000)
        base_fname = f"user_{user.id}_{timestamp}.{ext}"
        markup = make_video_action_keyboard(base_fname, lang=lang)
        bot.edit_message_text(
            "🎬 <b>Media qabul qilindi!</b>\n\nQuyidagi 12 ta studiya tugmalaridan birini tanlang:",
            chat_id=message.chat.id,
            message_id=status_msg.message_id,
            reply_markup=markup
        )
        increment_download_count(user.id, "direct_upload", "Telegram File", "upload")
    except Exception as e:
        print(f"Direct file yuklashda xatolik: {e}")
        bot.edit_message_text(get_text("err_generic", lang), message.chat.id, status_msg.message_id)

# ==================== HAVOLA BO'YICHA YUKLASH YOKI AI MATN ====================
@bot.message_handler(func=lambda msg: True and msg.text)
def handle_incoming_link_or_ai(message: types.Message):
    user = message.from_user
    register_user(user)
    lang = get_user_lang(user.id)
    cleanup_old_files(max_age_seconds=120)

    is_subbed, unsubscribed = check_channel_subscription(user.id)
    if not is_subbed:
        bot.send_message(message.chat.id, get_text("sub_required", lang), reply_markup=get_sub_keyboard(unsubscribed, lang))
        return

    txt_clean = message.text.strip()
    cmd_lower = txt_clean.split()[0].lower().split("@")[0] if txt_clean else ""
    if cmd_lower in ("/stat", "/stats", "/statistika", "/admin") or txt_clean in ("📊 Statistika", "📊 Статистика", "📊 Statistics", "statistika", "Statistika", "stat", "Stat"):
        handle_stats(message)
        return
    if cmd_lower in ("/kurs", "/valyuta", "kurs", "valyuta") or txt_clean in ("💱 Valyuta Kurslari", "💱 Курсы валют", "💱 Exchange Rates"):
        handle_kurs_cmd(message)
        return
    if cmd_lower == "/qr":
        handle_qr_cmd(message)
        return
    if cmd_lower in ("/tr", "/translate"):
        handle_translate_cmd(message)
        return
    if cmd_lower in ("/clean", "/clear"):
        handle_clean_storage(message)
        return
    if cmd_lower == "/profile":
        handle_profile(message)
        return
    if cmd_lower in ("/montaj", "/merge", "/reklama") or txt_clean in ("🎬 Reklama Montaj", "🎬 Видео Монтаж", "🎬 Video Montage", "montaj", "Montaj"):
        handle_montage_menu(message)
        return
    if cmd_lower == "/set_outro":
        handle_set_outro_cmd(message)
        return
    if cmd_lower == "/del_outro":
        handle_del_outro_cmd(message)
        return
    if cmd_lower in ("/set_watermark", "/watermark"):
        handle_set_watermark_cmd(message)
        return
    if cmd_lower in ("/original", "/antiduplikat", "/unique"):
        handle_original_cmd(message)
        return

    url = extract_url(message.text)

    # AGAR HAVOLA BO'LMASA -> SUN'IY INTELLEKTGA SAVOL SIFATIDA JAVOB BERISH!
    if not url:
        process_ai_query(message, message.text, lang)
        return

    # HAVOLA BO'LSA -> 12-BOSQICHLI VIDEO-FIRST TIZIM ORQALI XATOSIZ YUKLAB BERISH!
    platform = detect_platform(url)
    status_msg = bot.reply_to(message, get_text("analyzing", lang, platform=platform))
    timestamp = int(time.time() * 1000)
    downloaded_files = []

    try:
        downloaded_files, title = download_media_bulletproof(url, user.id, timestamp)

        if not downloaded_files:
            bot.edit_message_text(get_text("not_found", lang), chat_id=message.chat.id, message_id=status_msg.message_id)
            return

        bot_uname = (bot.get_me()).username
        safe_title = html.escape(str(title or "Video"))[:60]

        # A) KARUSEL (Albom) — Yuboriboq xotiradan o'chiriladi!
        if len(downloaded_files) > 1:
            opened_handles = []
            try:
                media_group = []
                for idx, fpath in enumerate(downloaded_files[:10]):
                    ext = os.path.splitext(fpath)[1].lower()
                    caption = f"📸 Karusel media ({idx+1}/{len(downloaded_files)})\n🤖 @{bot_uname}" if idx == 0 else ""
                    fh = open(fpath, "rb")
                    opened_handles.append(fh)
                    if ext in [".mp4", ".mov", ".mkv", ".webm"]:
                        media_group.append(types.InputMediaVideo(fh, caption=caption, parse_mode="HTML", supports_streaming=True))
                    else:
                        media_group.append(types.InputMediaPhoto(fh, caption=caption, parse_mode="HTML"))

                bot.send_media_group(chat_id=message.chat.id, media=media_group)
                increment_download_count(user.id, url, platform, "carousel")
                try:
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except Exception:
                    pass
            finally:
                for fh in opened_handles:
                    try:
                        fh.close()
                    except Exception:
                        pass
                safe_remove(*downloaded_files)
            return

        # B) BITTA ASOSIY FAYL
        downloaded_file = downloaded_files[0]
        ext = os.path.splitext(downloaded_file)[1].lower()

        # Rasm bo'lsa (faqat haqiqiy rasm postlar uchun) — Yuboriboq xotiradan o'chiriladi!
        if ext in [".jpg", ".jpeg", ".png", ".webp"]:
            try:
                with open(downloaded_file, "rb") as pf:
                    bot.send_photo(
                        chat_id=message.chat.id,
                        photo=pf,
                        caption=f"🖼 <b>{safe_title}</b>\n🌐 <b>{platform}</b>\n\n🤖 @{bot_uname}"
                    )
                increment_download_count(user.id, url, platform, "photo")
                try:
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except Exception:
                    pass
            finally:
                safe_remove(downloaded_file)
            return

        # Video bo'lsa -> Telefonda (iPhone / Android) bittada ochiladigan H.264 MP4 formatga tekshirish
        downloaded_file, vinfo = ensure_phone_playable_mp4(downloaded_file)
        file_size_mb = os.path.getsize(downloaded_file) / (1024 * 1024)
        base_fname = os.path.basename(downloaded_file)

        # AGAR FAYL 50 MB DAN KATTA BO'LSA -> AUTO-SPLITTER
        if file_size_mb > MAX_TELEGRAM_FILE_MB:
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton(get_text("btn_split_parts", lang), callback_data=f"split_video:{base_fname}"),
                types.InlineKeyboardButton(get_text("btn_audio_only", lang), callback_data=f"audio:{base_fname}")
            )
            bot.edit_message_text(
                get_text("large_file_split_prompt", lang, size=file_size_mb),
                chat_id=message.chat.id,
                message_id=status_msg.message_id,
                reply_markup=markup
            )
            return

        # NORMAL HAJMDAGI VIDEO (< 50 MB) — Yuborilgach, kompyuter xotirasidan DARHOL o'chiriladi!
        markup = make_video_action_keyboard(base_fname, lang=lang)
        caption = (
            f"🎬 <b>{safe_title}</b>\n\n"
            f"🌐 <b>Platforma:</b> {platform}\n"
            f"💾 <b>Hajmi:</b> {file_size_mb:.1f} MB\n\n"
            f"🤖 @{bot_uname}"
        )
        try:
            sent_ok = False
            try:
                with open(downloaded_file, "rb") as vf:
                    bot.send_video(
                        chat_id=message.chat.id,
                        video=vf,
                        caption=caption,
                        reply_markup=markup,
                        width=vinfo.get("width", 720),
                        height=vinfo.get("height", 1280),
                        duration=vinfo.get("duration", 15),
                        supports_streaming=True
                    )
                sent_ok = True
            except Exception as send_err:
                print(f"send_video 1-urinish xatosi, qayta kodlanmoqda: {send_err}")
                downloaded_file, vinfo = ensure_phone_playable_mp4(downloaded_file, force_reencode=True)
                try:
                    with open(downloaded_file, "rb") as vf2:
                        bot.send_video(
                            chat_id=message.chat.id,
                            video=vf2,
                            caption=caption,
                            reply_markup=markup,
                            supports_streaming=True
                        )
                    sent_ok = True
                except Exception:
                    with open(downloaded_file, "rb") as df:
                        bot.send_document(
                            chat_id=message.chat.id,
                            document=df,
                            caption=caption,
                            reply_markup=markup
                        )
                    sent_ok = True

            if sent_ok:
                increment_download_count(user.id, url, platform, "video")
                try:
                    bot.delete_message(message.chat.id, status_msg.message_id)
                except Exception:
                    pass
        finally:
            safe_remove(downloaded_file)

    except Exception as e:
        print(f"Yuklashda xatolik: {e}")
        safe_remove(*downloaded_files)
        try:
            bot.edit_message_text(get_text("err_generic", lang), chat_id=message.chat.id, message_id=status_msg.message_id)
        except Exception:
            pass

# ==================== CALLBACK QUERY (INTERAKTIV TUGMALAR) ====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call: types.CallbackQuery):
    user_id = call.from_user.id
    lang = get_user_lang(user_id)
    cleanup_old_files(max_age_seconds=120)

    # 1. Til tanlash
    if call.data.startswith("set_lang:"):
        new_lang = call.data.split(":")[1]
        set_user_lang(user_id, new_lang)
        bot.answer_callback_query(call.id, get_text("lang_changed", new_lang), show_alert=True)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        bot.send_message(call.message.chat.id, get_text("welcome", new_lang, name=call.from_user.first_name), reply_markup=get_main_reply_keyboard(new_lang))
        return

    # 2. Obunani tekshirish
    if call.data == "check_subscription":
        is_subbed, unsubscribed = check_channel_subscription(user_id)
        if is_subbed:
            bot.answer_callback_query(call.id, get_text("sub_success", lang), show_alert=True)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bot.send_message(call.message.chat.id, get_text("welcome", lang, name=call.from_user.first_name), reply_markup=get_main_reply_keyboard(lang))
        else:
            bot.answer_callback_query(call.id, get_text("sub_failed", lang), show_alert=True)
        return

    # 3. Referal, Statistika va Valyuta callbacklari
    if call.data == "open_referral":
        handle_referral(call.message)
        bot.answer_callback_query(call.id)
        return

    if call.data == "open_stats":
        text, markup = build_stats_message(call.from_user)
        bot.answer_callback_query(call.id, "📊 Statistika yangilandi!")
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        except Exception:
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
        return

    if call.data.startswith("kurs_amt:"):
        amt = float(call.data.split(":")[1])
        bot.answer_callback_query(call.id, f"💱 {amt:g} birlik bo'yicha hisoblandi!")
        markup = types.InlineKeyboardMarkup(row_width=3)
        markup.add(
            types.InlineKeyboardButton("💵 100$", callback_data="kurs_amt:100"),
            types.InlineKeyboardButton("💵 500$", callback_data="kurs_amt:500"),
            types.InlineKeyboardButton("💵 1000$", callback_data="kurs_amt:1000"),
        )
        markup.add(types.InlineKeyboardButton("🔄 1 birlik (Asosiy kurs)", callback_data="kurs_amt:1"))
        try:
            bot.edit_message_text(fetch_cbu_exchange_rates(amt), call.message.chat.id, call.message.message_id, reply_markup=markup)
        except Exception:
            bot.send_message(call.message.chat.id, fetch_cbu_exchange_rates(amt), reply_markup=markup)
        return

    if call.data == "clean_storage_cb":
        removed, freed_mb = cleanup_old_files(max_age_seconds=0)
        bot.answer_callback_query(call.id, f"🧹 Tozalandi! {removed} ta fayl ({freed_mb:.2f} MB) o'chirildi.", show_alert=True)
        text, markup = build_stats_message(call.from_user)
        try:
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        except Exception:
            pass
        return

    # 4. Asosiy video menyusiga qaytish
    if call.data.startswith("back_video:"):
        base_fname = call.data.split("back_video:")[1]
        markup = make_video_action_keyboard(base_fname, lang=lang)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        return

    # 5. Universal Tools callbacklari
    if call.data.startswith("tool_cmd:"):
        subcmd = call.data.split(":")[1]
        bot.answer_callback_query(call.id)
        if subcmd == "kurs":
            markup = types.InlineKeyboardMarkup(row_width=3)
            markup.add(
                types.InlineKeyboardButton("💵 100$", callback_data="kurs_amt:100"),
                types.InlineKeyboardButton("💵 500$", callback_data="kurs_amt:500"),
                types.InlineKeyboardButton("💵 1000$", callback_data="kurs_amt:1000"),
            )
            markup.add(types.InlineKeyboardButton("🔄 Kursni yangilash", callback_data="kurs_amt:1"))
            bot.send_message(call.message.chat.id, fetch_cbu_exchange_rates(1.0), reply_markup=markup)
        elif subcmd == "qr":
            msg = bot.send_message(call.message.chat.id, "📱 <b>QR-Kod yasash uchun matn yoki ssilka yuboring:</b>")
            USER_STATES[user_id] = {"action": "qr_make"}
            bot.register_next_step_handler(msg, process_qr_step)
        elif subcmd == "tr":
            msg = bot.send_message(call.message.chat.id, "🌍 <b>Tarjima qilish uchun matnni yuboring:</b>")
            USER_STATES[user_id] = {"action": "tr_text"}
            bot.register_next_step_handler(msg, process_tr_step)
        elif subcmd == "ai":
            msg = bot.send_message(call.message.chat.id, get_text("ai_prompt_ask", lang))
            USER_STATES[user_id] = {"action": "ai_query", "lang": lang}
            bot.register_next_step_handler(msg, process_ai_step)
        elif subcmd == "image":
            msg = bot.send_message(call.message.chat.id, get_text("image_prompt_ask", lang))
            USER_STATES[user_id] = {"action": "image_prompt", "lang": lang}
            bot.register_next_step_handler(msg, process_image_step)
        elif subcmd == "montaj":
            handle_montage_menu(call.message)
        elif subcmd == "set_outro":
            handle_set_outro_cmd(call.message)
        return

    # ------------------ PRO REKLAMA MONTAJ CALLBACKLARI ------------------
    if call.data == "montaj_start_two":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "🎬 <b>1-Videoni (Asosiy videoni) yuboring:</b>\n\n"
            "• Instagram / TikTok / YouTube linkini tashlang yoki video fayl yuboring.\n"
            "• Video davomiyligi <b>ixtiyoriy</b> (masalan: 10s, 25s, 1 daqiqa va h.k.).\n"
            "<i>(Bekor qilish uchun /cancel yozing)</i>"
        )
        USER_STATES[user_id] = {"action": "montaj_wait_v1"}
        bot.register_next_step_handler(msg, process_montage_step1)
        return

    if call.data == "montaj_use_saved_outro":
        bot.answer_callback_query(call.id)
        outro_path = get_saved_outro_path(user_id)
        if not outro_path:
            bot.send_message(call.message.chat.id, "⚠️ Sizda hali saqlangan Outro yo'q. Avval <code>/set_outro</code> orqali reklama videongizni saqlang.")
            return
        msg = bot.send_message(
            call.message.chat.id,
            "⚡ <b>1-Videoni (Instagram/TikTok linkini yoki video faylni) yuboring:</b>\n"
            "Saqlangan reklama (Outro) videongiz uning oxiriga avtomatik ulanadi!"
        )
        USER_STATES[user_id] = {"action": "montaj_wait_v1_with_saved"}
        bot.register_next_step_handler(msg, process_montage_step1)
        return

    if call.data == "montaj_set_outro":
        bot.answer_callback_query(call.id)
        handle_set_outro_cmd(call.message)
        return

    if call.data == "montaj_del_outro":
        user_outro = os.path.join(PROMO_DIR, f"outro_{user_id}.mp4")
        safe_remove(user_outro)
        bot.answer_callback_query(call.id, "🗑 Saqlangan Outro o'chirildi!", show_alert=True)
        handle_montage_menu(call.message)
        return

    if call.data == "montaj_set_wm":
        bot.answer_callback_query(call.id)
        cfg = get_watermark_settings()
        msg = bot.send_message(
            call.message.chat.id,
            f"💧 <b>Tepadan-Pastga Suzuvchi Shaffof Watermark</b>\n\n"
            f"Hozirgi yozuv: <code>{cfg.get('text')}</code>\n"
            f"✍️ <b>Yangi kanal yoki bot nikini yuboring</b> (Masalan: <code>@TELEGRAM_YULDUZLARI</code> yoki <code>@usman_khasan</code>):\n"
            f"<i>(O'chirish uchun <code>off</code> deb yozing)</i>"
        )
        USER_STATES[user_id] = {"action": "set_watermark_step"}
        bot.register_next_step_handler(msg, process_set_watermark_step)
        return

    if call.data == "antidup_start_single":
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "🛡 <b>100% Original Qilinadigan Videoni Yuboring:</b>\n\n"
            "• Instagram / TikTok / YouTube linkini tashlang yoki video fayl yuboring.\n"
            "• 10-Bosqichli Anti-Duplikat + Tepadan-pastga suzuvchi shaffof watermark + iPhone 16 Pro Max metama'lumotlari qo'llanadi!"
        )
        USER_STATES[user_id] = {"action": "antidup_wait_video"}
        bot.register_next_step_handler(msg, process_antidup_step)
        return

    if call.data.startswith("antidup_vid:"):
        base_fname = call.data.split("antidup_vid:")[1]
        src_temp = os.path.join(DOWNLOAD_DIR, f"ad_src_{int(time.time())}_{base_fname}")
        out_orig = os.path.join(DOWNLOAD_DIR, f"orig_{user_id}_{int(time.time())}.mp4")
        bot.answer_callback_query(call.id, "🛡 10-Bosqichli Anti-Duplikat boshlandi...")
        prog = bot.send_message(
            call.message.chat.id,
            "🛡 <b>10-Bosqichli Anti-Duplikat (100% Original) bajarilmoqda...</b>\n\n"
            "• 🔍 Vizual pHash, Sub-piksel Zoom & Micro-Grain...\n"
            "• 🎵 Audio Spektr & EBU R128 (-14 LUFS) Mastering...\n"
            "• 💧 Tepadan-pastga suzuvchi shaffof Telegram Watermark...\n"
            "• 📱 Apple iPhone 16 Pro Max (iOS 18.2) Metadata yozilmoqda..."
        )
        try:
            if not ensure_video_from_telegram(call.message, src_temp):
                bot.edit_message_text("⚠️ Asosiy videoni o'qib bo'lmadi. Videoni qayta yuklang.", call.message.chat.id, prog.message_id)
                return
            ok, ad_info = make_video_100_original(src_temp, out_orig)
            if ok and os.path.exists(out_orig):
                vinfo = get_video_stream_info(out_orig)
                fsize_mb = os.path.getsize(out_orig) / (1024 * 1024)
                bot_uname = get_cached_bot_username()
                cap = (
                    f"🛡 <b>100% ORIGINAL VIDEO (Reels / TikTok Top Uchun)!</b>\n\n"
                    f"🔍 <b>Vizual pHash siljishi:</b> +{ad_info.get('zoom', '2.5%')} (Sub-piksel + Micro-Grain)\n"
                    f"🎵 <b>Audio Fingerprint:</b> {ad_info.get('pitch', '+1.3%')} + Loudnorm (-14 LUFS)\n"
                    f"⏱ <b>Kadr & PTS Tezligi:</b> {ad_info.get('speed', '1.01x')} (GOP -g 29)\n"
                    f"📱 <b>Kamera Imzosi:</b> <code>{ad_info.get('device', 'iPhone 16 Pro Max')}</code>\n"
                    f"💧 <b>Watermark:</b> Tepadan-pastga suzuvchi shaffof ikona\n"
                    f"💾 <b>Hajmi:</b> {fsize_mb:.1f} MB\n\n"
                    f"🤖 @{bot_uname}"
                )
                with open(out_orig, "rb") as vf:
                    bot.send_video(
                        call.message.chat.id,
                        video=vf,
                        caption=cap,
                        width=vinfo.get("width", 720),
                        height=vinfo.get("height", 1280),
                        duration=vinfo.get("duration", 15),
                        supports_streaming=True
                    )
                increment_download_count(user_id, "anti_duplicate", "Anti-Duplicate Studio", "original")
                try:
                    bot.delete_message(call.message.chat.id, prog.message_id)
                except Exception:
                    pass
            else:
                bot.edit_message_text("❌ Anti-Duplikat ishlov berishda xatolik yuz berdi.", call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(src_temp, out_orig)
        return

    # Yuklangan har qanday videoning ostidagi «🎯 Reklama Montaj» tugmasi bosilganda:
    if call.data.startswith("montaj_from_vid:"):
        base_fname = call.data.split("montaj_from_vid:")[1]
        v1_temp = os.path.join(DOWNLOAD_DIR, f"m_src_{int(time.time())}_{base_fname}")
        bot.answer_callback_query(call.id, "🎬 Montaj studiyasi ochilmoqda...")

        if not ensure_video_from_telegram(call.message, v1_temp):
            bot.send_message(call.message.chat.id, "⚠️ Asosiy videoni o'qib bo'lmadi. Videoni qayta yuklang.")
            return

        dur1 = get_media_duration(v1_temp)
        session_key = f"{user_id}_{int(time.time())}"
        outro_path = get_saved_outro_path(user_id)

        if outro_path:
            # Saqlangan Outro mavjud -> Foydalanuvchiga darhol saqlangan outro bilan ulashni yoki yangi 2-video tashlashni taklif qilamiz!
            v2_copy = os.path.join(DOWNLOAD_DIR, f"montaj_v2_{session_key}.mp4")
            shutil.copyfile(outro_path, v2_copy)
            dur2 = get_media_duration(v2_copy)
            MONTAGE_CACHE[session_key] = {
                "user_id": user_id,
                "v1": v1_temp,
                "v2": v2_copy,
                "dur1": dur1,
                "dur2": dur2,
                "created": time.time()
            }
            mk = make_montage_mode_keyboard(session_key)
            mk.add(types.InlineKeyboardButton("🔄 Boshqa 2-Video tanlash", callback_data=f"montaj_pick_other_v2:{session_key}"))
            bot.send_message(
                call.message.chat.id,
                f"🎯 <b>REKLAMA MONTAJ STUDIYASI</b>\n\n"
                f"1️⃣ <b>1-Video (Tanlangan):</b> {dur1:.1f} soniya\n"
                f"2️⃣ <b>2-Video (Saqlangan Outro):</b> {dur2:.1f} soniya\n"
                f"⏱ <b>Jami davomiylik:</b> ~{dur1 + dur2:.1f} soniya\n\n"
                f"👇 <b>Rejimni tanlang (1 bosishda tayyor bo'ladi!):</b>",
                reply_markup=mk
            )
        else:
            # Saqlangan Outro yo'q -> 2-videoni so'raymiz
            MONTAGE_CACHE[session_key] = {
                "user_id": user_id,
                "v1": v1_temp,
                "v2": None,
                "dur1": dur1,
                "dur2": 0.0,
                "created": time.time()
            }
            msg = bot.send_message(
                call.message.chat.id,
                f"🎬 <b>1-Video tanlandi!</b> (Davomiyligi: {dur1:.1f} soniya)\n\n"
                f"📥 <b>Endi uning oxiriga ulanadigan 2-Videoni (Reklama / Outro videoni) yuboring:</b>\n"
                f"• Davomiyligi ixtiyoriy (10s, 19s, 30s, 1 daqiqa va h.k.) bo'lishi mumkin.\n"
                f"• Shu yuborgan 2-videongiz keyingi safar 1-bosishda ulash uchun avtomatik eslab qolinadi!"
            )
            USER_STATES[user_id] = {"action": "montaj_wait_v2", "session_key": session_key}
            bot.register_next_step_handler(msg, process_montage_step2)
        return

    if call.data.startswith("montaj_pick_other_v2:"):
        session_key = call.data.split("montaj_pick_other_v2:")[1]
        session = MONTAGE_CACHE.get(session_key)
        bot.answer_callback_query(call.id)
        if not session or not os.path.exists(session.get("v1", "")):
            bot.send_message(call.message.chat.id, "⚠️ Montaj sessiyasi eskirgan. Qaytadan <code>/montaj</code> bosing.")
            return
        safe_remove(session.get("v2"))
        session["v2"] = None
        msg = bot.send_message(
            call.message.chat.id,
            "📥 <b>Yangi 2-Videoni (yoki video linkini) yuboring:</b>\n"
            "(Davomiyligi ixtiyoriy — 1 daqiqagacha va undan uzun bo'lishi mumkin)"
        )
        USER_STATES[user_id] = {"action": "montaj_wait_v2", "session_key": session_key}
        bot.register_next_step_handler(msg, process_montage_step2)
        return

    if call.data.startswith("cancel_montaj:"):
        session_key = call.data.split("cancel_montaj:")[1]
        session = MONTAGE_CACHE.pop(session_key, None)
        if session:
            safe_remove(session.get("v1"), session.get("v2"))
        bot.answer_callback_query(call.id, "Montaj bekor qilindi.")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        return

    if call.data.startswith("do_montaj:"):
        parts = call.data.split(":")
        mode = parts[1]
        session_key = parts[2]
        session = MONTAGE_CACHE.pop(session_key, None)
        if not session or not os.path.exists(session.get("v1", "")) or not os.path.exists(session.get("v2", "")):
            bot.answer_callback_query(call.id, "⚠️ Video fayllari topilmadi yoki sessiya eskirgan.", show_alert=True)
            return

        v1_path = session["v1"]
        v2_path = session["v2"]
        out_montaj = os.path.join(DOWNLOAD_DIR, f"reklama_reel_{session_key}.mp4")

        bot.answer_callback_query(call.id, "🎬 Top-1 Pro Reels montaj boshlandi...")
        prog = bot.edit_message_text(
            "⏳ <b>Top-1 Pro Reels Montaj & 10-Bosqichli Anti-Duplikat bajarilmoqda...</b>\n\n"
            "• 📐 <b>Format:</b> 1080x1920 Full HD (Blurred 9:16 Fon + Smooth Fade)\n"
            "• 🎵 <b>Audio:</b> EBU R128 (-14 LUFS) + Transition Whoosh FX\n"
            "• 💧 <b>Watermark:</b> Tepadan-pastga suzuvchi shaffof Telegram ikona\n"
            "• 🛡 <b>Anti-Duplikat:</b> 10-Qatlamli 100% Original + iPhone 16 Pro Max Metadata\n"
            "<i>Iltimos, 15–30 soniya kuting...</i>",
            call.message.chat.id,
            call.message.message_id
        )

        try:
            ok, m_info = montage_two_videos(v1_path, v2_path, out_montaj, mode=mode, apply_anti_duplicate=True)
            if ok and os.path.exists(out_montaj):
                out_montaj, vinfo = ensure_phone_playable_mp4(out_montaj, apply_watermark=False)
                fsize_mb = os.path.getsize(out_montaj) / (1024 * 1024)
                bot_uname = get_cached_bot_username()
                ad = m_info.get("anti_dup", {})
                caption = (
                    f"🎬 <b>Tayyor Pro Reklama Reels (100% Original)!</b>\n\n"
                    f"🎛 <b>Rejim:</b> {m_info.get('mode_name', mode)}\n"
                    f"⏱ <b>1-Video:</b> {m_info.get('dur1', 0):.1f}s | <b>2-Video:</b> {m_info.get('dur2', 0):.1f}s\n"
                    f"⏳ <b>Jami davomiylik:</b> <b>{m_info.get('total', 0):.1f} soniya</b>\n"
                    f"🛡 <b>Anti-Duplikat:</b> 10-Bosqichli Original (Zoom +{ad.get('zoom', '2.5%')}, iPhone 16 Pro Max)\n"
                    f"💧 <b>Watermark:</b> Tepadan-pastga suzuvchi shaffof ikona\n"
                    f"📐 <b>Sifat:</b> 1080x1920 Full HD | 💾 <b>Hajmi:</b> {fsize_mb:.1f} MB\n\n"
                    f"🤖 @{bot_uname}"
                )
                with open(out_montaj, "rb") as mf:
                    bot.send_video(
                        call.message.chat.id,
                        video=mf,
                        caption=caption,
                        width=vinfo.get("width", 1080),
                        height=vinfo.get("height", 1920),
                        duration=int(m_info.get("total", 30)),
                        supports_streaming=True
                    )
                increment_download_count(user_id, "montage_reel", "Montage Studio", mode)
                try:
                    bot.delete_message(call.message.chat.id, prog.message_id)
                except Exception:
                    pass
            else:
                bot.edit_message_text("❌ Montaj qilishda xatolik yuz berdi. Videolarni tekshirib qayta urinib ko'ring.", call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Montaj xatoligi: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(v1_path, v2_path, out_montaj)
        return

    # ------------------ AUTO-SPLITTER (50 MB+) ------------------
    if call.data.startswith("split_video:"):
        base_fname = call.data.split("split_video:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)

        if not os.path.exists(video_path):
            bot.answer_callback_query(call.id, "⚠️ Video eskirgan yoki o'chirilgan.", show_alert=True)
            return

        bot.answer_callback_query(call.id, get_text("splitting_progress", lang))
        progress_msg = bot.send_message(call.message.chat.id, get_text("splitting_progress", lang))

        parts = []
        try:
            parts = split_large_video(video_path, DOWNLOAD_DIR, max_chunk_mb=46.0)
            bot.delete_message(call.message.chat.id, progress_msg.message_id)

            for idx, ppath in enumerate(parts, 1):
                part_caption = get_text("part_caption", lang, title=base_fname[:30], current=idx, total=len(parts), bot=(bot.get_me()).username)
                with open(ppath, "rb") as pf:
                    bot.send_video(call.message.chat.id, video=pf, caption=part_caption, supports_streaming=True)
                safe_remove(ppath)
                time.sleep(1)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Bo'laklashda xatolik: {e}")
        finally:
            safe_remove(video_path, *parts)
        return

    # ------------------ SHAZAM / MUSIQANI ANIQLASH ------------------
    if call.data.startswith("shazam:"):
        base_fname = call.data.split("shazam:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        bot.answer_callback_query(call.id, "🔍 Musiqa aniqlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("music_searching", lang))

        try:
            if not ensure_video_from_telegram(call.message, video_path):
                bot.edit_message_text("⚠️ Video faylini o'qib bo'lmadi.", call.message.chat.id, prog.message_id)
                return

            music_info = identify_music_from_video(video_path)
            bot.delete_message(call.message.chat.id, prog.message_id)

            if music_info:
                album_line = f"💿 <b>Albom:</b> {music_info['album']}\n" if music_info.get("album") else ""
                res_text = get_text("music_found", lang, title=music_info["title"], artist=music_info["artist"], album_line=album_line, bot=(bot.get_me()).username)
                bot.send_message(call.message.chat.id, res_text)
            else:
                bot.send_message(call.message.chat.id, get_text("music_not_found", lang))
        finally:
            safe_remove(video_path)
        return

    # ------------------ BASS BOOST AUDIO ------------------
    if call.data.startswith("bass:"):
        base_fname = call.data.split("bass:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        out_mp3 = os.path.join(DOWNLOAD_DIR, f"bass_{os.path.splitext(base_fname)[0]}.mp3")
        bot.answer_callback_query(call.id, "🔊 Bass Boost tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("bass_generating", lang))
        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_bass_boost(video_path, out_mp3) and os.path.exists(out_mp3):
                with open(out_mp3, "rb") as af:
                    bot.send_audio(call.message.chat.id, audio=af, caption=f"🔊 <b>Bass Boost (+12dB)</b> | @{(bot.get_me()).username}")
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, out_mp3)
        return

    # ------------------ 8D SURROUND AUDIO ------------------
    if call.data.startswith("audio8d:"):
        base_fname = call.data.split("audio8d:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        out_mp3 = os.path.join(DOWNLOAD_DIR, f"8d_{os.path.splitext(base_fname)[0]}.mp3")
        bot.answer_callback_query(call.id, "🎧 8D Audio tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("audio8d_generating", lang))
        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_8d_audio(video_path, out_mp3) and os.path.exists(out_mp3):
                with open(out_mp3, "rb") as af:
                    bot.send_audio(call.message.chat.id, audio=af, caption=f"🎧 <b>8D Surround Audio (Quloqchinda tinglang!)</b>\n🤖 @{(bot.get_me()).username}")
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, out_mp3)
        return

    # ------------------ KARAOKE MINUSOVKA ------------------
    if call.data.startswith("karaoke:"):
        base_fname = call.data.split("karaoke:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        out_mp3 = os.path.join(DOWNLOAD_DIR, f"karaoke_{os.path.splitext(base_fname)[0]}.mp3")
        bot.answer_callback_query(call.id, "🎤 Karaoke minusovka tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("karaoke_generating", lang))
        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_karaoke_minus(video_path, out_mp3) and os.path.exists(out_mp3):
                with open(out_mp3, "rb") as af:
                    bot.send_audio(call.message.chat.id, audio=af, caption=f"🎤 <b>Karaoke Minusovka (Vocal Removed)</b>\n🤖 @{(bot.get_me()).username}")
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, out_mp3)
        return

    # ------------------ HD THUMBNAIL (OBLOJKA) ------------------
    if call.data.startswith("thumb:"):
        base_fname = call.data.split("thumb:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        out_jpg = os.path.join(DOWNLOAD_DIR, f"thumb_{os.path.splitext(base_fname)[0]}.jpg")
        bot.answer_callback_query(call.id, "🖼 HD Oblojka olinmoqda...")
        try:
            if ensure_video_from_telegram(call.message, video_path) and extract_hd_thumbnail(video_path, out_jpg) and os.path.exists(out_jpg):
                with open(out_jpg, "rb") as jf:
                    bot.send_photo(call.message.chat.id, photo=jf, caption=f"🖼 <b>HD Video Oblojkasi (Thumbnail)</b>\n🤖 @{(bot.get_me()).username}")
            else:
                bot.send_message(call.message.chat.id, get_text("err_generic", lang))
        finally:
            safe_remove(video_path, out_jpg)
        return

    # ------------------ REVERSE VIDEO (TESKARI VIDEO) ------------------
    if call.data.startswith("reverse:"):
        base_fname = call.data.split("reverse:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        out_rev = os.path.join(DOWNLOAD_DIR, f"rev_{base_fname}")
        bot.answer_callback_query(call.id, "⏪ Teskari video tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("reverse_generating", lang))
        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_reverse_video(video_path, out_rev) and os.path.exists(out_rev):
                with open(out_rev, "rb") as rf:
                    bot.send_video(call.message.chat.id, video=rf, caption=f"⏪ <b>Teskari Video (Reverse Effect)</b>\n🤖 @{(bot.get_me()).username}", supports_streaming=True)
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, out_rev)
        return

    # ------------------ VIDEO TRIMMER ------------------
    if call.data.startswith("trim:"):
        base_fname = call.data.split("trim:")[1]
        bot.answer_callback_query(call.id)
        TRIM_CACHE[call.from_user.id] = call.message
        msg = bot.send_message(call.message.chat.id, get_text("trim_prompt", lang))
        USER_STATES[call.from_user.id] = {"action": "trim", "file": base_fname, "lang": lang}
        bot.register_next_step_handler(msg, process_trim_step)
        return

    # ------------------ SUBTITR TILI TANLASH ------------------
    if call.data.startswith("sub_vid:"):
        base_fname = call.data.split("sub_vid:")[1]
        markup = make_sub_lang_keyboard("do_sub_vid", base_fname)
        bot.edit_message_caption(
            caption="🌐 <b>Subtitr qaysi tilda yaratilsin?</b>\nNutq aniqlanib, videoga yoziladi:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("sub_txt:"):
        base_fname = call.data.split("sub_txt:")[1]
        markup = make_sub_lang_keyboard("do_sub_txt", base_fname)
        bot.edit_message_caption(
            caption="🌐 <b>Qaysi tildagi nutq matnga aylantirilsin?</b>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
        bot.answer_callback_query(call.id)
        return

    # ------------------ SUBTITRLI VIDEO (HARDCODE) ------------------
    if call.data.startswith("do_sub_vid:"):
        parts = call.data.split(":")
        sub_lang, base_fname = parts[1], parts[2]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        temp_audio = os.path.join(DOWNLOAD_DIR, f"temp_{os.path.splitext(base_fname)[0]}.wav")
        srt_path = os.path.join(DOWNLOAD_DIR, f"sub_{os.path.splitext(base_fname)[0]}.srt")
        sub_video_path = os.path.join(DOWNLOAD_DIR, f"subtitled_{base_fname}")

        bot.answer_callback_query(call.id, "🎬 AI Subtitr tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("sub_video_generating", lang))

        try:
            if not ensure_video_from_telegram(call.message, video_path):
                bot.edit_message_text("⚠️ Video faylini o'qib bo'lmadi.", call.message.chat.id, prog.message_id)
                return

            subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-ar", "16000", "-ac", "1", temp_audio], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            success, transcript_text = transcribe_audio_to_srt(temp_audio, srt_path, lang=sub_lang)
            safe_remove(temp_audio)

            if not success or not os.path.exists(srt_path):
                bot.edit_message_text(get_text("sub_not_found", lang), call.message.chat.id, prog.message_id)
                return

            burn_success = burn_subtitles_to_video(video_path, srt_path, sub_video_path)
            if burn_success and os.path.exists(sub_video_path):
                vinfo = get_video_stream_info(sub_video_path)
                with open(sub_video_path, "rb") as svf:
                    bot.send_video(
                        call.message.chat.id,
                        video=svf,
                        caption=f"🎬 <b>AI Subtitrli Video tayyor!</b>\n\n📝 <i>\"{transcript_text[:120]}...\"</i>\n\n🤖 @{(bot.get_me()).username}",
                        width=vinfo.get("width", 720),
                        height=vinfo.get("height", 1280),
                        duration=vinfo.get("duration", 15),
                        supports_streaming=True
                    )
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, temp_audio, srt_path, sub_video_path)
        return

    # ------------------ FAQAT SUBTITR MATNI VA .SRT ------------------
    if call.data.startswith("do_sub_txt:"):
        parts = call.data.split(":")
        sub_lang, base_fname = parts[1], parts[2]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        temp_audio = os.path.join(DOWNLOAD_DIR, f"temp_{os.path.splitext(base_fname)[0]}.wav")
        srt_path = os.path.join(DOWNLOAD_DIR, f"sub_{os.path.splitext(base_fname)[0]}.srt")

        bot.answer_callback_query(call.id, "📝 Nutq tahlil qilinmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("sub_text_generating", lang))

        try:
            if not ensure_video_from_telegram(call.message, video_path):
                bot.edit_message_text("⚠️ Video faylini o'qib bo'lmadi.", call.message.chat.id, prog.message_id)
                return

            subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vn", "-ar", "16000", "-ac", "1", temp_audio], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            success, transcript_text = transcribe_audio_to_srt(temp_audio, srt_path, lang=sub_lang)
            safe_remove(temp_audio)

            if not success or not transcript_text:
                bot.edit_message_text(get_text("sub_not_found", lang), call.message.chat.id, prog.message_id)
                return

            bot.send_message(call.message.chat.id, f"📝 <b>TRANSKRIPSIYA (MATN):</b>\n\n<i>\"{transcript_text[:3500]}\"</i>\n\n🤖 @{(bot.get_me()).username}")
            with open(srt_path, "rb") as sf:
                bot.send_document(call.message.chat.id, document=sf, caption="📄 <b>.SRT Subtitr fayli</b>\n(CapCut, Premiere Pro uchun)")
            bot.delete_message(call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, temp_audio, srt_path)
        return

    # ------------------ KRUGLYASH (1:1 VIDEO NOTE) ------------------
    if call.data.startswith("circle:"):
        base_fname = call.data.split("circle:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        circle_path = os.path.join(DOWNLOAD_DIR, f"circle_{base_fname}")

        bot.answer_callback_query(call.id, "🔄 Kruglyash tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("circle_generating", lang))

        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_circle_note(video_path, circle_path) and os.path.exists(circle_path):
                with open(circle_path, "rb") as cf:
                    bot.send_video_note(call.message.chat.id, cf)
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, circle_path)
        return

    # ------------------ MP3 AUDIO ------------------
    if call.data.startswith("audio:"):
        base_fname = call.data.split("audio:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        mp3_path = os.path.join(DOWNLOAD_DIR, f"audio_{os.path.splitext(base_fname)[0]}.mp3")

        bot.answer_callback_query(call.id, "🎧 MP3 ajratilmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("audio_generating", lang))

        try:
            if ensure_video_from_telegram(call.message, video_path) and extract_audio_mp3(video_path, mp3_path, title=base_fname[:30]) and os.path.exists(mp3_path):
                with open(mp3_path, "rb") as af:
                    bot.send_audio(call.message.chat.id, audio=af, caption=f"🎵 @{(bot.get_me()).username}")
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, mp3_path)
        return

    # ------------------ OVOZLI XABAR (VOICE NOTE) ------------------
    if call.data.startswith("voice:"):
        base_fname = call.data.split("voice:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        voice_path = os.path.join(DOWNLOAD_DIR, f"voice_{os.path.splitext(base_fname)[0]}.ogg")

        bot.answer_callback_query(call.id, "🎙 Ovozli xabar tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("voice_generating", lang))

        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_voice_ogg(video_path, voice_path) and os.path.exists(voice_path):
                with open(voice_path, "rb") as vf:
                    bot.send_voice(call.message.chat.id, voice=vf, caption=f"🎙 @{(bot.get_me()).username}")
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, voice_path)
        return

    # ------------------ 1.5x TEZLIK ------------------
    if call.data.startswith("speed:"):
        base_fname = call.data.split("speed:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        speed_path = os.path.join(DOWNLOAD_DIR, f"speed_{base_fname}")

        bot.answer_callback_query(call.id, "⚡ 1.5x tezlashtirilmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("speed_generating", lang))

        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_fast_speed(video_path, speed_path, speed=1.5) and os.path.exists(speed_path):
                with open(speed_path, "rb") as sf:
                    bot.send_video(call.message.chat.id, video=sf, caption=f"⚡ <b>1.5x</b> | @{(bot.get_me()).username}", supports_streaming=True)
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, speed_path)
        return

    # ------------------ GIF ANIMATSIYA ------------------
    if call.data.startswith("gif:"):
        base_fname = call.data.split("gif:")[1]
        video_path = os.path.join(DOWNLOAD_DIR, base_fname)
        gif_path = os.path.join(DOWNLOAD_DIR, f"gif_{os.path.splitext(base_fname)[0]}.mp4")

        bot.answer_callback_query(call.id, "🎞 GIF tayyorlanmoqda...")
        prog = bot.send_message(call.message.chat.id, get_text("gif_generating", lang))

        try:
            if ensure_video_from_telegram(call.message, video_path) and convert_to_gif_animation(video_path, gif_path) and os.path.exists(gif_path):
                with open(gif_path, "rb") as gf:
                    bot.send_animation(call.message.chat.id, animation=gf, caption=f"🎞 @{(bot.get_me()).username}")
                bot.delete_message(call.message.chat.id, prog.message_id)
            else:
                bot.edit_message_text(get_text("err_generic", lang), call.message.chat.id, prog.message_id)
        except Exception as e:
            bot.edit_message_text(f"❌ Xatolik: {e}", call.message.chat.id, prog.message_id)
        finally:
            safe_remove(video_path, gif_path)
        return

# ==================== TRIMMER PROCESSOR ====================
def process_trim_step(message: types.Message):
    user_id = message.from_user.id
    state = USER_STATES.get(user_id)
    if not state or state.get("action") != "trim":
        return

    lang = state.get("lang", "uz")
    base_fname = state.get("file")
    video_path = os.path.join(DOWNLOAD_DIR, base_fname)
    orig_msg = TRIM_CACHE.pop(user_id, None)

    del USER_STATES[user_id]

    if not message.text:
        bot.reply_to(message, get_text("trim_invalid", lang))
        return

    text = message.text.replace("—", "-").replace("–", "-")
    parts = text.split("-")
    if len(parts) != 2:
        bot.reply_to(message, get_text("trim_invalid", lang))
        return

    s_sec = parse_time_to_seconds(parts[0])
    e_sec = parse_time_to_seconds(parts[1])

    if s_sec is None or e_sec is None or s_sec >= e_sec:
        bot.reply_to(message, get_text("trim_invalid", lang))
        return

    prog = bot.reply_to(message, get_text("trimming_progress", lang))
    trimmed_fname = f"trim_{int(time.time())}_{base_fname}"
    trimmed_path = os.path.join(DOWNLOAD_DIR, trimmed_fname)

    try:
        if not ensure_video_from_telegram(orig_msg, video_path):
            bot.edit_message_text("⚠️ Video fayli topilmadi.", message.chat.id, prog.message_id)
            return

        success = trim_video(video_path, trimmed_path, s_sec, e_sec)
        if success and os.path.exists(trimmed_path):
            with open(trimmed_path, "rb") as tf:
                bot.send_video(
                    message.chat.id,
                    video=tf,
                    caption=f"✂️ <b>Qirqilgan lavha ({parts[0].strip()} - {parts[1].strip()})</b>\n🤖 @{(bot.get_me()).username}",
                    supports_streaming=True
                )
            bot.delete_message(message.chat.id, prog.message_id)
        else:
            bot.edit_message_text(get_text("err_generic", lang), message.chat.id, prog.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Xatolik: {e}", message.chat.id, prog.message_id)
    finally:
        safe_remove(video_path, trimmed_path)

# ==================== INLINE REJIM (@bot_username havola) ====================
@bot.inline_handler(func=lambda query: True)
def handle_inline_query(query: types.InlineQuery):
    url = extract_url(query.query)
    results = []
    bot_username = bot.get_me().username

    if url:
        platform = detect_platform(url)
        item = types.InlineQueryResultArticle(
            id="1",
            title=f"📥 {platform} videosini yuklash",
            description=f"Havola: {url[:50]}...",
            input_message_content=types.InputTextMessageContent(
                message_text=f"🎬 <b>{platform} videosini yuklash:</b>\n{url}\n\n🤖 @{bot_username} orqali yuklanmoqda...",
                parse_mode="HTML"
            ),
            reply_markup=types.InlineKeyboardMarkup().add(
                types.InlineKeyboardButton("⚡ Botga kirib yuklash", url=f"https://t.me/{bot_username}?start=dl")
            )
        )
        results.append(item)
    else:
        item = types.InlineQueryResultArticle(
            id="help",
            title="💡 Video havolasini yozing",
            description="Masalan: @bot_username https://instagram.com/reel/...",
            input_message_content=types.InputTextMessageContent(
                message_text=f"👋 <b>Universal Video Saver & AI Subtitle Bot</b>\nVideo linkini yuboring!\n\n🤖 @{bot_username}",
                parse_mode="HTML"
            )
        )
        results.append(item)

    bot.answer_inline_query(query.id, results, cache_time=5)

# ==================== BOTNI ISHGA TUSHIRISH ====================
if __name__ == '__main__':
    kill_other_bot_instances()
    ensure_ffmpeg_in_path()
    ffmpeg_loc = shutil.which("ffmpeg") or "Topilmadi (winget install Gyan.FFmpeg)"
    print("=" * 75)
    print("🚀 UNIVERSAL SUPER SAVER & MULTIMEDIA AI TELEGRAM BOT (#1 EDITION)")
    print(f"🎬 FFmpeg holati: {ffmpeg_loc}")
    print(f"👑 Admin Telegram ID: {ADMIN_ID} (@usman_khasan)")
    print("📱 12-Bosqichli VIDEO-FIRST Link Yuklagich: FAOL (Videoni rasm qilib yubormaydi!)")
    print("🎬 Top-1 Pro Reklama Montaj Studiyasi (/montaj, /set_outro — 5 xil rejim + Blurred BG + PiP + Transition FX): FAOL")
    print("🛡 10-Bosqichli Anti-Duplikat (100% Original Video — /original): FAOL")
    print("💧 Tepadan-Pastga Suzuvchi Shaffof Telegram Ikonka + @Handle Watermark (/set_watermark): FAOL")
    print("💱 4-Manbali Markaziy Bank Valyuta Kurslari (/kurs): FAOL")
    print("🧹 Avto-Xotira Tozalagich & Eski jarayonlarni yopish: FAOL")
    print("=" * 75)

    try:
        bot.set_my_commands([
            types.BotCommand("start", "🚀 Botni ishga tushirish"),
            types.BotCommand("montaj", "🎬 Pro Reklama Montaj Studiyasi (5 rejim + Anti-Duplikat)"),
            types.BotCommand("original", "🛡 Videoni 100% Original qilish (Anti-Duplikat)"),
            types.BotCommand("set_outro", "📌 Doimiy reklama (Outro) videoni saqlash"),
            types.BotCommand("set_watermark", "💧 Tepadan-pastga suzuvchi shaffof watermarkni sozlash"),
            types.BotCommand("stat", "📊 Bot va shaxsiy statistika"),
            types.BotCommand("kurs", "💱 Markaziy bank valyuta kurslari"),
            types.BotCommand("profile", "👤 Profilim va ma'lumotlar"),
            types.BotCommand("ai", "🧠 DeepSeek & ChatGPT savol-javob"),
            types.BotCommand("image", "🖼 NanoBanana AI rasm chizish"),
            types.BotCommand("tr", "🌍 AI professional tarjimon"),
            types.BotCommand("qr", "📱 QR-Kod yasash"),
            types.BotCommand("clean", "🧹 Xotirani tozalash")
        ])
    except Exception as e:
        print(f"Menyu komandalarini o'rnatish: {e}")

    try:
        bot.infinity_polling(timeout=35, long_polling_timeout=20)
    except Exception as e:
        print(f"Bot to'xtadi: {e}")