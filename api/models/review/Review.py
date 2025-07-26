from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.Base import PyObjectId

class ReviewModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    vendor_id: PyObjectId
    supplier_id: PyObjectId
    rating: int  # 1–5
    comment: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        allow_population_by_field_name = True
        json_encoders = {PyObjectId: str, datetime: lambda x: x.isoformat()}
