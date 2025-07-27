from fastapi import HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api import db
from api.models.user.User import User
from api.models.user.Role import Role
from api.extensions.jwt.dependencies import get_current_user
from datetime import datetime
from bson import ObjectId
from typing import Any, Dict
from api.extensions.helper.json_serializer import serialize_for_json, clean_user_data

async def signup(request: Request):
    try:
        data = await request.json()
        print(f"DEBUG: Request data received: {data}")  # Debug line
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    required_fields = ["username", "first_name", "last_name", "email", "password"]
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing fields: {', '.join(missing)}")

    # Get role from request, default to "vendor"
    role = data.get("role", "vendor")
    print(f"DEBUG: Role extracted from request: {role}")  # Debug line
    
    # Validate that the role exists
    if not Role.get_role_by_name(role):
        raise HTTPException(status_code=400, detail=f"Invalid role: {role}")

    try:
        result = User.signup(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"],
            role=role  # Pass the role parameter
        )
        print(f"DEBUG: User.signup result: {result}")  # Debug line
        return JSONResponse(
            content={"message": "User created", "data": result},
            status_code=201
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

async def signin(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    identifier = data.get("identifier")
    password = data.get("password")
    
    if not identifier or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    try:
        user = User.authenticate(identifier, password)
        token, expires = User.generate_token(str(user["_id"]))
        
        return JSONResponse(
            content={
                "message": "Login successful",
                "token": token,
                "expires": expires,
                "user": {
                    "id": user["_id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
                }
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

async def reset_password(request: Request):
    try:
        data = await request.json()
        email = data.get("email")
        new_password = data.get("new_password")
        if not email or not new_password:
            raise HTTPException(status_code=400, detail="Email and new password are required")

        user = User.get_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Hash the new password (assuming User.hash_password exists)
        hashed = User.hash_password(new_password)
        users_collection = getattr(db, "users", None)
        if users_collection is None:
            raise HTTPException(status_code=500, detail="Users collection not found in db module")
        users_collection.update_one({"email": email}, {"$set": {"password": hashed}})

        return JSONResponse(content={"message": "Password reset successful"}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")

async def update_profile(request: Request, current_user: dict = Depends(get_current_user)):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")
    
    # Use current user's ID from JWT token
    user_id = current_user["_id"]
    
    # Validate update data
    allowed_fields = {"name", "email", "phone1", "phone2", "current_password", "new_password"}
    update_data = {k: v for k, v in data.items() if k in allowed_fields and v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")
    
    # Validate password requirements if changing password
    if "new_password" in update_data:
        if len(update_data["new_password"]) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")
    
    try:
        result = User.update_profile(user_id, update_data)
        return JSONResponse(
            content={
                "message": "Profile updated successfully",
                "data": result
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")

async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        # Clean and serialize user data
        user_data = clean_user_data(current_user)
        
        return JSONResponse(
            content={
                "message": "Profile retrieved successfully",
                "data": user_data
            },
            status_code=200
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve profile: {str(e)}")