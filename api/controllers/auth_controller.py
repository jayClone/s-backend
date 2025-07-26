from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.user.User import User

async def signup(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    required_fields = ["username", "first_name", "last_name", "email", "password"]
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing fields: {', '.join(missing)}")

    try:
        result = User.signup(
            username=data["username"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"]
        )
        return JSONResponse(
            content={"message": "User created", "data": result},
            status_code=201
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signup failed: {str(e)}")

async def signin(request: Request):
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    identifier = data.get("identifier")
    password = data.get("password")
    
    if not identifier or not password:
        raise HTTPException(status_code=400, detail="Missing credentials")

    try:
        user = User.authenticate(identifier, password)
        token, expires = User.generate_token(str(user["_id"]))
        
        return JSONResponse(
            content={
                "message": "Login successful",
                "token": token,
                "expires": expires,
                "user": {
                    "id": user["_id"],
                    "username": user["username"],
                    "email": user["email"],
                    "role": user["role"]
                }
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")