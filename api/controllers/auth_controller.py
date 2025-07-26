from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.user.User import User

async def signup(request: Request):
    """
    Signup endpoint for new users using the updated User model.
    Accepts all fields from UserBaseModel.
    """
    try:
        try:
            data = await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request body cannot be empty")

        # Direct required fields check
        required_fields = ["username", "first_name", "last_name", "email", "password"]

        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

        # Validate username and email uniqueness
        if User.get_by_username(data["username"]):
            raise HTTPException(status_code=409, detail="Username already exists")
        User.check_email(data["email"])

        user = User.signup(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"],
        )

        print(f"User created: {user}")

        if user is None:
            raise HTTPException(status_code=500, detail="Failed to create user")

        return JSONResponse(
            content={
                "message": "User created successfully",
                "data": user  
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
