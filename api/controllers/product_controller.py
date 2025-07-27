from fastapi import HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.product.Product import ProductModel
from api.extensions.jwt.dependencies import get_current_user, require_supplier, require_admin, require_any_role
from typing import Optional
from api.models.Location import LocationModel
from api.db import db
from bson import ObjectId
from api.extensions.helper.json_serializer import serialize_for_json
import traceback

async def create_product(request: Request, current_user: dict = Depends(require_supplier)):
    """
    Endpoint to create a new product (supplier only).
    """
    print(f"DEBUG: create_product function called")
    print(f"DEBUG: current_user: {current_user}")
    
    try:
        data = await request.json()
        print(f"DEBUG: Received data: {data}")
    except JSONDecodeError:
        print(f"DEBUG: JSONDecodeError occurred")
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    # Remove supplier_id from request if present (we'll use it from JWT token)
    data.pop("supplier_id", None)
    print(f"DEBUG: Removed supplier_id from request data")
    
    # Use current user's ID as supplier_id (from JWT token)
    data["supplier_id"] = current_user["uid"]
    print(f"DEBUG: Current user ID from token: {current_user['uid']}")

    # Required fields (removed supplier_id since it comes from token)
    required_fields = ["name", "category", "price_per_unit", "unit", "available_quantity"]
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        print(f"DEBUG: Missing fields: {missing}")
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    # Fix location field if present
    if "location" in data and data["location"]:
        location = data["location"]
        # Convert 'zip' to 'pincode' if present
        if "zip" in location:
            location["pincode"] = location.pop("zip")
        # Add default country if not present
        if "country" not in location:
            location["country"] = "USA"
        print(f"DEBUG: Processed location: {location}")

    print(f"DEBUG: About to call ProductModel.create_product")
    try:
        print(f"DEBUG: Calling create_product with: {data}")
        
        # Try to create the product step by step
        try:
            product = ProductModel.create_product(
                name=data["name"],
                category=data["category"],
                price_per_unit=data["price_per_unit"],
                unit=data["unit"],
                available_quantity=data["available_quantity"],
                supplier_id=data["supplier_id"],
                location=data.get("location"),
                image_url=data.get("image_url") 
            )
            print(f"DEBUG: Product created successfully: {product}")
        except Exception as model_error:
            print(f"DEBUG: Error in ProductModel.create_product: {model_error}")
            import traceback
            print(f"DEBUG: Model error traceback: {traceback.format_exc()}")
            raise model_error

        print(f"DEBUG: About to return JSONResponse")
        return JSONResponse(
            content={
                "message": "Product created successfully",
                "data": product
            },
            status_code=201
        )
    except HTTPException as e:
        print(f"DEBUG: HTTPException caught: {e}")
        raise e
    except Exception as e:
        print(f"DEBUG: Exception caught: {e}")
        import traceback
        print(f"DEBUG: Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Product creation failed: {str(e)}")

async def update_product(product_id: str, request: Request, current_user: dict = Depends(require_supplier)):
    """
    Endpoint to update an existing product (supplier only).
    """
    try:
        data = await request.json()
    except JSONDecodeError:
        raise HTTPException(status_code=400, detail="Request body cannot be empty")

    # Remove _id if present in data to prevent updating it
    data.pop("_id", None)
    data.pop("id", None)
    data.pop("supplier_id", None)  # Remove supplier_id from request - it comes from token

    try:
        updated_product = ProductModel.update_product(
            product_id=product_id,
            name=data.get("name"),
            category=data.get("category"),
            price_per_unit=data.get("price_per_unit"),
            unit=data.get("unit"),
            available_quantity=data.get("available_quantity"),
            supplier_id=current_user["uid"],  # Use 'uid' instead of '_id'
            location=data.get("location"),
            image_url=data.get("image_url")
        )

        return JSONResponse(
            content={
                "message": "Product updated successfully",
                "data": updated_product
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product update failed: {str(e)}")
    
# get all products of supplier
async def get_all_products(request: Request, _=Depends(require_any_role)):
    """
    Endpoint to get all products (any authenticated user).
    """
    try:
        products = ProductModel.get_all_products()
        return JSONResponse(
            content={
                "message": "Products fetched successfully",
                "data": products
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")
    
# delete the product 
async def delete_product(product_id: str, request: Request, current_user: dict = Depends(require_supplier)):
    """
    Endpoint to delete a product (supplier only).
    """
    try:
        result = ProductModel.delete_product(product_id)
        return JSONResponse(
            content=result,
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product deletion failed: {str(e)}")
    
async def get_my_products(request: Request, current_user: dict = Depends(require_supplier)):
    """
    Endpoint to get all products for the current supplier (supplier only).
    """
    try:
        # Use current user's ID from JWT token
        supplier_id = current_user["uid"]
        print(f"DEBUG: Getting products for supplier: {supplier_id}")
        
        # Call the model method - use get_products_by_supplier
        products = ProductModel.get_products_by_supplier(supplier_id)
        return JSONResponse(
            content={
                "message": "Products fetched successfully",
                "data": products
            },
            status_code=200
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")