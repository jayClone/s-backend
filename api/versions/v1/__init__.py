from fastapi import APIRouter
from api.versions.v1.mail.root import router as mail_router
from fastapi.responses import JSONResponse

router = APIRouter()

# https://localhost:10007/api/v1
# https://localhost:10007/api/v1/
@router.get("", response_description="Api Version 1 Manager route")
@router.get("/", response_description="Api Version 1 Manager route")
async def hello_world():
    return JSONResponse(
        status_code=200,
        content={
        "location": "api/v1",
        "message": "API Version V1 - Initial Version",
    })

# https://localhost:10007/api/v1/mail
router.include_router(mail_router, prefix="/mail", tags=["API Version 1"])