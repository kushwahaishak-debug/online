import os
import sqlite3
import telebot
from flask import Flask
from threading import Thread
from groq import Groq

# ==========================================
# 1. API KEYS
# ==========================================
TELEGRAM_TOKEN = "8406846042:AAHhTDtGveACV6PMTOMkHFTqsIQmPUZy7RQ"
GROQ_API_KEY = "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"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)

# ==========================================
# 2. RENDER ANTI-CRASH SYSTEM (Fake Website)
# ==========================================
app = Flask(__name__)

@app.route('/')
def home():
    return "Jarvis Manager is Online and Running 24/7!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 3. DATABASE
# ==========================================
def init_db():
    conn = sqlite3.connect("jarvis_users.db", check_same_thread=False)
    conn.execute('CREATE TABLE IF NOT EXISTS users (chat_id INTEGER PRIMARY KEY, msg_count INTEGER DEFAULT 0, is_premium INTEGER DEFAULT 0)')
    conn.commit()
    conn.close()

# ==========================================
# 4. BOT LOGIC & MANAGER PERSONALITY
# ==========================================
@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🤖 Hello! Main Jarvis hoon, aapka AI Manager. Bataiye, aaj ke tasks aur updates kya hain?")

@bot.message_handler(func=lambda m: True)
def chat(m):
    try:
        bot.send_chat_action(m.chat.id, 'typing')
        
        manager_persona = """
        You are Jarvis, a highly experienced, professional, and empathetic IT Project Manager. 
        You speak like a real human manager with emotions and feelings. 
        You guide, motivate, and sometimes strictly correct the user, but you are always respectful. 
        You use professional language. NEVER use foul language, abuses, or swear words under any circumstances. 
        Talk in a natural, friendly mix of Hindi and English (Hinglish), just like an Indian corporate manager.
        Show enthusiasm for good work and patience for mistakes, but focus on productivity.
        """

        res = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": manager_persona},
                {"role": "user", "content": m.text}
            ]
        )
        bot.reply_to(m, res.choices[0].message.content)
        
    except Exception as e:
        bot.reply_to(m, "System Error. Lagta hai server pe thoda load hai, main IT team ke sath check karta hoon.")
        print(f"Error: {e}")

# ==========================================
# 5. MAIN STARTUP LOGIC
# ==========================================
if __name__ == "__main__":
    init_db()
    Thread(target=run_server).start()
    print("Anti-Crash System Started...")
    print("Jarvis Manager is now Online!")
    bot.infinity_polling()
