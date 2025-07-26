from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from fastapi import HTTPException
from bson import ObjectId
from api.db import db

class TransactionModel(BaseModel):
    transaction_id: str
    amount: float
    method: str  # UPI, Wallet, Card etc.
    status: Literal["success", "failed", "refunded"]
    date: datetime

class Transaction:
    @staticmethod
    def get_all_transactions():
        """Get all transactions"""
        try:
            transactions = list(db["transactions"].find({}))
            for txn in transactions:
                txn["_id"] = str(txn["_id"])
            return transactions
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch transactions: {str(e)}")

    @staticmethod
    def get_transaction_by_id(transaction_id: str):
        """Get transaction detail by ID"""
        try:
            txn = db["transactions"].find_one({"_id": ObjectId(transaction_id)})
            if not txn:
                raise HTTPException(status_code=404, detail="Transaction not found")
            txn["_id"] = str(txn["_id"])
            return txn
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch transaction: {str(e)}")
