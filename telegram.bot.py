import os
import sqlite3
import telebot
from flask import Flask
from threading import Thread
from groq import Groq

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
# ⚠️ DANGER ZONE: KEEP REPOSITORY PRIVATE
TELEGRAM_TOKEN = "8406846042:AAHhTDtGveACV6PMTOMkHFTqsIQmPUZy7RQ"
GROQ_API_KEY = "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"

USER_PASSWORD = "youbossishere"
ADMIN_PASSWORD = "88"
FREE_LIMIT = 30
DB_NAME = "jarvis_database.db"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

# ==========================================
# 2. IN-MEMORY CONVERSATION STORAGE
# ==========================================
# Ye dictionary users ki baatein yaad rakhegi
conversation_memory = {}

# ==========================================
# 3. DATABASE MANAGEMENT (Limits track karne ke liye)
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
# 4. ANTI-CRASH SYSTEM (Render)
# ==========================================
@app.route('/')
def home():
    return "🚀 Jarvis Elite Mentor is Online 24/7!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 5. BOT LOGIC & ELITE MENTOR PERSONALITY
# ==========================================
SYSTEM_PROMPT = """
You are Jarvis, a careful, ruthless mentor and an elite IT Manager.
Your Core Directives:
1. Exact Execution: If the user asks for a specific length (e.g., 5 lines, 10 lines, 2 paragraphs), you MUST provide exactly that. Do not overwrite or underwrite.
2. Structure & Clarity: Use bullet points, bold text, and numbered lists to make your answers bulletproof and easy to scan. Ask hard questions before giving solutions.
3. Tough Love & Mental Strength: Be direct, honest, and specific. Prioritize truth over tone. If the user is stressed or has a weak idea, give them immense mental strength, validate their emotions, but gently correct their misconceptions with reality. Stand strong like a pillar.
4. Contextual Brevity: For casual greetings ("Hi", "Hello"), give a one-line professional reply. Keep detailed analysis only for real queries.
5. Language: Speak in a natural, powerful mix of Hindi and English (Hinglish). Never use foul language. You do not just write code or text; you build the user's mindset.
"""

@bot.message_handler(commands=['start'])
def send_welcome(message):
    init_db()
    chat_id = message
