from fastapi import Depends, HTTPException, Request
from typing import Optional, List
from api.extensions.jwt import extract_data_from_token_request, verify_token
from api.models.user.User import User

async def get_current_user(request: Request) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    """
    try:
        # Extract user data from token
        token_data = extract_data_from_token_request(request)
        user_id = token_data.get("uid")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        # Get user from database
        user = User.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        if not user.get("is_active", True):
            raise HTTPException(status_code=403, detail="User account is deactivated")
        
        # Convert ObjectId to string
        user["_id"] = str(user["_id"])
        
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

async def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to get current active user
    """
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User account is deactivated")
    return current_user

def require_roles(required_roles: List[str]):
    """
    Dependency factory to require specific roles
    """
    async def role_checker(request: Request) -> dict:
        print(f"DEBUG: require_roles called with roles: {required_roles}")
        try:
            token_data = extract_data_from_token_request(request)
            print(f"DEBUG: Token data extracted: {token_data}")
            user_role = token_data.get("role")
            print(f"DEBUG: User role: {user_role}")
            
            if not user_role:
                print(f"DEBUG: No role assigned")
                raise HTTPException(status_code=403, detail="No role assigned")
            
            if user_role not in required_roles:
                print(f"DEBUG: Access denied. User role {user_role} not in {required_roles}")
                raise HTTPException(
                    status_code=403, 
                    detail=f"Access denied. Required roles: {required_roles}"
                )
            
            print(f"DEBUG: Role check passed")
            return token_data
        except HTTPException:
            raise
        except Exception as e:
            print(f"DEBUG: Role verification failed: {e}")
            raise HTTPException(status_code=403, detail=f"Role verification failed: {str(e)}")
    
    return role_checker

# Predefined role dependencies
require_admin = require_roles(["admin"])
require_supplier = require_roles(["supplier"])
require_vendor = require_roles(["vendor"])
require_admin_or_vendor = require_roles(["admin", "vendor"])
require_any_role = require_roles(["admin", "supplier", "vendor"]) 