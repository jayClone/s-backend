from pydantic import BaseModel
from typing import Optional, Literal

class PaymentBreakdownModel(BaseModel):
    amount: float
    mode: Literal["discount", "wallet", "cash"]
    note: Optional[str] = None
