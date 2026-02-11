"""
AfroMarket UK - Server with Firebase/Firestore Database
Production-ready API server using Firebase as the only database
"""

from fastapi import FastAPI, APIRouter, HTTPException, Depends, Query, Request, WebSocket, WebSocketDisconnect
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
import os
import logging
import json
import jwt
import bcrypt
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env', override=True)

# Import Firestore database
from firestore_db import firestore_db, seed_firestore_data, get_firebase_app
from firebase_auth import verify_firebase_token, is_firebase_configured
from email_service import email_service
from notification_service import ws_manager, NotificationService, PushNotificationService
from chatbot_service import get_afrobot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_HOURS = 24

# Initialize FastAPI
app = FastAPI(title="AfroMarket UK API", version="2.0.0")
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)


# ============ MIDDLEWARE ============

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = datetime.now().timestamp()
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        self.requests[client_ip] = [
            t for t in self.requests[client_ip] 
            if current_time - t < self.window_seconds
        ]
        
        if len(self.requests[client_ip]) >= self.max_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        self.requests[client_ip].append(current_time)
        return await call_next(request)


# Add middleware
app.add_middleware(RateLimitMiddleware, max_requests=200, window_seconds=60)

# CORS configuration
cors_origins = os.environ.get('CORS_ORIGINS', '*').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if cors_origins != ['*'] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ PYDANTIC MODELS ============

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

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
    ownerName: Optional[str] = None

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    image: Optional[str] = None
    weight: Optional[str] = None
    original_price: Optional[float] = None

class OrderCreate(BaseModel):
    items: list
    shipping_info: dict
    payment_info: dict
    total: float

class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class VendorApproval(BaseModel):
    vendorId: str
    status: str  # 'approved' or 'rejected'

class NotificationPreferencesUpdate(BaseModel):
    email_orders: Optional[bool] = None
    email_messages: Optional[bool] = None
    email_reviews: Optional[bool] = None
    email_admin_alerts: Optional[bool] = None
    email_marketing: Optional[bool] = None
    inapp_orders: Optional[bool] = None
    inapp_messages: Optional[bool] = None
    inapp_reviews: Optional[bool] = None
    inapp_admin_alerts: Optional[bool] = None
    inapp_marketing: Optional[bool] = None
    push_enabled: Optional[bool] = None
    push_orders: Optional[bool] = None
    push_messages: Optional[bool] = None
    push_reviews: Optional[bool] = None
    push_admin_alerts: Optional[bool] = None


# ============ AUTHENTICATION ============

def create_jwt_token(user_id: str, email: str, is_admin: bool = False):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'is_admin': is_admin,
        'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_jwt_token(credentials.credentials)
    user = await firestore_db.get_user_by_id(payload['user_id'])
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        payload = verify_jwt_token(credentials.credentials)
        return await firestore_db.get_user_by_id(payload['user_id'])
    except:
        return None


# ============ AUTH ROUTES ============

@api_router.post("/auth/register")
async def register_user(user_data: UserRegister):
    """Register a new user"""
    # Check if user exists
    existing = await firestore_db.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    password_hash = bcrypt.hashpw(user_data.password.encode(), bcrypt.gensalt()).decode()
    
    # Create user
    user = await firestore_db.create_user({
        'name': user_data.name,
        'email': user_data.email,
        'password_hash': password_hash,
        'is_admin': False,
        'is_vendor': False
    })
    
    # Generate token
    token = create_jwt_token(user['id'], user['email'])
    
    return {
        'success': True,
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }


@api_router.post("/auth/login")
async def login_user(credentials: UserLogin):
    """Login user"""
    user = await firestore_db.get_user_by_email(credentials.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not bcrypt.checkpw(credentials.password.encode(), user['password_hash'].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generate token
    token = create_jwt_token(user['id'], user['email'], user.get('is_admin', False))
    
    return {
        'success': True,
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'is_admin': user.get('is_admin', False)
        }
    }


@api_router.post("/auth/firebase")
async def firebase_auth(auth_data: FirebaseAuthRequest):
    """Authenticate with Firebase"""
    if not is_firebase_configured():
        raise HTTPException(status_code=500, detail="Firebase not configured")
    
    # Verify Firebase token
    firebase_user = verify_firebase_token(auth_data.idToken)
    if not firebase_user:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    
    # Get or create user
    user = await firestore_db.get_user_by_email(firebase_user['email'])
    
    if not user:
        user = await firestore_db.create_user({
            'firebase_uid': firebase_user['uid'],
            'name': auth_data.displayName or firebase_user.get('name', 'User'),
            'email': firebase_user['email'],
            'photo_url': auth_data.photoURL,
            'email_verified': firebase_user.get('email_verified', True),
            'is_admin': False,
            'is_vendor': False
        })
    
    # Generate JWT token
    token = create_jwt_token(user['id'], user['email'])
    
    return {
        'success': True,
        'token': token,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        }
    }


