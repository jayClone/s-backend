from pydantic import BaseModel
from typing import Literal
from datetime import datetime

class TransactionModel(BaseModel):
    transaction_id: str
    amount: float
    method: str  # UPI, Wallet, Card etc.
    status: Literal["success", "failed", "refunded"]
    date: datetime
