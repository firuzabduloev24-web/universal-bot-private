import os
import sys
import time
import sqlite3
import telebot
from telebot import types

# ----------------- SOZLAMALAR (CONFIG) -----------------
TOKEN = os.getenv("BOT_TOKEN", "8863390415:AAEj3E_H-Kv36OF9gb0pGJOXMvQd5KldSgQ")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1021089367"))

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ----------------- MA'LUMOTLAR BAZASI (SQLITE) -----------------
DB_PATH = "ish_topish.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # Foydalanuvchilar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            role TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Rezyumelar (Ish qidiruvchilar)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            full_name TEXT,
            age TEXT,
            profession TEXT,
            experience TEXT,
            salary TEXT,
            phone TEXT,
            region TEXT,
            about TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Vakansiyalar (Ish beruvchilar)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER,
            company_name TEXT,
            job_title TEXT,
            salary TEXT,
            requirements TEXT,
            region TEXT,
            contact TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Arizalar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vacancy_id INTEGER,
            seeker_id INTEGER,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Sozlamalar (Sponsor matni va boshqalar)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ----------------- DATABASE YORDAMCHI FUNKSIYALARI -----------------
def get_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id, username, full_name, role FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

def save_user(user_id, username, full_name, role=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (user_id, username, full_name, role)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username=excluded.username,
            full_name=excluded.full_name,
            role=COALESCE(excluded.role, users.role)
    """, (user_id, username, full_name, role))
    conn.commit()
    conn.close()

def set_user_role(user_id, role):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
    conn.commit()
    conn.close()

def get_sponsor():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = 'sponsor'")
    row = cur.fetchone()
    conn.close()
    return row[0] if row else ""

def set_sponsor(text):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO settings (key, value) VALUES ('sponsor', ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (text,))
    conn.commit()
    conn.close()

def get_resume(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row

def delete_resume(user_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM resumes WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()

def get_active_vacancies():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM vacancies WHERE status = 'active' ORDER BY id DESC LIMIT 30")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_resumes():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM resumes ORDER BY id DESC LIMIT 30")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_employer_vacancies(employer_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM vacancies WHERE employer_id = ? ORDER BY id DESC", (employer_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def log_admin(text):
    try:
        bot.send_message(ADMIN_ID, f"🔔 <b>Admin Bildirishnomasi:</b>\n{text}")
    except Exception as e:
        print(f"Admin log xatosi: {e}")

# ----------------- KLAVIATURALAR (MENYU) -----------------
def role_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("👨‍💻 Ish qidiruvchi", "🏢 Ish beruvchi")
    return markup

def seeker_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔍 Vakansiyalarni ko'rish", "📄 Mening rezyumem")
    markup.add("➕ Rezyume yaratish", "🔄 Rolni o'zgartirish")
    return markup

def employer_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("📢 Vakansiya joylash", "📋 Mening vakansiyalarim")
    markup.add("👥 Rezyumelarni ko'rish", "🔄 Rolni o'zgartirish")
    return markup

def cancel_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("❌ Bekor qilish")
    return markup

# ----------------- /START KOMANDASI -----------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "Foydalanuvchi"
    
    user = get_user(user_id)
    if not user:
        save_user(user_id, username, full_name)
        log_admin(f"Yangi foydalanuvchi kirdi:\n👤 {full_name} (@{username})\n🆔 ID: <code>{user_id}</code>")
    
    sponsor = get_sponsor()
    sponsor_msg = f"\n\n📢 <i>{sponsor}</i>" if sponsor else ""
    
    welcome_text = (
        f"Assalomu alaykum, <b>{full_name}</b>!\n\n"
        f"🤝 <b>Ish topish va Ish berish</b> botiga xush kelibsiz!\n"
        f"Bu yerda siz o'zingizga munosib ish yoki malakali xodim topishingiz mumkin.{sponsor_msg}\n\n"
        f"Iltimos, o'z maqomingizni tanlang:"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=role_keyboard())

# ----------------- ROLNI TANLASH VA O'ZGARTIRISH -----------------
@bot.message_handler(func=lambda m: m.text in ["👨‍💻 Ish qidiruvchi", "🏢 Ish beruvchi", "🔄 Rolni o'zgartirish"])
def handle_role(message):
    user_id = message.from_user.id
    if message.text == "🔄 Rolni o'zgartirish":
        bot.send_message(message.chat.id, "Iltimos, yangi rolingizni tanlang:", reply_markup=role_keyboard())
        return

    if message.text == "👨‍💻 Ish qidiruvchi":
        set_user_role(user_id, "seeker")
        bot.send_message(
            message.chat.id,
            "✅ Siz <b>Ish qidiruvchi</b> bo'limidasiz.\n"
            "Mavjud bo'sh ish o'rinlarini ko'rishingiz yoki ish beruvchilar sizni topishi uchun rezyume qoldirishingiz mumkin.",
            reply_markup=seeker_menu()
        )
    elif message.text == "🏢 Ish beruvchi":
        set_user_role(user_id, "employer")
        bot.send_message(
            message.chat.id,
            "✅ Siz <b>Ish beruvchi</b> bo'limidasiz.\n"
            "Yangi vakansiya e'lon qilishingiz yoki nomzodlar rezyumelarini ko'rishingiz mumkin.",
            reply_markup=employer_menu()
        )

# ----------------- REZYUME VA VAKANSIYA STATE -----------------
user_states = {}

@bot.message_handler(func=lambda m: m.text == "➕ Rezyume yaratish")
def start_resume(message):
    user_id = message.from_user.id
    res = get_resume(user_id)
    if res:
        bot.send_message(
            message.chat.id,
            "⚠️ Sizda allaqachon rezyume mavjud! Yangi rezyume kiritishdan oldin eskisini 'Mening rezyumem' bo'limidan o'chirishingiz mumkin.",
            reply_markup=seeker_menu()
        )
        return
    
    user_states[user_id] = {"step": "res_name", "data": {}}
    bot.send_message(message.chat.id, "📝 <b>1/8. To'liq ism-sharifingizni kiriting:</b>\n<i>(Masalan: Alisher Valiyev)</i>", reply_markup=cancel_keyboard())

@bot.message_handler(func=lambda m: m.text == "📢 Vakansiya joylash")
def start_vacancy(message):
    user_id = message.from_user.id
    user_states[user_id] = {"step": "vac_company", "data": {}}
    bot.send_message(message.chat.id, "📢 <b>1/6. Korxona yoki kompaniya nomini kiriting:</b>\n<i>(Masalan: 'Grand Stroy' MCHJ yoki Shaxsiy)</i>", reply_markup=cancel_keyboard())

@bot.message_handler(func=lambda m: m.from_user.id in user_states)
def handle_steps(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == "❌ Bekor qilish":
        user = get_user(user_id)
        role = user[3] if user else "seeker"
        del user_states[user_id]
        menu = seeker_menu() if role == "seeker" else employer_menu()
        bot.send_message(message.chat.id, "❌ Amal bekor qilindi.", reply_markup=menu)
        return

    state = user_states[user_id]
    step = state["step"]
    data = state["data"]

    # Rezyume
    if step == "res_name":
        data["name"] = text
        state["step"] = "res_age"
        bot.send_message(message.chat.id, "🎂 <b>2/8. Yoshingizni kiriting:</b>\n<i>(Masalan: 24)</i>")
    elif step == "res_age":
        data["age"] = text
        state["step"] = "res_prof"
        bot.send_message(message.chat.id, "💼 <b>3/8. Mutaxassisligingiz / Kasbingiz:</b>\n<i>(Masalan: Python Dasturchi, Sotuvchi, Haydovchi)</i>")
    elif step == "res_prof":
        data["prof"] = text
        state["step"] = "res_exp"
        bot.send_message(message.chat.id, "⏳ <b>4/8. Ish tajribangiz:</b>\n<i>(Masalan: 2 yil, Tajribasiz, 5 yildan ortiq)</i>")
    elif step == "res_exp":
        data["exp"] = text
        state["step"] = "res_salary"
        bot.send_message(message.chat.id, "💰 <b>5/8. Kutilayotgan maosh (oylik):</b>\n<i>(Masalan: 5 000 000 so'm yoki Kelishilgan)</i>")
    elif step == "res_salary":
        data["salary"] = text
        state["step"] = "res_region"
        bot.send_message(message.chat.id, "📍 <b>6/8. Viloyatingiz yoki shahringiz:</b>\n<i>(Masalan: Toshkent shahri)</i>")
    elif step == "res_region":
        data["region"] = text
        state["step"] = "res_phone"
        bot.send_message(message.chat.id, "📞 <b>7/8. Bog'lanish uchun telefon raqamingiz:</b>\n<i>(Masalan: +998901234567)</i>")
    elif step == "res_phone":
        data["phone"] = text
        state["step"] = "res_about"
        bot.send_message(message.chat.id, "✍️ <b>8/8. O'zingiz haqingizda qo'shimcha ma'lumot:</b>\n<i>(Biladigan tillaringiz, qobiliyatlaringiz yoki kompyuter dasturlari)</i>")
    elif step == "res_about":
        data["about"] = text
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO resumes (user_id, full_name, age, profession, experience, salary, phone, region, about)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, data["name"], data["age"], data["prof"], data["exp"], data["salary"], data["phone"], data["region"], data["about"]))
        conn.commit()
        conn.close()
        del user_states[user_id]
        bot.send_message(
            message.chat.id,
            "🎉 <b>Rezyume muvaffaqiyatli saqlandi!</b>\nEndi ish beruvchilar sizning rezyumengizni ko'ra oladilar.",
            reply_markup=seeker_menu()
        )
        log_admin(f"📄 Yangi Rezyume:\n👤 {data['name']}, {data['age']} yosh\n💼 Kasbi: {data['prof']}\n📍 Joyi: {data['region']}\n💰 Maosh: {data['salary']}")

    # Vakansiya
    elif step == "vac_company":
        data["company"] = text
        state["step"] = "vac_title"
        bot.send_message(message.chat.id, "💼 <b>2/6. Qanday kasb/lavozimga xodim kerak:</b>\n<i>(Masalan: Administrator, Grafik Dizayner, Oshpaz)</i>")
    elif step == "vac_title":
        data["title"] = text
        state["step"] = "vac_salary"
        bot.send_message(message.chat.id, "💰 <b>3/6. Taklif qilinayotgan oylik maosh:</b>\n<i>(Masalan: 4 000 000 - 6 000 000 so'm yoki Suhbat asosida)</i>")
    elif step == "vac_salary":
        data["salary"] = text
        state["step"] = "vac_req"
        bot.send_message(message.chat.id, "📋 <b>4/6. Nomzodga qo'yiladigan asosiy talablar:</b>\n<i>(Masalan: Rus tilini bilish, 1 yillik tajriba, mas'uliyatlilik)</i>")
    elif step == "vac_req":
        data["req"] = text
        state["step"] = "vac_region"
        bot.send_message(message.chat.id, "📍 <b>5/6. Ish joylashgan manzil (Shahar/Tuman):</b>\n<i>(Masalan: Toshkent sh., Chilonzor tumani)</i>")
    elif step == "vac_region":
        data["region"] = text
        state["step"] = "vac_contact"
        bot.send_message(message.chat.id, "📞 <b>6/6. Bog'lanish uchun telefon yoki Telegram username:</b>\n<i>(Masalan: +998901234567 yoki @username)</i>")
    elif step == "vac_contact":
        data["contact"] = text
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO vacancies (employer_id, company_name, job_title, salary, requirements, region, contact)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, data["company"], data["title"], data["salary"], data["req"], data["region"], data["contact"]))
        vac_id = cur.lastrowid
        conn.commit()
        conn.close()
        del user_states[user_id]
        bot.send_message(
            message.chat.id,
            "🎉 <b>Vakansiyangiz muvaffaqiyatli e'lon qilindi!</b>\nNomzodlar uni ko'rishadi va ariza topshirishlari mumkin.",
            reply_markup=employer_menu()
        )
        log_admin(f"📢 Yangi Vakansiya #{vac_id}:\n🏢 Kompaniya: {data['company']}\n💼 Lavozim: {data['title']}\n💰 Maosh: {data['salary']}\n📍 Joylashuv: {data['region']}")

# ----------------- REZYUMENI KO'RISH -----------------
@bot.message_handler(func=lambda m: m.text == "📄 Mening rezyumem")
def view_my_resume(message):
    user_id = message.from_user.id
    res = get_resume(user_id)
    if not res:
        bot.send_message(
            message.chat.id,
            "Sizda hali rezyume yo'q. '➕ Rezyume yaratish' tugmasi orqali rezyume yarating!",
            reply_markup=seeker_menu()
        )
        return
    
    res_text = (
        f"📄 <b>Sizning Rezyumengiz:</b>\n\n"
        f"👤 <b>F.I.SH:</b> {res[2]}\n"
        f"🎂 <b>Yoshi:</b> {res[3]}\n"
        f"💼 <b>Kasbi:</b> {res[4]}\n"
        f"⏳ <b>Tajriba:</b> {res[5]}\n"
        f"💰 <b>Kutilayotgan maosh:</b> {res[6]}\n"
        f"📍 <b>Hudud:</b> {res[8]}\n"
        f"📞 <b>Aloqa:</b> {res[7]}\n"
        f"✍️ <b>Qo'shimcha:</b> {res[9]}\n"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🗑 O'chirish", callback_data=f"del_res_{res[0]}"))
    bot.send_message(message.chat.id, res_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_res_"))
def callback_del_resume(call):
    user_id = call.from_user.id
    delete_resume(user_id)
    bot.answer_callback_query(call.id, "Rezyume o'chirildi!")
    bot.edit_message_text("🗑 Rezyumengiz muvaffaqiyatli o'chirildi.", chat_id=call.message.chat.id, message_id=call.message.message_id)

# ----------------- VAKANSIYALARNI KO'RISH -----------------
@bot.message_handler(func=lambda m: m.text == "🔍 Vakansiyalarni ko'rish")
def list_vacancies(message):
    vacancies = get_active_vacancies()
    if not vacancies:
        bot.send_message(message.chat.id, "Hozircha faol ish o'rinlari mavjud emas. Tez orada yangi e'lonlar qo'shiladi!", reply_markup=seeker_menu())
        return
    
    bot.send_message(message.chat.id, f"📋 <b>Eng so'nggi vakansiyalar (Jami: {len(vacancies)} ta):</b>")
    sponsor = get_sponsor()
    sponsor_msg = f"\n📢 <i>{sponsor}</i>\n" if sponsor else ""
    
    for vac in vacancies[:10]:
        vac_text = (
            f"💼 <b>Lavozim: {vac[3]}</b>\n"
            f"🏢 <b>Korxona:</b> {vac[2]}\n"
            f"💰 <b>Maosh:</b> {vac[4]}\n"
            f"📍 <b>Hudud:</b> {vac[6]}\n"
            f"📋 <b>Talablar:</b> {vac[5]}\n"
            f"📞 <b>Aloqa:</b> {vac[7]}\n"
            f"{sponsor_msg}"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📝 Ariza topshirish", callback_data=f"apply_{vac[0]}"))
        bot.send_message(message.chat.id, vac_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("apply_"))
def apply_vacancy(call):
    vac_id = int(call.data.split("_")[1])
    seeker_id = call.from_user.id
    
    resume = get_resume(seeker_id)
    if not resume:
        bot.answer_callback_query(call.id, "Avval 'Mening rezyumem' bo'limida rezyume yarating!", show_alert=True)
        return
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT employer_id, job_title, company_name FROM vacancies WHERE id = ?", (vac_id,))
    vac = cur.fetchone()
    
    if not vac:
        bot.answer_callback_query(call.id, "Bu vakansiya topilmadi yoki yopilgan.", show_alert=True)
        conn.close()
        return

    cur.execute("SELECT id FROM applications WHERE vacancy_id = ? AND seeker_id = ?", (vac_id, seeker_id))
    if cur.fetchone():
        bot.answer_callback_query(call.id, "Siz bu vakansiyaga allaqachon ariza topshirgansiz!", show_alert=True)
        conn.close()
        return
    
    cur.execute("INSERT INTO applications (vacancy_id, seeker_id) VALUES (?, ?)", (vac_id, seeker_id))
    conn.commit()
    conn.close()
    
    bot.answer_callback_query(call.id, "Arizangiz ish beruvchiga yuborildi!", show_alert=True)
    
    employer_id, job_title, company = vac
    notify_text = (
        f"📬 <b>Sizning vakansiyangizga yangi ariza keldi!</b>\n\n"
        f"💼 <b>Vakansiya:</b> {job_title} ({company})\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Nomzod:</b> {resume[2]} ({resume[3]} yosh)\n"
        f"💼 <b>Kasbi:</b> {resume[4]}\n"
        f"⏳ <b>Tajribasi:</b> {resume[5]}\n"
        f"💰 <b>Kutilayotgan oylik:</b> {resume[6]}\n"
        f"📍 <b>Hudud:</b> {resume[8]}\n"
        f"📞 <b>Telefon:</b> {resume[7]}\n"
        f"✍️ <b>Qo'shimcha:</b> {resume[9]}"
    )
    try:
        bot.send_message(employer_id, notify_text)
    except Exception as e:
        print(f"Ish beruvchiga yuborishda xato: {e}")

# ----------------- ISH BERUVCHI MENYUSI -----------------
@bot.message_handler(func=lambda m: m.text == "📋 Mening vakansiyalarim")
def my_vacancies(message):
    user_id = message.from_user.id
    vacancies = get_employer_vacancies(user_id)
    if not vacancies:
        bot.send_message(message.chat.id, "Siz hali birorta ham vakansiya e'lon qilmadingiz.", reply_markup=employer_menu())
        return
    
    for vac in vacancies:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM applications WHERE vacancy_id = ?", (vac[0],))
        app_count = cur.fetchone()[0]
        conn.close()
        
        text = (
            f"💼 <b>Lavozim:</b> {vac[3]}\n"
            f"🏢 <b>Korxona:</b> {vac[2]}\n"
            f"💰 <b>Maosh:</b> {vac[4]}\n"
            f"📍 <b>Hudud:</b> {vac[6]}\n"
            f"📊 <b>Kelib tushgan arizalar:</b> {app_count} ta\n"
            f"Holati: <b>{'Faol' if vac[8] == 'active' else 'Yopilgan'}</b>"
        )
        markup = types.InlineKeyboardMarkup()
        if vac[8] == 'active':
            markup.add(types.InlineKeyboardButton("🚫 E'lonni yopish", callback_data=f"close_vac_{vac[0]}"))
        bot.send_message(message.chat.id, text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("close_vac_"))
def close_vacancy(call):
    vac_id = int(call.data.split("_")[2])
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE vacancies SET status = 'closed' WHERE id = ?", (vac_id,))
    conn.commit()
    conn.close()
    bot.answer_callback_query(call.id, "Vakansiya yopildi!")
    bot.edit_message_text(f"🚫 Vakansiya #{vac_id} yopildi va qidiruvdan olib tashlandi.", chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.message_handler(func=lambda m: m.text == "👥 Rezyumelarni ko'rish")
def list_resumes(message):
    resumes = get_all_resumes()
    if not resumes:
        bot.send_message(message.chat.id, "Hozircha nomzodlar bazasida rezyumelar mavjud emas.", reply_markup=employer_menu())
        return
    
    bot.send_message(message.chat.id, f"👥 <b>Nomzodlar bazasi (Jami: {len(resumes)} ta):</b>")
    for res in resumes[:10]:
        res_text = (
            f"👤 <b>Nomzod:</b> {res[2]} ({res[3]} yosh)\n"
            f"💼 <b>Mutaxassisligi:</b> {res[4]}\n"
            f"⏳ <b>Tajriba:</b> {res[5]}\n"
            f"💰 <b>Kutilayotgan maosh:</b> {res[6]}\n"
            f"📍 <b>Hudud:</b> {res[8]}\n"
            f"📞 <b>Aloqa:</b> {res[7]}\n"
            f"✍️ <b>Ma'lumot:</b> {res[9]}"
        )
        bot.send_message(message.chat.id, res_text)

# ----------------- ADMIN BUYRUQLARI -----------------
@bot.message_handler(commands=['stat'])
def admin_stats(message):
    if message.from_user.id != ADMIN_ID:
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    u_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM resumes")
    r_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM vacancies")
    v_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM applications")
    a_count = cur.fetchone()[0]
    conn.close()

    text = (
        f"📊 <b>Bot Statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{u_count}</b> ta\n"
        f"📄 Rezyumelar: <b>{r_count}</b> ta\n"
        f"💼 Vakansiyalar: <b>{v_count}</b> ta\n"
        f"📬 Arizalar: <b>{a_count}</b> ta"
    )
    bot.send_message(message.chat.id, text)

@bot.message_handler(commands=['sponsor'])
def admin_sponsor(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        cur_sp = get_sponsor()
        bot.send_message(message.chat.id, f"Hozirgi homiy matni:\n'{cur_sp}'\n\nO'zgartirish: <code>/sponsor matn</code>\nO'chirish: <code>/sponsor off</code>")
    else:
        arg = parts[1].strip()
        if arg.lower() == "off":
            set_sponsor("")
            bot.send_message(message.chat.id, "✅ Homiy matni o'chirildi.")
        else:
            set_sponsor(arg)
            bot.send_message(message.chat.id, f"✅ Homiy matni saqlandi:\n'{arg}'")

@bot.message_handler(commands=['send'])
def admin_send(message):
    if message.from_user.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) == 1:
        bot.send_message(message.chat.id, "Xabar matnini kiriting. Masalan: <code>/send Yangilik!</code>")
        return
    text = parts[1]
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    conn.close()

    sent = 0
    bot.send_message(message.chat.id, f"Xabar {len(users)} ta foydalanuvchiga yuborilmoqda...")
    for (u_id,) in users:
        try:
            bot.send_message(u_id, text)
            sent += 1
            time.sleep(0.04)
        except Exception:
            pass
    bot.send_message(message.chat.id, f"✅ Xabar {sent} ta foydalanuvchiga muvaffaqiyatli yetkazildi!")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Ish topish va ish berish boti ishga tushirildi!")
    print(f"Admin ID: {ADMIN_ID}")
    print("=" * 50)
    while True:
        try:
            bot.infinity_polling(timeout=20, long_polling_timeout=10)
        except Exception as err:
            print(f"Xatolik: {err}. 5 soniyadan so'ng qayta ishga tushiriladi...")
            time.sleep(5)
