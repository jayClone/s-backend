from fastapi import APIRouter, HTTPException, Request
from api.extensions.mail import MAIL
import random

from api.extensions.mail.otpHtmlVariable import getHtml
from fastapi.responses import JSONResponse

router = APIRouter()

# https://localhost:10007/api/v1/mail
# https://localhost:10007/api/v1/mail/
@router.get("", response_description="Api Mail Home")
@router.get("/", response_description="Api Mail Home")
async def hello_world():
    return JSONResponse(
        content={
            "location": "api/v1/mail",
            "message": "API Version V1 - Initial Version",
            "version": "1.0.0",
            "status": 200,
            "status_message": "OK... Working Mail Home",
            "data": {
                "message": "Welcome to the Mail Home"
            }
        },
        status_code=200
    )

# Send Mail Api
# Description : Send Mail to the User
# Request Type : POST
# Path : http://localhost:port/api/v1/mail/send-otp
# Path : http://localhost:10007/api/v1/mail/send-otp
# Default Port : 10007

@router.post("/send-otp" , response_description="Send OTP to the User")
async def send_otp(request: Request):
    try:
        body = await request.json()
        email = body.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        otp = random.randint(100000, 999999)

        MAIL.sendHtmlMail(email, "Furniture Management System", "OTP for the Verification", f"Your OTP is {otp}", getHtml(otp))

        return JSONResponse(
            content={
            "status": 200,
            "status_message": "OK",
            "data": {
                "message": "OTP Sent Successfully to " + email
            }
            },
            status_code=200
        )
    except HTTPException as http_exc:
        raise http_exc
    except ValueError as e:
        detail = {
            "status": 400,
            "status_message": "Bad Request",
            "data": {
                "message": str(e)
            }
        }
        raise HTTPException(status_code=400, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Create Room Api 
# Description : Create a new room for Socket Server
# Request Type : POST
# Path : http://localhost:port/api/v1/mail/verify-otp
# Default Port : 10007
@router.post("/verify-otp", response_description="Add New Room")
async def verify_otp(request: Request):
    try:
        body = await request.json()
        email = body.get("email")
        
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")
        
        otp = body.get("otp")
        
        if not otp:
            raise HTTPException(status_code=400, detail="OTP is required")
        
        return JSONResponse(
            content={
            "status": 200,
            "status_message": "OK",
            "data": {
                "message": "Otp Verified Successfully"
            }
            },
            status_code=200
        )
    except HTTPException as http_exc:
        raise http_exc  # Re-raise HTTPExceptions to allow FastAPI to handle them properly
    except ValueError as e:
        detail = {
            "status": 400,
            "status_message": "Bad Request",
            "data": {
                "message": str(e)
            }
        }
        raise HTTPException(status_code=400, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
