# import datetime
from fastapi import HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.order.Order import Order
from datetime import datetime
from api.extensions.jwt.dependencies import get_current_user, require_vendor, require_supplier, require_any_role

# create booking function 
async def create_booking(request: Request, current_user: dict = Depends(require_vendor)):
    """
    Endpoint to create a new booking (vendor only).
    """
    try:
        data = await request.json()
        print(f"DEBUG: Received booking data: {data}")
    except JSONDecodeError:
        print("DEBUG: JSONDecodeError occurred")
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    # Use current user's ID as vendor_id (from JWT token)
    data["vendor_id"] = current_user["uid"]
    print(f"DEBUG: vendor_id set to: {current_user['uid']}")

    required_fields = ["supplier_id", "product_id", "qty", "total_price"]
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        print(f"DEBUG: Missing fields: {missing}")
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    try:
        print(f"DEBUG: Creating booking with data: {data}")
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
    
# get all booking of a supplier
async def get_bookings_by_supplier(supplier_id: str, request: Request, current_user: dict = Depends(require_supplier)):
    """
    Endpoint to get all bookings for a particular supplier (supplier only).
    """
    try:
        # Ensure supplier can only see their own bookings
        if current_user["_id"] != supplier_id:
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
async def get_bookings_by_vendor(vendor_id: str, request: Request, current_user: dict = Depends(require_vendor)):
    """
    Endpoint to get all bookings for a particular vendor (vendor only).
    """
    try:
        # Ensure vendor can only see their own bookings
        if current_user["_id"] != vendor_id:
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
async def update_booking_status_controller(booking_id: str, status: str, current_user: dict = Depends(require_supplier)):
    """
    Update the status of a booking (supplier only).
    """
    try:
        updated_booking = Order.update_booking_status(booking_id, status)
        return {
            "message": "Booking status updated successfully",
            "data": updated_booking
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")

async def get_my_bookings(request: Request, current_user: dict = Depends(require_vendor)):
    """
    Endpoint to get all bookings for the current vendor (vendor only).
    """
    try:
        # Use current user's ID from JWT token
        vendor_id = current_user["uid"]  # Use 'uid' instead of '_id'
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
