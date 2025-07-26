from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.user.User import User
from api.models.user.Role import Role

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

        role_name = data.get("role", "vendor")  # default to vendor if not provided
        role_obj = Role.get_role_by_name(role_name)
        if not role_obj:
            raise HTTPException(status_code=404, detail="Role not found")

        user = User(
            name=f"{data['first_name']} {data['last_name']}",
            email=data["email"],
            password=data["password"],
            phone1=data.get("phone1", ""),
            role=role_obj["name"]  # store ObjectId reference
        )
        result = user.save()
        return JSONResponse(
            content={
                "message": "User created successfully",
                "data": {
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                }
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

async def get_roles_for_frontend():
    roles = Role.get_all_roles()
    return JSONResponse(content={"roles": roles}, status_code=200)
