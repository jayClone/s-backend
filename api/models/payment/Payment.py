from pydantic import BaseModel
from typing import Optional, Literal
from fastapi import HTTPException
from bson import ObjectId
from api.db import db

class PaymentModel(BaseModel):
    amount: float
    mode: Literal["UPI", "Wallet", "Card", "Cash"]
    status: Literal["pending", "completed", "failed"]
    note: Optional[str] = None

class Payment:
    @staticmethod
    def create_payment(data: dict):
        """Create a payment record"""
        try:
            result = db["payments"].insert_one(data)
            data["_id"] = str(result.inserted_id)
            return data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")

    @staticmethod
    def get_all_payments():
        """Get all payments"""
        try:
            payments = list(db["payments"].find({}))
            for p in payments:
                p["_id"] = str(p["_id"])
            return payments
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch payments: {str(e)}")

    @staticmethod
    def get_payment_by_id(payment_id: str):
        """Get specific payment by ID"""
        try:
            payment = db["payments"].find_one({"_id": ObjectId(payment_id)})
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")
            payment["_id"] = str(payment["_id"])
            return payment
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch payment: {str(e)}")

    @staticmethod
    def update_payment(payment_id: str, update_data: dict):
        """Update payment details"""
        try:
            result = db["payments"].update_one(
                {"_id": ObjectId(payment_id)},
                {"$set": update_data}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Payment not found")
            return Payment.get_payment_by_id(payment_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update payment: {str(e)}")

    @staticmethod
    def delete_payment(payment_id: str):
        """Delete payment record"""
        try:
            result = db["payments"].delete_one({"_id": ObjectId(payment_id)})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Payment not found")
            return {"message": "Payment deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete payment: {str(e)}")
