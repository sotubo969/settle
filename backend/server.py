from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, update
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr

from database import get_db, init_db, User, Vendor, Product, Cart, Order
from auth import hash_password, verify_password, create_access_token, get_current_user
from payments import StripePayment, PayPalPaymentService
from oauth import GoogleOAuth, AppleOAuth
from utils import generate_order_id
from email_service import EmailService

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

app = FastAPI(title="AfroMarket UK API")
api_router = APIRouter(prefix="/api")

# Pydantic Models for requests
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class GoogleAuthRequest(BaseModel):
    token: str

class AppleAuthRequest(BaseModel):
    id_token: str
    user_data: Optional[dict] = None

class VendorRegisterRequest(BaseModel):
    businessName: str
    description: str
    email: EmailStr
    phone: str
    address: str
    city: str
    postcode: str

class CartAddRequest(BaseModel):
    productId: int
    quantity: int = 1

class OrderCreateRequest(BaseModel):
    items: list
    shippingInfo: dict
    paymentInfo: dict
    subtotal: float
    deliveryFee: float
    total: float

class PaymentIntentRequest(BaseModel):
    amount: float
    orderId: Optional[str] = None

class PayPalCreateRequest(BaseModel):
    amount: float
    returnUrl: str
    cancelUrl: str

class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

class AddressRequest(BaseModel):
    fullName: str
    address: str
    city: str
    postcode: str
    phone: str
    isDefault: bool = False

class PaymentMethodRequest(BaseModel):
    type: str  # 'card', 'paypal'
    cardNumber: Optional[str] = None
    cardHolder: Optional[str] = None
    expiryDate: Optional[str] = None
    isDefault: bool = False

class ProductCreateRequest(BaseModel):
    name: str
    brand: str
    description: str
    price: float
    originalPrice: Optional[float] = None
    image: str
    category: str
    categoryId: int
    stock: int
    weight: str
    featured: bool = False

class VendorApprovalRequest(BaseModel):
    vendorId: int
    status: str  # 'approved' or 'rejected'

# ============ AUTH ROUTES ============
@api_router.post("/auth/register")
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password=hash_password(user_data.password),
        role="customer",
        avatar=f"https://ui-avatars.com/api/?name={user_data.name.replace(' ', '+')}"
    )
    
    db.add(new_user)
    await db.flush()
    await db.refresh(new_user)
    
    token = create_access_token({"sub": str(new_user.id), "email": new_user.email})
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": new_user.id,
            "name": new_user.name,
            "email": new_user.email,
            "role": new_user.role,
            "avatar": new_user.avatar
        }
    }

@api_router.post("/auth/login")
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not user.password or not verify_password(user_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "avatar": user.avatar
        }
    }

@api_router.post("/auth/google")
async def google_auth(auth_data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    user_info = await GoogleOAuth.verify_token(auth_data.token)
    
    result = await db.execute(select(User).where(User.google_id == user_info['google_id']))
    user = result.scalar_one_or_none()
    
    if not user:
        result = await db.execute(select(User).where(User.email == user_info['email']))
        user = result.scalar_one_or_none()
        
        if user:
            user.google_id = user_info['google_id']
        else:
            user = User(
                name=user_info['name'],
                email=user_info['email'],
                google_id=user_info['google_id'],
                avatar=user_info['avatar'],
                role="customer"
            )
            db.add(user)
        
        await db.flush()
        await db.refresh(user)
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "avatar": user.avatar
        }
    }

@api_router.post("/auth/apple")
async def apple_auth(auth_data: AppleAuthRequest, db: AsyncSession = Depends(get_db)):
    user_info = await AppleOAuth.verify_token(auth_data.id_token)
    
    if auth_data.user_data:
        user_info.update(auth_data.user_data)
    
    result = await db.execute(select(User).where(User.apple_id == user_info['apple_id']))
    user = result.scalar_one_or_none()
    
    if not user:
        if user_info.get('email'):
            result = await db.execute(select(User).where(User.email == user_info['email']))
            user = result.scalar_one_or_none()
        
        if user:
            user.apple_id = user_info['apple_id']
        else:
            user = User(
                name=user_info.get('name', 'Apple User'),
                email=user_info.get('email', f"{user_info['apple_id']}@privaterelay.appleid.com"),
                apple_id=user_info['apple_id'],
                role="customer"
            )
            db.add(user)
        
        await db.flush()
        await db.refresh(user)
    
    token = create_access_token({"sub": str(user.id), "email": user.email})
    
    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "avatar": user.avatar
        }
    }

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "avatar": current_user.avatar,
        "phone": current_user.phone,
        "addresses": current_user.addresses,
        "payment_methods": current_user.payment_methods,
        "wishlist": current_user.wishlist
    }

