from fastapi import HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.review.Review import ReviewModel
from api.extensions.jwt.dependencies import get_current_user, require_vendor, require_any_role

async def give_review(request: Request, current_user: dict = Depends(require_vendor)):
    """
    Endpoint to give a review from a vendor to a supplier (vendor only).
    """
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    # Use current user's ID as vendor_id (from JWT token)
    data["vendor_id"] = current_user["uid"]  # Use 'uid' instead of '_id'

    # Required fields (removed vendor_id since it comes from token)
    required_fields = ["supplier_id", "rating"]
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    try:
        review = ReviewModel.give_review(
            vendor_id=data["vendor_id"],
            supplier_id=data["supplier_id"],
            rating=data["rating"],
            comment=data.get("comment")
        )

        return JSONResponse(
            content={
                "message": "Review submitted successfully",
                "data": review
            },
            status_code=201
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to give review: {str(e)}")

# Update list_reviews function
async def list_reviews(request: Request, _=Depends(require_any_role)):
    """
    Endpoint to list reviews (any authenticated user).
    """
    try:
        vendor_id = request.query_params.get("vendor_id")
        supplier_id = request.query_params.get("supplier_id")
        reviews = ReviewModel.list_reviews(vendor_id=vendor_id, supplier_id=supplier_id)
        return JSONResponse(
            content={
                "message": "Reviews fetched successfully",
                "data": reviews
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reviews: {str(e)}")