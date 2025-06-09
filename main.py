from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN
from InsuranceBot import InsuranceBot
from database import ChatHistoryDB
import asyncio
import aiohttp
import os

async def ping_server():
    if "RENDER_EXTERNAL_URL" in os.environ:
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    url = os.environ["RENDER_EXTERNAL_URL"]
                    async with session.get(url) as response:
                        print(f"Ping server response: {response.status}")
                except Exception as e:
                    print(f"Ping error: {e}")
                await asyncio.sleep(60 * 14)  # Ping every 14 minutes

def main():
    # Initialize bot and database
    chat_history_db = ChatHistoryDB()
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    bot_instance = InsuranceBot(chat_history_db)

    # Add handlers
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(MessageHandler(filters.COMMAND, bot_instance.unknown))
    application.add_handler(MessageHandler(filters.PHOTO, bot_instance.handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_instance.handle_text))

    # Start the ping service if running on Render
    if "RENDER_EXTERNAL_URL" in os.environ:
        application.loop.create_task(ping_server())

    # Start the bot
    print("Starting bot...")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
