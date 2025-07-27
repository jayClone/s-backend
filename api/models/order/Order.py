from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from fastapi import HTTPException

# from api.models.Location import LocationModel
# from api.models.payment.Transaction import TransactionModel
# from api.models.payment.Payment import PaymentModel
# from api.models.user.User import UserModel
from api.db import db  # Ensure this import is correct
from api.extensions.helper.json_serializer import serialize_for_json


class OrderModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    vendor_id: str
    supplier_id: str
    product_id: str
    qty: int
    total_price: float
    status: Literal["pending", "confirmed", "delivered", "cancelled"]
    order_date: datetime = Field(default_factory=datetime.utcnow)

    # payment_status: Optional[Literal["pending", "completed", "failed"]] = "pending"
    # payment_method: Optional[Literal["UPI", "COD", "Wallet", "Card"]] = None
    # payment_date: Optional[datetime] = None

    # location: Optional[LocationModel] = None
    # transaction: Optional[List[TransactionModel]] = None
    # payment: Optional[List[PaymentModel]] = None

    class Config:
        populate_by_name = True  # For Pydantic v2
        json_encoders = {datetime: lambda x: x.isoformat()}


class Order:


    @staticmethod
    def get_booking_by_id(booking_id: str):
        """Get a booking by its ID"""
        try:
            booking = db["orders"].find_one({"_id": ObjectId(booking_id)})
            if not booking:
                raise HTTPException(status_code=404, detail="Booking not found")
            booking["_id"] = str(booking["_id"])
            if "order_date" in booking and isinstance(booking["order_date"], datetime):
                booking["order_date"] = booking["order_date"].isoformat()
            return booking
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch booking: {str(e)}")
        
    @staticmethod
    def create_booking(order_data: dict):
        """Create a new booking"""
        try:
            print(f"DEBUG: Order.create_booking called with: {order_data}")
            if db is None:
                print("DEBUG: Database connection is None!")
                raise HTTPException(status_code=500, detail="Database connection not initialized")
            order_data["order_date"] = datetime.utcnow()
            order_data["status"] = "pending"
            # Validate required fields
            required_fields = ["vendor_id", "supplier_id", "product_id", "qty", "total_price"]
            for field in required_fields:
                if field not in order_data:
                    print(f"DEBUG: Missing field: {field}")
                    raise HTTPException(status_code=400, detail=f"Missing field: {field}")
            print(f"DEBUG: All required fields present. Types: {[type(order_data[f]) for f in required_fields]}")
            print(f"DEBUG: About to insert into DB: {order_data}")
            result = db["orders"].insert_one(order_data)
            print(f"DEBUG: Inserted booking with _id: {result.inserted_id}")
            order_data["_id"] = str(result.inserted_id)
            serialized = serialize_for_json(order_data)
            print(f"DEBUG: Serialized booking: {serialized}")
            return serialized
        except Exception as e:
            import traceback
            print(f"DEBUG: Exception in create_booking: {e}")
            print(f"DEBUG: Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")

    @staticmethod
    def list_bookings(vendor_id: Optional[str] = None, supplier_id: Optional[str] = None):
        """List all bookings, optionally filter by vendor or supplier"""
        try:
            query = {}
            if vendor_id:
                query["vendor_id"] = vendor_id
            if supplier_id:
                query["supplier_id"] = supplier_id
            bookings = list(db["orders"].find(query))
            for booking in bookings:
                booking["_id"] = str(booking["_id"])
            return bookings
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")

    # get all booking by vendor
    @staticmethod
    def get_bookings_by_vendor(vendor_id: str):
        """Get all bookings for a particular vendor"""
        try:
            bookings = list(db["orders"].find({"vendor_id": vendor_id}))
            for booking in bookings:
                booking["_id"] = str(booking["_id"])
                if "order_date" in booking and isinstance(booking["order_date"], datetime):
                    booking["order_date"] = booking["order_date"].isoformat()
            return serialize_for_json(bookings)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")
        

    # get all booking by supplier 
    @staticmethod
    def get_bookings_by_supplier(supplier_id: str):
        """Get all bookings for a particular supplier"""
        try:
            bookings = list(db["orders"].find({"supplier_id": supplier_id}))
            for booking in bookings:
                booking["_id"] = str(booking["_id"])
                if "order_date" in booking and isinstance(booking["order_date"], datetime):
                    booking["order_date"] = booking["order_date"].isoformat()
            return serialize_for_json(bookings)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")    


    @staticmethod
    def update_booking_status(booking_id: str, status: str):
        """Update booking status"""
        try:
            valid_statuses = ["pending", "confirmed", "delivered", "cancelled"]
            if status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
            result = db["orders"].update_one(
                {"_id": ObjectId(booking_id)},
                {"$set": {"status": status}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Booking not found")
            return serialize_for_json(Order.get_booking_by_id(booking_id))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")

    @staticmethod
    def update_booking(booking_id: str, update_data: dict):
        """Update booking details (not just status)"""
        try:
            result = db["orders"].update_one(
                {"_id": ObjectId(booking_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Booking not found")
            return Order.get_booking_by_id(booking_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")

    @staticmethod
    def delete_booking(booking_id: str):
        """Cancel/Delete booking"""
        try:
            result = db["orders"].delete_one({"_id": ObjectId(booking_id)})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Booking not found")
            return {"message": "Booking deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete booking: {str(e)}")
