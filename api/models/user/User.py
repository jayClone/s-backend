from datetime import datetime, timezone, timedelta
from bson import ObjectId
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Tuple
from api.db import db
from api.extensions.jwt.__init__ import create_token  # Ensure this import is correct
from api.models.user.Role import Role
import bcrypt
from dotenv import load_dotenv

load_dotenv()

class UserModel(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    username: str
    name: str
    email: EmailStr
    password: str
    phone1: str
    phone2: Optional[str] = None
    role: str = "vendor"
    is_active: bool = True
    login_count: int = 0

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}

class User:
    @staticmethod
    def get_collection():
        try:
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not initialized")
            return db["users"]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

    @staticmethod
    def hash_password(password):
        try:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing password: {str(e)}")

    @staticmethod
    def verify_password(password, hashed_password):
        try:
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    @staticmethod
    def is_password_hashed(password):
        return password.startswith('$2b$') if isinstance(password, str) else False

    @staticmethod
    def normalize_identifier(identifier: str) -> str:
        """Normalize identifiers for case-insensitive matching"""
        return identifier.strip().lower()

    @staticmethod
    def get_by_username(username: str):
        try:
            collection = User.get_collection()
            normalized_username = User.normalize_identifier(username)
            return collection.find_one({"username_lower": normalized_username})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

    @staticmethod
    def get_by_email(email: str):
        try:
            collection = User.get_collection()
            normalized_email = User.normalize_identifier(email)
            return collection.find_one({"email_lower": normalized_email})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

    @staticmethod
    def get_by_id(user_id: str):
        try:
            collection = User.get_collection()
            return collection.find_one({"_id": ObjectId(user_id)})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

    @staticmethod
    def authenticate(identifier: str, password: str):
        try:
            normalized_id = User.normalize_identifier(identifier)
            
            # Try username first
            user = User.get_by_username(normalized_id)
            if not user:
                # Try email if username not found
                user = User.get_by_email(normalized_id)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            if not user.get("is_active", True):
                raise HTTPException(status_code=403, detail="Account not active")

            if not User.verify_password(password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid credentials")

            # Handle role conversion
            user["_id"] = str(user["_id"])
            if isinstance(user["role"], ObjectId):
                role_obj = Role.get_by_id(str(user["role"]))
                user["role"] = role_obj["name"] if role_obj else "vendor"
            elif isinstance(user["role"], str):
                if not Role.get_role_by_name(user["role"]):
                    user["role"] = "vendor"

            return user
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

    @staticmethod
    def signup(username: str, first_name: str, last_name: str, email: str, password: str):
        try:
            # Normalize and validate
            normalized_username = User.normalize_identifier(username)
            normalized_email = User.normalize_identifier(email)
            
            # Get default role
            default_role = Role.get_role_by_name("vendor")
            if not default_role:
                raise HTTPException(status_code=500, detail="Default role not configured")

            # Check for existing user
            if User.get_by_username(normalized_username):
                raise HTTPException(status_code=409, detail="Username already exists")

            if User.get_by_email(normalized_email):
                raise HTTPException(status_code=409, detail="Email already exists")

            # Create new user
            new_user = {
                "username": username,
                "username_lower": normalized_username,
                "name": f"{first_name} {last_name}",
                "email": email,
                "email_lower": normalized_email,
                "password": User.hash_password(password),
                "phone1": "",
                "role": default_role["name"],
                "is_active": True,
                "login_count": 0,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }

            collection = User.get_collection()
            result = collection.insert_one(new_user)
            
            return {
                "id": str(result.inserted_id),
                "name": new_user["name"],
                "email": new_user["email"]
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

    @staticmethod
    def generate_token(user_id: str):
        try:
            user = User.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            role_name = user["role"]
            if isinstance(role_name, ObjectId):
                role = Role.get_by_id(str(role_name))
                role_name = role["name"] if role else "vendor"

            payload = {
                "uid": str(user["_id"]),
                "role": role_name,
                "permissions": ["*"] if role_name == "admin" else ["read", "write"]
            }
            # Ensure this returns both token and expiry
            return create_token(payload)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")