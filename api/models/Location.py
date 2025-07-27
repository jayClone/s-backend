from pydantic import BaseModel, Field
from typing import Optional

class LocationModel(BaseModel):
    address: str
    city: str
    state: str
    pincode: str
    country: str = "USA"  # Default value
    
    class Config:
        # Allow both 'zip' and 'pincode' for backward compatibility
        fields = {
            'zip': {'alias': 'pincode'}
        }
        # Allow extra fields to be ignored
        extra = "ignore"
