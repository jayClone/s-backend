from fastapi import APIRouter
from api.versions.v1.mail.root import router as mail_router
from api.versions.v1.user.auth import router as auth_router
from api.versions.v1.product import router as product_router
from fastapi.responses import JSONResponse

router = APIRouter()

# https://localhost:10021/api/v1
# https://localhost:10021/api/v1/
@router.get("", response_description="Api Version 1 Manager route")
@router.get("/", response_description="Api Version 1 Manager route")
async def hello_world():
    return JSONResponse(
        status_code=200,
        content={
        "location": "api/v1",
        "message": "API Version V1 - Initial Version",
    })

# https://localhost:10021/api/v1/mail
router.include_router(mail_router, prefix="/mail", tags=["API Version 1"])

# https://localhost:10021/api/v1/auth
router.include_router(auth_router, prefix="/auth", tags=["API Version 1"])

# https://localhost:10021/api/v1/auth
router.include_router(product_router, prefix="/product", tags=["API Version 1"])