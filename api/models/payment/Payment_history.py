from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from models.Base import PyObjectId
from models.payment.Transaction import TransactionModel
from models.payment.Payment_breakdown import PaymentBreakdownModel

class PaymentHistoryModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    order_id: PyObjectId
    payment_status: Literal["pending", "completed", "failed"]
    payment_method: Literal["UPI", "COD", "Wallet", "Card"]
    payment_date: datetime
    transaction: Optional[List[TransactionModel]] = None
    payment: Optional[List[PaymentBreakdownModel]] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {PyObjectId: str, datetime: lambda x: x.isoformat()}