@api_router.get("/auth/firebase/status")
async def firebase_status():
    """Check Firebase configuration status"""
    return {
        'configured': is_firebase_configured(),
        'message': 'Firebase is configured' if is_firebase_configured() else 'Firebase not configured'
    }


@api_router.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return {
        'success': True,
        'user': {
            'id': current_user['id'],
            'name': current_user['name'],
            'email': current_user['email'],
            'is_admin': current_user.get('is_admin', False),
            'is_vendor': current_user.get('is_vendor', False)
        }
    }


# ============ PRODUCT ROUTES ============

@api_router.get("/products")
async def get_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(50, le=100)
):
    """Get all products"""
    if search:
        products = await firestore_db.search_products(search, limit)
    else:
        products = await firestore_db.get_all_products(category=category, limit=limit)
    
    return products


@api_router.get("/products/{product_id}")
async def get_product(product_id: str):
    """Get product by ID"""
    product = await firestore_db.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@api_router.post("/products")
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new product (vendor only)"""
    # Get vendor
    vendor = await firestore_db.get_vendor_by_user_id(current_user['id'])
    if not vendor:
        vendor = await firestore_db.get_vendor_by_email(current_user['email'])
    
    if not vendor or vendor.get('status') != 'approved':
        raise HTTPException(status_code=403, detail="Vendor access required")
    
    product = await firestore_db.create_product({
        'vendor_id': vendor['id'],
        **product_data.dict()
    })
    
    return {'success': True, 'product': product}


# ============ VENDOR ROUTES ============

@api_router.get("/vendors")
async def get_vendors():
    """Get all approved vendors"""
    vendors = await firestore_db.get_all_vendors(status='approved', verified=True)
    return [{
        'id': v['id'],
        'name': v['business_name'],
        'rating': v.get('rating', 0),
        'totalSales': v.get('total_sales', 0),
        'location': v.get('location', v.get('city', '')),
        'verified': v.get('verified', False)
    } for v in vendors]


@api_router.post("/vendors/register/public")
async def register_vendor_public(vendor_data: VendorRegisterRequest):
    """Public vendor registration"""
    # Check if vendor exists
    existing = await firestore_db.get_vendor_by_email(vendor_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Vendor with this email already exists")
    
    # Create vendor
    vendor = await firestore_db.create_vendor({
        'business_name': vendor_data.businessName,
        'description': vendor_data.description,
        'email': vendor_data.email,
        'phone': vendor_data.phone,
        'address': vendor_data.address,
        'city': vendor_data.city,
        'postcode': vendor_data.postcode,
        'location': vendor_data.city,
        'status': 'pending',
        'verified': False
    })
    
    # Send email notification to admin
    email_sent = False
    try:
        email_sent = email_service.send_vendor_registration_notification({
            'business_name': vendor['business_name'],
            'owner_name': vendor_data.ownerName or 'Not provided',
            'email': vendor['email'],
            'phone': vendor['phone'],
            'address': vendor['address'],
            'city': vendor['city'],
            'postcode': vendor['postcode'],
            'description': vendor['description'],
            'vendor_id': vendor['id']
        })
    except Exception as e:
        logger.error(f"Failed to send vendor registration email: {e}")
    
    return {
        'success': True,
        'vendor': {'id': vendor['id'], 'businessName': vendor['business_name'], 'status': 'pending'},
        'emailSent': email_sent,
        'message': 'Application submitted! We will review within 2-3 business days.'
    }


@api_router.post("/admin/vendors/approve")
async def approve_vendor(approval: VendorApproval):
    """Approve or reject a vendor with comprehensive email notification"""
    vendor = await firestore_db.get_vendor_by_id(approval.vendorId)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Update vendor status
    await firestore_db.update_vendor(approval.vendorId, {
        'status': approval.status,
        'verified': approval.status == 'approved'
    })
    
    # Create in-app notification
    if approval.status == 'approved':
        title = "🎉 Your Vendor Application has been Approved!"
        message = f"Congratulations {vendor['business_name']}! You can now start selling."
        link = "/vendor/dashboard"
    else:
        title = "Vendor Application Update"
        message = f"Your application for {vendor['business_name']} was not approved."
        link = "/help"
    
    await firestore_db.create_notification({
        'vendor_id': approval.vendorId,
        'type': 'approval' if approval.status == 'approved' else 'rejection',
        'title': title,
        'message': message,
        'link': link
    })
    
    # Send comprehensive approval email notification
    email_sent = False
    try:
        # Get admin notes if provided in approval request
        admin_notes = getattr(approval, 'notes', '') or ''
        
        email_sent = email_service.send_vendor_approval_notification(
            vendor_email=vendor['email'], 
            vendor_name=vendor.get('business_name', vendor.get('businessName', 'Vendor')),
            approved=approval.status == 'approved',
            admin_notes=admin_notes
        )
        logger.info(f"Vendor approval email sent to {vendor['email']}: {email_sent}")
    except Exception as e:
        logger.error(f"Failed to send approval email: {e}")
    
    return {'success': True, 'emailSent': email_sent, 'notificationCreated': True}


# ============ OWNER DASHBOARD ROUTES ============

@api_router.get("/owner/vendors")
async def get_owner_vendors(
    status: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all vendors for owner dashboard"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    vendors = await firestore_db.get_all_vendors(status=status)
    return vendors


@api_router.put("/owner/vendors/{vendor_id}/approve")
async def owner_approve_vendor(
    vendor_id: str,
    status: str = Query(..., description="approved or rejected"),
    notes: Optional[str] = Query(None, description="Admin notes"),
    current_user: dict = Depends(get_current_user)
):
    """Approve or reject a vendor from owner dashboard with email notification"""
    # Check owner permissions
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    vendor = await firestore_db.get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Update vendor status
    await firestore_db.update_vendor(vendor_id, {
        'status': status,
        'verified': status == 'approved',
        'approval_notes': notes or '',
        'approved_by': current_user.get('email'),
        'approved_at': datetime.utcnow().isoformat()
    })
    
    # Create in-app notification
    if status == 'approved':
        title = "🎉 Your Vendor Application has been Approved!"
        message = f"Congratulations {vendor.get('business_name', 'Vendor')}! You can now start selling on AfroMarket UK."
        notif_type = 'approval'
        link = "/vendor/dashboard"
    else:
        title = "Vendor Application Update"
        message = f"Your application for {vendor.get('business_name', 'Vendor')} was not approved."
        if notes:
            message += f" Reason: {notes}"
        notif_type = 'rejection'
        link = "/help"
    
    await firestore_db.create_notification({
        'vendor_id': vendor_id,
        'type': notif_type,
        'title': title,
        'message': message,
        'link': link
    })
    
    # Send WebSocket notification
    await ws_manager.send_to_vendor(vendor_id, {
        'type': 'notification',
        'notification': {
            'type': notif_type,
            'title': title,
            'message': message,
            'link': link
        }
    })
    
    # Send comprehensive email notification
    email_sent = False
    try:
        email_sent = email_service.send_vendor_approval_notification(
            vendor_email=vendor.get('email', ''),
            vendor_name=vendor.get('business_name', vendor.get('businessName', 'Vendor')),
            approved=status == 'approved',
            admin_notes=notes or ''
        )
        logger.info(f"Owner approval email sent to {vendor.get('email')}: {email_sent}")
    except Exception as e:
        logger.error(f"Failed to send owner approval email: {e}")
    
    return {
        'success': True, 
        'vendor_id': vendor_id,
        'status': status,
        'emailSent': email_sent,
        'notificationCreated': True
    }


@api_router.get("/owner/stats")
async def get_owner_stats(current_user: dict = Depends(get_current_user)):
    """Get platform statistics for owner dashboard"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    # Get all counts
    all_vendors = await firestore_db.get_all_vendors()
    pending_vendors = [v for v in all_vendors if v.get('status') == 'pending']
    approved_vendors = [v for v in all_vendors if v.get('status') == 'approved']
    
    all_orders = await firestore_db.get_all_orders()
    total_revenue = sum(o.get('total', 0) for o in all_orders)
    
    products = await firestore_db.get_all_products()
    
    return {
        'totalVendors': len(all_vendors),
        'pendingVendors': len(pending_vendors),
        'approvedVendors': len(approved_vendors),
        'totalOrders': len(all_orders),
        'totalRevenue': total_revenue,
        'totalProducts': len(products),
        'platformCommission': total_revenue * 0.10
    }


