import re
import datetime
from telegram import Update
from telegram.ext import ContextTypes
from models import SessionLocal, Record

def parse_amount(text: str):
    try:
        return float(text)
    except:
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "欢迎使用记账 Bot！（单位：AED）\n"
        "/expense 金额 [备注] — 记录支出\n"
        "/income 金额 [备注] — 记录收入\n"
        "/summary — 本月汇总\n"
        "/total — 累计总计\n"
        "/history — 最近 100 条记录\n"
        "/clear — 清空记录\n\n"
        "或快捷发送 “+金额 [备注]” / “-金额 [备注]”（单位 AED）"
    )

async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("用法：/expense 金额 [备注]")
    amt = parse_amount(args[0])
    if amt is None:
        return await update.message.reply_text("请输入有效数字")
    remark = " ".join(args[1:]) if len(args) > 1 else ""
    db = SessionLocal()
    rec = Record(user_id=update.effective_user.id, type="expense", amount=amt, remark=remark)
    db.add(rec); db.commit(); db.close()
    await update.message.reply_text(f"✅ 已记录支出：{amt:.2f} AED，备注：{remark}")

async def income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("用法：/income 金额 [备注]")
    amt = parse_amount(args[0])
    if amt is None:
        return await update.message.reply_text("请输入有效数字")
    remark = " ".join(args[1:]) if len(args) > 1 else ""
    db = SessionLocal()
    rec = Record(user_id=update.effective_user.id, type="income", amount=amt, remark=remark)
    db.add(rec); db.commit(); db.close()
    await update.message.reply_text(f"✅ 已记录收入：{amt:.2f} AED，备注：{remark}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    db = SessionLocal()
    recs = db.query(Record).filter(
        Record.user_id == update.effective_user.id,
        Record.createdAt >= start_month
    ).all()
    db.close()
    total_in = sum(r.amount for r in recs if r.type == "income")
    total_ex = sum(r.amount for r in recs if r.type == "expense")
    bal = total_in - total_ex
    await update.message.reply_text(
        f"📊 本月汇总：\n"
        f"总收入：{total_in:.2f} AED\n"
        f"总支出：{total_ex:.2f} AED\n"
        f"净余额：{bal:.2f} AED"
    )

async def total(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    recs = db.query(Record).filter(Record.user_id == update.effective_user.id).all()
    db.close()
    total_in = sum(r.amount for r in recs if r.type == "income")
    total_ex = sum(r.amount for r in recs if r.type == "expense")
    bal = total_in - total_ex
    await update.message.reply_text(
        f"📈 累计总计：\n"
        f"累计收入：{total_in:.2f} AED\n"
        f"累计支出：{total_ex:.2f} AED\n"
        f"净余额：{bal:.2f} AED"
    )

async def history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    recs = (
        db.query(Record)
          .filter(Record.user_id == update.effective_user.id)
          .order_by(Record.createdAt.desc())
          .limit(100)
          .all()
    )
    db.close()
    if not recs:
        return await update.message.reply_text("没有找到任何历史记录。")
    lines = [
        f"{r.createdAt.strftime('%Y-%m-%d')} | {'收入' if r.type=='income' else '支出'} | {r.amount:.2f} AED | {r.remark}"
        for r in recs
    ]
    await update.message.reply_text("📜 最近 100 条记录：\n" + "\n".join(lines))

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db = SessionLocal()
    db.query(Record).filter(Record.user_id == update.effective_user.id).delete()
    db.commit(); db.close()
    await update.message.reply_text("🗑️ 已清空所有历史记录。")

async def quick_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    m = re.match(r'^([+-])\s*(\d+(?:\.\d+)?)(?:\s+(.+))?$', text)
    if not m:
        return
    sign, amt_str, remark = m.groups()
    amt = float(amt_str)
    rec_type = "income" if sign == "+" else "expense"
    remark = remark or ""
    db = SessionLocal()
    rec = Record(user_id=update.effective_user.id, type=rec_type, amount=amt, remark=remark)
    db.add(rec); db.commit()
    # 计算累计
    recs = db.query(Record).filter(Record.user_id == update.effective_user.id).all()
    total_in = sum(r.amount for r in recs if r.type == "income")
    total_ex = sum(r.amount for r in recs if r.type == "expense")
    bal = total_in - total_ex
    db.close()
    await update.message.reply_text(
        f"✅ 已记录{'收入' if rec_type=='income' else '支出'}：{amt:.2f} AED，备注：{remark}\n"
        f"📈 累计：收入 {total_in:.2f} AED  支出 {total_ex:.2f} AED  余额 {bal:.2f} AED"
    )
