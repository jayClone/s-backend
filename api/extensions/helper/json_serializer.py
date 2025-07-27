from datetime import datetime
from bson import ObjectId
from typing import Any, Dict, List, Union

def serialize_for_json(data: Any) -> Any:
    """
    Recursively serialize data to be JSON compatible.
    Converts datetime objects to ISO format strings and ObjectId to strings.
    """
    if isinstance(data, dict):
        return {key: serialize_for_json(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [serialize_for_json(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

def clean_user_data(user_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean user data for JSON response, removing sensitive fields and serializing dates.
    """
    if not isinstance(user_data, dict):
        return user_data
    
    # Remove sensitive fields
    sensitive_fields = ["password", "email_lower", "username_lower"]
    cleaned_data = {k: v for k, v in user_data.items() if k not in sensitive_fields}
    
    # Serialize for JSON
    return serialize_for_json(cleaned_data) 