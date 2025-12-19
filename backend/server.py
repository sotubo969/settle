from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, Cookie, Header
from fastapi.security import HTTPBearer
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, update
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

from database import get_db, init_db, User, Vendor, Product, Cart, Order, Analytics, PageVisit, PasswordResetToken
import secrets
from auth import hash_password, verify_password, create_access_token, get_current_user
from payments import StripePayment, PayPalPaymentService
from oauth import GoogleOAuth, AppleOAuth
from utils import generate_order_id
from email_service import EmailService
from mongo_db import get_mongo_db, init_mongo_indexes
from auth_emergent import (
    exchange_session_id, 
    create_or_update_user, 
    save_session, 
    delete_session,
    get_current_user_from_token
)
from subscription_models import (
    VendorTier,
    MembershipTier,
    VENDOR_PRICING,
    CUSTOMER_PRICING,
    FEATURED_PRICING,
    calculate_commission,
    calculate_service_fee,
    calculate_delivery_fee,
    calculate_premium_discount,
    calculate_roi_for_vendor,
    calculate_customer_roi,
    calculate_loyalty_points,
    get_vendor_benefits,
    get_customer_benefits
)

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

# ============ EMERGENT AUTH ROUTES (Google OAuth) ============
class SessionExchangeRequest(BaseModel):
    session_id: str

@api_router.post("/auth/session")
async def exchange_session(request: SessionExchangeRequest):
    """
    Exchange session_id from Emergent Auth for user data and set session cookie
    """
    from fastapi import Response
    
    # Get user data from Emergent Auth service
    user_data = await exchange_session_id(request.session_id)
    
    # Get MongoDB instance
    mongo_db = get_mongo_db()
    
    # Create or update user in MongoDB
    user_id = await create_or_update_user(mongo_db, user_data)
    
    # Save session to database
    session_token = user_data.get("session_token")
    await save_session(mongo_db, user_id, session_token)
    
    # Return user data (frontend will handle cookie setting for now)
    return {
        "success": True,
        "session_token": session_token,
        "user": {
            "user_id": user_id,
            "email": user_data.get("email"),
            "name": user_data.get("name"),
            "picture": user_data.get("picture")
        }
    }

