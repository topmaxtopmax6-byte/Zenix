import os
import logging
import requests
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- RENDER HEALTH CHECK SERVER ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"Zenix Top-Up Bot is alive and running 24/7!")

def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    logger.info(f"Health check server listening on port {port}")
    server.serve_forever()
# ----------------------------------

BOT_TOKEN = "8938472378:AAG_e-nuxPRPeH57S9s1KXbsKOfnwPmy4HI"
SUPPORT_CHANNEL = "https://t.me/zenixtopup1"
SUPPORT_USERNAME = "https://t.me/Zenixsupport12"
ZENIX_STORE_URL = "https://t.me/zenixstore12"

WELCOME_PHOTO_URL = "https://i.ibb.co/L50nLpD/IMG-20261017-163743-753.jpg" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🛒 **ZENIX TOPUP**\n\n"
        "⚡ **24/7 AUTOMATED SERVICE** 🟢\n\n"
        "💎 **WELCOME TO ZENIX TOP-UP BOT** ✨\n\n"
        "👇 **አማራጮቹን ከታች ይምረጡ:**"
    )
    
    keyboard = [
        [InlineKeyboardButton("🕹️ Items", callback_data="items_menu")],
        [InlineKeyboardButton("🛒 Zenix Store", url=ZENIX_STORE_URL)],
        [InlineKeyboardButton("💳 My Balance", callback_data="my_balance")],
        [InlineKeyboardButton("🧾 My Orders", callback_data="my_orders")],
        [InlineKeyboardButton("📢 Our Channel", url=SUPPORT_CHANNEL)],
        [InlineKeyboardButton("🎧 Contact Support", url=SUPPORT_USERNAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_photo(
            photo=WELCOME_PHOTO_URL,
            caption=welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    elif update.callback_query:
        try:
            await update.callback_query.message.delete()
        except Exception:
            pass
        await context.bot.send_photo(
            chat_id=update.callback_query.message.chat_id,
            photo=WELCOME_PHOTO_URL,
            caption=welcome_text,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    back_keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]]
    back_markup = InlineKeyboardMarkup(back_keyboard)

    if query.data == "items_menu":
        games_keyboard = [
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        try:
            await query.message.delete()
        except Exception:
            pass
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="🎮 **ITEMS MENU**\n\nℹ️ ምንም እቃዎች የሉም።",
            reply_markup=InlineKeyboardMarkup(games_keyboard),
            parse_mode="Markdown"
        )

    elif query.data == "my_balance":
        dashboard_text = (
            "💳 **USER DASHBOARD - BALANCE**\n\n"
            f"👤 **User:** {query.from_user.first_name}\n"
            f"🆔 **Telegram ID:** `{query.from_user.id}`\n"
            "💰 **Current Balance:** `0.00 ETB` 🇪🇹"
        )
        await query.message.reply_text(dashboard_text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "my_orders":
        # እዚህ ጋር የጠየቋቸው የትዕዛዝ መረጃዎች (Username, Telegram ID, Game Name, Game ID, Package) በዝርዝር ይወጣሉ
        user = query.from_user
        username = f"@{user.username}" if user.username else "None"
        telegram_id = user.id
        
        # የተጠቃሚውን የትዕዛዝ መረጃ ከ context እንቀበላለን (ከሌለ Default እናደርገዋለን)
        order_data = context.user_data.get("last_order", None)
        
        if order_data:
            game_name = order_data.get("game_name", "N/A")
            game_id = order_data.get("game_id", "N/A")
            package = order_data.get("package", "N/A")
        else:
            game_name = "N/A"
            game_id = "N/A"
            package = "N/A"

        orders_text = (
            "🧾 **YOUR LATEST ORDER (MY ORDERS)**\n\n"
            f"👤 **Telegram Username:** {username}\n"
            f"🆔 **Telegram ID:** `{telegram_id}`\n"
            f"🎮 **Game Name:** {game_name}\n"
            f"🔢 **Game ID:** `{game_id}`\n"
            f"📦 **Game Package:** {package}\n\n"
            "ℹ️ እስካሁን ያደረጉት ትዕዛዝ ይህ ነው።"
        )
        await query.message.reply_text(orders_text, reply_markup=back_markup, parse_mode="Markdown")

    elif query.data == "back_to_menu":
        await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ℹ️ እባክዎ ከላይ ያሉትን ማውጫዎች (Menu) ይጠቀሙ።", parse_mode="Markdown")

def main():
    threading.Thread(target=run_health_server, daemon=True).start()

    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    app = ApplicationBuilder().token(BOT_TOKEN).request(request).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    logger.info("ቦቱ በሰላም 24/7 እየሰራ ነው...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
