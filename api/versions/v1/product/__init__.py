from fastapi import APIRouter, Request, Depends
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse
from api.controllers.product_controller import (
    create_product, 
    update_product, 
    get_all_products, 
    delete_product, 
    get_my_products
)
from api.extensions.jwt.dependencies import get_current_user, require_supplier, require_any_role

# Base Product Router
router = APIRouter()

# http://localhost:10021/api/v1/product/
@router.get("", response_description="Product API Home")
@router.get("/", response_description="Product API Home")
async def product_home_route(_=Depends(RateLimiter(times=5, seconds=60))):
    return JSONResponse(
        content={
            "location": "api/v1/product",
            "message": "Welcome to the Product API"
        },
        status_code=200
    )

# http://localhost:10021/api/v1/product/create
@router.post("/create", response_description="Create a new product")
async def create_product_route(request: Request, current_user: dict = Depends(require_supplier)):
    return await create_product(request, current_user)

# http://localhost:10021/api/v1/product/update/{product_id}
@router.put("/update/{product_id}", response_description="Update product")
async def update_product_route(product_id: str, request: Request, current_user: dict = Depends(require_supplier)):
    return await update_product(product_id, request, current_user)

# http://localhost:10021/api/v1/product/get_all_products
@router.get("/get_all_products", response_description="Get all products")
async def get_all_products_route(request: Request, _=Depends(require_any_role)):
    return await get_all_products(request)

# http://localhost:10021/api/v1/product/delete/{product_id}
@router.delete("/delete/{product_id}", response_description="Delete a product")
async def delete_product_route(product_id: str, request: Request, current_user: dict = Depends(require_supplier)):
    return await delete_product(product_id, request, current_user)

# http://localhost:10021/api/v1/product/my_products
@router.get("/my_products", response_description="Get current supplier's products")
async def get_my_products_route(request: Request, current_user: dict = Depends(require_supplier)):
    return await get_my_products(request, current_user)

