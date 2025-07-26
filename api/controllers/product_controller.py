from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from json import JSONDecodeError
from api.models.product.Product import ProductModel

async def create_product(request: Request):
    """
    Endpoint to create a new product.
    Accepts all fields from ProductModel.
    """
    try:
        try:
            data = await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request body cannot be empty")

        # Required fields as per ProductModel
        required_fields = ["name", "category", "price_per_unit", "unit", "available_quantity", "supplier_id"]
        missing = [field for field in required_fields if field not in data or not data[field]]
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

        # Create the product using the static method
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

        # If you have a save method, save to DB here
        # product.save()

        return JSONResponse(
            content={
                "message": "Product created successfully",
                "data": product.dict(by_alias=True)
            },
            status_code=201
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product creation failed: {str(e)}")

async def update_product(product_id: str, request: Request):
    """
    Endpoint to update an existing product.
    Accepts any updatable fields from ProductModel except _id.
    """
    try:
        try:
            data = await request.json()
        except JSONDecodeError:
            raise HTTPException(status_code=400, detail="Request body cannot be empty")

        # Remove _id if present in data to prevent updating it
        data.pop("_id", None)
        data.pop("id", None)

        # Call the static update method
        updated_product = ProductModel.update_product(
            product_id=product_id,
            name=data.get("name"),
            category=data.get("category"),
            price_per_unit=data.get("price_per_unit"),
            unit=data.get("unit"),
            available_quantity=data.get("available_quantity"),
            supplier_id=data.get("supplier_id"),
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
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product update failed: {str(e)}")
    
# get all products of supplier
async def get_all_products(request: Request):
    """
    Endpoint to get all products.
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
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")
    
# delete the product 
async def delete_product(product_id: str, request: Request):
    """
    Endpoint to delete a product by its ID.
    """
    try:
        result = ProductModel.delete_product(product_id)
        return JSONResponse(
            content=result,
            status_code=200
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product deletion failed: {str(e)}")
    
# get all products of supplier
async def get_products_by_supplier(supplier_id: str, request: Request):
    """
    Endpoint to get all products for a particular supplier.
    """
    try:
        products = ProductModel.get_products_by_supplier(supplier_id)
        return JSONResponse(
            content={
                "message": "Products fetched successfully",
                "data": products
            },
            status_code=200
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products for supplier: {str(e)}")