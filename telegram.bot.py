import os
import sqlite3
import telebot
from flask import Flask
from threading import Thread
from groq import Groq

# ==========================================
# 1. API KEYS (APNI KEYS YAHAN DALO)
# ==========================================
TELEGRAM_TOKEN = "8406846042:AAHhTDtGveACV6PMTOMkHFTqsIQmPUZy7RQ"
GROQ_API_KEY = "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"
ADMIN_USERNAME = "ishankushwaha"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. RENDER ANTI-CRASH SYSTEM (Fake Website)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Jarvis Bot is Online and Running 24/7!"

def run_server():
    # Render jo bhi port dega, hum use yahan catch kar lenge
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 3. DATABASE
# ==========================================
def init_db():
    conn = sqlite3.connect("jarvis_users.db")
    conn.execute('CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, msg_count INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# ==========================================
# 4. BOT LOGIC
# ==========================================
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🤖 Jarvis System Online 24/7!")

@bot.message_handler(func=lambda m: True)
def chat(m):
    try:
        bot.send_chat_action(m.chat.id, 'typing')
        # Groq AI call
        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": m.text}]
        )
        bot.reply_to(m, res.choices[0].message.content)
    except Exception as e:
        bot.reply_to(m, "System Error. Main abhi thoda busy hoon.")

# ==========================================
# 5. MAIN STARTUP
# ==========================================
if __name__ == "__main__":
    init_db()
    # 1. Render ko khush rakhne ke liye website start karo
    Thread(target=run_server).start()
    print("Anti-Crash System Started...")
    
    # 2. Asli kaam: Bot start karo
    print("Jarvis Bot Started...")
    bot.infinity_polling()
