# bot.py
import os
from telegram.ext import ApplicationBuilder, CommandHandler
from handlers import start, expense, income, summary
from models import init_db

def main():
    init_db()
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("expense", expense))
    app.add_handler(CommandHandler("income", income))
    app.add_handler(CommandHandler("summary", summary))
    print("Bot 已启动，按 Ctrl+C 停止")
    app.run_polling()

if __name__ == "__main__":
    main()