@api_router.get("/auth/me/oauth")
async def get_me_oauth(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """
    Get current user from Emergent Auth session
    """
    # Get MongoDB instance
    mongo_db = get_mongo_db()
    
    # Get user from session token
    user_data = await get_current_user_from_token(
        session_token=session_token,
        authorization=authorization,
        db=mongo_db
    )
    
    return {
        "user_id": user_data.get("user_id"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "picture": user_data.get("picture"),
        "role": user_data.get("role", "customer")
    }

@api_router.post("/auth/logout/oauth")
async def logout_oauth(session_token: Optional[str] = Cookie(None)):
    """
    Logout user and delete session from Emergent Auth
    """
    if session_token:
        # Get MongoDB instance
        mongo_db = get_mongo_db()
        
        # Delete session from database
        await delete_session(mongo_db, session_token)
    
    return {"success": True, "message": "Logged out successfully"}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    password: str
    confirmPassword: str

@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Request password reset - sends email with reset link"""
    from email_service import email_service
    
    # Find user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()
    
    # Always return success message to prevent email enumeration
    success_message = "If an account with this email exists, you will receive a password reset link shortly."
    
    if not user:
        return {"success": True, "message": success_message}
    
    # Invalidate any existing reset tokens for this user
    await db.execute(
        update(PasswordResetToken)
        .where(PasswordResetToken.user_id == user.id, PasswordResetToken.used == False)
        .values(used=True)
    )
    
    # Generate secure token
    reset_token = secrets.token_urlsafe(32)
    
    # Set expiration to 30 minutes from now
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    # Save token to database
    new_token = PasswordResetToken(
        user_id=user.id,
        token=reset_token,
        expires_at=expires_at,
        used=False
    )
    db.add(new_token)
    await db.flush()
    
    # Generate reset link
    frontend_url = os.environ.get('FRONTEND_URL', 'https://code-fetcher-23.preview.emergentagent.com')
    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    
    # Send email
    try:
        email_service.send_password_reset_email(
            to_email=user.email,
            user_name=user.name,
            reset_link=reset_link
        )
        logger.info(f"Password reset email sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send password reset email: {str(e)}")
    
    return {"success": True, "message": success_message}

@api_router.get("/auth/reset-password/verify/{token}")
async def verify_reset_token(token: str, db: AsyncSession = Depends(get_db)):
    """Verify if a reset token is valid"""
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        )
    )
    reset_token = result.scalar_one_or_none()
    
    if not reset_token:
        raise HTTPException(
            status_code=400, 
            detail="Invalid or expired reset link. Please request a new password reset."
        )
    
    # Get user info (don't expose too much)
    user_result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = user_result.scalar_one_or_none()
    
    return {
        "valid": True,
        "email": user.email if user else None,
        "expiresAt": reset_token.expires_at.isoformat()
    }

@api_router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    """Reset password using token"""
    from email_service import email_service
    
    # Validate passwords match
    if request.password != request.confirmPassword:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Validate password strength
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    
    if not any(c.isupper() for c in request.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter")
    
    if not any(c.islower() for c in request.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one lowercase letter")
    
    if not any(c.isdigit() for c in request.password):
        raise HTTPException(status_code=400, detail="Password must contain at least one number")
    
    # Find and validate token
    result = await db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == request.token,
            PasswordResetToken.used == False,
            PasswordResetToken.expires_at > datetime.utcnow()
        )
    )
    reset_token = result.scalar_one_or_none()
    
    if not reset_token:
        raise HTTPException(
            status_code=400, 
            detail="Invalid or expired reset link. Please request a new password reset."
        )
    
    # Get user
    user_result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Hash new password
    user.password = hash_password(request.password)
    user.updated_at = datetime.utcnow()
    
    # Invalidate the token
    reset_token.used = True
    
    await db.flush()
    await db.commit()
    
    # Send confirmation email
    try:
        email_service.send_password_changed_confirmation(
            to_email=user.email,
            user_name=user.name
        )
        logger.info(f"Password changed confirmation sent to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send password changed email: {str(e)}")
    
    return {
        "success": True, 
        "message": "Your password has been successfully reset. You can now login with your new password."
    }

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
    
    wishlist = list(user.wishlist if user.wishlist else [])
    
    if product_id in wishlist:
        wishlist.remove(product_id)
        user.wishlist = wishlist
        user.updated_at = datetime.utcnow()
        
        # Mark as modified to trigger SQLAlchemy update
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(user, "wishlist")
        
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
async def get_my_vendor_products(
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

@api_router.get("/")
async def root():
    return {"status": "ok", "message": "AfroMarket UK API is running"}

# ============ SUBSCRIPTION & MONETIZATION ENDPOINTS ============

@api_router.get("/subscriptions/vendor-tiers")
async def get_vendor_tiers():
    """Get all vendor subscription tiers with pricing and features"""
    return {
        "tiers": {
            "basic": VENDOR_PRICING[VendorTier.BASIC],
            "professional": VENDOR_PRICING[VendorTier.PROFESSIONAL],
            "elite": VENDOR_PRICING[VendorTier.ELITE]
        }
    }

@api_router.get("/subscriptions/customer-tiers")
async def get_customer_tiers():
    """Get customer membership tiers"""
    return {
        "tiers": {
            "free": CUSTOMER_PRICING[MembershipTier.FREE],
            "plus": CUSTOMER_PRICING[MembershipTier.PLUS]
        }
    }

@api_router.post("/subscriptions/vendor/calculate-roi")
async def vendor_roi_calculator(
    current_tier: str,
    target_tier: str,
    monthly_sales: float
):
    """Calculate ROI for vendor tier upgrade"""
    try:
        current = VendorTier(current_tier)
        target = VendorTier(target_tier)
        roi = calculate_roi_for_vendor(monthly_sales, current, target)
        return {
            "success": True,
            "roi": roi
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/subscriptions/customer/calculate-roi")
async def customer_roi_calculator(
    monthly_orders: int,
    avg_order_value: float
):
    """Calculate ROI for premium membership"""
    roi = calculate_customer_roi(monthly_orders, avg_order_value)
    return {
        "success": True,
        "roi": roi
    }

@api_router.get("/subscriptions/featured-pricing")
async def get_featured_pricing():
    """Get featured listing pricing"""
    return {"pricing": FEATURED_PRICING}

@api_router.post("/orders/calculate-fees")
async def calculate_order_fees(
    order_total: float,
    is_express: bool = False,
    is_premium_member: bool = False
):
    """Calculate all fees for an order"""
    service_fee = calculate_service_fee(order_total)
    delivery_fee = calculate_delivery_fee(order_total, is_express, is_premium_member)
    premium_discount = calculate_premium_discount(order_total, 
        MembershipTier.PLUS if is_premium_member else MembershipTier.FREE)
    
    subtotal = order_total
    total = subtotal + service_fee + delivery_fee - premium_discount
    
    return {
        "subtotal": round(subtotal, 2),
        "service_fee": service_fee,
        "delivery_fee": delivery_fee,
        "premium_discount": premium_discount,
        "total": round(total, 2),
        "breakdown": {
            "order_items": round(subtotal, 2),
            "service_fee": f"+£{service_fee}",
            "delivery": f"+£{delivery_fee}" if delivery_fee > 0 else "FREE",
            "premium_discount": f"-£{premium_discount}" if premium_discount > 0 else None
        }
    }

@api_router.post("/vendors/upgrade-tier")
async def upgrade_vendor_tier(
    vendor_id: int,
    new_tier: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade vendor subscription tier"""
    if current_user.role != "vendor":
        raise HTTPException(status_code=403, detail="Only vendors can upgrade tiers")
    
    try:
        tier = VendorTier(new_tier)
        vendor = await db.get(Vendor, vendor_id)
        
        if not vendor or vendor.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Vendor not found")
        
        # Update vendor tier (add subscription_tier field if not exists)
        # This would integrate with Stripe for actual billing
        
        return {
            "success": True,
            "message": f"Upgraded to {tier.value} tier",
            "benefits": get_vendor_benefits(tier)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@api_router.post("/customers/upgrade-premium")
async def upgrade_customer_premium(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upgrade customer to premium membership"""
    # This would integrate with Stripe for actual billing
    
    return {
        "success": True,
        "message": "Upgraded to AfroMarket PLUS",
        "benefits": get_customer_benefits(MembershipTier.PLUS),
        "next_billing_date": (datetime.now() + timedelta(days=30)).isoformat()
    }

# ============ OWNER DASHBOARD ROUTES (Protected) ============
OWNER_EMAIL = "sotubodammy@gmail.com"

async def verify_owner(current_user: User = Depends(get_current_user)):
    """Verify that the current user is the owner"""
    if current_user.email != OWNER_EMAIL:
        raise HTTPException(status_code=403, detail="Access denied. Owner only.")
    return current_user

@api_router.get("/owner/dashboard")
async def get_owner_dashboard(
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get owner dashboard overview with all statistics"""
    from sqlalchemy import func
    
    # Get total vendors
    vendor_result = await db.execute(select(func.count(Vendor.id)))
    total_vendors = vendor_result.scalar() or 0
    
    # Get approved vendors
    approved_result = await db.execute(select(func.count(Vendor.id)).where(Vendor.status == "approved"))
    approved_vendors = approved_result.scalar() or 0
    
    # Get pending vendors
    pending_result = await db.execute(select(func.count(Vendor.id)).where(Vendor.status == "pending"))
    pending_vendors = pending_result.scalar() or 0
    
    # Get total products
    product_result = await db.execute(select(func.count(Product.id)))
    total_products = product_result.scalar() or 0
    
    # Get total orders
    order_result = await db.execute(select(func.count(Order.id)))
    total_orders = order_result.scalar() or 0
    
    # Get total revenue
    revenue_result = await db.execute(select(func.sum(Order.total)))
    total_revenue = revenue_result.scalar() or 0
    
    # Get total commission earned
    commission_result = await db.execute(select(func.sum(Order.commission)))
    total_commission = commission_result.scalar() or 0
    
    # Get total users
    user_result = await db.execute(select(func.count(User.id)))
    total_users = user_result.scalar() or 0
    
    # Get orders by status
    pending_orders_result = await db.execute(select(func.count(Order.id)).where(Order.status == "pending"))
    pending_orders = pending_orders_result.scalar() or 0
    
    completed_orders_result = await db.execute(select(func.count(Order.id)).where(Order.status == "completed"))
    completed_orders = completed_orders_result.scalar() or 0
    
    # Get recent orders (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders_result = await db.execute(
        select(func.count(Order.id)).where(Order.created_at >= seven_days_ago)
    )
    recent_orders = recent_orders_result.scalar() or 0
    
    # Get page visits (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    visits_result = await db.execute(
        select(func.sum(PageVisit.visits)).where(PageVisit.date >= thirty_days_ago)
    )
    total_visits = visits_result.scalar() or 0
    
    # Get product analytics (clicks)
    product_clicks_result = await db.execute(
        select(func.count(Analytics.id)).where(Analytics.event_type == "product_click")
    )
    product_clicks = product_clicks_result.scalar() or 0
    
    return {
        "overview": {
            "totalVendors": total_vendors,
            "approvedVendors": approved_vendors,
            "pendingVendors": pending_vendors,
            "totalProducts": total_products,
            "totalOrders": total_orders,
            "totalRevenue": round(total_revenue, 2),
            "totalCommission": round(total_commission, 2),
            "totalUsers": total_users,
            "pendingOrders": pending_orders,
            "completedOrders": completed_orders,
            "recentOrders": recent_orders,
            "totalPageVisits": total_visits,
            "productClicks": product_clicks
        }
    }

@api_router.get("/owner/vendors")
async def get_owner_vendors(
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get all vendors with detailed information"""
    from sqlalchemy import func
    
    result = await db.execute(select(Vendor).order_by(Vendor.created_at.desc()))
    vendors = result.scalars().all()
    
    vendor_data = []
    for vendor in vendors:
        # Get product count for vendor
        product_count_result = await db.execute(
            select(func.count(Product.id)).where(Product.vendor_id == vendor.id)
        )
        product_count = product_count_result.scalar() or 0
        
        # Calculate vendor revenue from orders
        # Get orders containing this vendor's products
        orders_result = await db.execute(select(Order))
        all_orders = orders_result.scalars().all()
        
        vendor_revenue = 0
        vendor_orders = 0
        for order in all_orders:
            for item in order.items:
                if item.get('vendorId') == vendor.id:
                    vendor_revenue += item.get('price', 0) * item.get('quantity', 1)
                    vendor_orders += 1
        
        vendor_data.append({
            "id": vendor.id,
            "businessName": vendor.business_name,
            "email": vendor.email,
            "phone": vendor.phone,
            "address": vendor.address,
            "city": vendor.city,
            "postcode": vendor.postcode,
            "location": vendor.location,
            "description": vendor.description,
            "status": vendor.status,
            "verified": vendor.verified,
            "rating": vendor.rating,
            "totalSales": vendor.total_sales,
            "commission": vendor.commission,
            "productCount": product_count,
            "revenue": round(vendor_revenue, 2),
            "orderCount": vendor_orders,
            "createdAt": vendor.created_at.isoformat(),
            "updatedAt": vendor.updated_at.isoformat()
        })
    
    return {"vendors": vendor_data}

@api_router.get("/owner/products")
async def get_owner_products(
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get all products with vendor details and analytics"""
    from sqlalchemy import func
    
    result = await db.execute(select(Product).order_by(Product.created_at.desc()))
    products = result.scalars().all()
    
    product_data = []
    for product in products:
        # Get click count for this product
        clicks_result = await db.execute(
            select(func.count(Analytics.id)).where(
                Analytics.product_id == product.id,
                Analytics.event_type == "product_click"
            )
        )
        clicks = clicks_result.scalar() or 0
        
        # Get view count
        views_result = await db.execute(
            select(func.count(Analytics.id)).where(
                Analytics.product_id == product.id,
                Analytics.event_type == "product_view"
            )
        )
        views = views_result.scalar() or 0
        
        # Get add to cart count
        cart_adds_result = await db.execute(
            select(func.count(Analytics.id)).where(
                Analytics.product_id == product.id,
                Analytics.event_type == "add_to_cart"
            )
        )
        cart_adds = cart_adds_result.scalar() or 0
        
        # Get vendor info
        vendor_result = await db.execute(select(Vendor).where(Vendor.id == product.vendor_id))
        vendor = vendor_result.scalar_one_or_none()
        
        product_data.append({
            "id": product.id,
            "name": product.name,
            "brand": product.brand,
            "description": product.description,
            "price": product.price,
            "originalPrice": product.original_price,
            "image": product.image,
            "category": product.category,
            "categoryId": product.category_id,
            "stock": product.stock,
            "weight": product.weight,
            "inStock": product.in_stock,
            "featured": product.featured,
            "rating": product.rating,
            "reviews": product.reviews,
            "vendorId": product.vendor_id,
            "vendorName": vendor.business_name if vendor else "Unknown",
            "vendorStatus": vendor.status if vendor else "unknown",
            "analytics": {
                "clicks": clicks,
                "views": views,
                "cartAdds": cart_adds
            },
            "createdAt": product.created_at.isoformat(),
            "updatedAt": product.updated_at.isoformat()
        })
    
    return {"products": product_data}

@api_router.get("/owner/analytics")
async def get_owner_analytics(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analytics for the platform"""
    from sqlalchemy import func
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get page visits by day
    visits_result = await db.execute(
        select(PageVisit).where(PageVisit.date >= start_date).order_by(PageVisit.date)
    )
    visits = visits_result.scalars().all()
    
    daily_visits = {}
    for visit in visits:
        date_key = visit.date.strftime("%Y-%m-%d")
        if date_key not in daily_visits:
            daily_visits[date_key] = {"visits": 0, "uniqueVisitors": 0}
        daily_visits[date_key]["visits"] += visit.visits
        daily_visits[date_key]["uniqueVisitors"] += visit.unique_visitors
    
    # Get product analytics
    product_analytics_result = await db.execute(
        select(
            Analytics.product_id,
            Analytics.event_type,
            func.count(Analytics.id).label('count')
        ).where(
            Analytics.created_at >= start_date,
            Analytics.product_id.isnot(None)
        ).group_by(Analytics.product_id, Analytics.event_type)
    )
    product_analytics = product_analytics_result.all()
    
    # Get top products by clicks
    top_products_result = await db.execute(
        select(
            Analytics.product_id,
            func.count(Analytics.id).label('clicks')
        ).where(
            Analytics.event_type == "product_click",
            Analytics.product_id.isnot(None)
        ).group_by(Analytics.product_id).order_by(func.count(Analytics.id).desc()).limit(10)
    )
    top_products_data = top_products_result.all()
    
    top_products = []
    for prod_id, clicks in top_products_data:
        prod_result = await db.execute(select(Product).where(Product.id == prod_id))
        product = prod_result.scalar_one_or_none()
        if product:
            top_products.append({
                "id": product.id,
                "name": product.name,
                "image": product.image,
                "clicks": clicks
            })
    
    # Get orders by day
    orders_result = await db.execute(
        select(Order).where(Order.created_at >= start_date).order_by(Order.created_at)
    )
    orders = orders_result.scalars().all()
    
    daily_orders = {}
    daily_revenue = {}
    for order in orders:
        date_key = order.created_at.strftime("%Y-%m-%d")
        if date_key not in daily_orders:
            daily_orders[date_key] = 0
            daily_revenue[date_key] = 0
        daily_orders[date_key] += 1
        daily_revenue[date_key] += order.total
    
    return {
        "period": f"Last {days} days",
        "dailyVisits": daily_visits,
        "dailyOrders": daily_orders,
        "dailyRevenue": daily_revenue,
        "topProducts": top_products,
        "totalVisits": sum(v["visits"] for v in daily_visits.values()),
        "totalOrders": len(orders),
        "totalRevenue": round(sum(daily_revenue.values()), 2)
    }

@api_router.get("/owner/transactions")
async def get_owner_transactions(
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get all transactions grouped by vendor"""
    from sqlalchemy import func
    
    # Get all orders
    orders_result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    orders = orders_result.scalars().all()
    
    # Get all vendors
    vendors_result = await db.execute(select(Vendor))
    vendors = {v.id: v for v in vendors_result.scalars().all()}
    
    vendor_transactions = {}
    all_transactions = []
    
    for order in orders:
        # Get user info
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        user = user_result.scalar_one_or_none()
        
        # Track by vendor
        for item in order.items:
            vendor_id = item.get('vendorId')
            if vendor_id:
                if vendor_id not in vendor_transactions:
                    vendor = vendors.get(vendor_id)
                    vendor_transactions[vendor_id] = {
                        "vendorId": vendor_id,
                        "vendorName": vendor.business_name if vendor else "Unknown",
                        "totalRevenue": 0,
                        "totalOrders": 0,
                        "totalCommission": 0,
                        "transactions": []
                    }
                
                item_total = item.get('price', 0) * item.get('quantity', 1)
                item_commission = item_total * 0.10  # 10% commission
                
                vendor_transactions[vendor_id]["totalRevenue"] += item_total
                vendor_transactions[vendor_id]["totalOrders"] += 1
                vendor_transactions[vendor_id]["totalCommission"] += item_commission
                vendor_transactions[vendor_id]["transactions"].append({
                    "orderId": order.order_id,
                    "productName": item.get('name'),
                    "quantity": item.get('quantity'),
                    "price": item.get('price'),
                    "total": item_total,
                    "commission": round(item_commission, 2),
                    "vendorEarning": round(item_total - item_commission, 2),
                    "date": order.created_at.isoformat(),
                    "status": order.status
                })
        
        all_transactions.append({
            "id": order.id,
            "orderId": order.order_id,
            "customerName": user.name if user else "Unknown",
            "customerEmail": user.email if user else "Unknown",
            "items": len(order.items),
            "subtotal": order.subtotal,
            "deliveryFee": order.delivery_fee,
            "commission": order.commission,
            "total": order.total,
            "status": order.status,
            "paymentMethod": order.payment_info.get('method', 'Unknown'),
            "createdAt": order.created_at.isoformat()
        })
    
    # Round totals
    for vid in vendor_transactions:
        vendor_transactions[vid]["totalRevenue"] = round(vendor_transactions[vid]["totalRevenue"], 2)
        vendor_transactions[vid]["totalCommission"] = round(vendor_transactions[vid]["totalCommission"], 2)
    
    return {
        "vendorTransactions": list(vendor_transactions.values()),
        "allTransactions": all_transactions,
        "summary": {
            "totalTransactions": len(all_transactions),
            "totalRevenue": round(sum(t["total"] for t in all_transactions), 2),
            "totalCommission": round(sum(t["commission"] for t in all_transactions), 2)
        }
    }

@api_router.get("/owner/sales")
async def get_owner_sales(
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get sales statistics per vendor"""
    from sqlalchemy import func
    
    # Get all vendors
    vendors_result = await db.execute(select(Vendor))
    vendors = vendors_result.scalars().all()
    
    # Get all orders
    orders_result = await db.execute(select(Order))
    orders = orders_result.scalars().all()
    
    vendor_sales = []
    for vendor in vendors:
        # Calculate sales from orders
        total_sales = 0
        total_items_sold = 0
        order_count = 0
        
        for order in orders:
            for item in order.items:
                if item.get('vendorId') == vendor.id:
                    total_sales += item.get('price', 0) * item.get('quantity', 1)
                    total_items_sold += item.get('quantity', 1)
                    order_count += 1
        
        # Get product count
        product_count_result = await db.execute(
            select(func.count(Product.id)).where(Product.vendor_id == vendor.id)
        )
        product_count = product_count_result.scalar() or 0
        
        commission_earned = total_sales * 0.10  # 10% commission
        vendor_earning = total_sales - commission_earned
        
        vendor_sales.append({
            "vendorId": vendor.id,
            "vendorName": vendor.business_name,
            "email": vendor.email,
            "status": vendor.status,
            "verified": vendor.verified,
            "productCount": product_count,
            "totalSales": round(total_sales, 2),
            "totalItemsSold": total_items_sold,
            "orderCount": order_count,
            "commissionEarned": round(commission_earned, 2),
            "vendorEarning": round(vendor_earning, 2),
            "averageOrderValue": round(total_sales / order_count, 2) if order_count > 0 else 0
        })
    
    # Sort by total sales
    vendor_sales.sort(key=lambda x: x["totalSales"], reverse=True)
    
    return {
        "vendorSales": vendor_sales,
        "summary": {
            "totalVendors": len(vendors),
            "totalSales": round(sum(v["totalSales"] for v in vendor_sales), 2),
            "totalCommission": round(sum(v["commissionEarned"] for v in vendor_sales), 2),
            "totalVendorEarnings": round(sum(v["vendorEarning"] for v in vendor_sales), 2)
        }
    }

@api_router.get("/owner/deliveries")
async def get_owner_deliveries(
    status: Optional[str] = None,
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Get all deliveries with tracking information"""
    query = select(Order).order_by(Order.created_at.desc())
    
    if status:
        query = query.where(Order.delivery_status == status)
    
    result = await db.execute(query)
    orders = result.scalars().all()
    
    deliveries = []
    for order in orders:
        # Get user info
        user_result = await db.execute(select(User).where(User.id == order.user_id))
        user = user_result.scalar_one_or_none()
        
        deliveries.append({
            "id": order.id,
            "orderId": order.order_id,
            "customerName": user.name if user else "Unknown",
            "customerEmail": user.email if user else "Unknown",
            "shippingAddress": order.shipping_info,
            "items": order.items,
            "itemCount": len(order.items),
            "total": order.total,
            "orderStatus": order.status,
            "deliveryStatus": order.delivery_status or "processing",
            "trackingNumber": order.tracking_number,
            "carrier": order.carrier,
            "estimatedDelivery": order.estimated_delivery.isoformat() if order.estimated_delivery else None,
            "deliveredAt": order.delivered_at.isoformat() if order.delivered_at else None,
            "createdAt": order.created_at.isoformat(),
            "updatedAt": order.updated_at.isoformat()
        })
    
    # Count by status
    status_counts = {
        "processing": 0,
        "shipped": 0,
        "in_transit": 0,
        "out_for_delivery": 0,
        "delivered": 0
    }
    for d in deliveries:
        status_key = d["deliveryStatus"]
        if status_key in status_counts:
            status_counts[status_key] += 1
    
    return {
        "deliveries": deliveries,
        "statusCounts": status_counts,
        "totalDeliveries": len(deliveries)
    }

class DeliveryUpdateRequest(BaseModel):
    deliveryStatus: str
    trackingNumber: Optional[str] = None
    carrier: Optional[str] = None
    estimatedDelivery: Optional[str] = None

@api_router.put("/owner/deliveries/{order_id}")
async def update_delivery(
    order_id: str,
    delivery_data: DeliveryUpdateRequest,
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Update delivery status and tracking information"""
    result = await db.execute(select(Order).where(Order.order_id == order_id))
    order = result.scalar_one_or_none()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.delivery_status = delivery_data.deliveryStatus
    
    if delivery_data.trackingNumber:
        order.tracking_number = delivery_data.trackingNumber
    if delivery_data.carrier:
        order.carrier = delivery_data.carrier
    if delivery_data.estimatedDelivery:
        order.estimated_delivery = datetime.fromisoformat(delivery_data.estimatedDelivery.replace('Z', '+00:00'))
    
    if delivery_data.deliveryStatus == "delivered":
        order.delivered_at = datetime.utcnow()
        order.status = "completed"
    
    order.updated_at = datetime.utcnow()
    await db.flush()
    
    return {"success": True, "message": "Delivery updated successfully"}

# Analytics tracking endpoint
class AnalyticsEventRequest(BaseModel):
    eventType: str
    pageUrl: Optional[str] = None
    productId: Optional[int] = None
    sessionId: Optional[str] = None

@api_router.post("/analytics/track")
async def track_analytics_event(
    event_data: AnalyticsEventRequest,
    db: AsyncSession = Depends(get_db)
):
    """Track analytics events (page views, product clicks, etc.)"""
    new_event = Analytics(
        event_type=event_data.eventType,
        page_url=event_data.pageUrl,
        product_id=event_data.productId,
        session_id=event_data.sessionId
    )
    
    db.add(new_event)
    await db.flush()
    
    # Also update page visits if it's a page view
    if event_data.eventType == "page_view" and event_data.pageUrl:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(PageVisit).where(
                PageVisit.date == today,
                PageVisit.page == event_data.pageUrl
            )
        )
        page_visit = result.scalar_one_or_none()
        
        if page_visit:
            page_visit.visits += 1
        else:
            new_visit = PageVisit(
                date=today,
                page=event_data.pageUrl,
                visits=1,
                unique_visitors=1
            )
            db.add(new_visit)
    
    return {"success": True}

# Vendor approval by owner
@api_router.put("/owner/vendors/{vendor_id}/approve")
async def owner_approve_vendor(
    vendor_id: int,
    status: str = Query(..., regex="^(approved|rejected)$"),
    current_user: User = Depends(verify_owner),
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject a vendor"""
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    vendor.status = status
    vendor.verified = (status == "approved")
    vendor.updated_at = datetime.utcnow()
    
    await db.flush()
    
    # Send email notification
    if status == "approved":
        try:
            await EmailService.send_vendor_approval_notification(vendor.email, vendor.business_name)
        except:
            pass
    
    return {"success": True, "message": f"Vendor {status}"}

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
    # Initialize MongoDB indexes for Emergent Auth
    await init_mongo_indexes()
    logger.info("MongoDB indexes initialized")

@app.on_event("shutdown")
async def shutdown():
    from mongo_db import close_mongo_connection
    await close_mongo_connection()
    logger.info("Shutting down")
