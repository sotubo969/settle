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
    """Approve or reject a vendor"""
    vendor = await firestore_db.get_vendor_by_id(approval.vendorId)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    # Update vendor status
    await firestore_db.update_vendor(approval.vendorId, {
        'status': approval.status,
        'verified': approval.status == 'approved'
    })
    
    # Create notification
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
    
    # Send email
    email_sent = False
    try:
        email_sent = email_service.send_vendor_approval_email(
            vendor['email'], 
            vendor['business_name'], 
            approval.status == 'approved'
        )
    except Exception as e:
        logger.error(f"Failed to send approval email: {e}")
    
    return {'success': True, 'emailSent': email_sent, 'notificationCreated': True}


# ============ ORDER ROUTES ============

@api_router.post("/orders")
async def create_order(
    order_data: OrderCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new order"""
    # Get vendor IDs from items
    vendor_ids = list(set(item.get('vendorId') for item in order_data.items if item.get('vendorId')))
    
    order = await firestore_db.create_order({
        'user_id': current_user['id'],
        'items': order_data.items,
        'shipping_info': order_data.shipping_info,
        'payment_info': {k: v for k, v in order_data.payment_info.items() if k != 'cardNumber'},
        'total': order_data.total,
        'vendor_ids': vendor_ids,
        'status': 'pending'
    })
    
    # Notify vendors
    for vendor_id in vendor_ids:
        vendor_items = [i for i in order_data.items if i.get('vendorId') == vendor_id]
        vendor_total = sum(i.get('price', 0) * i.get('quantity', 1) for i in vendor_items)
        
        await firestore_db.create_notification({
            'vendor_id': vendor_id,
            'type': 'order',
            'title': f"🛒 New Order #{order['order_id']}!",
            'message': f"New order with {len(vendor_items)} item(s) totaling £{vendor_total:.2f}",
            'link': f"/vendor/dashboard?tab=orders&order={order['order_id']}",
            'data': {'order_id': order['order_id'], 'total': vendor_total}
        })
        
        # WebSocket notification
        await ws_manager.send_to_vendor(vendor_id, {
            'type': 'notification',
            'notification': {
                'type': 'order',
                'title': f"🛒 New Order #{order['order_id']}!",
                'message': f"New order with {len(vendor_items)} item(s) totaling £{vendor_total:.2f}",
                'link': f"/vendor/dashboard?tab=orders"
            }
        })
    
    # Clear cart
    await firestore_db.clear_user_cart(current_user['id'])
    
    return {
        'success': True,
        'order': {
            'id': order['id'],
            'orderId': order['order_id'],
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
