from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class PaymentHistory(Base):
    __tablename__ = "payment_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_id = Column(String(255), unique=True, nullable=False)
    payment_method = Column(String(50), nullable=False)  # alipay, wechat, etc.
    status = Column(Enum("pending", "completed", "failed", "refunded", name="payment_status"), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)