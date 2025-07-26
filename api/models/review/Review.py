from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReviewModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    vendor_id: str
    supplier_id: str
    rating: int  # 1–5
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True  # For Pydantic v2
        json_encoders = {datetime: lambda x: x.isoformat()}
