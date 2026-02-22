from pydantic import BaseModel

class TransactionCreate(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    location: str
    device_id: str
    merchant_type: str
