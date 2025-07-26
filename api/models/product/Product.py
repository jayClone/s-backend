from pydantic import BaseModel, Field
from typing import Optional
from api.models.Location import LocationModel

class ProductModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    category: str
    price_per_unit: float
    unit: str  # e.g., kg, litre
    available_quantity: float
    location: Optional[LocationModel] = None
    supplier_id: str

    class Config:
        populate_by_name = True  # For Pydantic v2
        json_encoders = {}
