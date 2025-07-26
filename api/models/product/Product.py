from pydantic import BaseModel, Field
from typing import Optional
from models.Base import PyObjectId
from models.Location import LocationModel

class ProductModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    category: str
    price_per_unit: float
    unit: str  # e.g., kg, litre
    available_quantity: float
    location: Optional[LocationModel] = None
    supplier_id: PyObjectId

    class Config:
        allow_population_by_field_name = True
        json_encoders = {PyObjectId: str}
