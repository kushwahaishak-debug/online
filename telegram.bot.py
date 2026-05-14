import telebot

# ==========================================
# 🛑 MANAGER'S AUTO-FILE GENERATOR 🛑
# Yeh code khud teri CSV file bana dega!
# ==========================================
sample_data = """Product_Name,Price,Stock
iPhone 15 Pro,$999,In Stock
Sony Headphones,$250,Low Stock
Nike Sneakers,$120,In Stock
"""
# File create aur save ho rahi hai
with open("Free_Sample.csv", "w") as file:
    file.write(sample_data)
print("✅ Manager: 'Free_Sample.csv' Ready!")

# ==========================================
# 🤖 BOT KA ASLI ENGINE 🤖
# ==========================================

# YAHAN APNA TOKEN PASTE KAR (Inverted commas ' ' ke andar)
API_TOKEN = '8347331722:AAGCo-R2trbp98Wgw_Ko6xy3tVR2YPR3O5o'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = "Hello! Main Yourseller ka personal bot hu. 🤖\n\nCheck my commands:\n/sample - Free mein thoda data text mein dekho\n/getfile - Free sample CSV file download karo 📂\n/buy - Poora 1000+ Premium Dataset kharido 🔥"
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['sample'])
def send_sample(message):
    bot.reply_to(message, "📦 *FREE SAMPLE DATA* 📦\n1. iPhone 15 Pro | $999\n2. Sony Headphones | $250\n\nAsli CSV file chahiye toh /getfile type karo!", parse_mode='Markdown')

@bot.message_handler(commands=['buy'])
def send_buy_link(message):
    bot.reply_to(message, "🔥 *PREMIUM E-COMMERCE LEADS* 🔥\nPrice: $10 Only!\n\nLink: [Coming Soon... Dukan ready ho rahi hai!]", parse_mode='Markdown')

@bot.message_handler(commands=['getfile'])
def send_free_file(message):
    bot.reply_to(message, "Ruko bhai, tumhara free sample CSV nikal raha hu... 📂")
    try:
        doc = open('Free_Sample.csv', 'rb')
        bot.send_document(message.chat.id, doc)
        bot.send_message(message.chat.id, "Yeh sirf trailer tha! Baki ke 980+ leads chahiye toh /buy type karo! 🔥")
    except Exception as e:
        bot.reply_to(message, "⚠️ Error aa gaya bhai.")

print("🚀 Manager: Salesman Bot is ONLINE... Grahak lao!")
bot.polling()