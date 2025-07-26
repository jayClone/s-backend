from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.user.User import User
from api.models.user.Role import Role

async def signup(request: Request):
    """
    Signup endpoint for new users using the User.signup static method.
    Accepts all fields from UserBaseModel.
    """
    try:
        try:
            data = await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request body cannot be empty")

        required_fields = ["username", "first_name", "last_name", "email", "password"]
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

        # Use the static signup method
        result = User.signup(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"]
        )
        return JSONResponse(
            content={
                "message": "User created successfully",
                "data": result
            },
            status_code=201
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup Failed: {str(e)}")

async def signin(request: Request):
    """
    Signin endpoint for users.
    Accepts 'username' or 'email' and 'password'.
    Returns JWT token if successful.
    """
    try:
        try:
            data = await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request body cannot be empty")

        identifier = data.get("identifier")  # Can be username or email
        password = data.get("password")

        if not identifier or not password:
            raise HTTPException(status_code=400, detail="Missing username/email or password")

        # Authenticate user
        user = User.authenticate(identifier, password)

        # Generate JWT token
        token, expires = User.generate_token(user["_id"])

        return JSONResponse(
            content={
                "message": "Signin successful",
                "token": token,
                "expires": expires,
                "user": {
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
                }
            },
            status_code=200
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login Failed: {str(e)}")
