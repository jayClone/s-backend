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
    def signup(username: str, first_name: str, last_name: str, email: str, password: str, role: str = "vendor"):
        try:
            print(f"DEBUG: Signup called with role: {role}")  # Debug line
            
            # Normalize and validate
            normalized_username = User.normalize_identifier(username)
            normalized_email = User.normalize_identifier(email)
            
            # Get the specified role
            role_obj = Role.get_role_by_name(role)
            print(f"DEBUG: Role object found: {role_obj}")  # Debug line
            
            if not role_obj:
                raise HTTPException(status_code=400, detail=f"Role '{role}' not found. Available roles: admin, supplier, vendor")

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
                "role": role,  # Use the role string directly instead of role_obj["name"]
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
                "email": new_user["email"],
                "role": new_user["role"]
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
        
    @staticmethod
    def list_users():
        """List all users (admin only)"""
        try:
            collection = User.get_collection()
            users = list(collection.find({}))
            for user in users:
                user["_id"] = str(user["_id"])
            return users
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error listing users: {str(e)}")

    @staticmethod
    def get_user_by_id(user_id: str):
        """Get user by ID"""
        try:
            user = User.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            user["_id"] = str(user["_id"])
            return user
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving user: {str(e)}")

    @staticmethod
    def update_user(user_id: str, update_data: dict):
        """Update user fields (name, phone, etc.)"""
        try:
            collection = User.get_collection()
            allowed_fields = {"name", "phone1", "phone2", "email"}
            update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
            if not update_fields:
                raise HTTPException(status_code=400, detail="No valid fields to update")
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
            return User.get_user_by_id(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating user: {str(e)}")

    @staticmethod
    def delete_user(user_id: str):
        """Delete user by ID"""
        try:
            collection = User.get_collection()
            result = collection.delete_one({"_id": ObjectId(user_id)})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
            return {"message": "User deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting user: {str(e)}")

    @staticmethod
    def get_locations(user_id: str):
        """Get all locations for a user"""
        try:
            collection = User.get_collection()
            user = collection.find_one({"_id": ObjectId(user_id)})
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            locations = user.get("locations", [])
            for loc in locations:
                loc["id"] = str(loc.get("id", ""))
            return locations
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving locations: {str(e)}")

    @staticmethod
    def add_location(user_id: str, location_data: dict):
        """Add a new location for a user"""
        from bson import ObjectId
        try:
            collection = User.get_collection()
            location_data["id"] = str(ObjectId())
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$push": {"locations": location_data}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
            return location_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding location: {str(e)}")

    @staticmethod
    def update_location(user_id: str, loc_id: str, update_data: dict):
        """Update a specific location for a user"""
        try:
            collection = User.get_collection()
            result = collection.update_one(
                {"_id": ObjectId(user_id), "locations.id": loc_id},
                {"$set": {f"locations.$.{k}": v for k, v in update_data.items()}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Location not found")
            return User.get_locations(user_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error updating location: {str(e)}")

    @staticmethod
    def delete_location(user_id: str, loc_id: str):
        """Delete a specific location for a user"""
        try:
            collection = User.get_collection()
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$pull": {"locations": {"id": loc_id}}}
            )
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Location not found")
            return {"message": "Location deleted"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting location: {str(e)}")