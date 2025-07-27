# import datetime
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.order.Order import Order
from datetime import datetime

# create booking function 
async def create_booking(request: Request):
    """
    Endpoint to create a new booking.
    """
    try:
        try:
            data = await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request body cannot be empty")

        # You may want to validate required fields here
        required_fields = ["vendor_id", "supplier_id", "product_id", "qty", "total_price"]
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

        booking = Order.create_booking(data)
          # Convert datetime to string for JSON
        if "order_date" in booking and isinstance(booking["order_date"], datetime):
             booking["order_date"] = booking["order_date"].isoformat()
        return JSONResponse(
            content={
                "message": "Booking created successfully",
                "data": booking
            },
            status_code=201
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create booking: {str(e)}")
    
# get all booking of a supplier
async def get_bookings_by_supplier(supplier_id: str, request: Request):
    """
    Endpoint to get all bookings for a particular supplier.
    """
    try:
        bookings = Order.get_bookings_by_supplier(supplier_id)
        return JSONResponse(
            content={
                "message": "Bookings fetched successfully",
                "data": bookings
            },
            status_code=200
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")


# get all booking of a vendor
async def get_bookings_by_vendor(vendor_id: str, request: Request):
    """
    Endpoint to get all bookings for a particular vendor.
    """
    try:
        bookings = Order.get_bookings_by_vendor(vendor_id)
        return JSONResponse(
            content={
                "message": "Bookings fetched successfully",
                "data": bookings
            },
            status_code=200
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bookings: {str(e)}")
    
# update status 
async def update_booking_status_controller(booking_id: str, status: str):
    """
    Update the status of a booking.
    """
    try:
        updated_booking = Order.update_booking_status(booking_id, status)
        return {
            "message": "Booking status updated successfully",
            "data": updated_booking
        }
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update booking: {str(e)}")
