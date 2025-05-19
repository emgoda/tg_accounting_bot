# models.py
import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 从环境变量读取数据库 URL
engine = create_engine(os.getenv("DB_URL"), echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Record(Base):
    __tablename__ = "records"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, index=True)
    type      = Column(String)        # "income" 或 "expense"
    amount    = Column(Float)
    remark    = Column(String, default="")
    createdAt = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
