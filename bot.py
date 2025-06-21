import os
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from models import init_db
from handlers import (
    start,
    expense,
    income,
    summary,
    total,
    history,
    clear,
    quick_record
)

def main():
    # 调试打印：启动时检查环境
    print("▶▶▶ [DEBUG] Bot 脚本启动，正在检查环境……")
    print("▶▶▶ [DEBUG] BOT_TOKEN =", os.getenv("BOT_TOKEN"))
    print("▶▶▶ [DEBUG] DB_URL    =", os.getenv("DB_URL"))

    # 初始化数据库（如果表不存在则创建）
    init_db()

    # 从环境变量读取 Bot Token
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("请先设置 BOT_TOKEN 环境变量")

    # 构建并启动应用
    app = ApplicationBuilder().token(token).build()

    # 注册命令处理
    app.add_handler(CommandHandler("start",   start))
    app.add_handler(CommandHandler("expense", expense))
    app.add_handler(CommandHandler("income",  income))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("total",   total))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(CommandHandler("clear",   clear))

    # 注册快捷记账：只拦截以 + 或 - 开头的文本（且不是命令）
    app.add_handler(
        MessageHandler(
            filters.Regex(r'^[+-]\s*\d') & ~filters.COMMAND,
            quick_record
        )
    )

    print("Bot 已启动，按 Ctrl+C 停止")
    app.run_polling()

if __name__ == "__main__":
    main()
