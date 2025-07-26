from pydantic import BaseModel

class LocationModel(BaseModel):
    address: str
    city: str
    state: str
    pincode: str
    lat: float
    lng: float
