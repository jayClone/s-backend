from fastapi import APIRouter, Request, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse
from api.controllers.auth_controller import signup, signin


# Base User Router
router = APIRouter()


# http://localhost:10021/api/v1/user/auth/
@router.get("", response_description="User API Home")
@router.get("/", response_description="User API Home")
async def user_home_route(_=Depends(RateLimiter(times=5, seconds=60))):
    return JSONResponse(
        content={
            "location": "api/v1/user/auth",
            "message": "Welcome to the User API"
        },
        status_code=200
    )

# User Signup Route
@router.post("/signup", response_description="Signup new user")
async def signup_route(request: Request):
    return await signup(request)

# User Login Route
@router.post("/signin", response_description="Login user and return JWT token")
async def login_route(request: Request):
    return await signin(request)