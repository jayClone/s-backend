from fastapi import APIRouter
from api.versions.v1 import router as v1_router
from api.versions.v2 import router as v2_router
from fastapi.responses import JSONResponse

router = APIRouter()

# https://localhost:10007/api
# https://localhost:10007/api/
@router.get("", response_description="Api Version Manager route")
@router.get("/", response_description="Api Version Manager route")
# Define the API Version Manager Route
async def hello_world():
    return JSONResponse(
        status_code=200,
        content={
            "location": "api/",
            "message": "Hello World",
        }
    )

# Include the API Versions

# https://localhost:10007/api/v1
router.include_router(v1_router, prefix="/v1", tags=["API Version 1"])

# Your Future API Updates Goes Here...
router.include_router(v2_router, prefix="/v2", tags=["API Version 2"])