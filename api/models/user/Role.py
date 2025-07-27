from pydantic import BaseModel
from datetime import datetime, timezone
from bson import ObjectId
from api.db import db
from fastapi import HTTPException
from typing import Optional, List, Dict, Any

# Role base model for validation
class RoleBaseModel(BaseModel):
    name: str
    priority: int
    permissions: List[str]
    created_at: datetime = datetime.now(timezone.utc)
    updated_at: datetime = datetime.now(timezone.utc)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
            datetime: datetime.isoformat,
        }

class Role:
    @staticmethod
    def get_collection() -> Any:
        try:
            if db is None:
                raise HTTPException(status_code=500, detail="Database connection not initialized")
            return db["roles"]
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get collection: {str(e)}")

    def __init__(self, name: str, priority: int, permissions: Optional[List[str]] = None, 
                 created_at: Optional[datetime] = None, updated_at: Optional[datetime] = None) -> None:
        self.name = name
        self.priority = priority 
        self.permissions = permissions or []
        self.created_at = created_at or datetime.now(timezone.utc)
        self.updated_at = updated_at or datetime.now(timezone.utc)

    def save(self) -> Dict[str, str]:
        try:
            collection = Role.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")
            
            role_data = RoleBaseModel(
                name=self.name,
                priority=self.priority,
                permissions=self.permissions,
                created_at=self.created_at,
                updated_at=self.updated_at
            ).model_dump()
            
            if hasattr(self, '_id'):
                role_data['_id'] = self._id
                collection.update_one({"_id": self._id}, {"$set": role_data})
            else:
                result = collection.insert_one(role_data)
                self._id = result.inserted_id
            
            return {"role_id": str(self._id)}
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save role: {str(e)}")

    @staticmethod
    def create_default_roles() -> bool:
        try:
            collection = Role.get_collection()
            if collection is None:
                print("Database Connection Error")
                return False
            existing_docs_count = collection.count_documents({})
            if existing_docs_count > 0:
                print("Roles collection is not empty. Skipping default roles creation.")
                return True

            default_roles = [
                {
                    "name": "admin", 
                    "priority": 0, 
                    "permissions": ["*"]
                },
                {
                    "name": "supplier", 
                    "priority": -1, 
                    "permissions": ["read", "write", "manage_products"]
                },
                {
                    "name": "vendor",
                    "priority": 1,
                    "permissions": ["read", "write", "order"]
                }
                ]

            created_roles = []
            for role_data in default_roles:
                existing_role = collection.find_one({"name": role_data["name"]})
                if existing_role is None:
                    role = Role(
                        name=role_data["name"],
                        priority=role_data["priority"],
                        permissions=role_data["permissions"]
                    )
                    role.save()
                    created_roles.append(role_data["name"])

            return True
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error in create_default_roles: {str(e)}")
            return False

    @staticmethod
    def get_role_by_name(name: str) -> Optional[Dict[str, Any]]:
        try:
            collection = Role.get_collection()
            if collection is None:
                return None
            role = collection.find_one({"name": name})
            if role:
                if "created_at" in role:
                    role["created_at"] = role["created_at"].isoformat()
                if "updated_at" in role:
                    role["updated_at"] = role["updated_at"].isoformat()
            return role
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error retrieving role by name: {e}")
            return None

    @staticmethod
    def get_by_id(role_id: str) -> Optional[Dict[str, Any]]:
        try:
            collection = Role.get_collection()
            if collection is None:
                return None
            role = collection.find_one({"_id": ObjectId(role_id)})
            if role:
                if "created_at" in role:
                    role["created_at"] = role["created_at"].isoformat()
                if "updated_at" in role:
                    role["updated_at"] = role["updated_at"].isoformat()
            return role
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error retrieving role by ID: {e}")
            return None
    
    @staticmethod 
    def get_all_roles() -> List[Dict[str, Any]]:
        try:
            collection = Role.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")
            
            roles = list(collection.find())
            for role in roles:
                role['_id'] = str(role['_id'])
                if "created_at" in role:
                    role["created_at"] = role["created_at"].isoformat()
                if "updated_at" in role:
                    role["updated_at"] = role["updated_at"].isoformat()
            return roles
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to get all roles: {str(e)}")

    @staticmethod
    def update_role(role_id: str, name: Optional[str] = None, 
                   priority: Optional[int] = None, 
                   permissions: Optional[List[str]] = None) -> Dict[str, str]:
        try:
            collection = Role.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")

            existing_role = collection.find_one({"_id": ObjectId(role_id)})
            if not existing_role:
                raise HTTPException(status_code=404, detail="Role not found")

            role = Role(
                name=existing_role.get("name"),
                priority=existing_role.get("priority"),
                permissions=existing_role.get("permissions", []),
                created_at=existing_role.get("created_at"),
                updated_at=datetime.now(timezone.utc)
            )
            role._id = existing_role.get("_id")

            if name:
                role.name = name
            if priority is not None:
                role.priority = priority
            if permissions is not None:
                role.permissions = permissions

            return role.save()
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")

    @staticmethod
    def delete_role(role_id: str) -> bool:
        try:
            collection = Role.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")

            result = collection.delete_one({"_id": ObjectId(role_id)})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Role not found")

            return True
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete role: {str(e)}")

    @staticmethod
    def add_permission(role_id: str, permission: str) -> List[str]:
        try:
            collection = Role.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")

            existing_role = collection.find_one({"_id": ObjectId(role_id)})
            if not existing_role:
                raise HTTPException(status_code=404, detail="Role not found")

            current_permissions = existing_role.get("permissions", [])

            if permission not in current_permissions:
                current_permissions.append(permission)
                collection.update_one(
                    {"_id": ObjectId(role_id)},
                    {"$set": {"permissions": current_permissions, "updated_at": datetime.now(timezone.utc)}}
                )

            return current_permissions
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to add permission: {str(e)}")

    @staticmethod
    def remove_permission(role_id: str, permission: str) -> List[str]:
        try:
            collection = Role.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")

            existing_role = collection.find_one({"_id": ObjectId(role_id)})
            if not existing_role:
                raise HTTPException(status_code=404, detail="Role not found")

            current_permissions = existing_role.get("permissions", [])

            if permission in current_permissions:
                current_permissions.remove(permission)
                collection.update_one(
                    {"_id": ObjectId(role_id)},
                    {"$set": {"permissions": current_permissions, "updated_at": datetime.now(timezone.utc)}}
                )
            
            return current_permissions
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to remove permission: {str(e)}")

    @staticmethod
    def has_permission(role_id: str, permission: str) -> bool:
        try:
            collection = Role.get_collection()
            if collection is None:
                raise HTTPException(status_code=500, detail="Database connection error")
                
            existing_role = collection.find_one({"_id": ObjectId(role_id)})
            if not existing_role:
                raise HTTPException(status_code=404, detail="Role not found")
                
            current_permissions = existing_role.get("permissions", [])
            return permission in current_permissions
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to check permission: {str(e)}")