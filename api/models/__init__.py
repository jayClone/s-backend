from api.db import isMongoDBAvailable
from fastapi import HTTPException

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

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        print(f"Error initializing default data: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error initializing default data: {str(e)}")
