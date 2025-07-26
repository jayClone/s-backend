from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from api.models.Location import LocationModel
from api.models.payment.Transaction import TransactionModel
from api.models.payment.Payment_breakdown import PaymentBreakdownModel


class OrderModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    vendor_id: str
    supplier_id: str
    product_id: str
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
        populate_by_name = True  # For Pydantic v2
        json_encoders = {datetime: lambda x: x.isoformat()}
