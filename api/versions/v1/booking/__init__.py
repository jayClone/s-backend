from fastapi import APIRouter, Request, Depends,Body
from fastapi.responses import JSONResponse
from fastapi_limiter.depends import RateLimiter
from api.controllers.order_controller import create_booking,get_bookings_by_vendor,get_bookings_by_supplier, get_my_bookings, get_my_supplier_bookings,update_booking_status_controller
from api.extensions.jwt.dependencies import require_vendor, require_supplier

router = APIRouter()


# http://localhost:10021/api/v1/order
# http://localhost:10021/api/v1/order/
@router.get("", response_description="order API Home")
@router.get("/", response_description="order API Home")
async def user_home_route(_=Depends(RateLimiter(times=5, seconds=60))):
    return JSONResponse(
        content={
            "location": "api/v1/order",
            "message": "Welcome to the Order API"
        },
        status_code=200
    )

# http://localhost:10021/api/v1/order/create
@router.post("/create", response_description="Create a new booking")
async def create_booking_route(
    request: Request,
    current_user: dict = Depends(require_vendor)  # <-- FIX: inject vendor user
):
    return await create_booking(request, current_user)

# http://localhost:10021/api/v1/order/vendor/{vendor_id}
@router.get("/vendor/{vendor_id}", response_description="Get all bookings for a vendor")
async def get_bookings_by_vendor_route(
    vendor_id: str,
    request: Request,
    current_user: dict = Depends(require_vendor)
):
    return await get_bookings_by_vendor(vendor_id, request, current_user)

# http://localhost:10021/api/v1/order/supplier/{supplier_id}
@router.get("/supplier/{supplier_id}", response_description="Get all bookings for a supplier")
async def get_bookings_by_supplier_route(
    supplier_id: str,
    request: Request,
    current_user: dict = Depends(require_supplier)
):
    return await get_bookings_by_supplier(supplier_id, request, current_user)

# http://localhost:10021/api/v1/order/update_status/{booking_id}
@router.put("/update_status/{booking_id}", response_description="Update booking status")
async def update_booking_status_route(
    booking_id: str,
    request: Request,
    current_user: dict = Depends(require_supplier)  # <-- must be require_supplier
):
    data = await request.json()
    status = data.get("status")
    return await update_booking_status_controller(booking_id, status, current_user)

@router.get("/my-bookings", response_description="Get all bookings for the current vendor")
async def get_my_bookings_route(
    request: Request,
    current_user: dict = Depends(require_vendor)
):
    return await get_my_bookings(request, current_user)

@router.get("/my-supplier-bookings", response_description="Get all bookings for the current supplier")
async def get_my_supplier_bookings_route(
    request: Request,
    current_user: dict = Depends(require_supplier)
):
    return await get_my_supplier_bookings(request, current_user)
