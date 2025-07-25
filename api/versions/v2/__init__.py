from fastapi import APIRouter

router = APIRouter()

@router.get("/", response_description="Api Version 2 Manager route")
async def hello_world():
    return {
        "location" : "api/v2",
        "message" : "API Version V2 - Initial Version",
    }