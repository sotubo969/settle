from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, Cookie, Header, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
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

from database import get_db, init_db, User, Vendor, Product, Cart, Order, Analytics, PageVisit, PasswordResetToken, Advertisement, VendorWallet, WalletTransaction
import secrets
from auth import hash_password, verify_password, create_access_token, get_current_user, get_current_user_from_db
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
from chatbot_service import AfroBotService
from firebase_auth import verify_firebase_token, is_firebase_configured

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

class FirebaseAuthRequest(BaseModel):
    idToken: str
    displayName: Optional[str] = None
    photoURL: Optional[str] = None

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

# Chatbot Request Models
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatMessage(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[str] = None

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

# ============ ADVERTISEMENT PRICING ============
# Reasonable pricing for UK market - not too expensive, not too cheap
AD_PRICING = {
    "basic": {
        "name": "Basic Ad",
        "description": "Shows in product listings with 'Sponsored' badge",
        "placement": "products",
        "7_days": 9.99,
        "14_days": 16.99,
        "30_days": 29.99,
        "boost_multiplier": 1.5  # 50% more visibility
    },
    "featured": {
        "name": "Featured Ad",
        "description": "Highlighted in Featured Products section on homepage",
        "placement": "homepage",
        "7_days": 19.99,
        "14_days": 34.99,
        "30_days": 59.99,
        "boost_multiplier": 2.5  # 150% more visibility
    },
    "premium_banner": {
        "name": "Premium Banner",
        "description": "Large banner ad on homepage carousel - maximum exposure",
        "placement": "homepage_banner",
        "7_days": 34.99,
        "14_days": 59.99,
        "30_days": 99.99,
        "boost_multiplier": 5.0  # 400% more visibility
    }
}

# Pay-per-performance pricing
AD_PERFORMANCE_PRICING = {
    "cost_per_impression": 0.001,  # £0.001 per impression (£1 per 1000 impressions / CPM)
    "cost_per_click": 0.05,  # £0.05 per click (CPC)
    "min_daily_budget": 1.0,  # Minimum £1 daily budget
    "min_total_budget": 5.0,  # Minimum £5 total budget
}

# Wallet top-up options
WALLET_TOPUP_OPTIONS = [
    {"amount": 10, "label": "£10"},
    {"amount": 25, "label": "£25"},
    {"amount": 50, "label": "£50"},
    {"amount": 100, "label": "£100"},
    {"amount": 250, "label": "£250"},
    {"amount": 500, "label": "£500"},
]

# Advertisement Request Models
class AdCreateRequest(BaseModel):
    title: str
    description: Optional[str] = None
    image: str
    link_url: Optional[str] = None
    product_id: Optional[int] = None
    ad_type: str  # 'basic', 'featured', 'premium_banner'
    billing_type: str = 'fixed'  # 'fixed', 'per_impression', 'per_click', 'per_both'
    duration_days: Optional[int] = None  # For fixed billing
    daily_budget: Optional[float] = None  # For pay-per-performance
    total_budget: Optional[float] = None  # For pay-per-performance

class AdApprovalRequest(BaseModel):
    ad_id: int
    action: str  # 'approve' or 'reject'
    admin_notes: Optional[str] = None

# Wallet Request Models
class WalletTopUpRequest(BaseModel):
    amount: float  # Amount in GBP

class AutoRechargeSetupRequest(BaseModel):
    enabled: bool
    threshold: float = 5.0  # Recharge when balance falls below this
    amount: float = 20.0  # Amount to add
    payment_method_id: Optional[str] = None  # Stripe payment method

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
    
    token = create_access_token({"sub": str(new_user.id), "email": new_user.email, "name": new_user.name, "role": new_user.role})
    
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
    
    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name, "role": user.role})
    
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
    
    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name, "role": user.role})
    
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
    
    token = create_access_token({"sub": str(user.id), "email": user.email, "name": user.name, "role": user.role})
    
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