@api_router.get("/owner/dashboard")
async def get_owner_dashboard(current_user: dict = Depends(get_current_user)):
    """Get comprehensive owner dashboard data"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    all_vendors = await firestore_db.get_all_vendors()
    all_orders = await firestore_db.get_all_orders()
    products = await firestore_db.get_all_products()
    
    total_revenue = sum(o.get('total', 0) for o in all_orders)
    pending_vendors = len([v for v in all_vendors if v.get('status') == 'pending'])
    
    return {
        'totalRevenue': total_revenue,
        'totalOrders': len(all_orders),
        'totalVendors': len(all_vendors),
        'pendingVendors': pending_vendors,
        'totalProducts': len(products),
        'platformCommission': total_revenue * 0.10,
        'recentOrders': all_orders[:10] if all_orders else []
    }


@api_router.get("/owner/products")
async def get_owner_products(current_user: dict = Depends(get_current_user)):
    """Get all products for owner dashboard"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    products = await firestore_db.get_all_products()
    return {'products': products}


@api_router.get("/owner/analytics")
async def get_owner_analytics(
    days: int = Query(30, description="Number of days for analytics"),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics data for owner dashboard"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    all_orders = await firestore_db.get_all_orders()
    products = await firestore_db.get_all_products()
    
    # Calculate basic analytics
    total_revenue = sum(o.get('total', 0) for o in all_orders)
    avg_order_value = total_revenue / len(all_orders) if all_orders else 0
    
    return {
        'totalRevenue': total_revenue,
        'totalOrders': len(all_orders),
        'averageOrderValue': avg_order_value,
        'totalProducts': len(products),
        'period': f'{days} days'
    }


@api_router.get("/owner/transactions")
async def get_owner_transactions(current_user: dict = Depends(get_current_user)):
    """Get all transactions for owner dashboard"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    all_orders = await firestore_db.get_all_orders()
    # Transform orders into transactions format
    transactions = [{
        'id': o.get('id'),
        'orderId': o.get('order_id'),
        'amount': o.get('total', 0),
        'status': o.get('status', 'pending'),
        'date': o.get('created_at'),
        'user': o.get('shipping_info', {}).get('fullName', 'Unknown')
    } for o in all_orders]
    
    return transactions


@api_router.get("/owner/sales")
async def get_owner_sales(current_user: dict = Depends(get_current_user)):
    """Get sales data for owner dashboard"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    all_orders = await firestore_db.get_all_orders()
    return all_orders


@api_router.get("/owner/deliveries")
async def get_owner_deliveries(current_user: dict = Depends(get_current_user)):
    """Get delivery data for owner dashboard"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    all_orders = await firestore_db.get_all_orders()
    # Filter orders that need delivery tracking
    deliveries = [{
        'id': o.get('id'),
        'orderId': o.get('order_id'),
        'status': o.get('delivery_status', o.get('status', 'pending')),
        'address': o.get('shipping_info', {}),
        'trackingNumber': o.get('tracking_number', ''),
        'carrier': o.get('carrier', ''),
        'estimatedDelivery': o.get('estimated_delivery', ''),
        'date': o.get('created_at')
    } for o in all_orders]
    
    return deliveries


@api_router.put("/owner/deliveries/{order_id}")
async def update_owner_delivery(
    order_id: str,
    status: str = Query(...),
    tracking_number: str = Query(''),
    carrier: str = Query(''),
    estimated_delivery: str = Query(''),
    current_user: dict = Depends(get_current_user)
):
    """Update delivery status for an order"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Owner access required")
    
    await firestore_db.update_order(order_id, {
        'delivery_status': status,
        'tracking_number': tracking_number,
        'carrier': carrier,
        'estimated_delivery': estimated_delivery
    })
    
    return {'success': True, 'message': 'Delivery updated'}


