# import datetime
from fastapi import HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.order.Order import Order
from datetime import datetime
from api.extensions.jwt.dependencies import get_current_user, require_vendor, require_supplier, require_any_role
from typing import Optional

# create booking function 
async def create_booking(request: Request, current_user: dict):
    """
    Endpoint to create a new booking (vendor only).
    """
    try:
        data = await request.json()
        print(f"DEBUG: Received booking data: {data}")
    except JSONDecodeError:
        print("DEBUG: JSONDecodeError occurred")
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    print(f"DEBUG: current_user: {current_user}")
    if not current_user or "uid" not in current_user:
        print("DEBUG: current_user is missing or does not have 'uid'")
        raise HTTPException(status_code=401, detail="Invalid or missing user ID in token")
    data["vendor_id"] = current_user["uid"]
    print(f"DEBUG: vendor_id set to: {current_user['uid']}")

    required_fields = ["supplier_id", "product_id", "qty", "total_price"]
    # FIX: Accept 0 and 0.0 as valid values
    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        print(f"DEBUG: Missing fields: {missing}")
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    print(f"DEBUG: About to call Order.create_booking with: {data}")
    try:
        booking = Order.create_booking(data)
        print(f"DEBUG: Booking created: {booking}")
        if "order_date" in booking and isinstance(booking["order_date"], datetime):
            booking["order_date"] = booking["order_date"].isoformat()
        return JSONResponse(
            content={
                "message": "Booking created successfully",
                "data": booking
            },
            status_code=201
        )
    except HTTPException as e:
        print(f"DEBUG: HTTPException: {e}")
        raise e
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception: {e}")
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")
    
async def get_bookings_by_supplier(supplier_id: str, request: Request, current_user: Optional[dict] = None):
    """
    Endpoint to get all bookings for a particular supplier (supplier only).
    """
    try:
        if not current_user or current_user.get("uid") != supplier_id:
            raise HTTPException(status_code=403, detail="Access denied: can only view own bookings")
        bookings = Order.get_bookings_by_supplier(supplier_id)
        return JSONResponse(
            content={
                "message": "Bookings fetched successfully",
                "data": bookings
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")

# get all booking of a vendor
async def get_bookings_by_vendor(vendor_id: str, request: Request, current_user: Optional[dict] = None):
    """
    Endpoint to get all bookings for a particular vendor (vendor only).
    """
    try:
        if not current_user or current_user.get("uid") != vendor_id:
            raise HTTPException(status_code=403, detail="Access denied: can only view own bookings")
        bookings = Order.get_bookings_by_vendor(vendor_id)
        return JSONResponse(
            content={
                "message": "Bookings fetched successfully",
                "data": bookings
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")
    
# update status 
async def update_booking_status_controller(booking_id: str, status: str, current_user: dict):
    """
    Update the status of a booking (supplier only).
    """
    try:
        # Fetch the booking to check supplier_id
        booking = Order.get_booking_by_id(booking_id)
        if not booking or booking.get("supplier_id") != current_user["uid"]:
            raise HTTPException(status_code=403, detail="Access denied: can only update your own bookings")
        updated_booking = Order.update_booking_status(booking_id, status)
        return {
            "message": "Booking status updated successfully",
            "data": updated_booking
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")

async def get_my_bookings(request: Request, current_user: dict):
    """
    Endpoint to get all bookings for the current vendor (vendor only).
    """
    try:
        vendor_id = current_user["uid"]
        bookings = Order.get_bookings_by_vendor(vendor_id)
        return JSONResponse(
            content={
                "message": "Bookings fetched successfully",
                "data": bookings
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")

async def get_my_supplier_bookings(request: Request, current_user: dict):
    """
    Endpoint to get all bookings for the current supplier (supplier only).
    """
    try:
        supplier_id = current_user["uid"]
        bookings = Order.get_bookings_by_supplier(supplier_id)
        return JSONResponse(
            content={
                "message": "Bookings fetched successfully",
                "data": bookings
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")
