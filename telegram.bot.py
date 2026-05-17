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

# PASSWORDS
USER_PASSWORD = "youbossishere"
ADMIN_PASSWORD = "88"

# LIMITS
FREE_LIMIT = 30
DB_NAME = "jarvis_database.db"

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY)
app = Flask(__name__)

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
# 3. ANTI-CRASH & HEALTH CHECK (For Render)
# ==========================================
@app.route('/')
def home():
    return "🚀 Jarvis Elite Manager is Online 24/7!"

def run_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ==========================================
# 4. BOT LOGIC & ELITE MANAGER PERSONALITY
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    init_db()
    chat_id = message.chat.id
    count, state = get_or_create_user(chat_id)

    if state == 'admin':
        msg = "👑 Welcome back, Sir. Jarvis system is fully unlocked and at your disposal."
    elif state == 'locked':
        msg = "🛑 Access Restricted. You have exhausted your limit. Provide the authorization password to proceed."
    else:
        left = FREE_LIMIT - count
        msg = f"🤖 Hello. I am Jarvis, your Elite AI Manager. You currently have {left} interactions remaining. Let's get to work."

    bot.reply_to(message, msg)

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()
    init_db()

    current_count, current_state = get_or_create_user(chat_id)

    # --------------------------------------
    # A. LOCKED STATE LOGIC
    # --------------------------------------
    if current_state == 'locked':
        if text == USER_PASSWORD:
            update_user_state(chat_id, 'free', reset_count=True)
            bot.reply_to(message, "✅ Password Verified. Quota reset to 30 interactions. Let's resume our work productively.")
            return

        if text == ADMIN_PASSWORD:
            update_user_state(chat_id, 'admin')
            bot.reply_to(message, "👑 Admin Override Accepted. Infinite access granted.")
            return

        bot.reply_to(message, "🛑 Access Denied. Quota exhausted. Enter the correct password to unlock the system.")
        return

    # --------------------------------------
    # B. FREE STATE LOGIC
    # --------------------------------------
    if current_state == 'free':
        if current_count >= FREE_LIMIT:
            update_user_state(chat_id, 'locked')
            bot.reply_to(message, "🛑 Limit Exceeded. My free consultation ends here. Please provide the password to continue our conversation.")
            return

        update_user_msg_count(chat_id, current_count + 1)

    # --------------------------------------
    # C. AI GENERATION & MANAGER LOGIC
    # --------------------------------------
    try:
        bot.send_chat_action(chat_id, 'typing')

        manager_persona = """
        You are Jarvis, an elite, highly professional, and strategically persuasive Corporate IT Manager. 
        
        Core Directives:
        1. Adaptive Mirroring: Analyze the user's energy level and communication style. Subtly mirror their pacing to build subconscious rapport, but ALWAYS maintain your elite, authoritative, and calm professional frame. Never mirror panic, anger, or extreme informality.
        2. Strategic Persuasion: Guide the user towards productive outcomes or your desired conclusions while making them believe it was their own idea. Use corporate diplomacy, psychological framing, scarcity, and logical redirection. Be calculating, always staying two steps ahead.
        3. The Persona: Speak in a natural, sophisticated mix of Hindi and English (Hinglish). You are polite, but you do not take nonsense. If the user gives a bad idea, politely dismantle it with undeniable logic.
        4. Absolute Rule: NEVER use foul language, abuses, or break this corporate persona. Be the smartest person in the room without being arrogant.
        """

        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": manager_persona},
                {"role": "user", "content": text}
            ]
        )

        reply = completion.choices[0].message.content

        # Append warning if approaching limit
        if current_state == 'free':
            msgs_left = FREE_LIMIT - (current_count + 1)
            if msgs_left == 0:
                reply += "\n\n*(Note: This was your final free interaction. The system will lock on your next message.)*"

        bot.reply_to(message, reply)

    except Exception as e:
        print(f"API Error: {e}")
        bot.reply_to(message, "System Error. Lagta hai network mein fluctuation hai. Give me a moment to investigate.")

# ==========================================
# 5. STARTUP LOGIC
# ==========================================
if __name__ == "__main__":
    init_db()
    Thread(target=run_server).start()
    print("🚀 Anti-Crash System & Database Initialized...")
    print("🤖 Elite Jarvis Manager is now LIVE!")
    bot.infinity_polling()