# ============ VENDOR STOCK MANAGEMENT ============

@api_router.get("/vendor/products")
async def get_vendor_products(current_user: dict = Depends(get_current_user)):
    """Get all products for the logged-in vendor"""
    # Get vendor by user email
    vendor = await firestore_db.get_vendor_by_email(current_user.get('email'))
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account not found")
    
    if vendor.get('status') != 'approved':
        raise HTTPException(status_code=403, detail="Vendor account not approved yet")
    
    products = await firestore_db.get_products_by_vendor(vendor['id'])
    
    # Add low stock warnings
    for product in products:
        stock = product.get('stock_quantity', 0)
        product['low_stock'] = stock < 20
        product['out_of_stock'] = stock <= 0
    
    return {
        'products': products,
        'vendor_id': vendor['id'],
        'business_name': vendor.get('business_name')
    }


@api_router.put("/vendor/products/{product_id}/stock")
async def update_product_stock(
    product_id: str,
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Update stock quantity for a product"""
    # Get vendor by user email
    vendor = await firestore_db.get_vendor_by_email(current_user.get('email'))
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account not found")
    
    # Verify product belongs to vendor
    product = await firestore_db.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.get('vendor_id') != vendor['id']:
        raise HTTPException(status_code=403, detail="Not authorized to update this product")
    
    body = await request.json()
    new_stock = body.get('stock_quantity')
    
    if new_stock is None or new_stock < 0:
        raise HTTPException(status_code=400, detail="Invalid stock quantity")
    
    # Update product stock
    await firestore_db.update_product(product_id, {
        'stock_quantity': new_stock,
        'in_stock': new_stock > 0,
        'updated_at': datetime.utcnow().isoformat()
    })
    
    return {
        'success': True,
        'product_id': product_id,
        'new_stock': new_stock,
        'in_stock': new_stock > 0,
        'low_stock': new_stock < 20
    }


@api_router.get("/vendor/dashboard")
async def get_vendor_dashboard(current_user: dict = Depends(get_current_user)):
    """Get vendor dashboard data"""
    vendor = await firestore_db.get_vendor_by_email(current_user.get('email'))
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor account not found")
    
    # Get vendor's products
    products = await firestore_db.get_products_by_vendor(vendor['id'])
    
    # Get vendor's orders
    orders = await firestore_db.get_vendor_orders(vendor['id'])
    
    # Calculate stats
    total_products = len(products)
    low_stock_count = sum(1 for p in products if p.get('stock_quantity', 0) < 20)
    out_of_stock_count = sum(1 for p in products if p.get('stock_quantity', 0) <= 0)
    total_orders = len(orders)
    total_revenue = sum(order.get('total', 0) for order in orders if order.get('status') == 'completed')
    pending_orders = sum(1 for o in orders if o.get('status') in ['pending', 'processing'])
    
    return {
        'vendor': {
            'id': vendor['id'],
            'business_name': vendor.get('business_name'),
            'status': vendor.get('status'),
            'verified': vendor.get('verified', False)
        },
        'stats': {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'out_of_stock_count': out_of_stock_count,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': round(total_revenue, 2)
        },
        'products': products[:10],  # Latest 10 products
        'orders': orders[:10],  # Latest 10 orders
        'alerts': {
            'low_stock': [p for p in products if 0 < p.get('stock_quantity', 0) < 20][:5],
            'out_of_stock': [p for p in products if p.get('stock_quantity', 0) <= 0][:5]
        }
    }


# ============ WISHLIST ENDPOINTS ============

@api_router.get("/wishlist")
async def get_wishlist(current_user: dict = Depends(get_current_user)):
    """Get user's wishlist"""
    wishlist = await firestore_db.get_user_wishlist(current_user['id'])
    return {'items': wishlist}


@api_router.post("/wishlist")
async def add_to_wishlist(
    product_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
):
    """Add product to wishlist"""
    await firestore_db.add_to_wishlist(current_user['id'], product_id)
    return {'success': True, 'message': 'Added to wishlist'}


@api_router.post("/wishlist/toggle")
async def toggle_wishlist(
    request: Request,
    current_user: dict = Depends(get_current_user)
):
    """Toggle product in wishlist (add if not exists, remove if exists)"""
    try:
        body = await request.json()
        product_id = body.get('product_id')
        if not product_id:
            raise HTTPException(status_code=400, detail="product_id is required")
        
        # Check if product is already in wishlist
        wishlist = await firestore_db.get_user_wishlist(current_user['id'])
        is_in_wishlist = any(item.get('product_id') == product_id for item in wishlist)
        
        if is_in_wishlist:
            await firestore_db.remove_from_wishlist(current_user['id'], product_id)
            return {'success': True, 'in_wishlist': False, 'message': 'Removed from wishlist'}
        else:
            await firestore_db.add_to_wishlist(current_user['id'], product_id)
            return {'success': True, 'in_wishlist': True, 'message': 'Added to wishlist'}
    except Exception as e:
        logger.error(f"Error toggling wishlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/wishlist/{product_id}")
async def remove_from_wishlist(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove product from wishlist"""
    await firestore_db.remove_from_wishlist(current_user['id'], product_id)
    return {'success': True, 'message': 'Removed from wishlist'}


@api_router.delete("/wishlist/remove/{product_id}")
async def remove_from_wishlist_alt(
    product_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove product from wishlist (alternative endpoint)"""
    await firestore_db.remove_from_wishlist(current_user['id'], product_id)
    return {'success': True, 'message': 'Removed from wishlist'}


# ============ ADS ENDPOINTS ============

@api_router.get("/ads/pending")
async def get_pending_ads(current_user: dict = Depends(get_current_user)):
    """Get pending ads for approval"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Admin access required")
    # Return empty list for now - ads feature placeholder
    return {'ads': []}


@api_router.get("/ads/all")
async def get_all_ads(current_user: dict = Depends(get_current_user)):
    """Get all ads"""
    if not current_user.get('is_admin') and current_user.get('email') != 'sotubodammy@gmail.com':
        raise HTTPException(status_code=403, detail="Admin access required")
    # Return empty list for now - ads feature placeholder
    return {'ads': []}


# ============ ORDER ROUTES ============

@api_router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new order and send payment notifications"""
    # Get vendor IDs from items
    vendor_ids = list(set(item.get('vendorId') for item in order_data.items if item.get('vendorId')))
    
    order = await firestore_db.create_order({
        'user_id': current_user['id'],
        'items': order_data.items,
        'shipping_info': order_data.shipping_info,
        'payment_info': {k: v for k, v in order_data.payment_info.items() if k != 'cardNumber'},
        'total': order_data.total,
        'vendor_ids': vendor_ids,
        'status': 'confirmed'  # Payment confirmed
    })
    
    # Prepare data for email notifications
    order_id = order['order_id']
    
    # Get vendor details and prepare vendor-specific data
    vendors_data = []
    for vendor_id in vendor_ids:
        vendor_items = [i for i in order_data.items if i.get('vendorId') == vendor_id]
        vendor_total = sum(i.get('price', 0) * i.get('quantity', 1) for i in vendor_items)
        
        # Get vendor info from database
        vendor = await firestore_db.get_vendor_by_id(vendor_id)
        if vendor:
            # Add vendor name to items for email
            for item in vendor_items:
                item['vendor_name'] = vendor.get('business_name', vendor.get('businessName', 'Vendor'))
            
            vendors_data.append({
                'id': vendor_id,
                'name': vendor.get('business_name', vendor.get('businessName', 'Vendor')),
                'email': vendor.get('email', ''),
                'items': vendor_items
            })
        
        # Create in-app notification for vendor
        await firestore_db.create_notification({
            'vendor_id': vendor_id,
            'type': 'order',
            'title': f"🛒 New Order #{order_id}!",
            'message': f"New order with {len(vendor_items)} item(s) totaling £{vendor_total:.2f}",
            'link': f"/vendor/dashboard?tab=orders&order={order_id}",
            'data': {'order_id': order_id, 'total': vendor_total}
        })
        
        # WebSocket notification
        await ws_manager.send_to_vendor(vendor_id, {
            'type': 'notification',
            'notification': {
                'type': 'order',
                'title': f"🛒 New Order #{order_id}!",
                'message': f"New order with {len(vendor_items)} item(s) totaling £{vendor_total:.2f}",
                'link': "/vendor/dashboard?tab=orders"
            }
        })
    
    # Calculate delivery info
    subtotal = sum(i.get('price', 0) * i.get('quantity', 1) for i in order_data.items)
    delivery_fee = order_data.total - subtotal
    
    # Prepare order data for emails
    email_order_data = {
        'order_id': order_id,
        'items': order_data.items,
        'shipping_info': order_data.shipping_info,
        'delivery_info': {
            'estimated_days': '2-4 days',  # Default estimate
            'zone_name': 'Standard',
            'delivery_option': 'Standard Delivery',
            'delivery_fee': delivery_fee
        },
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': order_data.total,
        'payment_method': order_data.payment_info.get('method', 'Card')
    }
    
    # Customer info
    customer_info = {
        'name': current_user.get('name', 'Customer'),
        'email': current_user.get('email', '')
    }
    
    # Send all payment notifications asynchronously (don't block order completion)
    try:
        import asyncio
        asyncio.create_task(
            email_service.send_all_payment_notifications(
                order_data=email_order_data,
                customer_info=customer_info,
                vendors_data=vendors_data
            )
        )
        logger.info(f"Payment notifications queued for order #{order_id}")
    except Exception as e:
        logger.error(f"Failed to queue payment notifications: {str(e)}")
    
    # Clear cart
    await firestore_db.clear_user_cart(current_user['id'])
    
    return {
        'success': True,
        'order': {
            'id': order['id'],
            'orderId': order_id,
            'total': order['total'],
            'status': order['status']
        }
    }


@api_router.get("/orders")
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    """Get current user's orders"""
    orders = await firestore_db.get_user_orders(current_user['id'])
    return orders


# ============ CART ROUTES ============

@api_router.get("/cart")
async def get_cart(current_user: dict = Depends(get_current_user)):
    """Get user's cart"""
    cart_items = await firestore_db.get_user_cart(current_user['id'])
    
    # Enrich with product details
    enriched_items = []
    for item in cart_items:
        product = await firestore_db.get_product_by_id(item['product_id'])
        if product:
            enriched_items.append({
                **item,
                'product': product
            })
    
    return {'success': True, 'items': enriched_items}


@api_router.post("/cart/add")
async def add_to_cart(
    product_id: str,
    quantity: int = 1,
    current_user: dict = Depends(get_current_user)
):
    """Add item to cart"""
    result = await firestore_db.add_to_cart(current_user['id'], product_id, quantity)
    return {'success': True, 'item': result}


@api_router.delete("/cart/{item_id}")
async def remove_from_cart(
    item_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Remove item from cart"""
    await firestore_db.update_cart_item(item_id, 0)
    return {'success': True}


# ============ NOTIFICATION ROUTES ============

@api_router.get("/vendor/notifications")
async def get_vendor_notifications(
    current_user: dict = Depends(get_current_user),
    unread_only: bool = False
):
    """Get vendor notifications"""
    vendor = await firestore_db.get_vendor_by_user_id(current_user['id'])
    if not vendor:
        vendor = await firestore_db.get_vendor_by_email(current_user['email'])
    
    if not vendor:
        return {'success': True, 'notifications': [], 'unreadCount': 0}
    
    notifications = await firestore_db.get_vendor_notifications(vendor['id'], unread_only)
    unread = [n for n in notifications if not n.get('is_read')]
    
    return {
        'success': True,
        'notifications': [{
            'id': n['id'],
            'type': n['type'],
            'title': n['title'],
            'message': n['message'],
            'link': n.get('link'),
            'isRead': n.get('is_read', False),
            'createdAt': n['created_at'].isoformat() if hasattr(n['created_at'], 'isoformat') else str(n['created_at'])
        } for n in notifications],
        'unreadCount': len(unread)
    }


@api_router.put("/vendor/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Mark notification as read"""
    await firestore_db.mark_notification_read(notification_id)
    return {'success': True}


@api_router.put("/vendor/notifications/mark-all-read")
async def mark_all_read(current_user: dict = Depends(get_current_user)):
    """Mark all notifications as read"""
    vendor = await firestore_db.get_vendor_by_user_id(current_user['id'])
    if not vendor:
        vendor = await firestore_db.get_vendor_by_email(current_user['email'])
    
    if vendor:
        await firestore_db.mark_all_notifications_read(vendor['id'])
    
    return {'success': True}


@api_router.get("/vendor/notifications/by-email/{email}")
async def get_notifications_by_email(email: str):
    """Get notifications by vendor email"""
    vendor = await firestore_db.get_vendor_by_email(email)
    if not vendor:
        return {'success': True, 'notifications': [], 'unreadCount': 0, 'vendorStatus': None}
    
    notifications = await firestore_db.get_vendor_notifications(vendor['id'])
    unread = [n for n in notifications if not n.get('is_read')]
    
    return {
        'success': True,
        'vendorStatus': vendor.get('status'),
        'vendorName': vendor.get('business_name'),
        'notifications': [{
            'id': n['id'],
            'type': n['type'],
            'title': n['title'],
            'message': n['message'],
            'isRead': n.get('is_read', False),
            'createdAt': n['created_at'].isoformat() if hasattr(n['created_at'], 'isoformat') else str(n['created_at'])
        } for n in notifications[:10]],
        'unreadCount': len(unread)
    }


@api_router.get("/vendor/notifications/preferences")
async def get_notification_preferences(current_user: dict = Depends(get_current_user)):
    """Get notification preferences"""
    vendor = await firestore_db.get_vendor_by_user_id(current_user['id'])
    if not vendor:
        vendor = await firestore_db.get_vendor_by_email(current_user['email'])
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor not found")
    
    prefs = await firestore_db.get_notification_preferences(vendor['id'])
    
    return {
        'success': True,
        'preferences': {
            'email': {
                'orders': prefs.get('email_orders', True),
                'messages': prefs.get('email_messages', True),
                'reviews': prefs.get('email_reviews', True),
                'adminAlerts': prefs.get('email_admin_alerts', True),
                'marketing': prefs.get('email_marketing', False)
            },
            'inapp': {
                'orders': prefs.get('inapp_orders', True),
                'messages': prefs.get('inapp_messages', True),
                'reviews': prefs.get('inapp_reviews', True),
                'adminAlerts': prefs.get('inapp_admin_alerts', True),
                'marketing': prefs.get('inapp_marketing', True)
            },
            'push': {
                'enabled': prefs.get('push_enabled', True),
                'orders': prefs.get('push_orders', True),
                'messages': prefs.get('push_messages', True),
                'reviews': prefs.get('push_reviews', False),
                'adminAlerts': prefs.get('push_admin_alerts', True)
            }
        }
    }


@api_router.put("/vendor/notifications/preferences")
async def update_notification_preferences(
    prefs_update: NotificationPreferencesUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update notification preferences"""
    vendor = await firestore_db.get_vendor_by_user_id(current_user['id'])
    if not vendor:
        vendor = await firestore_db.get_vendor_by_email(current_user['email'])
    
    if not vendor:
        raise HTTPException(status_code=403, detail="Vendor not found")
    
    updates = {k: v for k, v in prefs_update.dict().items() if v is not None}
    await firestore_db.update_notification_preferences(vendor['id'], updates)
    
    return {'success': True}


# ============ CONTACT FORM ============

@api_router.post("/contact")
async def submit_contact_form(contact: ContactForm):
    """Submit contact form"""
    submission = await firestore_db.create_contact_submission({
        'name': contact.name,
        'email': contact.email,
        'subject': contact.subject,
        'message': contact.message
    })
    
    # Send email notification to admin
    try:
        email_service.send_email(
            os.environ.get('ADMIN_EMAIL', 'sotubodammy@gmail.com'),
            f"New Contact Form: {contact.subject}",
            f"<h3>New Contact Form Submission</h3><p><b>From:</b> {contact.name} ({contact.email})</p><p><b>Subject:</b> {contact.subject}</p><p><b>Message:</b></p><p>{contact.message}</p>"
        )
    except Exception as e:
        logger.error(f"Failed to send contact form email: {e}")
    
    return {'success': True, 'message': 'Message sent successfully'}


# ============ PUSH NOTIFICATIONS ============

@api_router.get("/push/vapid-key")
async def get_vapid_key():
    """Get VAPID public key"""
    return {
        'success': True,
        'publicKey': PushNotificationService.get_public_key(),
        'configured': PushNotificationService.is_configured()
    }


# ============ WEBSOCKET ============

@app.websocket("/ws/vendor/{vendor_id}")
async def vendor_websocket(websocket: WebSocket, vendor_id: str):
    """WebSocket for real-time vendor notifications"""
    await ws_manager.connect(websocket, vendor_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get('type') == 'ping':
                    await websocket.send_json({'type': 'pong', 'timestamp': datetime.utcnow().isoformat()})
            except:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


@api_router.get("/ws/status")
async def ws_status():
    """WebSocket status"""
    return {
        'success': True,
        'connected_vendors': ws_manager.get_connected_vendors(),
        'total_connections': sum(len(c) for c in ws_manager.active_connections.values())
    }


# ============ CHATBOT API ============

class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@api_router.get("/chatbot/welcome")
async def get_chatbot_welcome():
    """Get welcome message and initial options for chatbot"""
    afrobot = get_afrobot()
    session_id = await afrobot.create_chat_session()
    return {
        "success": True,
        "welcome_message": afrobot.get_welcome_message(),
        "quick_replies": afrobot.get_quick_replies(),
        "session_id": session_id,
        "bot_name": "AfroBot"
    }

@api_router.post("/chatbot/message")
async def send_chatbot_message(request: ChatMessageRequest):
    """Send a message to AfroBot and get response"""
    afrobot = get_afrobot()
    
    # Create session if not provided
    session_id = request.session_id
    if not session_id:
        session_id = await afrobot.create_chat_session()
    
    # Get AI response
    response = await afrobot.get_chat_response(
        message=request.message,
        session_id=session_id
    )
    
    return {
        "success": True,
        "response": response,
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.get("/chatbot/quick-replies")
async def get_chatbot_quick_replies():
    """Get quick reply suggestions"""
    afrobot = get_afrobot()
    return {
        "success": True,
        "quick_replies": afrobot.get_quick_replies()
    }


# ============ DELIVERY API ============

from delivery_service import get_delivery_service, FREE_DELIVERY_THRESHOLD

class DeliveryCalculateRequest(BaseModel):
    postcode: str
    subtotal: float
    weight_kg: float = 1.0
    delivery_option: str = "standard"

@api_router.post("/delivery/calculate")
async def calculate_delivery(request: DeliveryCalculateRequest):
    """Calculate delivery cost based on postcode and order details"""
    delivery_service = get_delivery_service()
    result = delivery_service.calculate(
        postcode=request.postcode,
        subtotal=request.subtotal,
        weight_kg=request.weight_kg,
        option=request.delivery_option
    )
    return result

@api_router.get("/delivery/options")
async def get_delivery_options(
    postcode: str = Query(..., description="UK postcode"),
    subtotal: float = Query(..., description="Order subtotal in GBP"),
    weight_kg: float = Query(1.0, description="Total weight in kg")
):
    """Get all available delivery options for a postcode"""
    delivery_service = get_delivery_service()
    result = delivery_service.get_options(
        postcode=postcode,
        subtotal=subtotal,
        weight_kg=weight_kg
    )
    return result

@api_router.get("/delivery/zones")
async def get_delivery_zones():
    """Get information about all delivery zones"""
    delivery_service = get_delivery_service()
    return {
        "zones": delivery_service.get_zones_info(),
        "free_delivery_threshold": FREE_DELIVERY_THRESHOLD
    }


# ============ HEALTH & STATUS ============

@api_router.get("/health")
async def health():
    """Health check"""
    return {'status': 'ok', 'database': 'firestore', 'message': 'AfroMarket UK API is running'}


@api_router.get("/")
async def root():
    return {'status': 'ok', 'database': 'firestore'}


# Include router
app.include_router(api_router)


# ============ STARTUP ============

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("Starting AfroMarket UK API with Firestore...")
    
    # Initialize Firebase
    firebase_app = get_firebase_app()
    if firebase_app:
        logger.info("Firebase initialized successfully")
        
        # Seed data if needed
        try:
            await seed_firestore_data()
        except Exception as e:
            logger.error(f"Failed to seed data: {e}")
    else:
        logger.error("Firebase initialization failed!")
    
    logger.info("AfroMarket UK API ready!")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("Shutting down AfroMarket UK API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
