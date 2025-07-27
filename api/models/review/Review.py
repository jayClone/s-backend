from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from fastapi import HTTPException
from bson import ObjectId
from api.db import db  # Assuming you have a database module to handle MongoDB connections
from api.extensions.helper.json_serializer import serialize_for_json

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
# class Review:
#     @staticmethod
#     def get_collection():
#         try:
#             if db is None:
#                 raise HTTPException(status_code=500, detail="Database connection not initialized")
#             return db["reviews"]
#         except HTTPException as http_exc:
#             raise http_exc
#         except Exception as e:
#             print(f"Error accessing database: {e}")
#             raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

 # give the review on products by suppliers
    @staticmethod
    def give_review(
    vendor_id: str,
    supplier_id: str,
    rating: int,
    comment: Optional[str] = None
):
        try:
            if not (1 <= rating <= 5):
                raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

            review = ReviewModel(
                vendor_id=vendor_id,
                supplier_id=supplier_id,
                rating=rating,
                comment=comment
            )
            review_dict = review.model_dump(by_alias=True)
            if review_dict.get("_id") is None:
                review_dict.pop("_id")
            db["reviews"].insert_one(review_dict)
            if "_id" in review_dict:
                review_dict["_id"] = str(review_dict["_id"])
            if "created_at" in review_dict and isinstance(review_dict["created_at"], datetime):
                review_dict["created_at"] = review_dict["created_at"].isoformat()
            return serialize_for_json(review_dict)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error giving review: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to give review: {str(e)}")
        
    # list reviews by vendor_id and supplier_id
    @staticmethod
    def list_reviews(vendor_id: Optional[str] = None, supplier_id: Optional[str] = None):
        """List all reviews, optionally filter by vendor or supplier"""
        try:
            query = {}
            if vendor_id:
                query["vendor_id"] = vendor_id
            if supplier_id:
                query["supplier_id"] = supplier_id
            
            reviews = list(db["reviews"].find(query))
            # Serialize all reviews for JSON
            serialized_reviews = []
            for review in reviews:
                serialized_review = serialize_for_json(review)
                serialized_reviews.append(serialized_review)
            return serialized_reviews
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch reviews: {str(e)}")
        