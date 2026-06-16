import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


BOT_TOKEN = os.environ.get("BOT_TOKEN")
NUMVERIFY_KEY = os.environ.get("NUMVERIFY_KEY")




async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Namaste! Mujhe koi bhi phone number bhejo (with country code, "
        "e.g. +919876543210), main carrier, location, aur line type bata dunga.\n\n"
        "/help - instructions dekhne ke liye"
    )




async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bas number type karo, country code ke saath. Example:\n+14155552671\n+919876543210"
    )




async def lookup_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    number = update.message.text.strip().replace(" ", "")


    if not NUMVERIFY_KEY:
        await update.message.reply_text("Server config error: NUMVERIFY_KEY missing.")
        return


    await update.message.reply_text("Searching...")


    try:
        resp = requests.get(
            "http://apilayer.net/api/validate",
            params={"access_key": NUMVERIFY_KEY, "number": number},
            timeout=10,
        )
        data = resp.json()
    except Exception as e:
        logger.error(f"API error: {e}")
        await update.message.reply_text("Kuch error aa gaya, baad mein try karo.")
        return


    if not data.get("valid"):
        await update.message.reply_text(
            "Yeh number valid nahi hai ya format galat hai. "
            "Country code ke saath try karo, e.g. +919876543210"
        )
        return


    reply = (
        f"📞 Number: {data.get('international_format', 'N/A')}\n"
        f"🌍 Country: {data.get('country_name', 'N/A')}\n"
        f"📍 Location: {data.get('location', 'N/A') or 'N/A'}\n"
        f"📡 Carrier: {data.get('carrier', 'N/A') or 'N/A'}\n"
        f"📱 Line type: {data.get('line_type', 'N/A') or 'N/A'}"
    )
    await update.message.reply_text(reply)




def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN environment variable not set")


    app = Application.builder().token(BOT_TOKEN).build()


    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lookup_number))


    logger.info("Bot starting...")
    app.run_polling()




if __name__ == "__main__":
    main()