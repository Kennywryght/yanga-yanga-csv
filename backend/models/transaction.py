from ..db.db import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from datetime import datetime
from sqlalchemy import Boolean  # Add at the top if miss

class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, index=True)  # For backward compatibility
    file_hash = Column(String(32), unique=True, index=True)  # MD5 hash length is 32
    details = Column(String(255), nullable=False)  # Increased length and made non-nullable
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=True)
    transaction_date = Column(DateTime, nullable=False, index=True)  # Actual transaction date
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # When record was created
    timestamp = Column(DateTime, default=datetime.utcnow)  # ✅ FIXED: Corrected usage
    needs_confirmation = Column(Boolean, default=False)


    __table_args__ = (
        Index('idx_file_category', 'file_hash', 'category'),
        Index('idx_date_amount', 'transaction_date', 'amount'),
        {'extend_existing': True} 
    )

    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, category={self.category}, date={self.transaction_date})>"
