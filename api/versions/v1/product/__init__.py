from fastapi import APIRouter, Request, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse
from api.controllers.product_controller import create_product,update_product,get_all_products,delete_product,get_products_by_supplier



# Base User Router
router = APIRouter()


# http://localhost:10021/api/v1/product/
@router.get("", response_description="product API Home")
@router.get("/", response_description="product API Home")
async def user_home_route(_=Depends(RateLimiter(times=5, seconds=60))):
    return JSONResponse(
        content={
            "location": "api/v1/user/product",
            "message": "Welcome to the Product API"
        },
        status_code=200
    )
# http://localhost:10021/api/v1/product/create
@router.post("/create", response_description="Create a new product")
async def create_product_route(request: Request):
    return await create_product(request)

# http://localhost:10021/api/v1/product/update
@router.put("/update/{product_id}", response_description="Update product")
async def update_product_route(product_id: str, request: Request):
    return await update_product(product_id, request)

# http://localhost:10021/api/v1/product/get_all_products
@router.get("/get_all_products", response_description="Get all products")
async def get_all_products_route(request: Request):
    return await get_all_products(request)

# http://localhost:10021/api/v1/product/delete/{product_id}
@router.delete("/delete/{product_id}", response_description="Delete a product")
async def delete_product_route(product_id: str, request: Request):
    return await delete_product(product_id, request)

# http://localhost:10021/api/v1/product/supplier/{supplier_id}
@router.get("/supplier/{supplier_id}", response_description="Get all products for a supplier")
async def get_products_by_supplier_route(supplier_id: str, request: Request):
    return await get_products_by_supplier(supplier_id, request)

