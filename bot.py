import sqlite3
from telegram import Update, WebAppInfo, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Replace with your actual bot token and Telegram User ID
TOKEN = "8821949588:AAE-vjau8wbmto9NcSdWlJau-kfEh_wP21g"
ADMIN_ID = 123456789  

# --- 1. Database Setup (Wallet System) ---
def setup_db():
    conn = sqlite3.connect('bingo.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, balance REAL)''')
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = sqlite3.connect('bingo.db')
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = c.fetchone()
    if not result:
        c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0.0))
        conn.commit()
        result = (0.0,)
    conn.close()
    return result[0]

def update_balance(user_id, amount):
    balance = get_balance(user_id)
    new_balance = balance + amount
    conn = sqlite3.connect('bingo.db')
    c = conn.cursor()
    c.execute("UPDATE users SET balance=? WHERE user_id=?", (new_balance, user_id))
    conn.commit()
    conn.close()
    return new_balance

# --- 2. Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = get_balance(user_id)
    
    # Button to launch the Mini App (Requires a hosted HTTPS webpage)
    web_app_url = "https://test994101.github.io/maya-bingo1/" 
    keyboard = [[InlineKeyboardButton("Play Bingo", web_app=WebAppInfo(url=web_app_url))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Welcome to Telegram Bingo!\nYour Wallet Balance: ${balance}",
        reply_markup=reply_markup
    )

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # In a real app, this links to a payment gateway
    await update.message.reply_text("To deposit, send funds to [Payment Link] and message the Admin.")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = get_balance(user_id)
    await update.message.reply_text(f"Your balance is ${balance}. Contact Admin to request a withdrawal.")

# --- 3. Admin System ---
async def admin_add_funds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Unauthorized.")
        return
    
    try:
        # Command format: /addfunds [user_id] [amount]
        target_user = int(context.args[0])
        amount = float(context.args[1])
        new_balance = update_balance(target_user, amount)
        await update.message.reply_text(f"Success. User {target_user} now has ${new_balance}.")
    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /addfunds [user_id] [amount]")

# --- 4. Launch Bot ---
if __name__ == '__main__':
    setup_db()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("withdraw", withdraw))
    app.add_handler(CommandHandler("addfunds", admin_add_funds))
    
    print("Bot is running...")
    app.run_polling()
