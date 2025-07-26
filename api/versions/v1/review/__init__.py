from fastapi import APIRouter, Request, Depends
from api.controllers.review_controller import give_review,list_reviews
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter

router = APIRouter()


# http://localhost:10021/api/v1/review
# http://localhost:10021/api/v1/review/
@router.get("", response_description="review API Home")
@router.get("/", response_description="review API Home")
async def user_home_route(_=Depends(RateLimiter(times=5, seconds=60))):
    return JSONResponse(
        content={
            "location": "api/v1/review",
            "message": "Welcome to the Review API"
        },
        status_code=200
    )

# http://localhost:10021/api/v1/review/give
@router.post("/give", response_description="Give a review")
async def give_review_route(request: Request):
    return await give_review(request)

# http://localhost:10021/api/v1/review/list
@router.get("/list", response_description="List reviews")
async def list_reviews_route(request: Request):
    return await list_reviews(request)