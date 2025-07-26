from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from api.models.payment.Transaction import TransactionModel
from api.models.payment.Payment import PaymentModel
from fastapi import HTTPException
from bson import ObjectId
from api.db import db

class PaymentHistoryModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    order_id: str
    payment_status: Literal["pending", "completed", "failed"]
    payment_method: Literal["UPI", "COD", "Wallet", "Card"]
    payment_date: datetime
    transaction: Optional[List[TransactionModel]] = None
    payment: Optional[List[PaymentModel]] = None

    class Config:
        populate_by_name = True  # For Pydantic v2
        json_encoders = {datetime: lambda x: x.isoformat()}

class PaymentHistory:
    @staticmethod
    def get_all_order_histories(vendor_id: Optional[str] = None, supplier_id: Optional[str] = None):
        """Get all order histories, optionally filter by vendor or supplier"""
        try:
            query = {}
            if vendor_id:
                query["vendor_id"] = vendor_id
            if supplier_id:
                query["supplier_id"] = supplier_id
            histories = list(db["payment_history"].find(query))
            for history in histories:
                history["_id"] = str(history["_id"])
            return histories
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch order histories: {str(e)}")

    @staticmethod
    def get_order_history_by_id(booking_id: str):
        """Get one order record by booking/order ID"""
        try:
            history = db["payment_history"].find_one({"order_id": booking_id})
            if not history:
                raise HTTPException(status_code=404, detail="Order history not found")
            history["_id"] = str(history["_id"])
            return history
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch order history: {str(e)}")

    @staticmethod
    def get_all_payment_histories():
        """Get all payment histories"""
        try:
            histories = list(db["payment_history"].find({}))
            for history in histories:
                history["_id"] = str(history["_id"])
            return histories
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch payment histories: {str(e)}")

    @staticmethod
    def get_payment_history_by_id(payment_id: str):
        """Get one payment history by payment ID (_id)"""
        try:
            history = db["payment_history"].find_one({"_id": ObjectId(payment_id)})
            if not history:
                raise HTTPException(status_code=404, detail="Payment history not found")
            history["_id"] = str(history["_id"])
            return history
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch payment history: {str(e)}")

    @staticmethod
    def update_order_history(booking_id: str, update_data: dict):
        """Update order history details by booking/order ID"""
        try:
            result = db["payment_history"].update_one(
                {"order_id": booking_id},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Order history not found")
            return PaymentHistory.get_order_history_by_id(booking_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update order history: {str(e)}")

    @staticmethod
    def update_payment_history(payment_id: str, update_data: dict):
        """Update payment history details by payment ID (_id)"""
        try:
            result = db["payment_history"].update_one(
                {"_id": ObjectId(payment_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Payment history not found")
            return PaymentHistory.get_payment_history_by_id(payment_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update payment history: {str(e)}")