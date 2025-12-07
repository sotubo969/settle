from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from models import UserRegister, UserLogin
import auth
from auth import hash_password, verify_password, create_access_token, get_current_user, get_current_vendor
from utils import serialize_doc, generate_order_id

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db_client = client[os.environ['DB_NAME']]

# Set database for auth module
auth.set_database(db_client)

app = FastAPI(title="AfroMarket UK API")
api_router = APIRouter(prefix="/api")

# ============ AUTHENTICATION ROUTES ============
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
    existing_user = await db_client.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_dict = {
        "name": user_data.name,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "role": "customer",
        "avatar": f"https://ui-avatars.com/api/?name={user_data.name.replace(' ', '+')}",
        "addresses": [],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db_client.users.insert_one(user_dict)
    user_dict["_id"] = result.inserted_id
    
    token = create_access_token({"sub": str(result.inserted_id), "email": user_data.email})
    
    return {
        "success": True,
        "token": token,
        "user": serialize_doc(user_dict)
    }

@api_router.post("/auth/login")
async def login(user_data: UserLogin):
    user = await db_client.users.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": str(user["_id"]), "email": user["email"]})
    
    return {
        "success": True,
        "token": token,
        "user": serialize_doc(user)
    }

@api_router.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return serialize_doc(current_user)

# ============ PRODUCT ROUTES ============
@api_router.get("/products")
async def get_products(
    category: Optional[str] = None,
    vendor: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None
):
    query = {}
    
    if category:
        query["category"] = {"$regex": category, "$options": "i"}
    if vendor:
        query["vendor.name"] = {"$regex": vendor, "$options": "i"}
    if minPrice is not None or maxPrice is not None:
        query["price"] = {}
        if minPrice is not None:
            query["price"]["$gte"] = minPrice
        if maxPrice is not None:
            query["price"]["$lte"] = maxPrice
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"brand": {"$regex": search, "$options": "i"}},
            {"category": {"$regex": search, "$options": "i"}}
        ]
    if featured is not None:
        query["featured"] = featured
    
    products = await db_client.products.find(query).to_list(1000)
    return [serialize_doc(p) for p in products]

@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = await db_client.products.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return serialize_doc(product)

# ============ VENDOR ROUTES ============
@api_router.post("/vendors/register")
async def register_vendor(vendor_data: dict):
    vendor_dict = {
        "businessName": vendor_data["businessName"],
        "description": vendor_data["description"],
        "email": vendor_data["email"],
        "phone": vendor_data["phone"],
        "address": vendor_data["address"],
        "city": vendor_data["city"],
        "postcode": vendor_data["postcode"],
        "location": vendor_data["city"],
        "verified": False,
        "rating": 0.0,
        "totalSales": 0,
        "commission": 1.0,
        "status": "pending",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db_client.vendors.insert_one(vendor_dict)
    vendor_dict["_id"] = result.inserted_id
    
    return {
        "success": True,
        "vendor": serialize_doc(vendor_dict)
    }

@api_router.get("/vendors")
async def get_vendors():
    vendors = await db_client.vendors.find({"status": "approved"}).to_list(1000)
    return [serialize_doc(v) for v in vendors]

# ============ CART ROUTES ============
@api_router.get("/cart")
async def get_cart(current_user: dict = Depends(get_current_user)):
    cart = await db_client.carts.find_one({"userId": ObjectId(current_user["_id"])})
    if not cart:
        return {"items": []}
    
    # Populate product details
    cart_items = []
    for item in cart.get("items", []):
        product = await db_client.products.find_one({"_id": item["productId"]})
        if product:
            product_data = serialize_doc(product)
            product_data["quantity"] = item["quantity"]
            cart_items.append(product_data)
    
    return {"items": cart_items}

@api_router.post("/cart/add")
async def add_to_cart(cart_data: dict, current_user: dict = Depends(get_current_user)):
    product_id = ObjectId(cart_data["productId"])
    quantity = cart_data.get("quantity", 1)
    
    product = await db_client.products.find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    cart = await db_client.carts.find_one({"userId": ObjectId(current_user["_id"])})
    
    if not cart:
        cart = {
            "userId": ObjectId(current_user["_id"]),
            "items": [{"productId": product_id, "quantity": quantity}],
            "updatedAt": datetime.utcnow()
        }
        await db_client.carts.insert_one(cart)
    else:
        items = cart.get("items", [])
        existing_item = next((item for item in items if item["productId"] == product_id), None)
        
        if existing_item:
            existing_item["quantity"] += quantity
        else:
            items.append({"productId": product_id, "quantity": quantity})
        
        await db_client.carts.update_one(
            {"userId": ObjectId(current_user["_id"])},
            {"$set": {"items": items, "updatedAt": datetime.utcnow()}}
        )
    
    return {"success": True, "message": "Product added to cart"}

@api_router.delete("/cart/clear")
async def clear_cart(current_user: dict = Depends(get_current_user)):
    await db_client.carts.delete_one({"userId": ObjectId(current_user["_id"])})
    return {"success": True, "message": "Cart cleared"}

# ============ ORDER ROUTES ============
@api_router.post("/orders")
async def create_order(order_data: dict, current_user: dict = Depends(get_current_user)):
    order_dict = {
        "orderId": generate_order_id(),
        "userId": ObjectId(current_user["_id"]),
        "items": order_data["items"],
        "shippingInfo": order_data["shippingInfo"],
        "paymentInfo": order_data["paymentInfo"],
        "subtotal": order_data["subtotal"],
        "deliveryFee": order_data["deliveryFee"],
        "commission": len(order_data["items"]) * 1.0,
        "total": order_data["total"],
        "status": "pending",
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    
    result = await db_client.orders.insert_one(order_dict)
    await db_client.carts.delete_one({"userId": ObjectId(current_user["_id"])})
    
    order_dict["_id"] = result.inserted_id
    return serialize_doc(order_dict)

@api_router.get("/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    orders = await db_client.orders.find({"userId": ObjectId(current_user["_id"])}).to_list(1000)
    return [serialize_doc(o) for o in orders]

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()