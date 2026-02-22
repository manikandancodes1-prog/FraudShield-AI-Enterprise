from sqlalchemy import Column, Integer, String, Float, TIMESTAMP
from sqlalchemy.sql import func
from ..core.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, index=True)
    user_id = Column(String)
    amount = Column(Float)
    location = Column(String)
    device_id = Column(String)
    merchant_type = Column(String)
    risk_score = Column(Float)
    fraud_probability = Column(Float)
    status = Column(String)
    
    
    reasons = Column(String, nullable=True) 
    
    created_at = Column(TIMESTAMP, server_default=func.now())