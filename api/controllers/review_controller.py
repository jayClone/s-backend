from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.review.Review import ReviewModel

async def give_review(request: Request):
    """
    Endpoint to give a review from a vendor to a supplier.
    """
    try:
        try:
            data = await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request body cannot be empty")

        required_fields = ["vendor_id", "supplier_id", "rating"]
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

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
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to give review: {str(e)}")
    
# list reviews by vendor_id and supplier_id
async def list_reviews(request: Request):
    """
    Endpoint to list reviews. Optional query params: vendor_id, supplier_id.
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
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list reviews: {str(e)}")