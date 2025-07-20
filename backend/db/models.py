from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index  # ✅ Boolean added
from datetime import datetime
from .db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, index=True)
    file_hash = Column(String(32), unique=True, index=True)
    details = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)  # 

    # ✅ ✅ ✅ ADD THIS:
    needs_confirmation = Column(Boolean, default=False)

    __table_args__ = (
        Index('idx_file_category', 'file_hash', 'category'),
        Index('idx_date_amount', 'transaction_date', 'amount'),
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, category={self.category}, date={self.transaction_date})>"
