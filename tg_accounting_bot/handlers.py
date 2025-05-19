# handlers.py
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
        "欢迎使用自动记账 Bot！\n"
        "/expense 金额 [备注] — 记录支出\n"
        "/income 金额 [备注] — 记录收入\n"
        "/summary — 查看本月收支汇总"
    )

async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("用法：/expense 金额 [备注]")
    amt = parse_amount(args[0])
    if amt is None:
        return await update.message.reply_text("请输入有效数字")
    remark = " ".join(args[1:]) if len(args)>1 else ""
    db = SessionLocal()
    rec = Record(user_id=update.effective_user.id, type="expense", amount=amt, remark=remark)
    db.add(rec); db.commit(); db.close()
    await update.message.reply_text(f"✅ 已记录支出：{amt}，备注：{remark}")

async def income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args:
        return await update.message.reply_text("用法：/income 金额 [备注]")
    amt = parse_amount(args[0])
    if amt is None:
        return await update.message.reply_text("请输入有效数字")
    remark = " ".join(args[1:]) if len(args)>1 else ""
    db = SessionLocal()
    rec = Record(user_id=update.effective_user.id, type="income", amount=amt, remark=remark)
    db.add(rec); db.commit(); db.close()
    await update.message.reply_text(f"✅ 已记录收入：{amt}，备注：{remark}")

async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.utcnow()
    start_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    db = SessionLocal()
    recs = db.query(Record).filter(
        Record.user_id==update.effective_user.id,
        Record.createdAt>=start_month
    ).all()
    db.close()
    income_total = sum(r.amount for r in recs if r.type=="income")
    expense_total = sum(r.amount for r in recs if r.type=="expense")
    bal = income_total - expense_total
    await update.message.reply_text(
        f"📊 本月汇总：\n"
        f"总收入：{income_total:.2f}\n"
        f"总支出：{expense_total:.2f}\n"
        f"净余额：{bal:.2f}"
    )
