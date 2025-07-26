from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from models.Base import PyObjectId
from models.Location import LocationModel
from models.payment.Transaction import TransactionModel
from models.payment.Payment_breakdown import PaymentBreakdownModel

class OrderModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    vendor_id: PyObjectId
    supplier_id: PyObjectId
    product_id: PyObjectId
    qty: int
    total_price: float
    status: Literal["pending", "confirmed", "delivered", "cancelled"]
    order_date: datetime = Field(default_factory=datetime.utcnow)

    payment_status: Optional[Literal["pending", "completed", "failed"]] = "pending"
    payment_method: Optional[Literal["UPI", "COD", "Wallet", "Card"]] = None
    payment_date: Optional[datetime] = None

    location: Optional[LocationModel] = None
    transaction: Optional[List[TransactionModel]] = None
    payment: Optional[List[PaymentBreakdownModel]] = None

    class Config:
        allow_population_by_field_name = True
        json_encoders = {PyObjectId: str, datetime: lambda x: x.isoformat()}