@api_router.post("/auth/forgot-password")
async def forgot_password(email_data: dict, db: AsyncSession = Depends(get_db)):
    email = email_data.get('email')
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Don't reveal if email exists for security
        return {"success": True, "message": "If email exists, reset instructions sent"}
    
    # TODO: Generate reset token and send email
    # For now, just log it
    print(f"\n{'='*60}")
    print(f"PASSWORD RESET REQUEST")
    print(f"{'='*60}")
    print(f"Email: {email}")
    print(f"User: {user.name}")
    print(f"Reset Link: https://afrobasket.preview.emergentagent.com/reset-password?token=GENERATED_TOKEN")
    print(f"{'='*60}\n")
    
    return {"success": True, "message": "Password reset instructions sent"}

# ============ PRODUCT ROUTES ============
@api_router.get("/products")
async def get_products(
    category: Optional[str] = None,
    vendor: Optional[str] = None,
    minPrice: Optional[float] = None,
    maxPrice: Optional[float] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Product)
    
    if category:
        query = query.where(Product.category.ilike(f"%{category}%"))
    if minPrice is not None:
        query = query.where(Product.price >= minPrice)
    if maxPrice is not None:
        query = query.where(Product.price <= maxPrice)
    if search:
        query = query.where(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.brand.ilike(f"%{search}%"),
                Product.category.ilike(f"%{search}%")
            )
        )
    if featured is not None:
        query = query.where(Product.featured == featured)
    
    result = await db.execute(query)
    products = result.scalars().all()
    
    return [{
        "id": p.id,
        "name": p.name,
        "brand": p.brand,
        "description": p.description,
        "price": p.price,
        "originalPrice": p.original_price,
        "image": p.image,
        "category": p.category,
        "categoryId": p.category_id,
        "vendor": p.vendor_info,
        "vendorId": p.vendor_id,
        "rating": p.rating,
        "reviews": p.reviews,
        "stock": p.stock,
        "weight": p.weight,
        "inStock": p.in_stock,
        "featured": p.featured
    } for p in products]

@api_router.get("/products/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "name": product.name,
        "brand": product.brand,
        "description": product.description,
        "price": product.price,
        "originalPrice": product.original_price,
        "image": product.image,
        "category": product.category,
        "categoryId": product.category_id,
        "vendor": product.vendor_info,
        "vendorId": product.vendor_id,
        "rating": product.rating,
        "reviews": product.reviews,
        "stock": product.stock,
        "weight": product.weight,
        "inStock": product.in_stock,
        "featured": product.featured
    }

# ============ VENDOR ROUTES ============
@api_router.post("/vendors/register")
async def register_vendor(vendor_data: VendorRegisterRequest, db: AsyncSession = Depends(get_db)):
    from email_service import email_service
    from datetime import datetime
    
    new_vendor = Vendor(
        business_name=vendor_data.businessName,
        description=vendor_data.description,
        email=vendor_data.email,
        phone=vendor_data.phone,
        address=vendor_data.address,
        city=vendor_data.city,
        postcode=vendor_data.postcode,
        location=vendor_data.city,
        verified=False,
        status="pending"
    )
    
    db.add(new_vendor)
    await db.flush()
    await db.refresh(new_vendor)
    
    # Send email notification to admin
    vendor_email_data = {
        'business_name': new_vendor.business_name,
        'email': new_vendor.email,
        'phone': new_vendor.phone,
        'address': new_vendor.address,
        'city': new_vendor.city,
        'postcode': new_vendor.postcode,
        'description': new_vendor.description,
        'created_at': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    }
    
    # Send notification email (will work in background)
    try:
        email_service.send_vendor_registration_notification(vendor_email_data)
    except Exception as e:
        logger.warning(f"Failed to send email notification: {str(e)}")
        # Don't fail the registration if email fails
    
    return {
        "success": True,
        "vendor": {
            "id": new_vendor.id,
            "businessName": new_vendor.business_name,
            "status": new_vendor.status
        }
    }

