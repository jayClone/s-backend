from datetime import datetime, timezone
import json
from bson import ObjectId
from fastapi import HTTPException, Request
from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Tuple, Union
from api.db import db
from api.extensions.jwt import create_token, verify_token, extract_token_from_request
from api.models.user.Role import Role
import bcrypt
import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

# User base model for validation
class UserBaseModel(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: List[EmailStr]
    password: str
    role: ObjectId  # This references the _id field from Role collection
    role_status: bool = True
    login_count: int = 0
    is_active: bool = True
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: datetime.isoformat,
        }

    @field_validator('email')
    def ensure_email_is_list(cls, v):
        if isinstance(v, str):
            return [v]
        return v

class User:
    @staticmethod
    def get_collection():
        try:
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not initialized")
            return db["users"]
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error accessing database: {e}")
            raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

    def __init__(self, username, first_name, last_name, email, password, role, role_status=True, login_count=0, is_active=True, created_at=None, updated_at=None):
        self.username = username
        self.first_name = first_name
        self.last_name = last_name
        if isinstance(email, str):
            self.email = [email]
        elif isinstance(email, list):
            self.email = [str(e) for e in email]
        else:
            self.email = []
        self.password = password
        self.role = role
        self.role_status = role_status
        self.login_count = login_count
        self.is_active = is_active
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    @staticmethod
    def hash_password(password):
        try:
            return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing password: {str(e)}")

    @staticmethod
    def verify_password(password, hashed_password):
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), 
                hashed_password.encode('utf-8') if isinstance(hashed_password, str) else hashed_password
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Password verification failed: {str(e)}")

    @staticmethod
    def is_password_hashed(password):
        """Check if a password is already hashed"""
        try:
            if isinstance(password, bytes):
                return password.decode('utf-8').startswith('$2b$')
            elif isinstance(password, str):
                return password.startswith('$2b$')
            return False
        except Exception:
            return False

    def save(self):
        try:
            # Hash the password if it's not already hashed
            if not User.is_password_hashed(self.password):
                self.password = User.hash_password(self.password)

            collection = User.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")

            # Validate data using the schema
            user_data = UserBaseModel(
                username=self.username,
                first_name=self.first_name,
                last_name=self.last_name,
                email=self.email,
                password=self.password,
                role=self.role,
                role_status=self.role_status,
                login_count=self.login_count,
                is_active=self.is_active,
                created_at=self.created_at,
                updated_at=self.updated_at
            ).model_dump()

            if hasattr(self, '_id'):
                user_data['_id'] = self._id
                collection.update_one({"_id": self._id}, {"$set": user_data})
            else:
                result = collection.insert_one(user_data)
                self._id = result.inserted_id

            return {"user_id": str(self._id)}

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error saving user: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to save user: {str(e)}")

    @staticmethod
    def get_by_username(username):
        try:
            collection = User.get_collection()
            if collection is None:
                return None
            return collection.find_one({"username": username})
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error retrieving user by username: {e}")
            return None

    @staticmethod
    def get_by_email(email):
        try:
            collection = User.get_collection()
            if collection is None:
                return None
            return collection.find_one({"email": {"$in": [email]}})
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            return None

    @staticmethod
    def get_by_id(user_id):
        try:
            collection = User.get_collection()
            if collection is None:
                return None
            return collection.find_one({"_id": ObjectId(user_id)})
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error retrieving user by ID: {e}")
            return None

    @staticmethod
    def check_username(username):
        try:
            if not username or len(username) < 3:
                raise HTTPException(
                    status_code=400,
                    detail="Username must be at least 3 characters long"
                )
            if User.get_by_username(username):
                raise HTTPException(
                    status_code=409,
                    detail="Username already exists"
                )
            return True
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )

    @staticmethod
    def check_email(email):
        try:
            if not email or len(email) < 5:
                raise HTTPException(
                    status_code=400,
                    detail="Email must be at least 5 characters long"
                )
            if User.get_by_email(email):
                raise HTTPException(
                    status_code=409,
                    detail="Email already exists"
                )
            return True
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error checking email: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid email: {str(e)}")

    def increment_login_count(self):
        try:
            self.login_count += 1
            self.updated_at = datetime.now(timezone.utc)
            result = self.save()
            return self.login_count
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error incrementing login count: {e}")
            return 0

    def needs_password_reset(self):
        return self.login_count == 0

    def reset_password(self, new_password):
        try:
            self.password = new_password  # Will be hashed on save
            self.updated_at = datetime.now(timezone.utc)
            return self.save()
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error resetting password: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to reset password: {str(e)}")

    @staticmethod
    def authenticate(username, password):
        try:
            user = User.get_by_username(username)
            if not user:
                raise HTTPException(status_code=401, detail="Invalid username or password")

            if not User.verify_password(password, user["password"]):
                raise HTTPException(status_code=401, detail="Invalid username or password")

            # Convert ObjectId to string for JSON serialization
            user["_id"] = str(user["_id"])
            user["role"] = str(user["role"])

            return user

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Authentication error: {e}")
            raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

    def add_email(self, new_email):
        """Add a new email to the user's email list if it doesn't already exist"""
        try:
            if new_email not in self.email:
                self.email.append(new_email)
                self.updated_at = datetime.now(timezone.utc)
                self.save()
            return {"emails": self.email}
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error adding email: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to add email: {str(e)}")

    def remove_email(self, email_to_remove):
        """Remove an email from the user's email list if it exists and is not the last one"""
        try:
            if email_to_remove in self.email and len(self.email) > 1:
                self.email.remove(email_to_remove)
                self.updated_at = datetime.now(timezone.utc)
                self.save()
            elif len(self.email) <= 1:
                raise HTTPException(status_code=400, detail="Cannot remove the last email address")
            return {"emails": self.email}
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error removing email: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to remove email: {str(e)}")

    @staticmethod
    def signup(username: str, first_name: str, last_name: str, email: str, password: str):
        try:
            # Get default role
            default_role = Role.get_role_by_name("user")
            if not default_role:
                raise HTTPException(
                    status_code=404,
                    detail="Default role not found"
                )

            # Check if user/email already exists
            if User.get_by_username(username):
                raise HTTPException(
                    status_code=409,
                    detail="Username already exists")

            if User.get_by_email(email):
                raise HTTPException(
                    status_code=409,
                    detail="Email already exists")

            new_user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role=default_role["_id"],
                is_active=False  # Default inactive
            )

            new_user.save()
            return {
                "username": new_user.username,
                "email": new_user.email,
            }

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error signing up user: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Signup failed: {str(e)}"
            )

    @staticmethod
    def login(identifier: str, password: str):
        try:
            user = User.get_by_username(identifier)
            if not user:
                user = User.get_by_email(identifier)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid username or password"
                )

            if not user.get("is_active", False):
                raise HTTPException(
                    status_code=403,
                    detail="User is not active"
                )
            if not User.verify_password(password, user["password"]):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid username or password"
                )

            # Increment login count and update user
            obj = User(
                username=user["username"],
                first_name=user["first_name"],
                last_name=user["last_name"],
                email=user["email"],
                password=user["password"],
                role=user["role"],
                role_status=user.get("role_status", True),
                login_count=user.get("login_count", 0),
                is_active=user.get("is_active", True),
                created_at=user.get("created_at"),
                updated_at=user.get("updated_at")
            )
            obj._id = user["_id"]
            obj.increment_login_count()
            obj.save()

            # Generate token
            token, expires = User.generate_token(obj._id)
            if not token:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to generate token"
                )

            return {
                "token": token,
                "expires": expires,
            }

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Login error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Login failed: {str(e)}"
            )

    @staticmethod
    def generate_token(id: str):
        try:
            # Fetch the user by ID
            user = User.get_by_id(id)
            if not user:
                raise HTTPException(
                    status_code=404,
                    detail="User not found"
                )

            # Fetch the user's role by role
            role = Role.get_by_id(user["role"])
            if not role:
                raise HTTPException(
                    status_code=404,
                    detail="Role not found"
                )

            # Prepare the payload with the uid, role_id, and role data
            payload = {
                "uid": str(user["_id"]),
                "role_id": str(user["role"]),
                "permissions": role["permissions"],
                "role_status": user.get("role_status", True),
            }

            # Create and return just the token string
            return create_token(payload)
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Token generation error: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Token generation failed: {str(e)}"
            )

    @staticmethod
    def get_email_by_identifier(identifier):
        """Get email by username or email"""
        try:
            user = User.get_by_username(identifier)
            if not user:
                user = User.get_by_email(identifier)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            return user["email"][0]
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error retrieving email: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to retrieve email: {str(e)}")

    @staticmethod
    def activate_user(token):
        """Activate user account using the token"""
        try:
            # Decode the token to get the user ID
            payload = verify_token(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid token")

            user_id = payload.get("uid")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Fetch the user by ID
            collection = User.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")

            # Update the user directly in the database
            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {
                    "$set": {
                        "is_active": True,
                        "updated_at": datetime.now(timezone.utc)
                    }
                }
            )

            if result.modified_count == 0:
                raise HTTPException(status_code=404, detail="User not found")

            token, expires = User.generate_token(user_id)

            if not token:
                raise HTTPException(status_code=500, detail="Failed to generate token")

            return {
                "token": token,
                "expires": expires,
            }

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error activating user: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to activate user: {str(e)}")

    @staticmethod
    def generate_verify_token(identifier):
        """Generate a verification token for the user"""
        try:
            email = User.get_email_by_identifier(identifier)
            if not email:
                raise HTTPException(status_code=404, detail="User not found")

            user = User.get_by_email(email)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Generate the token

            token = User.generate_token(user["_id"])

            return token

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error generating verification token: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate verification token: {str(e)}")
            
    @staticmethod
    async def generate_refresh_token_from_request(request: Request) -> Tuple[str, int]:
        """
        Generate a refresh token from a request containing a valid access token
        
        Args:
            request: FastAPI Request object
            
        Returns:
            Tuple of (refresh_token, expiry_timestamp)
            
        Raises:
            HTTPException: If authentication fails, token expired, or user not found
        """
        try:
            # Extract token from request
            token = extract_token_from_request(request)
            
            # Verify token (will raise HTTPException if expired or invalid)
            payload = verify_token(token)
            
            # Get user ID from payload
            user_id = payload.get("uid")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
            
            # Verify user exists
            user = User.get_by_id(user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")
                
            # Fetch the user's role
            role = Role.get_by_id(user["role"])
            if not role:
                raise HTTPException(status_code=404, detail="Role not found")
            
            # Prepare the payload for refresh token - maintain the same fields as in generate_token
            refresh_payload = {
                "uid": str(user["_id"]),
                "role_id": str(user["role"]),
                "permissions": role["permissions"],
                "role_status": user.get("role_status", True),
                "refresh": True  # Add indicator that this is a refresh token
            }
            
            # Set refresh token expiry to 30 minutes
            expires_delta = timedelta(minutes=30)
            
            # Create refresh token with longer expiry (30 minutes)
            refresh_token, expiry_timestamp = create_token(refresh_payload, expires_delta=expires_delta)

            return refresh_token, expiry_timestamp
            
        except HTTPException as he:
            # Re-raise HTTP exceptions as-is
            raise he
        except Exception as e:
            print(f"Refresh token generation error: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate refresh token: {str(e)}")
