from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple
from fastapi import HTTPException, Request
import jwt as pyjwt  # Make sure PyJWT is installed: pip install PyJWT
from dotenv import load_dotenv
import os

if os.getenv('ENVIRONMENT') == 'development':
    load_dotenv('.env.development')
else:
    load_dotenv()

# You should store this securely in environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "ioufhds7fhaw0478fhwunidscn78q2309nsac")
JWT_ALGORITHM = "HS256"

def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> Tuple[str, int]:
    """
    Create a JWT token with the given data
    
    Args:
        data: Dictionary of data to include in the token
        expires_delta: Can be a timedelta object or a number of seconds for token expiration
    
    Returns:
        Tuple of (token, expiry_timestamp)
    """
    try:
        to_encode = data.copy()
        current_time = datetime.now(timezone.utc)

        if expires_delta:
            # Check if expires_delta is an integer or a timedelta
            if isinstance(expires_delta, int):
                # If it's an integer, treat it as seconds
                expire = current_time + timedelta(seconds=expires_delta)
            else:
                # Otherwise assume it's a timedelta object
                expire = current_time + expires_delta
        else:
            # Default: 15 minutes
            expire = current_time + timedelta(minutes=15)

        # Convert datetime to Unix timestamp for JWT
        exp_timestamp = int(expire.timestamp())
        to_encode.update({"exp": exp_timestamp})
        
        encoded_jwt = pyjwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        # If using PyJWT >= 2.x, encoded_jwt is str. If < 2.x, it may be bytes.
        if isinstance(encoded_jwt, bytes):
            encoded_jwt = encoded_jwt.decode("utf-8")
        return encoded_jwt, exp_timestamp
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create token: {str(e)}"
        )

def refresh_token(token: str, expires_delta: Optional[timedelta] = None) -> Tuple[str, int]:
    """
    Refresh a JWT token by creating a new one with the same data
    
    Returns:
        Tuple of (token, expiry_timestamp)
    """
    try:
        decoded_data = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Remove the 'exp' field to create a new token
        decoded_data.pop("exp", None)
        current_time = datetime.now(timezone.utc)
        if expires_delta:
            expire = current_time + expires_delta
        else:
            expire = current_time + timedelta(minutes=15)  # Default 15 minutes
        decoded_data.update({"exp": expire})

        new_token, expiry_timestamp = create_token(decoded_data)

        return new_token, expiry_timestamp
    except HTTPException as http_exc:
        raise http_exc
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh token: {str(e)}"
        )

def extract_token_from_request(request: Request) -> str:
    """
    Extract JWT token from the request headers

    Args:
        request: FastAPI Request object

    Returns:
        str: JWT token

    Raises:
        HTTPException: If token is not found
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise HTTPException(
                status_code=401,
                detail="Authorization header missing"
            )
        
        # Split the header to get the token
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )
        return token
    except HTTPException as http_exc:
        raise http_exc
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract token: {str(e)}"
        )

def extract_data_from_token_request(request: Request) -> dict:
    """
    Extract and verify data from the JWT token in the request

    Args:
        request: FastAPI Request object

    Returns:
        dict: Decoded data from the token

    Raises:
        HTTPException: If token is invalid or data extraction fails
    """
    try:
        token = extract_token_from_request(request)
        decoded_data = verify_token(token)
        return decoded_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract data from token: {str(e)}"
        )

def verify_token(token: str, required_roles: Optional[list[str]] = None) -> dict:
    """
    Verify JWT token and optionally check for required roles
    
    Args:
        token: JWT token to verify
        required_roles: Optional list of roles required for access
        
    Returns:
        dict: Decoded token data
        
    Raises:
        HTTPException: If token is invalid, expired, or role check fails
    """
    try:
        decoded_data = pyjwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check expiration explicitly (although JWT already checks this internally)
        if "exp" in decoded_data:
            expiry_timestamp = decoded_data["exp"]
            current_timestamp = datetime.now(timezone.utc).timestamp()
            if current_timestamp > expiry_timestamp:
                raise HTTPException(status_code=401, detail="Token has expired")
        
        # If roles are required, check them
        if required_roles:
            user_roles = decoded_data.get("roles", [])
            if not any(role in user_roles for role in required_roles):
                raise HTTPException(
                    status_code=403,
                    detail="Insufficient permissions"
                )
        return decoded_data
    except HTTPException as http_exc:
        raise http_exc
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify token: {str(e)}"
        )