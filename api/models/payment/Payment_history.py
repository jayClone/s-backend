from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from models.payment.Transaction import TransactionModel
from models.payment.Payment_breakdown import PaymentBreakdownModel

class PaymentHistoryModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    order_id: str
    payment_status: Literal["pending", "completed", "failed"]
    payment_method: Literal["UPI", "COD", "Wallet", "Card"]
    payment_date: datetime
    transaction: Optional[List[TransactionModel]] = None
    payment: Optional[List[PaymentBreakdownModel]] = None

    class Config:
        populate_by_name = True  # For Pydantic v2
        json_encoders = {datetime: lambda x: x.isoformat()}