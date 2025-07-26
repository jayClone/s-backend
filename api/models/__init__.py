from api.db import isMongoDBAvailable
from fastapi import HTTPException

from api.models.user.Role import Role

def init_models():
    """
    Initialize default data for the application.
    This function creates default roles and users if they don't exist.
    """
    # Check if MongoDB is available
    if not isMongoDBAvailable:
        raise HTTPException(status_code=503, detail="MongoDB is not available. Skipping default data initialization.")


    try:
        print("Initializing Models...")
        roles_result = Role.create_default_roles()
        if roles_result is None:
            raise HTTPException(status_code=500, detail="Failed to create default roles. Skipping user creation.")
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error initializing default data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error initializing default data: {str(e)}")
