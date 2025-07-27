from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse
from api.controllers.auth_controller import signup, signin, update_profile, get_profile
from api.extensions.jwt.dependencies import get_current_user, require_admin, require_any_role

# Base User Router
router = APIRouter()

# Public routes (no authentication required)
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

@router.post("/signup", response_description="Signup new user")
async def signup_route(request: Request):
    return await signup(request)

@router.post("/signin", response_description="Login user and return JWT token")
async def login_route(request: Request):
    return await signin(request)

# Protected routes (authentication required)
@router.get("/profile", response_description="Get current user profile")
async def get_profile_route(current_user: dict = Depends(get_current_user)):
    return await get_profile(current_user)

@router.put("/profile", response_description="Update user profile")
async def update_profile_route(request: Request, current_user: dict = Depends(get_current_user)):
    return await update_profile(request, current_user)

# Admin-only routes
@router.get("/users", response_description="List all users (admin only)")
async def list_users_route(_=Depends(require_admin)):
    from api.models.user.User import User
    try:
        users = User.list_users()
        return JSONResponse(
            content={
                "message": "Users retrieved successfully",
                "data": users
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve users: {str(e)}")