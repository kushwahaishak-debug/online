import os
import sqlite3
import telebot
from flask import Flask
from threading import Thread
from groq import Groq

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
TELEGRAM_TOKEN = "8406846042:AAHhTDtGveACV6PMTOMkHFTqsIQmPUZy7RQ"
GROQ_API_KEY = "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"

USER_PASSWORD = "youbossishere"
ADMIN_PASSWORD = "88"

# ⚠️ MENTOR NOTE: Maine checking ke liye limit 3 kardi hai. 
# Test karne ke baad tu isko wapas 30 kar lena.
FREE_LIMIT = 3 
DB_NAME = "jarvis_database.db"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)
conversation_memory = {}

# ==========================================
# 2. DATABASE MANAGEMENT
# ==========================================
db_conn = sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    cursor = db_conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        chat_id INTEGER PRIMARY KEY,
                        msg_count INTEGER DEFAULT 0,
                        state TEXT DEFAULT 'free'
                      )''')
    db_conn.commit()

def get_or_create_user(chat_id):
    cursor = db_conn.cursor()
    cursor.execute("SELECT msg_count, state FROM users WHERE chat_id = ?", (chat_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.execute("INSERT INTO users (chat_id) VALUES (?)", (chat_id,))
        db_conn.commit()
        return 0, 'free'
    return user[0], user[1]

def update_user_msg_count(chat_id, count):
    cursor = db_conn.cursor()
    cursor.execute("UPDATE users SET msg_count = ? WHERE chat_id = ?", (count, chat_id))
    db_conn.commit()

def update_user_state(chat_id, state, reset_count=False):
    cursor = db_conn.cursor()
    if reset_count:
        cursor.execute("UPDATE users SET state = ?, msg_count = 0 WHERE chat_id = ?", (state, chat_id))
    else:
        cursor.execute("UPDATE users SET state = ? WHERE chat_id = ?", (state, chat_id))
    db_conn.commit()

# ==========================================
# 3. WEB SERVER (RENDER KEEP-ALIVE)
# ==========================================
@app.route('/')
def home():
    return "🚀 Jarvis System is Online!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# ==========================================
# 4. BOT LOGIC & PERSONALITY
# ==========================================
SYSTEM_PROMPT = """
You are Jarvis, a careful, ruthless mentor and an elite IT Manager.

CRITICAL FORMATTING RULES:
1. NEVER use the star/asterisk symbol (*). DO NOT use it for bold text, do not use it for italics, and do not use it for bullet points.
2. If you need to make a list, ONLY use numbers at the start of the line (e.g., 1. 2. 3.). Never place numbers at the end.
3. Keep the text clean, highly structured, and strictly professional.

Your Core Directives:
1. Exact Execution: Provide exactly what the user asks for. 
2. Tough Love & Mental Strength: Be direct, honest, and specific. Give reality checks. Focus on building the user's mindset.
3. Contextual Brevity: For casual greetings ("Hi", "Hello"), give a one-line professional reply. 
4. Language: Speak in a natural, powerful mix of Hindi and English (Hinglish).
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    init_db()
    chat_id = message.chat.id
    count, state = get_or_create_user(chat_id)
    conversation_memory[chat_id] = []

    if state == 'admin':
        msg = "Welcome back, Boss. Memory cleared. System fully unlocked."
    elif state == 'locked':
        msg = "Access Restricted. Quota over. Enter password to proceed."
    else:
        left = FREE_LIMIT - count
        msg = f"Main Jarvis hoon, aapka Mentor aur Manager. Aapke paas {left} free messages hain. Bataiye kya stress-test karna hai?"

    bot.reply_to(message, msg)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()
    init_db()

    current_count, current_state = get_or_create_user(chat_id)

    # LOCKED STATE
    if current_state == 'locked':
        if text == USER_PASSWORD:
            update_user_state(chat_id, 'free', reset_count=True)
            conversation_memory[chat_id] = [] 
            bot.reply_to(message, "Password Verified. Quota reset. Let's work.")
            return
        if text == ADMIN_PASSWORD:
            update_user_state(chat_id, 'admin')
            conversation_memory[chat_id] = []
            bot.reply_to(message, "Admin Override Accepted. Infinite access granted.")
            return
        bot.reply_to(message, "Access Denied. Quota exhausted. Enter correct password.")
        return

    # FREE STATE
    if current_state == 'free':
        if current_count >= FREE_LIMIT:
            update_user_state(chat_id, 'locked')
            bot.reply_to(message, "Limit Exceeded. Action required: Enter the password to continue.")
            return
        update_user_msg_count(chat_id, current_count + 1)

    # MEMORY & API CALL
    if chat_id not in conversation_memory:
        conversation_memory[chat_id] = []

    conversation_memory[chat_id].append({"role": "user", "content": text})

    if len(conversation_memory[chat_id]) > 10:
        conversation_memory[chat_id] = conversation_memory[chat_id][-10:]

    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}] + conversation_memory[chat_id]

    try:
        bot.send_chat_action(chat_id, 'typing')
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_for_api
        )
        reply = completion.choices[0].message.content
        
        # DEFENSE IN DEPTH: Agar AI galti se star bhej bhi de, toh code usko hata dega
        reply = reply.replace("*", "")

        conversation_memory[chat_id].append({"role": "assistant", "content": reply})

        if current_state == 'free':
            if (FREE_LIMIT - (current_count + 1)) == 0:
                reply += "\n\n(Reality Check: This was your final free interaction. System will lock next.)"

        bot.reply_to(message, reply)
    except Exception as e:
        print(f"API Error: {e}", flush=True)
        bot.reply_to(message, "System Error. Network fluctuation hai. Ek minute baad try kar.")

# ==========================================
# 5. BULLETPROOF STARTUP LOGIC
# ==========================================
if __name__ == "__main__":
    try:
        init_db()
        print("Database Initialized.", flush=True)
        Thread(target=run_server, daemon=True).start()
        print("Anti-Crash Web Server Started.", flush=True)
        print("Jarvis is LIVE! Ready for client.", flush=True)
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"FATAL CRASH: {e}", flush=True)