@api_router.get("/vendors")
async def get_vendors(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Vendor).where(Vendor.status == "approved"))
    vendors = result.scalars().all()
    
    return [{
        "id": v.id,
        "name": v.business_name,
        "rating": v.rating,
        "totalSales": v.total_sales,
        "location": v.location,
        "verified": v.verified
    } for v in vendors]

# ============ VENDOR PRODUCT MANAGEMENT ============
@api_router.post("/vendor/products")
async def create_vendor_product(
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get vendor for current user
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="You must be a registered vendor")
    
    if vendor.status != "approved":
        raise HTTPException(status_code=403, detail="Your vendor account is not approved yet")
    
    new_product = Product(
        name=product_data['name'],
        brand=product_data['brand'],
        description=product_data['description'],
        price=product_data['price'],
        original_price=product_data.get('originalPrice'),
        image=product_data['image'],
        category=product_data['category'],
        category_id=product_data['categoryId'],
        vendor_id=vendor.id,
        vendor_info={
            "name": vendor.business_name,
            "rating": vendor.rating,
            "location": vendor.location,
            "totalSales": vendor.total_sales
        },
        stock=product_data['stock'],
        weight=product_data['weight'],
        featured=product_data.get('featured', False)
    )
    
    db.add(new_product)
    await db.flush()
    await db.refresh(new_product)
    
    return {
        "success": True,
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price
        }
    }

@api_router.get("/vendor/products")
async def get_vendor_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get vendor for current user
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="You must be a registered vendor")
    
    # Get all products for this vendor
    result = await db.execute(select(Product).where(Product.vendor_id == vendor.id))
    products = result.scalars().all()
    
    return [{
        "id": p.id,
        "name": p.name,
        "brand": p.brand,
        "price": p.price,
        "originalPrice": p.original_price,
        "image": p.image,
        "category": p.category,
        "stock": p.stock,
        "featured": p.featured,
        "inStock": p.in_stock
    } for p in products]