# ============ FIREBASE AUTH ROUTES ============
@api_router.post("/auth/firebase")
async def firebase_auth(auth_data: FirebaseAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user via Firebase ID token.
    Creates or updates user in database and returns JWT token.
    
    - Google Sign-In: Users are automatically verified
    - Email/Password: Users must verify email before this endpoint accepts them
    """
    try:
        # Verify Firebase token
        firebase_user = await verify_firebase_token(auth_data.idToken)
        
        # Check if email is verified (Google users are always verified)
        if not firebase_user['email_verified']:
            raise HTTPException(
                status_code=403, 
                detail="Email not verified. Please verify your email before logging in."
            )
        
        email = firebase_user['email']
        firebase_uid = firebase_user['uid']
        auth_provider = firebase_user['auth_provider']
        
        # Check if user exists by firebase_uid or email
        result = await db.execute(select(User).where(User.firebase_uid == firebase_uid))
        user = result.scalar_one_or_none()
        
        if not user:
            # Check by email
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
        
        if user:
            # Update existing user with Firebase info
            user.firebase_uid = firebase_uid
            user.auth_provider = auth_provider
            user.email_verified = True
            
            if auth_data.displayName and not user.name:
                user.name = auth_data.displayName
            if auth_data.photoURL:
                user.avatar = auth_data.photoURL
            
            user.updated_at = datetime.utcnow()
            await db.flush()
        else:
            # Create new user
            name = auth_data.displayName or firebase_user.get('name') or email.split('@')[0]
            avatar = auth_data.photoURL or firebase_user.get('picture') or f"https://ui-avatars.com/api/?name={name.replace(' ', '+')}"
            
            user = User(
                name=name,
                email=email,
                firebase_uid=firebase_uid,
                auth_provider=auth_provider,
                email_verified=True,
                avatar=avatar,
                role="customer"
            )
            
            db.add(user)
            await db.flush()
            await db.refresh(user)
        
        # Create JWT token
        token = create_access_token({
            "sub": str(user.id), 
            "email": user.email, 
            "name": user.name, 
            "role": user.role,
            "auth_provider": auth_provider,
            "email_verified": True
        })
        
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role,
                "avatar": user.avatar,
                "emailVerified": True,
                "authProvider": auth_provider
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Firebase auth error: {e}")
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")

@api_router.get("/auth/firebase/status")
async def firebase_status():
    """Check if Firebase is configured"""
    return {
        "configured": is_firebase_configured(),
        "message": "Firebase is configured" if is_firebase_configured() else "Firebase not configured - please set FIREBASE_SERVICE_ACCOUNT"
    }

@api_router.get("/auth/me")
async def get_me(
    credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile information"""
    from auth import get_current_user_from_db
    
    current_user = await get_current_user_from_db(credentials, db)
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
        "avatar": current_user.avatar,
        "phone": current_user.phone,
        "addresses": current_user.addresses or [],
        "payment_methods": current_user.payment_methods or [],
        "wishlist": current_user.wishlist or []
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
async def register_vendor(vendor_data: VendorRegisterRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    from email_service import email_service
    from datetime import datetime
    
    new_vendor = Vendor(
        user_id=current_user.id,  # Link vendor to current user
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
    from email_service import email_service
    
    # Validate shipping info has required fields
    shipping_info = order_data.shippingInfo
    required_fields = ['fullName', 'address', 'city', 'postcode', 'phone']
    missing_fields = [f for f in required_fields if not shipping_info.get(f)]
    
    if missing_fields:
        raise HTTPException(
            status_code=400, 
            detail=f"Missing required shipping information: {', '.join(missing_fields)}"
        )
    
    # Calculate proper commission (10% of subtotal)
    commission = order_data.subtotal * 0.10
    
    new_order = Order(
        order_id=generate_order_id(),
        user_id=current_user.id,
        items=order_data.items,
        shipping_info=order_data.shippingInfo,
        payment_info=order_data.paymentInfo,
        subtotal=order_data.subtotal,
        delivery_fee=order_data.deliveryFee,
        commission=commission,
        total=order_data.total,
        status="confirmed",
        delivery_status="processing"
    )
    
    db.add(new_order)
    await db.flush()
    await db.refresh(new_order)
    
    # Clear the cart
    result = await db.execute(select(Cart).where(Cart.user_id == current_user.id))
    cart = result.scalar_one_or_none()
    if cart:
        await db.delete(cart)
    
    # Send confirmation email to customer
    try:
        order_email_data = {
            'orderId': new_order.order_id,
            'items': order_data.items,
            'subtotal': order_data.subtotal,
            'deliveryFee': order_data.deliveryFee,
            'total': order_data.total,
            'shippingInfo': order_data.shippingInfo
        }
        email_service.send_order_confirmation(
            to_email=current_user.email,
            customer_name=current_user.name,
            order_data=order_email_data
        )
        logger.info(f"Order confirmation email sent to {current_user.email}")
    except Exception as e:
        logger.error(f"Failed to send order confirmation email: {str(e)}")
    
    # Send notification to vendors
    try:
        # Group items by vendor
        vendor_items = {}
        for item in order_data.items:
            vendor_id = item.get('vendorId')
            if vendor_id:
                if vendor_id not in vendor_items:
                    vendor_items[vendor_id] = []
                vendor_items[vendor_id].append(item)
        
        # Send email to each vendor
        for vendor_id, items in vendor_items.items():
            vendor_result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
            vendor = vendor_result.scalar_one_or_none()
            if vendor:
                customer_info = {
                    'name': shipping_info.get('fullName', current_user.name),
                    'email': current_user.email,
                    'phone': shipping_info.get('phone', ''),
                    'address': shipping_info.get('address', ''),
                    'city': shipping_info.get('city', ''),
                    'postcode': shipping_info.get('postcode', '')
                }
                vendor_order_data = {
                    'orderId': new_order.order_id,
                    'items': items
                }
                email_service.send_vendor_order_notification(
                    to_email=vendor.email,
                    vendor_name=vendor.business_name,
                    order_data=vendor_order_data,
                    customer_info=customer_info
                )
                logger.info(f"Order notification sent to vendor {vendor.business_name}")
    except Exception as e:
        logger.error(f"Failed to send vendor notification: {str(e)}")
    
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

# ============ VENDOR DASHBOARD ROUTES ============
async def get_vendor_for_user(user_id: int, db: AsyncSession):
    """Helper to get vendor for a user"""
    result = await db.execute(select(Vendor).where(Vendor.user_id == user_id))
    return result.scalar_one_or_none()

@api_router.get("/vendor/dashboard")
async def get_vendor_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive vendor dashboard data"""
    from sqlalchemy import func
    
    vendor = await get_vendor_for_user(current_user.id, db)
    if not vendor:
        raise HTTPException(status_code=403, detail="You are not a registered vendor")
    
    # Get vendor products
    products_result = await db.execute(select(Product).where(Product.vendor_id == vendor.id))
    products = products_result.scalars().all()
    product_ids = [p.id for p in products]
    
    # Get all orders
    orders_result = await db.execute(select(Order))
    all_orders = orders_result.scalars().all()
    
    # Calculate vendor statistics
    total_revenue = 0
    total_orders = 0
    total_items_sold = 0
    pending_orders = 0
    completed_orders = 0
    processing_orders = 0
    
    for order in all_orders:
        for item in order.items:
            if item.get('vendorId') == vendor.id:
                item_total = item.get('price', 0) * item.get('quantity', 1)
                total_revenue += item_total
                total_items_sold += item.get('quantity', 1)
                total_orders += 1
                
                if order.status == 'pending':
                    pending_orders += 1
                elif order.status == 'completed':
                    completed_orders += 1
                else:
                    processing_orders += 1
    
    commission = total_revenue * 0.10
    net_earnings = total_revenue - commission
    
    # Get product analytics
    analytics_result = await db.execute(
        select(func.count(Analytics.id)).where(
            Analytics.product_id.in_(product_ids),
            Analytics.event_type == "product_view"
        )
    )
    total_views = analytics_result.scalar() or 0
    
    clicks_result = await db.execute(
        select(func.count(Analytics.id)).where(
            Analytics.product_id.in_(product_ids),
            Analytics.event_type == "product_click"
        )
    )
    total_clicks = clicks_result.scalar() or 0
    
    return {
        "vendor": {
            "id": vendor.id,
            "businessName": vendor.business_name,
            "email": vendor.email,
            "status": vendor.status,
            "verified": vendor.verified,
            "rating": vendor.rating
        },
        "stats": {
            "totalProducts": len(products),
            "totalRevenue": round(total_revenue, 2),
            "totalOrders": total_orders,
            "totalItemsSold": total_items_sold,
            "commission": round(commission, 2),
            "netEarnings": round(net_earnings, 2),
            "pendingOrders": pending_orders,
            "processingOrders": processing_orders,
            "completedOrders": completed_orders,
            "totalViews": total_views,
            "totalClicks": total_clicks
        }
    }

@api_router.get("/vendor/orders")
async def get_vendor_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all orders for this vendor with customer details"""
    vendor = await get_vendor_for_user(current_user.id, db)
    if not vendor:
        raise HTTPException(status_code=403, detail="You are not a registered vendor")
    
    # Get all orders
    orders_result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    all_orders = orders_result.scalars().all()
    
    vendor_orders = []
    for order in all_orders:
        vendor_items = []
        vendor_total = 0
        
        for item in order.items:
            if item.get('vendorId') == vendor.id:
                vendor_items.append(item)
                vendor_total += item.get('price', 0) * item.get('quantity', 1)
        
        if vendor_items:
            # Get customer info
            user_result = await db.execute(select(User).where(User.id == order.user_id))
            customer = user_result.scalar_one_or_none()
            shipping = order.shipping_info or {}
            
            vendor_orders.append({
                "id": order.id,
                "orderId": order.order_id,
                "customer": {
                    "name": shipping.get('fullName', customer.name if customer else 'Unknown'),
                    "email": customer.email if customer else 'Unknown',
                    "phone": shipping.get('phone', customer.phone if customer else ''),
                    "address": shipping.get('address', ''),
                    "city": shipping.get('city', ''),
                    "postcode": shipping.get('postcode', '')
                },
                "items": vendor_items,
                "itemCount": len(vendor_items),
                "total": round(vendor_total, 2),
                "commission": round(vendor_total * 0.10, 2),
                "netEarning": round(vendor_total * 0.90, 2),
                "status": order.status,
                "deliveryStatus": order.delivery_status or 'processing',
                "trackingNumber": order.tracking_number,
                "createdAt": order.created_at.isoformat(),
                "updatedAt": order.updated_at.isoformat()
            })
    
    return {"orders": vendor_orders, "totalOrders": len(vendor_orders)}

@api_router.get("/vendor/sales")
async def get_vendor_sales(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get sales data for charts"""
    from sqlalchemy import func
    from collections import defaultdict
    
    vendor = await get_vendor_for_user(current_user.id, db)
    if not vendor:
        raise HTTPException(status_code=403, detail="You are not a registered vendor")
    
    # Get vendor products
    products_result = await db.execute(select(Product).where(Product.vendor_id == vendor.id))
    products = {p.id: p for p in products_result.scalars().all()}
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get orders within date range
    orders_result = await db.execute(
        select(Order).where(Order.created_at >= start_date).order_by(Order.created_at)
    )
    orders = orders_result.scalars().all()
    
    # Calculate daily sales
    daily_sales = defaultdict(lambda: {"revenue": 0, "orders": 0, "items": 0})
    product_sales = defaultdict(lambda: {"quantity": 0, "revenue": 0})
    
    for order in orders:
        date_key = order.created_at.strftime("%Y-%m-%d")
        
        for item in order.items:
            if item.get('vendorId') == vendor.id:
                item_revenue = item.get('price', 0) * item.get('quantity', 1)
                daily_sales[date_key]["revenue"] += item_revenue
                daily_sales[date_key]["orders"] += 1
                daily_sales[date_key]["items"] += item.get('quantity', 1)
                
                product_id = item.get('productId')
                if product_id:
                    product_sales[product_id]["quantity"] += item.get('quantity', 1)
                    product_sales[product_id]["revenue"] += item_revenue
    
    # Format daily sales for chart
    chart_data = []
    for date_key in sorted(daily_sales.keys()):
        chart_data.append({
            "date": date_key,
            "revenue": round(daily_sales[date_key]["revenue"], 2),
            "orders": daily_sales[date_key]["orders"],
            "items": daily_sales[date_key]["items"]
        })
    
    # Format product sales
    product_chart_data = []
    for product_id, data in sorted(product_sales.items(), key=lambda x: x[1]["revenue"], reverse=True):
        product = products.get(product_id)
        if product:
            product_chart_data.append({
                "productId": product_id,
                "productName": product.name,
                "image": product.image,
                "quantity": data["quantity"],
                "revenue": round(data["revenue"], 2)
            })
    
    return {
        "period": f"Last {days} days",
        "dailySales": chart_data,
        "productSales": product_chart_data[:10],  # Top 10 products
        "summary": {
            "totalRevenue": round(sum(d["revenue"] for d in chart_data), 2),
            "totalOrders": sum(d["orders"] for d in chart_data),
            "totalItemsSold": sum(d["items"] for d in chart_data)
        }
    }

@api_router.get("/vendor/transactions")
async def get_vendor_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get vendor transactions/payouts from platform"""
    vendor = await get_vendor_for_user(current_user.id, db)
    if not vendor:
        raise HTTPException(status_code=403, detail="You are not a registered vendor")
    
    # Get all orders
    orders_result = await db.execute(select(Order).order_by(Order.created_at.desc()))
    orders = orders_result.scalars().all()
    
    transactions = []
    total_earned = 0
    total_commission = 0
    total_pending = 0
    total_paid = 0
    
    for order in orders:
        vendor_items = []
        vendor_revenue = 0
        
        for item in order.items:
            if item.get('vendorId') == vendor.id:
                vendor_items.append(item)
                vendor_revenue += item.get('price', 0) * item.get('quantity', 1)
        
        if vendor_items:
            commission = vendor_revenue * 0.10
            net_earning = vendor_revenue - commission
            
            # Determine payout status based on order status
            payout_status = "pending"
            if order.status == "completed":
                payout_status = "paid"
                total_paid += net_earning
            else:
                total_pending += net_earning
            
            total_earned += vendor_revenue
            total_commission += commission
            
            transactions.append({
                "id": order.id,
                "orderId": order.order_id,
                "date": order.created_at.isoformat(),
                "items": len(vendor_items),
                "grossAmount": round(vendor_revenue, 2),
                "platformFee": round(commission, 2),
                "netAmount": round(net_earning, 2),
                "orderStatus": order.status,
                "payoutStatus": payout_status
            })
    
    return {
        "transactions": transactions,
        "summary": {
            "totalGrossEarnings": round(total_earned, 2),
            "totalPlatformFees": round(total_commission, 2),
            "totalNetEarnings": round(total_earned - total_commission, 2),
            "pendingPayout": round(total_pending, 2),
            "totalPaid": round(total_paid, 2)
        }
    }

@api_router.get("/vendor/products/analytics")
async def get_vendor_product_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analytics for vendor's products"""
    from sqlalchemy import func
    
    vendor = await get_vendor_for_user(current_user.id, db)
    if not vendor:
        raise HTTPException(status_code=403, detail="You are not a registered vendor")
    
    # Get vendor products
    products_result = await db.execute(select(Product).where(Product.vendor_id == vendor.id))
    products = products_result.scalars().all()
    
    product_analytics = []
    for product in products:
        # Get views
        views_result = await db.execute(
            select(func.count(Analytics.id)).where(
                Analytics.product_id == product.id,
                Analytics.event_type == "product_view"
            )
        )
        views = views_result.scalar() or 0
        
        # Get clicks
        clicks_result = await db.execute(
            select(func.count(Analytics.id)).where(
                Analytics.product_id == product.id,
                Analytics.event_type == "product_click"
            )
        )
        clicks = clicks_result.scalar() or 0
        
        # Get add to cart
        cart_adds_result = await db.execute(
            select(func.count(Analytics.id)).where(
                Analytics.product_id == product.id,
                Analytics.event_type == "add_to_cart"
            )
        )
        cart_adds = cart_adds_result.scalar() or 0
        
        product_analytics.append({
            "id": product.id,
            "name": product.name,
            "image": product.image,
            "price": product.price,
            "stock": product.stock,
            "views": views,
            "clicks": clicks,
            "cartAdds": cart_adds,
            "conversionRate": round((cart_adds / views * 100) if views > 0 else 0, 2)
        })
    
    # Sort by views
    product_analytics.sort(key=lambda x: x["views"], reverse=True)
    
    return {"products": product_analytics}

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

# ============ AFROBOT CHATBOT ROUTES ============
@api_router.get("/chatbot/welcome")
async def get_chatbot_welcome():
    """Get AfroBot welcome message and quick replies"""
    return {
        "success": True,
        "message": AfroBotService.get_welcome_message(),
        "quick_replies": AfroBotService.get_quick_replies(),
        "bot_name": "AfroBot"
    }

@api_router.post("/chatbot/message")
async def send_chatbot_message(request: ChatMessageRequest):
    """Send a message to AfroBot and get response"""
    import uuid
    
    # Generate session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get AI response
    response = await AfroBotService.get_chat_response(
        message=request.message,
        session_id=session_id
    )
    
    return {
        "success": True,
        "session_id": session_id,
        "response": response,
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.get("/chatbot/quick-replies")
async def get_quick_replies():
    """Get available quick reply options"""
    return {
        "success": True,
        "quick_replies": AfroBotService.get_quick_replies()
    }

# ============ VENDOR WALLET ROUTES ============

@api_router.get("/wallet")
async def get_wallet(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vendor wallet balance and info"""
    # Get vendor using user_id (consistent with dashboard)
    vendor = await get_vendor_for_user(current_user.id, db)
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account required")
    
    # Get or create wallet
    result = await db.execute(select(VendorWallet).where(VendorWallet.vendor_id == vendor.id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        wallet = VendorWallet(vendor_id=vendor.id, balance=0.0)
        db.add(wallet)
        await db.flush()
    
    return {
        "success": True,
        "wallet": {
            "id": wallet.id,
            "balance": wallet.balance,
            "total_deposited": wallet.total_deposited,
            "total_spent": wallet.total_spent,
            "auto_recharge_enabled": wallet.auto_recharge_enabled,
            "auto_recharge_threshold": wallet.auto_recharge_threshold,
            "auto_recharge_amount": wallet.auto_recharge_amount,
            "has_payment_method": bool(wallet.stripe_payment_method_id)
        },
        "topup_options": WALLET_TOPUP_OPTIONS,
        "performance_pricing": AD_PERFORMANCE_PRICING
    }

@api_router.post("/wallet/topup")
async def topup_wallet(
    request: WalletTopUpRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a payment intent to top up wallet"""
    if request.amount < 5:
        raise HTTPException(status_code=400, detail="Minimum top-up amount is £5")
    
    if request.amount > 1000:
        raise HTTPException(status_code=400, detail="Maximum top-up amount is £1000")
    
    # Get vendor using user_id (consistent with dashboard)
    vendor = await get_vendor_for_user(current_user.id, db)
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account required")
    
    # Get or create wallet
    result = await db.execute(select(VendorWallet).where(VendorWallet.vendor_id == vendor.id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        wallet = VendorWallet(vendor_id=vendor.id, balance=0.0)
        db.add(wallet)
        await db.flush()
    
    # Create Stripe payment intent
    try:
        payment_result = await StripePayment.create_payment_intent(
            amount=request.amount,
            currency="gbp",
            metadata={
                "type": "wallet_topup",
                "vendor_id": str(vendor.id),
                "wallet_id": str(wallet.id)
            }
        )
        
        return {
            "success": True,
            "client_secret": payment_result['clientSecret'],
            "payment_intent_id": payment_result['paymentIntentId'],
            "amount": request.amount
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

@api_router.post("/wallet/confirm-topup")
async def confirm_wallet_topup(
    payment_intent_id: str,
    amount: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm wallet top-up after successful Stripe payment"""
    # Get vendor using user_id (consistent with dashboard)
    vendor = await get_vendor_for_user(current_user.id, db)
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account required")
    
    # Get wallet
    result = await db.execute(select(VendorWallet).where(VendorWallet.vendor_id == vendor.id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    # Update wallet balance
    wallet.balance += amount
    wallet.total_deposited += amount
    
    # Create transaction record
    transaction = WalletTransaction(
        vendor_id=vendor.id,
        wallet_id=wallet.id,
        type="topup",
        amount=amount,
        balance_after=wallet.balance,
        description=f"Wallet top-up via Stripe",
        stripe_payment_id=payment_intent_id
    )
    db.add(transaction)
    await db.flush()
    
    return {
        "success": True,
        "message": f"£{amount:.2f} added to your wallet",
        "new_balance": wallet.balance
    }

@api_router.post("/wallet/setup-auto-recharge")
async def setup_auto_recharge(
    request: AutoRechargeSetupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Set up automatic wallet recharge"""
    # Get vendor using user_id (consistent with dashboard)
    vendor = await get_vendor_for_user(current_user.id, db)
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account required")
    
    # Get wallet
    result = await db.execute(select(VendorWallet).where(VendorWallet.vendor_id == vendor.id))
    wallet = result.scalar_one_or_none()
    
    if not wallet:
        wallet = VendorWallet(vendor_id=vendor.id, balance=0.0)
        db.add(wallet)
        await db.flush()
    
    # Update auto-recharge settings
    wallet.auto_recharge_enabled = request.enabled
    wallet.auto_recharge_threshold = request.threshold
    wallet.auto_recharge_amount = request.amount
    
    if request.payment_method_id:
        wallet.stripe_payment_method_id = request.payment_method_id
    
    await db.flush()
    
    return {
        "success": True,
        "message": "Auto-recharge settings updated",
        "auto_recharge": {
            "enabled": wallet.auto_recharge_enabled,
            "threshold": wallet.auto_recharge_threshold,
            "amount": wallet.auto_recharge_amount
        }
    }

@api_router.get("/wallet/transactions")
async def get_wallet_transactions(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get wallet transaction history"""
    # Get vendor using user_id (consistent with dashboard)
    vendor = await get_vendor_for_user(current_user.id, db)
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account required")
    
    # Get transactions
    result = await db.execute(
        select(WalletTransaction)
        .where(WalletTransaction.vendor_id == vendor.id)
        .order_by(WalletTransaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    transactions = result.scalars().all()
    
    return {
        "success": True,
        "transactions": [{
            "id": t.id,
            "type": t.type,
            "amount": t.amount,
            "balance_after": t.balance_after,
            "description": t.description,
            "ad_id": t.ad_id,
            "created_at": t.created_at.isoformat()
        } for t in transactions]
    }

async def deduct_from_wallet(vendor_id: int, amount: float, description: str, ad_id: int, db: AsyncSession):
    """Internal function to deduct from vendor wallet for ad spend"""
    # Get wallet
    result = await db.execute(select(VendorWallet).where(VendorWallet.vendor_id == vendor_id))
    wallet = result.scalar_one_or_none()
    
    if not wallet or wallet.balance < amount:
        return False, "Insufficient wallet balance"
    
    # Deduct from balance
    wallet.balance -= amount
    wallet.total_spent += amount
    
    # Create transaction record
    transaction = WalletTransaction(
        vendor_id=vendor_id,
        wallet_id=wallet.id,
        type="ad_spend",
        amount=-amount,
        balance_after=wallet.balance,
        description=description,
        ad_id=ad_id
    )
    db.add(transaction)
    
    # Check if auto-recharge needed
    if wallet.auto_recharge_enabled and wallet.balance < wallet.auto_recharge_threshold:
        if wallet.stripe_payment_method_id:
            # TODO: Trigger auto-recharge via Stripe
            pass
    
    return True, wallet.balance

# ============ ADVERTISEMENT ROUTES ============

@api_router.get("/ads/pricing")
async def get_ad_pricing():
    """Get advertisement pricing options"""
    return {
        "success": True,
        "pricing": AD_PRICING,
        "performance_pricing": AD_PERFORMANCE_PRICING
    }

@api_router.post("/ads/create")
async def create_advertisement(
    ad_data: AdCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new advertisement (Vendor only)"""
    # Get vendor
    result = await db.execute(
        select(Vendor).where(Vendor.email == current_user.email)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Only vendors can create ads")
    
    if vendor.status != "approved":
        raise HTTPException(status_code=403, detail="Your vendor account must be approved first")
    
    # Validate ad type
    if ad_data.ad_type not in AD_PRICING:
        raise HTTPException(status_code=400, detail="Invalid ad type")
    
    # Handle different billing types
    price = None
    if ad_data.billing_type == 'fixed':
        # Traditional fixed-duration ads
        if ad_data.duration_days not in [7, 14, 30]:
            raise HTTPException(status_code=400, detail="Duration must be 7, 14, or 30 days")
        pricing_key = f"{ad_data.duration_days}_days"
        price = AD_PRICING[ad_data.ad_type][pricing_key]
    else:
        # Pay-per-performance ads - validate budget
        if not ad_data.total_budget:
            raise HTTPException(status_code=400, detail="Total budget is required for pay-per-performance ads")
        
        if ad_data.total_budget < AD_PERFORMANCE_PRICING["min_total_budget"]:
            raise HTTPException(status_code=400, detail=f"Minimum total budget is £{AD_PERFORMANCE_PRICING['min_total_budget']}")
        
        if ad_data.daily_budget and ad_data.daily_budget < AD_PERFORMANCE_PRICING["min_daily_budget"]:
            raise HTTPException(status_code=400, detail=f"Minimum daily budget is £{AD_PERFORMANCE_PRICING['min_daily_budget']}")
        
        # For pay-per-performance, check wallet balance
        result = await db.execute(select(VendorWallet).where(VendorWallet.vendor_id == vendor.id))
        wallet = result.scalar_one_or_none()
        
        if not wallet or wallet.balance < ad_data.total_budget:
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient wallet balance. You need £{ad_data.total_budget:.2f} but have £{wallet.balance if wallet else 0:.2f}"
            )
    
    # Calculate price
    pricing_key = f"{ad_data.duration_days}_days"
    price = AD_PRICING[ad_data.ad_type][pricing_key]
    
    # Verify product belongs to vendor if product_id provided
    if ad_data.product_id:
        result = await db.execute(
            select(Product).where(
                Product.id == ad_data.product_id,
                Product.vendor_id == vendor.id
            )
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=400, detail="Product not found or doesn't belong to you")
    
    # Create advertisement
    new_ad = Advertisement(
        vendor_id=vendor.id,
        title=ad_data.title,
        description=ad_data.description,
        image=ad_data.image,
        link_url=ad_data.link_url,
        product_id=ad_data.product_id,
        ad_type=ad_data.ad_type,
        placement=AD_PRICING[ad_data.ad_type]["placement"],
        duration_days=ad_data.duration_days,
        price=price,
        status="pending",
        payment_status="pending"
    )
    
    db.add(new_ad)
    await db.flush()
    
    return {
        "success": True,
        "message": "Advertisement created! Please complete payment and wait for admin approval.",
        "ad_id": new_ad.id,
        "price": price,
        "ad_type": ad_data.ad_type,
        "duration_days": ad_data.duration_days
    }

@api_router.post("/ads/{ad_id}/pay")
async def pay_for_advertisement(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process payment for an advertisement"""
    # Get the ad
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    # Verify ownership
    result = await db.execute(
        select(Vendor).where(Vendor.email == current_user.email)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor or ad.vendor_id != vendor.id:
        raise HTTPException(status_code=403, detail="You don't own this advertisement")
    
    if ad.payment_status == "paid":
        raise HTTPException(status_code=400, detail="Advertisement already paid for")
    
    # Create Stripe payment intent
    try:
        payment_result = await StripePayment.create_payment_intent(
            amount=ad.price,
            currency="gbp",
            metadata={
                "ad_id": str(ad.id),
                "vendor_id": str(vendor.id),
                "ad_type": ad.ad_type
            }
        )
        
        return {
            "success": True,
            "client_secret": payment_result['clientSecret'],
            "payment_intent_id": payment_result['paymentIntentId'],
            "amount": ad.price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment error: {str(e)}")

@api_router.post("/ads/{ad_id}/confirm-payment")
async def confirm_ad_payment(
    ad_id: int,
    payment_intent_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Confirm payment for an advertisement"""
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    # Update payment status
    ad.payment_status = "paid"
    ad.payment_intent_id = payment_intent_id
    await db.flush()
    
    # Send notification to admin
    try:
        email_service = EmailService()
        admin_email = os.environ.get("ADMIN_EMAIL", "sotubodammy@gmail.com")
        
        result = await db.execute(select(Vendor).where(Vendor.id == ad.vendor_id))
        vendor = result.scalar_one_or_none()
        
        await email_service.send_email(
            to_email=admin_email,
            subject=f"🎯 New Ad Pending Approval - {ad.title}",
            body=f"""
            <h2>New Advertisement Requires Approval</h2>
            <p><strong>Vendor:</strong> {vendor.business_name if vendor else 'Unknown'}</p>
            <p><strong>Ad Title:</strong> {ad.title}</p>
            <p><strong>Ad Type:</strong> {ad.ad_type}</p>
            <p><strong>Duration:</strong> {ad.duration_days} days</p>
            <p><strong>Price Paid:</strong> £{ad.price:.2f}</p>
            <p><strong>Description:</strong> {ad.description or 'N/A'}</p>
            <br>
            <p>Please review and approve/reject this ad in the Owner Dashboard.</p>
            """
        )
    except Exception as e:
        print(f"Failed to send admin notification: {e}")
    
    return {
        "success": True,
        "message": "Payment confirmed! Your ad is now pending admin approval."
    }

@api_router.get("/ads/vendor")
async def get_vendor_ads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all ads for the current vendor"""
    result = await db.execute(
        select(Vendor).where(Vendor.email == current_user.email)
    )
    vendor = result.scalar_one_or_none()
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor not found")
    
    result = await db.execute(
        select(Advertisement).where(Advertisement.vendor_id == vendor.id).order_by(Advertisement.created_at.desc())
    )
    ads = result.scalars().all()
    
    return {
        "success": True,
        "ads": [{
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "image": ad.image,
            "ad_type": ad.ad_type,
            "placement": ad.placement,
            "status": ad.status,
            "payment_status": ad.payment_status,
            "duration_days": ad.duration_days,
            "price": ad.price,
            "impressions": ad.impressions,
            "clicks": ad.clicks,
            "ctr": round((ad.clicks / ad.impressions * 100), 2) if ad.impressions > 0 else 0,
            "start_date": ad.start_date.isoformat() if ad.start_date else None,
            "end_date": ad.end_date.isoformat() if ad.end_date else None,
            "admin_notes": ad.admin_notes,
            "created_at": ad.created_at.isoformat()
        } for ad in ads]
    }

@api_router.get("/ads/pending")
async def get_pending_ads(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all pending ads for admin approval (Owner only)"""
    if current_user.email != os.environ.get("ADMIN_EMAIL", "sotubodammy@gmail.com"):
        raise HTTPException(status_code=403, detail="Owner access required")
    
    result = await db.execute(
        select(Advertisement).where(
            Advertisement.status == "pending",
            Advertisement.payment_status == "paid"
        ).order_by(Advertisement.created_at.desc())
    )
    ads = result.scalars().all()
    
    # Get vendor info for each ad
    ads_with_vendor = []
    for ad in ads:
        result = await db.execute(select(Vendor).where(Vendor.id == ad.vendor_id))
        vendor = result.scalar_one_or_none()
        
        ads_with_vendor.append({
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "image": ad.image,
            "link_url": ad.link_url,
            "ad_type": ad.ad_type,
            "ad_type_name": AD_PRICING[ad.ad_type]["name"],
            "placement": ad.placement,
            "duration_days": ad.duration_days,
            "price": ad.price,
            "vendor": {
                "id": vendor.id if vendor else None,
                "business_name": vendor.business_name if vendor else "Unknown",
                "email": vendor.email if vendor else ""
            },
            "created_at": ad.created_at.isoformat()
        })
    
    return {
        "success": True,
        "ads": ads_with_vendor
    }

@api_router.get("/ads/all")
async def get_all_ads_admin(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all ads for admin dashboard (Owner only)"""
    if current_user.email != os.environ.get("ADMIN_EMAIL", "sotubodammy@gmail.com"):
        raise HTTPException(status_code=403, detail="Owner access required")
    
    result = await db.execute(
        select(Advertisement).order_by(Advertisement.created_at.desc())
    )
    ads = result.scalars().all()
    
    ads_with_vendor = []
    for ad in ads:
        result = await db.execute(select(Vendor).where(Vendor.id == ad.vendor_id))
        vendor = result.scalar_one_or_none()
        
        ads_with_vendor.append({
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "image": ad.image,
            "ad_type": ad.ad_type,
            "ad_type_name": AD_PRICING[ad.ad_type]["name"],
            "placement": ad.placement,
            "status": ad.status,
            "payment_status": ad.payment_status,
            "duration_days": ad.duration_days,
            "price": ad.price,
            "impressions": ad.impressions,
            "clicks": ad.clicks,
            "start_date": ad.start_date.isoformat() if ad.start_date else None,
            "end_date": ad.end_date.isoformat() if ad.end_date else None,
            "vendor": {
                "id": vendor.id if vendor else None,
                "business_name": vendor.business_name if vendor else "Unknown"
            },
            "created_at": ad.created_at.isoformat()
        })
    
    return {
        "success": True,
        "ads": ads_with_vendor
    }

@api_router.post("/ads/{ad_id}/approve")
async def approve_or_reject_ad(
    ad_id: int,
    request: AdApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve or reject an advertisement (Owner only)"""
    if current_user.email != os.environ.get("ADMIN_EMAIL", "sotubodammy@gmail.com"):
        raise HTTPException(status_code=403, detail="Owner access required")
    
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    if ad.payment_status != "paid":
        raise HTTPException(status_code=400, detail="Ad must be paid before approval")
    
    if request.action == "approve":
        ad.status = "active"
        ad.approved_by = current_user.email
        ad.approved_at = datetime.utcnow()
        ad.start_date = datetime.utcnow()
        ad.end_date = datetime.utcnow() + timedelta(days=ad.duration_days)
        ad.admin_notes = request.admin_notes
        message = "Advertisement approved and is now live!"
    elif request.action == "reject":
        ad.status = "rejected"
        ad.admin_notes = request.admin_notes or "Ad rejected by admin"
        message = "Advertisement rejected"
        # TODO: Process refund via Stripe
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
    
    await db.flush()
    
    # Notify vendor
    try:
        result = await db.execute(select(Vendor).where(Vendor.id == ad.vendor_id))
        vendor = result.scalar_one_or_none()
        
        if vendor:
            email_service = EmailService()
            status_text = "approved and is now live" if request.action == "approve" else "rejected"
            
            await email_service.send_email(
                to_email=vendor.email,
                subject=f"📢 Your Ad '{ad.title}' has been {request.action}d",
                body=f"""
                <h2>Advertisement Update</h2>
                <p>Your advertisement <strong>"{ad.title}"</strong> has been <strong>{status_text}</strong>.</p>
                {'<p><strong>Admin Notes:</strong> ' + request.admin_notes + '</p>' if request.admin_notes else ''}
                {f'<p>Your ad will run from <strong>{ad.start_date.strftime("%d %b %Y")}</strong> to <strong>{ad.end_date.strftime("%d %b %Y")}</strong>.</p>' if request.action == "approve" else ''}
                <p>Thank you for advertising with AfroMarket UK!</p>
                """
            )
    except Exception as e:
        print(f"Failed to send vendor notification: {e}")
    
    return {
        "success": True,
        "message": message
    }

@api_router.get("/ads/active")
async def get_active_ads(
    placement: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get active ads for display on the website"""
    now = datetime.utcnow()
    
    query = select(Advertisement).where(
        Advertisement.status == "active",
        Advertisement.start_date <= now,
        Advertisement.end_date >= now
    )
    
    if placement:
        query = query.where(Advertisement.placement == placement)
    
    result = await db.execute(query.order_by(Advertisement.ad_type.desc()))  # Premium first
    ads = result.scalars().all()
    
    # Get product info for ads with product_id
    active_ads = []
    for ad in ads:
        ad_data = {
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "image": ad.image,
            "link_url": ad.link_url,
            "ad_type": ad.ad_type,
            "placement": ad.placement,
            "product_id": ad.product_id
        }
        
        if ad.product_id:
            result = await db.execute(select(Product).where(Product.id == ad.product_id))
            product = result.scalar_one_or_none()
            if product:
                ad_data["product"] = {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "image": product.image
                }
        
        active_ads.append(ad_data)
    
    return {
        "success": True,
        "ads": active_ads
    }

@api_router.post("/ads/{ad_id}/impression")
async def track_ad_impression(ad_id: int, db: AsyncSession = Depends(get_db)):
    """Track an ad impression"""
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    
    if ad and ad.status == "active":
        ad.impressions += 1
        await db.flush()
    
    return {"success": True}

@api_router.post("/ads/{ad_id}/click")
async def track_ad_click(ad_id: int, db: AsyncSession = Depends(get_db)):
    """Track an ad click"""
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    
    if ad and ad.status == "active":
        ad.clicks += 1
        await db.flush()
    
    return {"success": True}

@api_router.post("/ads/{ad_id}/pause")
async def pause_ad(
    ad_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Pause an active ad (Vendor can pause their own ads)"""
    result = await db.execute(select(Advertisement).where(Advertisement.id == ad_id))
    ad = result.scalar_one_or_none()
    
    if not ad:
        raise HTTPException(status_code=404, detail="Advertisement not found")
    
    # Check ownership
    result = await db.execute(select(Vendor).where(Vendor.email == current_user.email))
    vendor = result.scalar_one_or_none()
    
    is_owner = current_user.email == os.environ.get("ADMIN_EMAIL", "sotubodammy@gmail.com")
    is_ad_owner = vendor and ad.vendor_id == vendor.id
    
    if not (is_owner or is_ad_owner):
        raise HTTPException(status_code=403, detail="You don't have permission to pause this ad")
    
    if ad.status == "active":
        ad.status = "paused"
        await db.flush()
        return {"success": True, "message": "Ad paused"}
    elif ad.status == "paused":
        ad.status = "active"
        await db.flush()
        return {"success": True, "message": "Ad resumed"}
    else:
        raise HTTPException(status_code=400, detail="Can only pause/resume active ads")

app.include_router(api_router)

# Security Headers Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        # Note: HSTS should be set at the reverse proxy/load balancer level for production
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

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
