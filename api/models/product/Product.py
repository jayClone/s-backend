from pydantic import BaseModel, Field
from typing import Optional
from fastapi import HTTPException
from bson import ObjectId
from api.models.Location import LocationModel
from api.db import db
from api.extensions.helper.json_serializer import serialize_for_json

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
            print(f"DEBUG: create_product called with: name={name}, category={category}, supplier_id={supplier_id}")
            
            # Validate required fields
            if not all([name, category, price_per_unit, unit, available_quantity, supplier_id]):
                raise HTTPException(status_code=400, detail="Missing required product fields.")

            # Handle location conversion if it's a dict
            location_obj = None
            if location:
                print(f"DEBUG: Processing location: {location}")
                if isinstance(location, dict):
                    # Convert 'zip' to 'pincode' if present
                    if "zip" in location:
                        location["pincode"] = location.pop("zip")
                    # Add default country if not present
                    if "country" not in location:
                        location["country"] = "USA"
                    print(f"DEBUG: Creating LocationModel with: {location}")
                    try:
                        location_obj = LocationModel(**location)
                        print(f"DEBUG: LocationModel created successfully")
                    except Exception as loc_error:
                        print(f"DEBUG: Error creating LocationModel: {loc_error}")
                        raise HTTPException(status_code=400, detail=f"Invalid location data: {str(loc_error)}")
                elif isinstance(location, LocationModel):
                    location_obj = location

            # Create product instance
            print(f"DEBUG: Creating ProductModel instance")
            try:
                product = ProductModel(
                    name=name,
                    category=category,
                    price_per_unit=price_per_unit,
                    unit=unit,
                    available_quantity=available_quantity,
                    supplier_id=supplier_id,
                    location=location_obj,
                    image_url=image_url
                )
                print(f"DEBUG: ProductModel instance created successfully")
            except Exception as product_error:
                print(f"DEBUG: Error creating ProductModel instance: {product_error}")
                raise HTTPException(status_code=400, detail=f"Invalid product data: {str(product_error)}")

            # Prepare dict for MongoDB, remove _id if None
            print(f"DEBUG: Preparing product dict for MongoDB")
            product_dict = product.model_dump(by_alias=True)
            if product_dict.get("_id") is None:
                product_dict.pop("_id")
            print(f"DEBUG: Product dict prepared: {product_dict}")

            # Save to DB
            print(f"DEBUG: Saving to database")
            try:
                result = db["products"].insert_one(product_dict)
                print(f"DEBUG: Database insert successful, inserted_id: {result.inserted_id}")
            except Exception as db_error:
                print(f"DEBUG: Database insert error: {db_error}")
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
            
            # Get the created product from database with the actual _id
            print(f"DEBUG: Retrieving created product from database")
            try:
                created_product = db["products"].find_one({"_id": result.inserted_id})
                print(f"DEBUG: Retrieved product: {created_product}")
            except Exception as retrieve_error:
                print(f"DEBUG: Error retrieving created product: {retrieve_error}")
                raise HTTPException(status_code=500, detail=f"Error retrieving created product: {str(retrieve_error)}")
            
            # Serialize for JSON response
            print(f"DEBUG: Serializing product for JSON")
            try:
                serialized_product = serialize_for_json(created_product)
                print(f"DEBUG: Product serialized successfully")
                return serialized_product
            except Exception as serialize_error:
                print(f"DEBUG: Error serializing product: {serialize_error}")
                raise HTTPException(status_code=500, detail=f"Error serializing product: {str(serialize_error)}")

        except HTTPException as http_exc:
            print(f"DEBUG: HTTPException in create_product: {http_exc}")
            raise http_exc
        except Exception as e:
            print(f"DEBUG: Unexpected error in create_product: {e}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
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
            # Remove None values
            update_data = {k: v for k, v in locals().items() if k != 'product_id' and v is not None}
            
            if not update_data:
                raise HTTPException(status_code=400, detail="No valid fields to update")
            
            result = db["products"].update_one(
                {"_id": ObjectId(product_id)},
                {"$set": update_data}
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="Product not found")
            
            # Return updated product
            updated_product = db["products"].find_one({"_id": ObjectId(product_id)})
            return serialize_for_json(updated_product)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update product: {str(e)}")
        
# get the all product 

    @staticmethod
    def get_all_products():
        """Get all products"""
        try:
            products = list(db["products"].find({}))
            # Serialize all products for JSON
            serialized_products = []
            for product in products:
                serialized_product = serialize_for_json(product)
                serialized_products.append(serialized_product)
            return serialized_products
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")

    @staticmethod
    def get_my_products(supplier_id: str):
        """Get all products for the current supplier"""
        try:
            products = list(db["products"].find({"supplier_id": supplier_id}))
            print(f"DEBUG: Found {len(products)} products")
            
            # Serialize all products for JSON
            serialized_products = []
            for product in products:
                serialized_product = serialize_for_json(product)
                serialized_products.append(serialized_product)
            
            return serialized_products
        except Exception as e:
            print(f"DEBUG: Error getting products: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")

# Keep the existing get_products_by_supplier method for backward compatibility
    @staticmethod
    def get_products_by_supplier(supplier_id: str):
        """Get all products for a particular supplier"""
        try:
            products = list(db["products"].find({"supplier_id": supplier_id}))
            # Serialize all products for JSON
            serialized_products = []
            for product in products:
                serialized_product = serialize_for_json(product)
                serialized_products.append(serialized_product)
            return serialized_products
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to fetch products for supplier: {str(e)}")
            
    # delete product
    @staticmethod
    def delete_product(product_id: str):
            """Delete a product"""
            try:
                result = db["products"].delete_one({"_id": ObjectId(product_id)})
                if result.deleted_count == 0:
                    raise HTTPException(status_code=404, detail="Product not found")
                return {"message": "Product deleted successfully"}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to delete product: {str(e)}")
            
    # get product by id
    @staticmethod
    def get_product_by_id(product_id: str):
            """Get a product by ID"""
            try:
                product = db["products"].find_one({"_id": ObjectId(product_id)})
                if not product:
                    raise HTTPException(status_code=404, detail="Product not found")
                return serialize_for_json(product)
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")