@api_router.put("/vendor/products/{product_id}")
async def update_vendor_product(
    product_id: int,
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get vendor for current user
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="You must be a registered vendor")
    
    # Get product and verify ownership
    result = await db.execute(select(Product).where(Product.id == product_id, Product.vendor_id == vendor.id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or you don't have permission")
    
    # Update fields
    if 'name' in product_data:
        product.name = product_data['name']
    if 'brand' in product_data:
        product.brand = product_data['brand']
    if 'description' in product_data:
        product.description = product_data['description']
    if 'price' in product_data:
        product.price = product_data['price']
    if 'originalPrice' in product_data:
        product.original_price = product_data['originalPrice']
    if 'image' in product_data:
        product.image = product_data['image']
    if 'stock' in product_data:
        product.stock = product_data['stock']
        product.in_stock = product_data['stock'] > 0
    if 'featured' in product_data:
        product.featured = product_data['featured']
    
    product.updated_at = datetime.utcnow()
    await db.flush()
    
    return {"success": True, "message": "Product updated successfully"}

@api_router.delete("/vendor/products/{product_id}")
async def delete_vendor_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get vendor for current user
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="You must be a registered vendor")
    
    # Get product and verify ownership
    result = await db.execute(select(Product).where(Product.id == product_id, Product.vendor_id == vendor.id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or you don't have permission")
    
    await db.delete(product)
    await db.flush()
    
    return {"success": True, "message": "Product deleted successfully"}

@api_router.get("/vendor/dashboard/stats")
async def get_vendor_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get vendor for current user
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="You must be a registered vendor")
    
    # Get product count
    result = await db.execute(select(Product).where(Product.vendor_id == vendor.id))
    products = result.scalars().all()
    
    # Get orders for this vendor's products (simplified)
    total_revenue = sum(p.price * 10 for p in products)  # Mock calculation
    
    return {
        "totalSales": vendor.total_sales,
        "totalProducts": len(products),
        "revenue": total_revenue,
        "pendingOrders": 5,  # Mock
        "rating": vendor.rating
    }

# ============ CART ROUTES ============
@api_router.get("/cart")
async def get_cart(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if not cart or not cart.items:
        return {"items": []}
    
    cart_items = []
    for item in cart.items:
        product_result = await db.execute(select(Product).where(Product.id == item['productId']))
        product = product_result.scalar_one_or_none()
        
        if product:
            cart_items.append({
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "price": product.price,
                "image": product.image,
                "quantity": item['quantity'],
                "stock": product.stock,
                "weight": product.weight,
                "vendor": product.vendor_info
            })
    
    return {"items": cart_items}

@api_router.post("/cart/add")
async def add_to_cart(
    cart_data: CartAddRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Product).where(Product.id == cart_data.productId))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if not cart:
        cart = Cart(user_id=current_user.id, items=[])
        db.add(cart)
    
    items = list(cart.items or [])
    existing_item = next((item for item in items if item['productId'] == cart_data.productId), None)
    
    if existing_item:
        existing_item['quantity'] += cart_data.quantity
    else:
        items.append({"productId": cart_data.productId, "quantity": cart_data.quantity})
    
    cart.items = items
    cart.updated_at = datetime.utcnow()
    
    # Mark as modified to trigger SQLAlchemy update
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(cart, "items")
    
    await db.flush()
    await db.commit()
    
    return {"success": True, "message": "Product added to cart"}

@api_router.put("/cart/update/{product_id}")
async def update_cart_quantity(
    product_id: int,
    quantity: int = Query(..., ge=1),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = list(cart.items or [])
    item_found = False
    
    for item in items:
        if item['productId'] == product_id:
            item['quantity'] = quantity
            item_found = True
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Product not in cart")
    
    cart.items = items
    cart.updated_at = datetime.utcnow()
    
    # Mark as modified to trigger SQLAlchemy update
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(cart, "items")
    
    await db.flush()
    await db.commit()
    
    return {"success": True, "message": "Cart updated"}

@api_router.delete("/cart/remove/{product_id}")
async def remove_from_cart(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items = list(cart.items or [])
    items = [item for item in items if item['productId'] != product_id]
    
    cart.items = items
    cart.updated_at = datetime.utcnow()
    
    # Mark as modified to trigger SQLAlchemy update
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(cart, "items")
    
    await db.flush()
    await db.commit()
    
    return {"success": True, "message": "Product removed from cart"}

@api_router.delete("/cart/clear")
async def clear_cart(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    
    if cart:
        await db.delete(cart)
        await db.flush()
        await db.commit()
    
    return {"success": True, "message": "Cart cleared"}

# ============ ORDER ROUTES ============
@api_router.post("/orders")
async def create_order(
    order_data: OrderCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    new_order = Order(
        order_id=generate_order_id(),
        user_id=current_user.id,
        items=order_data.items,
        shipping_info=order_data.shippingInfo,
        payment_info=order_data.paymentInfo,
        subtotal=order_data.subtotal,
        delivery_fee=order_data.deliveryFee,
        commission=len(order_data.items) * 1.0,
        total=order_data.total,
        status="pending"
    )
    
    db.add(new_order)
    await db.flush()
    await db.refresh(new_order)
    
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    if cart:
        await db.delete(cart)
    
    return {
        "id": new_order.id,
        "orderId": new_order.order_id,
        "total": new_order.total,
        "status": new_order.status,
        "createdAt": new_order.created_at.isoformat()
    }

@api_router.get("/orders")
async def get_orders(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.user_id == current_user.id))
    orders = result.scalars().all()
    
    return [{
        "id": o.id,
        "orderId": o.order_id,
        "items": len(o.items),
        "total": o.total,
        "status": o.status,
        "date": o.created_at.strftime("%Y-%m-%d")
    } for o in orders]

# ============ PAYMENT ROUTES ============
@api_router.post("/payment/stripe/create-intent")
async def create_stripe_intent(payment_data: PaymentIntentRequest):
    result = await StripePayment.create_payment_intent(
        amount=payment_data.amount,
        metadata={"orderId": payment_data.orderId} if payment_data.orderId else None
    )
    return result

@api_router.post("/payment/stripe/confirm/{payment_intent_id}")
async def confirm_stripe_payment(payment_intent_id: str):
    result = await StripePayment.confirm_payment(payment_intent_id)
    return result

@api_router.post("/payment/stripe/apple-pay")
async def process_apple_pay(payment_method_id: str, amount: float):
    result = await StripePayment.process_apple_pay(payment_method_id, amount)
    return result

@api_router.post("/payment/paypal/create")
async def create_paypal_payment(payment_data: PayPalCreateRequest):
    result = await PayPalPaymentService.create_payment(
        amount=payment_data.amount,
        return_url=payment_data.returnUrl,
        cancel_url=payment_data.cancelUrl
    )
    return result

@api_router.post("/payment/paypal/execute")
async def execute_paypal_payment(payment_id: str, payer_id: str):
    result = await PayPalPaymentService.execute_payment(payment_id, payer_id)
    return result

# ============ PROFILE MANAGEMENT ROUTES ============
@api_router.put("/profile/update")
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if profile_data.name:
        current_user.name = profile_data.name
    if profile_data.phone:
        current_user.phone = profile_data.phone
    if profile_data.avatar:
        current_user.avatar = profile_data.avatar
    
    current_user.updated_at = datetime.utcnow()
    await db.flush()
    
    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone": current_user.phone,
            "avatar": current_user.avatar
        }
    }

@api_router.post("/profile/addresses")
async def add_address(
    address_data: AddressRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    addresses = current_user.addresses or []
    
    # If this is default, unset other defaults
    if address_data.isDefault:
        for addr in addresses:
            addr['isDefault'] = False
    
    new_address = address_data.dict()
    addresses.append(new_address)
    
    current_user.addresses = addresses
    current_user.updated_at = datetime.utcnow()
    await db.flush()
    
    return {"success": True, "addresses": addresses}

@api_router.delete("/profile/addresses/{index}")
async def delete_address(
    index: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    addresses = current_user.addresses or []
    
    if 0 <= index < len(addresses):
        addresses.pop(index)
        current_user.addresses = addresses
        current_user.updated_at = datetime.utcnow()
        await db.flush()
        return {"success": True, "addresses": addresses}
    
    raise HTTPException(status_code=404, detail="Address not found")

@api_router.post("/profile/payment-methods")
async def add_payment_method(
    payment_data: PaymentMethodRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    payment_methods = current_user.payment_methods or []
    
    # If this is default, unset other defaults
    if payment_data.isDefault:
        for pm in payment_methods:
            pm['isDefault'] = False
    
    new_method = payment_data.dict()
    # Mask card number for security
    if new_method.get('cardNumber'):
        new_method['cardNumberMasked'] = '**** **** **** ' + new_method['cardNumber'][-4:]
        del new_method['cardNumber']
    
    payment_methods.append(new_method)
    
    current_user.payment_methods = payment_methods
    current_user.updated_at = datetime.utcnow()
    await db.flush()
    
    return {"success": True, "paymentMethods": payment_methods}

@api_router.delete("/profile/payment-methods/{index}")
async def delete_payment_method(
    index: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    payment_methods = current_user.payment_methods or []
    
    if 0 <= index < len(payment_methods):
        payment_methods.pop(index)
        current_user.payment_methods = payment_methods
        current_user.updated_at = datetime.utcnow()
        await db.flush()
        return {"success": True, "paymentMethods": payment_methods}
    
    raise HTTPException(status_code=404, detail="Payment method not found")

# ============ WISHLIST ROUTES ============
@api_router.post("/wishlist/add/{product_id}")
async def add_to_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if product exists
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get fresh user from db
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    
    wishlist = list(user.wishlist if user.wishlist else [])
    
    if product_id not in wishlist:
        wishlist.append(product_id)
        user.wishlist = wishlist
        user.updated_at = datetime.utcnow()
        
        # Mark as modified to trigger SQLAlchemy update
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "wishlist")
        
        await db.commit()
        await db.refresh(user)
    
    return {"success": True, "message": "Added to wishlist"}

@api_router.delete("/wishlist/remove/{product_id}")
async def remove_from_wishlist(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Get fresh user from db
    result = await db.execute(select(User).where(User.id == current_user.id))
    user = result.scalar_one_or_none()
    
    wishlist = user.wishlist if user.wishlist else []
    
    if product_id in wishlist:
        wishlist.remove(product_id)
        user.wishlist = wishlist
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
    
    return {"success": True, "message": "Removed from wishlist"}

@api_router.get("/wishlist")
async def get_wishlist(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    wishlist = current_user.wishlist or []
    
    products = []
    for product_id in wishlist:
        result = await db.execute(select(Product).where(Product.id == product_id))
        product = result.scalar_one_or_none()
        
        if product:
            products.append({
                "id": product.id,
                "name": product.name,
                "brand": product.brand,
                "price": product.price,
                "originalPrice": product.original_price,
                "image": product.image,
                "rating": product.rating,
                "reviews": product.reviews,
                "inStock": product.in_stock
            })
    
    return {"items": products}

# ============ VENDOR PRODUCT MANAGEMENT ============
@api_router.post("/vendor/products")
async def create_product(
    product_data: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Check if user is a vendor
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id, Vendor.status == "approved"))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Only approved vendors can add products")
    
    new_product = Product(
        name=product_data.name,
        brand=product_data.brand,
        description=product_data.description,
        price=product_data.price,
        original_price=product_data.originalPrice,
        image=product_data.image,
        category=product_data.category,
        category_id=product_data.categoryId,
        vendor_id=vendor.id,
        vendor_info={
            "name": vendor.business_name,
            "rating": vendor.rating,
            "location": vendor.location,
            "totalSales": vendor.total_sales
        },
        stock=product_data.stock,
        weight=product_data.weight,
        featured=product_data.featured,
        in_stock=product_data.stock > 0
    )
    
    db.add(new_product)
    await db.flush()
    await db.refresh(new_product)
    
    return {
        "success": True,
        "product": {
            "id": new_product.id,
            "name": new_product.name,
            "price": new_product.price
        }
    }

@api_router.get("/vendor/my-products")
async def get_vendor_products(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        return {"products": []}
    
    result = await db.execute(select(Product).where(Product.vendor_id == vendor.id))
    products = result.scalars().all()
    
    return [{
        "id": p.id,
        "name": p.name,
        "brand": p.brand,
        "price": p.price,
        "stock": p.stock,
        "category": p.category,
        "image": p.image,
        "featured": p.featured,
        "inStock": p.in_stock
    } for p in products]

@api_router.put("/vendor/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor not found")
    
    result = await db.execute(select(Product).where(Product.id == product_id, Product.vendor_id == vendor.id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = product_data.name
    product.brand = product_data.brand
    product.description = product_data.description
    product.price = product_data.price
    product.original_price = product_data.originalPrice
    product.image = product_data.image
    product.category = product_data.category
    product.category_id = product_data.categoryId
    product.stock = product_data.stock
    product.weight = product_data.weight
    product.featured = product_data.featured
    product.in_stock = product_data.stock > 0
    product.updated_at = datetime.utcnow()
    
    await db.flush()
    
    return {"success": True, "message": "Product updated"}

@api_router.delete("/vendor/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Vendor).where(Vendor.user_id == current_user.id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor not found")
    
    result = await db.execute(select(Product).where(Product.id == product_id, Product.vendor_id == vendor.id))
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await db.delete(product)
    await db.flush()
    
    return {"success": True, "message": "Product deleted"}

# ============ ADMIN VENDOR APPROVAL ============
@api_router.post("/admin/vendors/approve")
async def approve_vendor(
    approval_data: VendorApprovalRequest,
    db: AsyncSession = Depends(get_db)
):
    # TODO: Add admin authentication check
    
    result = await db.execute(select(Vendor).where(Vendor.id == approval_data.vendorId))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    vendor.status = approval_data.status
    vendor.verified = (approval_data.status == "approved")
    vendor.updated_at = datetime.utcnow()
    
    await db.flush()
    
    if approval_data.status == "approved":
        await EmailService.send_vendor_approval_notification(vendor.email, vendor.business_name)
    
    return {"success": True, "message": f"Vendor {approval_data.status}"}

@api_router.get("/admin/vendors/pending")
async def get_pending_vendors(db: AsyncSession = Depends(get_db)):
    # TODO: Add admin authentication check
    
    result = await db.execute(select(Vendor).where(Vendor.status == "pending"))
    vendors = result.scalars().all()
    
    return [{
        "id": v.id,
        "businessName": v.business_name,
        "email": v.email,
        "phone": v.phone,
        "city": v.city,
        "description": v.description,
        "createdAt": v.created_at.isoformat()
    } for v in vendors]

# Health check
@api_router.get("/health")
async def health_check():
    return {"status": "ok", "message": "AfroMarket UK API is running"}

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

@app.on_event("startup")
async def startup():
    await init_db()
    logger.info("Database initialized")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down")
