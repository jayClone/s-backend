from pydantic import BaseModel, Field
from typing import Optional
from fastapi import HTTPException
from bson import ObjectId
from api.models.Location import LocationModel
from api.db import db

class ProductModel(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    category: str
    price_per_unit: float
    unit: str  # e.g., kg, litre
    available_quantity: float
    image_url: Optional[str] = None
    location: Optional[LocationModel] = None
    supplier_id: str

    class Config:
        populate_by_name = True  # For Pydantic v2
        json_encoders = {}

    class Product:
        @staticmethod
        def get_collection():
            try:
                if db is None:
                    raise HTTPException(status_code=500, detail="Database connection not initialized")
                return db["products"]
            except HTTPException as http_exc:
                raise http_exc
            except Exception as e:
                print(f"Error accessing database: {e}")
                raise HTTPException(status_code=500, detail=f"Error accessing database: {str(e)}")

    # def __init__(self, name, category, price_per_unit, unit, available_quantity, image_url, supplier_id, location=None, _id=None):
    #     self.name = name
    #     self.category = category
    #     self.price_per_unit = price_per_unit
    #     self.unit = unit
    #     self.available_quantity = available_quantity
    #     self.image_url = image_url
    #     self.supplier_id = supplier_id
    #     self.location = location
    #     self._id = _id
        
    @staticmethod
    def create_product(
        name: str,
        category: str,
        price_per_unit: float,
        unit: str,
        available_quantity: float,
        supplier_id: str,
        location: Optional[LocationModel] = None,
        image_url: Optional[str] = None,
    ):
        try:
            # Validate required fields
            if not all([name, category, price_per_unit, unit, available_quantity, supplier_id]):
                raise HTTPException(status_code=400, detail="Missing required product fields.")

            # Create product instance
            product = ProductModel(
                name=name,
                category=category,
                price_per_unit=price_per_unit,
                unit=unit,
                available_quantity=available_quantity,
                supplier_id=supplier_id,
                location=location,
                image_url=image_url
            )

            # Prepare dict for MongoDB, remove _id if None
            product_dict = product.model_dump(by_alias=True)
            if product_dict.get("_id") is None:
                product_dict.pop("_id")

            # Save to DB
            db["products"].insert_one(product_dict)

            return product

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error creating product: {e}")
            raise HTTPException(status_code=500, detail=f"Product creation failed: {str(e)}")

# update product
    @staticmethod
    def update_product(
        product_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        price_per_unit: Optional[float] = None,
        unit: Optional[str] = None,
        available_quantity: Optional[float] = None,
        supplier_id: Optional[str] = None,
        location: Optional[LocationModel] = None,
        image_url: Optional[str] = None,
    ):
        try:
            # Build update dict, skipping None values and _id
            update_fields = {}
            if name is not None:
                update_fields["name"] = name
            if category is not None:
                update_fields["category"] = category
            if price_per_unit is not None:
                update_fields["price_per_unit"] = price_per_unit
            if unit is not None:
                update_fields["unit"] = unit
            if available_quantity is not None:
                update_fields["available_quantity"] = available_quantity
            if supplier_id is not None:
                update_fields["supplier_id"] = supplier_id
            if location is not None:
                update_fields["location"] = location
            if image_url is not None:
                update_fields["image_url"] = image_url

            if not update_fields:
                raise HTTPException(status_code=400, detail="No fields to update.")

            # def serialize_mongo_document(doc):
            #     if not doc:
            #         return doc
            #     doc = dict(doc)
            #     if "_id" in doc and isinstance(doc["_id"], ObjectId):
            #         doc["_id"] = str(doc["_id"])
            #     return doc

            result = db["products"].update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_fields}
            )

            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Product not found.")

            # Return the updated product
            updated_product = db["products"].find_one({"_id": ObjectId(product_id)})
            if not updated_product:
                raise HTTPException(status_code=404, detail="Product not found after update.")
            # Serialize ObjectId to str for JSON response

            if "_id" in updated_product and isinstance(updated_product["_id"], ObjectId):
                updated_product["_id"] = str(updated_product["_id"])

            return updated_product

        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error updating product: {e}")
            raise HTTPException(status_code=500, detail=f"Product update failed: {str(e)}")
        
# get the all product 

    @staticmethod
    def get_all_products():
        try:
            products_cursor = db["products"].find()
            products = []
            for product in products_cursor:
                # Convert ObjectId to str for JSON serialization
                if "_id" in product and isinstance(product["_id"], ObjectId):
                    product["_id"] = str(product["_id"])
                products.append(product)
            return products
        except Exception as e:
            print(f"Error fetching products: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")
        
# get products by supplier
    @staticmethod
    def get_products_by_supplier(supplier_id: str):
        try:
            products_cursor = db["products"].find({"supplier_id": supplier_id})
            products = []
            for product in products_cursor:
                if "_id" in product and isinstance(product["_id"], ObjectId):
                    product["_id"] = str(product["_id"])
                products.append(product)
            return products
        except Exception as e:
            print(f"Error fetching products for supplier: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch products for supplier: {str(e)}")
        
# delete product
    @staticmethod
    def delete_product(product_id: str):
        try:
            result = db["products"].delete_one({"_id": ObjectId(product_id)})
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="Product not found.")
            return {"message": "Product deleted successfully", "product_id": product_id}
        except HTTPException as http_exc:
            raise http_exc
        except Exception as e:
            print(f"Error deleting product: {e}")
            raise HTTPException(status_code=500, detail=f"Product deletion failed: {str(e)}")

