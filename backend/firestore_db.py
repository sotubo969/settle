"""
Firebase Firestore Database Service for AfroMarket UK
Replaces SQLAlchemy/SQLite with Firestore
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials, firestore, auth
from google.cloud.firestore_v1 import FieldFilter, Query

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env', override=False)

logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
_firebase_app = None
_firestore_client = None


def get_firebase_app():
    """Get or initialize Firebase Admin app"""
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    try:
        # Try to get existing app
        _firebase_app = firebase_admin.get_app()
        return _firebase_app
    except ValueError:
        pass
    
    # Initialize new app
    service_account_json = os.environ.get('FIREBASE_SERVICE_ACCOUNT')
    
    if service_account_json:
        try:
            service_account = json.loads(service_account_json)
            cred = credentials.Certificate(service_account)
            _firebase_app = firebase_admin.initialize_app(cred)
            logger.info("Firebase Admin initialized with service account")
            return _firebase_app
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            return None
    
    logger.warning("Firebase service account not configured")
    return None


def get_firestore_client():
    """Get Firestore client"""
    global _firestore_client
    
    if _firestore_client is not None:
        return _firestore_client
    
    app = get_firebase_app()
    if app:
        _firestore_client = firestore.client()
        return _firestore_client
    
    return None


# Helper function to convert Firestore document to dict
def doc_to_dict(doc) -> Optional[Dict]:
    """Convert Firestore document to dictionary with ID"""
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None


def docs_to_list(docs) -> List[Dict]:
    """Convert Firestore documents to list of dictionaries"""
    return [doc_to_dict(doc) for doc in docs if doc.exists]


def get_utc_now():
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


# ============ COLLECTIONS ============

class FirestoreDB:
    """Main Firestore database interface"""
    
    def __init__(self):
        self.db = get_firestore_client()
    
    # ============ USERS ============
    
    async def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        user_data['created_at'] = get_utc_now()
        user_data['updated_at'] = get_utc_now()
        
        # Use Firebase Auth UID if provided, otherwise generate
        user_id = user_data.pop('firebase_uid', None)
        
        if user_id:
            doc_ref = self.db.collection('users').document(user_id)
            doc_ref.set(user_data)
        else:
            doc_ref = self.db.collection('users').add(user_data)[1]
            user_id = doc_ref.id
        
        user_data['id'] = user_id
        return user_data
    
    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        doc = self.db.collection('users').document(user_id).get()
        return doc_to_dict(doc)
    
    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        docs = self.db.collection('users').where(
            filter=FieldFilter('email', '==', email)
        ).limit(1).get()
        
        for doc in docs:
            return doc_to_dict(doc)
        return None
    
    async def update_user(self, user_id: str, updates: Dict) -> bool:
        """Update user data"""
        updates['updated_at'] = get_utc_now()
        self.db.collection('users').document(user_id).update(updates)
        return True
    
    async def get_user_by_reset_token(self, reset_token: str) -> Optional[Dict]:
        """Get user by password reset token"""
        docs = self.db.collection('users').where('reset_token', '==', reset_token).limit(1).get()
        for doc in docs:
            return doc_to_dict(doc)
        return None
    
    async def get_all_users(self, limit: int = 100) -> List[Dict]:
        """Get all users"""
        docs = self.db.collection('users').limit(limit).get()
        return docs_to_list(docs)
    
    # ============ VENDORS ============
    
    async def create_vendor(self, vendor_data: Dict) -> Dict:
        """Create a new vendor"""
        vendor_data['created_at'] = get_utc_now()
        vendor_data['updated_at'] = get_utc_now()
        vendor_data['status'] = vendor_data.get('status', 'pending')
        vendor_data['verified'] = vendor_data.get('verified', False)
        vendor_data['rating'] = vendor_data.get('rating', 0)
        vendor_data['total_sales'] = vendor_data.get('total_sales', 0)
        
        doc_ref = self.db.collection('vendors').add(vendor_data)[1]
        vendor_data['id'] = doc_ref.id
        return vendor_data
    
    async def get_vendor_by_id(self, vendor_id: str) -> Optional[Dict]:
        """Get vendor by ID"""
        doc = self.db.collection('vendors').document(vendor_id).get()
        return doc_to_dict(doc)
    
    async def get_vendor_by_email(self, email: str) -> Optional[Dict]:
        """Get vendor by email"""
        docs = self.db.collection('vendors').where(
            filter=FieldFilter('email', '==', email)
        ).limit(1).get()
        
        for doc in docs:
            return doc_to_dict(doc)
        return None
    
    async def get_vendor_by_user_id(self, user_id: str) -> Optional[Dict]:
        """Get vendor by user ID"""
        docs = self.db.collection('vendors').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).limit(1).get()
        
        for doc in docs:
            return doc_to_dict(doc)
        return None
    
    async def get_all_vendors(self, status: str = None, verified: bool = None) -> List[Dict]:
        """Get all vendors with optional filters"""
        query = self.db.collection('vendors')
        
        if status:
            query = query.where(filter=FieldFilter('status', '==', status))
        if verified is not None:
            query = query.where(filter=FieldFilter('verified', '==', verified))
        
        docs = query.get()
        return docs_to_list(docs)
    
    async def update_vendor(self, vendor_id: str, updates: Dict) -> bool:
        """Update vendor data"""
        updates['updated_at'] = get_utc_now()
        self.db.collection('vendors').document(vendor_id).update(updates)
        return True
    
    # ============ PRODUCTS ============
    
    async def create_product(self, product_data: Dict) -> Dict:
        """Create a new product"""
        product_data['created_at'] = get_utc_now()
        product_data['updated_at'] = get_utc_now()
        product_data['rating'] = product_data.get('rating', 0)
        product_data['review_count'] = product_data.get('review_count', 0)
        product_data['in_stock'] = product_data.get('in_stock', True)
        
        doc_ref = self.db.collection('products').add(product_data)[1]
        product_data['id'] = doc_ref.id
        return product_data
    
    async def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get product by ID"""
        doc = self.db.collection('products').document(product_id).get()
        return doc_to_dict(doc)
    
    async def get_all_products(self, category: str = None, vendor_id: str = None, 
                                in_stock: bool = None, limit: int = 100) -> List[Dict]:
        """Get all products with optional filters"""
        query = self.db.collection('products')
        
        if category:
            query = query.where(filter=FieldFilter('category', '==', category))
        if vendor_id:
            query = query.where(filter=FieldFilter('vendor_id', '==', vendor_id))
        if in_stock is not None:
            query = query.where(filter=FieldFilter('in_stock', '==', in_stock))
        
        docs = query.limit(limit).get()
        return docs_to_list(docs)
    
    async def get_products_by_vendor(self, vendor_id: str, limit: int = 100) -> List[Dict]:
        """Get all products for a specific vendor"""
        docs = self.db.collection('products').where('vendor_id', '==', vendor_id).limit(limit).get()
        return docs_to_list(docs)
    
    async def search_products(self, query_text: str, limit: int = 50) -> List[Dict]:
        """Search products by name (basic search)"""
        # Firestore doesn't support full-text search natively
        # This is a basic implementation - for production, consider Algolia or Elasticsearch
        docs = self.db.collection('products').limit(limit).get()
        results = []
        query_lower = query_text.lower()
        
        for doc in docs:
            data = doc_to_dict(doc)
            if data and (query_lower in data.get('name', '').lower() or 
                        query_lower in data.get('description', '').lower()):
                results.append(data)
        
        return results
    
    async def update_product(self, product_id: str, updates: Dict) -> bool:
        """Update product data"""
        updates['updated_at'] = get_utc_now()
        self.db.collection('products').document(product_id).update(updates)
        return True
    
    async def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        self.db.collection('products').document(product_id).delete()
        return True
    
    # ============ ORDERS ============
    
    async def create_order(self, order_data: Dict) -> Dict:
        """Create a new order"""
        order_data['created_at'] = get_utc_now()
        order_data['updated_at'] = get_utc_now()
        order_data['status'] = order_data.get('status', 'pending')
        
        # Generate order ID
        import random
        import string
        order_data['order_id'] = 'AFM-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        doc_ref = self.db.collection('orders').add(order_data)[1]
        order_data['id'] = doc_ref.id
        return order_data
    
    async def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """Get order by document ID"""
        doc = self.db.collection('orders').document(order_id).get()
        return doc_to_dict(doc)
    
    async def get_order_by_order_id(self, order_id: str) -> Optional[Dict]:
        """Get order by order_id field"""
        docs = self.db.collection('orders').where(
            filter=FieldFilter('order_id', '==', order_id)
        ).limit(1).get()
        
        for doc in docs:
            return doc_to_dict(doc)
        return None
    
    async def get_user_orders(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get orders for a user"""
        try:
            docs = self.db.collection('orders').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).limit(limit).get()
            results = docs_to_list(docs)
            # Sort by created_at descending in Python to avoid composite index requirement
            results.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error fetching user orders: {e}")
            return []
    
    async def get_vendor_orders(self, vendor_id: str, limit: int = 50) -> List[Dict]:
        """Get orders containing products from a vendor"""
        try:
            docs = self.db.collection('orders').where(
                filter=FieldFilter('vendor_ids', 'array_contains', vendor_id)
            ).limit(limit).get()
            results = docs_to_list(docs)
            # Sort by created_at descending in Python
            results.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error fetching vendor orders: {e}")
            return []
    
    async def get_all_orders(self, limit: int = 500) -> List[Dict]:
        """Get all orders for admin/owner dashboard"""
        try:
            docs = self.db.collection('orders').limit(limit).get()
            results = docs_to_list(docs)
            results.sort(key=lambda x: str(x.get('created_at', '')), reverse=True)
            return results
        except Exception as e:
            logger.error(f"Error fetching all orders: {e}")
            return []
    
    async def update_order(self, order_id: str, updates: Dict) -> bool:
        """Update order data"""
        updates['updated_at'] = get_utc_now()
        self.db.collection('orders').document(order_id).update(updates)
        return True
    
    # ============ CART ============
    
    async def get_user_cart(self, user_id: str) -> List[Dict]:
        """Get cart items for a user"""
        docs = self.db.collection('carts').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).get()
        return docs_to_list(docs)
    
    async def add_to_cart(self, user_id: str, product_id: str, quantity: int = 1) -> Dict:
        """Add item to cart"""
        # Check if item already in cart
        docs = self.db.collection('carts').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).where(
            filter=FieldFilter('product_id', '==', product_id)
        ).limit(1).get()
        
        for doc in docs:
            # Update quantity
            current = doc.to_dict()
            new_qty = current.get('quantity', 0) + quantity
            doc.reference.update({'quantity': new_qty, 'updated_at': get_utc_now()})
            return {'id': doc.id, 'quantity': new_qty}
        
        # Add new cart item
        cart_item = {
            'user_id': user_id,
            'product_id': product_id,
            'quantity': quantity,
            'created_at': get_utc_now(),
            'updated_at': get_utc_now()
        }
        doc_ref = self.db.collection('carts').add(cart_item)[1]
        cart_item['id'] = doc_ref.id
        return cart_item
    
    async def update_cart_item(self, cart_item_id: str, quantity: int) -> bool:
        """Update cart item quantity"""
        if quantity <= 0:
            self.db.collection('carts').document(cart_item_id).delete()
        else:
            self.db.collection('carts').document(cart_item_id).update({
                'quantity': quantity,
                'updated_at': get_utc_now()
            })
        return True
    
    async def update_cart_item_quantity(self, user_id: str, product_id: str, quantity: int) -> Dict:
        """Update cart item quantity by user_id and product_id"""
        docs = self.db.collection('carts').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).where(
            filter=FieldFilter('product_id', '==', product_id)
        ).limit(1).get()
        
        for doc in docs:
            if quantity <= 0:
                doc.reference.delete()
                return {'deleted': True}
            else:
                doc.reference.update({
                    'quantity': quantity,
                    'updated_at': get_utc_now()
                })
                return {'id': doc.id, 'product_id': product_id, 'quantity': quantity}
        
        return None
    
    async def remove_from_cart(self, user_id: str, product_id: str) -> bool:
        """Remove item from cart by user_id and product_id"""
        docs = self.db.collection('carts').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).where(
            filter=FieldFilter('product_id', '==', product_id)
        ).get()
        
        for doc in docs:
            doc.reference.delete()
        return True
    
    async def clear_cart(self, user_id: str) -> bool:
        """Alias for clear_user_cart"""
        return await self.clear_user_cart(user_id)
    
    async def clear_user_cart(self, user_id: str) -> bool:
        """Clear all cart items for a user"""
        docs = self.db.collection('carts').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).get()
        
        for doc in docs:
            doc.reference.delete()
        return True
    
    # ============ WISHLIST ============
    
    async def get_user_wishlist(self, user_id: str) -> List[Dict]:
        """Get user's wishlist with product details"""
        try:
            docs = self.db.collection('wishlists').where(
                filter=FieldFilter('user_id', '==', user_id)
            ).get()
            
            wishlist_items = docs_to_list(docs)
            
            # Get product details for each item
            for item in wishlist_items:
                product = await self.get_product_by_id(item.get('product_id'))
                if product:
                    item['product'] = product
            
            return wishlist_items
        except Exception as e:
            logger.error(f"Error fetching wishlist: {e}")
            return []
    
    async def add_to_wishlist(self, user_id: str, product_id: str) -> Dict:
        """Add product to wishlist"""
        # Check if already exists
        docs = self.db.collection('wishlists').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).where(
            filter=FieldFilter('product_id', '==', product_id)
        ).limit(1).get()
        
        for doc in docs:
            return {'id': doc.id, 'message': 'Already in wishlist'}
        
        # Add new item
        item = {
            'user_id': user_id,
            'product_id': product_id,
            'created_at': get_utc_now()
        }
        doc_ref = self.db.collection('wishlists').add(item)[1]
        item['id'] = doc_ref.id
        return item
    
    async def remove_from_wishlist(self, user_id: str, product_id: str) -> bool:
        """Remove product from wishlist"""
        docs = self.db.collection('wishlists').where(
            filter=FieldFilter('user_id', '==', user_id)
        ).where(
            filter=FieldFilter('product_id', '==', product_id)
        ).get()
        
        for doc in docs:
            doc.reference.delete()
        return True
    
    # ============ NOTIFICATIONS ============
    
    async def create_notification(self, notification_data: Dict) -> Dict:
        """Create a notification"""
        notification_data['created_at'] = get_utc_now()
        notification_data['is_read'] = False
        
        doc_ref = self.db.collection('notifications').add(notification_data)[1]
        notification_data['id'] = doc_ref.id
        return notification_data
    
    async def get_vendor_notifications(self, vendor_id: str, unread_only: bool = False, 
                                        limit: int = 50) -> List[Dict]:
        """Get notifications for a vendor"""
        try:
            query = self.db.collection('notifications').where(
                filter=FieldFilter('vendor_id', '==', vendor_id)
            )
            
            if unread_only:
                query = query.where(filter=FieldFilter('is_read', '==', False))
            
            # Try with order_by (requires composite index)
            try:
                docs = query.order_by('created_at', direction=Query.DESCENDING).limit(limit).get()
            except Exception:
                # Fallback: fetch without order and sort in Python
                docs = query.limit(limit * 2).get()
                results = docs_to_list(docs)
                # Sort by created_at descending
                results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
                return results[:limit]
            
            return docs_to_list(docs)
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return []
    
    async def mark_notification_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        self.db.collection('notifications').document(notification_id).update({
            'is_read': True,
            'read_at': get_utc_now()
        })
        return True
    
    async def mark_all_notifications_read(self, vendor_id: str) -> bool:
        """Mark all notifications as read for a vendor"""
        docs = self.db.collection('notifications').where(
            filter=FieldFilter('vendor_id', '==', vendor_id)
        ).where(
            filter=FieldFilter('is_read', '==', False)
        ).get()
        
        for doc in docs:
            doc.reference.update({'is_read': True, 'read_at': get_utc_now()})
        return True
    
    # ============ ADS ============
    
    async def create_ad(self, ad_data: Dict) -> Dict:
        """Create an advertisement"""
        ad_data['created_at'] = get_utc_now()
        ad_data['updated_at'] = get_utc_now()
        ad_data['status'] = ad_data.get('status', 'pending')
        ad_data['impressions'] = 0
        ad_data['clicks'] = 0
        
        doc_ref = self.db.collection('ads').add(ad_data)[1]
        ad_data['id'] = doc_ref.id
        return ad_data
    
    async def get_active_ads(self, limit: int = 10) -> List[Dict]:
        """Get active advertisements"""
        docs = self.db.collection('ads').where(
            filter=FieldFilter('status', '==', 'active')
        ).limit(limit).get()
        return docs_to_list(docs)
    
    async def get_vendor_ads(self, vendor_id: str) -> List[Dict]:
        """Get ads for a vendor"""
        docs = self.db.collection('ads').where(
            filter=FieldFilter('vendor_id', '==', vendor_id)
        ).get()
        return docs_to_list(docs)
    
    async def update_ad(self, ad_id: str, updates: Dict) -> bool:
        """Update advertisement"""
        updates['updated_at'] = get_utc_now()
        self.db.collection('ads').document(ad_id).update(updates)
        return True
    
    async def increment_ad_stats(self, ad_id: str, impressions: int = 0, clicks: int = 0) -> bool:
        """Increment ad statistics"""
        from google.cloud.firestore_v1 import Increment
        updates = {}
        if impressions:
            updates['impressions'] = Increment(impressions)
        if clicks:
            updates['clicks'] = Increment(clicks)
        
        if updates:
            self.db.collection('ads').document(ad_id).update(updates)
        return True
    
    # ============ CONTACT FORM ============
    
    async def create_contact_submission(self, contact_data: Dict) -> Dict:
        """Create a contact form submission"""
        contact_data['created_at'] = get_utc_now()
        contact_data['status'] = 'new'
        
        doc_ref = self.db.collection('contact_submissions').add(contact_data)[1]
        contact_data['id'] = doc_ref.id
        return contact_data
    
    async def get_contact_submissions(self, status: str = None, limit: int = 50) -> List[Dict]:
        """Get contact form submissions"""
        query = self.db.collection('contact_submissions')
        
        if status:
            query = query.where(filter=FieldFilter('status', '==', status))
        
        docs = query.order_by('created_at', direction=Query.DESCENDING).limit(limit).get()
        return docs_to_list(docs)
    
    # ============ REVIEWS ============
    
    async def create_review(self, review_data: Dict) -> Dict:
        """Create a product review"""
        review_data['created_at'] = get_utc_now()
        
        doc_ref = self.db.collection('reviews').add(review_data)[1]
        review_data['id'] = doc_ref.id
        return review_data
    
    async def get_product_reviews(self, product_id: str, limit: int = 50) -> List[Dict]:
        """Get reviews for a product"""
        docs = self.db.collection('reviews').where(
            filter=FieldFilter('product_id', '==', product_id)
        ).order_by('created_at', direction=Query.DESCENDING).limit(limit).get()
        return docs_to_list(docs)
    
    # ============ MESSAGES ============
    
    async def create_message(self, message_data: Dict) -> Dict:
        """Create a message"""
        message_data['created_at'] = get_utc_now()
        message_data['is_read'] = False
        
        doc_ref = self.db.collection('messages').add(message_data)[1]
        message_data['id'] = doc_ref.id
        return message_data
    
    async def get_user_messages(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get messages for a user"""
        # Get messages where user is sender or receiver
        sent_docs = self.db.collection('messages').where(
            filter=FieldFilter('sender_id', '==', user_id)
        ).limit(limit).get()
        
        received_docs = self.db.collection('messages').where(
            filter=FieldFilter('receiver_id', '==', user_id)
        ).limit(limit).get()
        
        messages = docs_to_list(sent_docs) + docs_to_list(received_docs)
        messages.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        return messages[:limit]
    
    # ============ NOTIFICATION PREFERENCES ============
    
    async def get_notification_preferences(self, vendor_id: str) -> Optional[Dict]:
        """Get notification preferences for a vendor"""
        doc = self.db.collection('notification_preferences').document(vendor_id).get()
        if doc.exists:
            return doc_to_dict(doc)
        
        # Return defaults
        return {
            'id': vendor_id,
            'email_orders': True,
            'email_messages': True,
            'email_reviews': True,
            'email_admin_alerts': True,
            'email_marketing': False,
            'inapp_orders': True,
            'inapp_messages': True,
            'inapp_reviews': True,
            'inapp_admin_alerts': True,
            'inapp_marketing': True,
            'push_enabled': True,
            'push_orders': True,
            'push_messages': True,
            'push_reviews': False,
            'push_admin_alerts': True
        }
    
    async def update_notification_preferences(self, vendor_id: str, updates: Dict) -> bool:
        """Update notification preferences"""
        updates['updated_at'] = get_utc_now()
        self.db.collection('notification_preferences').document(vendor_id).set(updates, merge=True)
        return True
    
    # ============ PUSH SUBSCRIPTIONS ============
    
    async def create_push_subscription(self, subscription_data: Dict) -> Dict:
        """Create a push subscription"""
        subscription_data['created_at'] = get_utc_now()
        subscription_data['is_active'] = True
        
        doc_ref = self.db.collection('push_subscriptions').add(subscription_data)[1]
        subscription_data['id'] = doc_ref.id
        return subscription_data
    
    async def get_vendor_push_subscriptions(self, vendor_id: str, active_only: bool = True) -> List[Dict]:
        """Get push subscriptions for a vendor"""
        query = self.db.collection('push_subscriptions').where(
            filter=FieldFilter('vendor_id', '==', vendor_id)
        )
        
        if active_only:
            query = query.where(filter=FieldFilter('is_active', '==', True))
        
        docs = query.get()
        return docs_to_list(docs)
    
    async def deactivate_push_subscription(self, subscription_id: str) -> bool:
        """Deactivate a push subscription"""
        self.db.collection('push_subscriptions').document(subscription_id).update({
            'is_active': False,
            'updated_at': get_utc_now()
        })
        return True


# Global instance
firestore_db = FirestoreDB()


# ============ DATA SEEDING ============

async def seed_firestore_data():
    """Seed initial data to Firestore"""
    db = firestore_db
    
    # Check if products already exist
    existing_products = await db.get_all_products(limit=1)
    if existing_products:
        logger.info("Firestore data already seeded")
        return
    
    logger.info("Seeding Firestore data...")
    
    # Create vendors
    vendors_data = [
        {
            "business_name": "Mama Nkechi's African Store",
            "email": "mama.nkechi@afromarket.co.uk",
            "phone": "+44 20 7123 4567",
            "address": "123 Brixton Road",
            "city": "London",
            "postcode": "SW9 6DE",
            "location": "London",
            "description": "Authentic Nigerian groceries and spices",
            "rating": 4.8,
            "total_sales": 254,
            "verified": True,
            "status": "approved"
        },
        {
            "business_name": "Wosiwosi Foods",
            "email": "info@wosiwosi.co.uk",
            "phone": "+44 161 234 5678",
            "address": "45 Moss Side Road",
            "city": "Manchester",
            "postcode": "M14 4PX",
            "location": "Manchester",
            "description": "Premium West African food products",
            "rating": 4.6,
            "total_sales": 189,
            "verified": True,
            "status": "approved"
        },
        {
            "business_name": "African Food Warehouse",
            "email": "sales@afwhouse.co.uk",
            "phone": "+44 121 345 6789",
            "address": "78 Stratford Road",
            "city": "Birmingham",
            "postcode": "B11 1AG",
            "location": "Birmingham",
            "description": "Wholesale and retail African groceries",
            "rating": 4.5,
            "total_sales": 312,
            "verified": True,
            "status": "approved"
        }
    ]
    
    created_vendors = []
    for vendor_data in vendors_data:
        vendor = await db.create_vendor(vendor_data)
        created_vendors.append(vendor)
        logger.info(f"Created vendor: {vendor['business_name']}")
    
    # Create products
    products_data = [
        # Fresh Produce
        {"name": "Fresh Plantains (Ripe)", "brand": "Tropical Fresh", "category": "Fresh Produce", "price": 3.99, "original_price": 4.99, "image": "https://images.unsplash.com/photo-1603833665858-e61d17a86224?w=400", "description": "Sweet ripe plantains perfect for frying", "weight": "1kg", "vendor_id": created_vendors[0]['id']},
        {"name": "Fresh Cassava", "brand": "Farm Fresh", "category": "Fresh Produce", "price": 4.49, "original_price": 5.49, "image": "https://images.unsplash.com/photo-1598030343246-3235b9a1f0f0?w=400", "description": "Fresh cassava roots for boiling or frying", "weight": "1kg", "vendor_id": created_vendors[0]['id']},
        {"name": "Scotch Bonnet Peppers", "brand": "Spice King", "category": "Fresh Produce", "price": 2.99, "image": "https://images.unsplash.com/photo-1583119022894-919a68a3d0e3?w=400", "description": "Fresh hot scotch bonnet peppers", "weight": "200g", "vendor_id": created_vendors[1]['id']},
        {"name": "Fresh Okra", "brand": "Garden Fresh", "category": "Fresh Produce", "price": 3.49, "image": "https://images.unsplash.com/photo-1425543103986-22abb7d7e8d2?w=400", "description": "Fresh okra for soups and stews", "weight": "500g", "vendor_id": created_vendors[2]['id']},
        
        # Grains & Flours
        {"name": "Poundo Yam Flour", "brand": "Ola-Ola", "category": "Grains & Flours", "price": 8.99, "original_price": 10.99, "image": "https://images.unsplash.com/photo-1586201375761-83865001e8ac?w=400", "description": "Premium yam flour for smooth poundo", "weight": "2kg", "vendor_id": created_vendors[0]['id']},
        {"name": "White Garri (Ijebu)", "brand": "Niji Foods", "category": "Grains & Flours", "price": 6.99, "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400", "description": "Fine white garri from Ijebu", "weight": "2kg", "vendor_id": created_vendors[1]['id']},
        {"name": "Semovita", "brand": "Golden Penny", "category": "Grains & Flours", "price": 7.49, "image": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=400", "description": "Golden semolina flour", "weight": "2kg", "vendor_id": created_vendors[2]['id']},
        {"name": "Nigerian Brown Beans", "brand": "Oloyin", "category": "Grains & Flours", "price": 5.99, "image": "https://images.unsplash.com/photo-1515543904323-712af97fa435?w=400", "description": "Premium honey beans", "weight": "1kg", "vendor_id": created_vendors[0]['id']},
        {"name": "Ofada Rice", "brand": "Afro Rice", "category": "Grains & Flours", "price": 9.99, "image": "https://images.unsplash.com/photo-1586201375761-83865001e8ac?w=400", "description": "Local Nigerian brown rice", "weight": "2kg", "vendor_id": created_vendors[1]['id']},
        
        # Condiments & Seasonings
        {"name": "Maggi Cubes (Pack of 100)", "brand": "Maggi", "category": "Condiments & Seasonings", "price": 5.99, "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400", "description": "Classic seasoning cubes", "weight": "400g", "vendor_id": created_vendors[0]['id']},
        {"name": "Ground Crayfish", "brand": "Mama's Choice", "category": "Condiments & Seasonings", "price": 7.99, "image": "https://images.unsplash.com/photo-1599909533681-74ccf2f3d00b?w=400", "description": "Finely ground dried crayfish", "weight": "200g", "vendor_id": created_vendors[1]['id']},
        {"name": "Iru (Locust Beans)", "brand": "Traditional", "category": "Condiments & Seasonings", "price": 4.99, "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400", "description": "Fermented locust beans for authentic flavor", "weight": "100g", "vendor_id": created_vendors[2]['id']},
        {"name": "Suya Spice Mix", "brand": "Spice Master", "category": "Condiments & Seasonings", "price": 3.99, "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=400", "description": "Authentic suya pepper mix", "weight": "100g", "vendor_id": created_vendors[0]['id']},
        {"name": "Palm Oil (Zomi)", "brand": "Devon King's", "category": "Condiments & Seasonings", "price": 8.99, "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=400", "description": "Pure red palm oil", "weight": "1L", "vendor_id": created_vendors[1]['id']},
        
        # Frozen Foods
        {"name": "Goat Meat (Fresh Frozen)", "brand": "Halal Meats", "category": "Frozen Foods & Meats", "price": 14.99, "image": "https://images.unsplash.com/photo-1603048297172-c92544798d5a?w=400", "description": "Premium halal goat meat", "weight": "1kg", "vendor_id": created_vendors[2]['id']},
        {"name": "Stockfish (Okporoko)", "brand": "Nordic Catch", "category": "Frozen Foods & Meats", "price": 12.99, "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400", "description": "Dried stockfish", "weight": "500g", "vendor_id": created_vendors[0]['id']},
        {"name": "Frozen Tilapia", "brand": "Ocean Fresh", "category": "Frozen Foods & Meats", "price": 9.99, "image": "https://images.unsplash.com/photo-1544943910-4c1dc44aab44?w=400", "description": "Whole frozen tilapia", "weight": "1kg", "vendor_id": created_vendors[1]['id']},
        {"name": "Smoked Mackerel (Titus)", "brand": "Sea Catch", "category": "Frozen Foods & Meats", "price": 6.99, "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?w=400", "description": "Traditional smoked mackerel", "weight": "500g", "vendor_id": created_vendors[2]['id']},
        
        # Snacks
        {"name": "Chin Chin", "brand": "Mama's Kitchen", "category": "Snacks & Confectionery", "price": 4.99, "image": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400", "description": "Crunchy fried dough snack", "weight": "400g", "vendor_id": created_vendors[0]['id']},
        {"name": "Plantain Chips", "brand": "Crispy Delights", "category": "Snacks & Confectionery", "price": 3.49, "image": "https://images.unsplash.com/photo-1566478989037-eec170784d0b?w=400", "description": "Crispy salted plantain chips", "weight": "200g", "vendor_id": created_vendors[1]['id']},
        {"name": "Kulikuli (Groundnut Cake)", "brand": "Northern Treats", "category": "Snacks & Confectionery", "price": 2.99, "image": "https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=400", "description": "Traditional peanut snack", "weight": "150g", "vendor_id": created_vendors[2]['id']},
        
        # Drinks
        {"name": "Zobo Drink (Hibiscus)", "brand": "Natural Brews", "category": "Drinks & Beverages", "price": 3.99, "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400", "description": "Refreshing hibiscus drink", "weight": "500ml", "vendor_id": created_vendors[0]['id']},
        {"name": "Milo Chocolate Drink", "brand": "Nestle", "category": "Drinks & Beverages", "price": 6.99, "image": "https://images.unsplash.com/photo-1517578239113-b03992dcdd25?w=400", "description": "Chocolate malt drink", "weight": "400g", "vendor_id": created_vendors[1]['id']},
        {"name": "Peak Milk (Evaporated)", "brand": "Peak", "category": "Drinks & Beverages", "price": 2.49, "image": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=400", "description": "Creamy evaporated milk", "weight": "410g", "vendor_id": created_vendors[2]['id']},
        {"name": "Palm Wine (Fresh)", "brand": "Tropical", "category": "Drinks & Beverages", "price": 7.99, "image": "https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400", "description": "Natural palm wine", "weight": "1L", "vendor_id": created_vendors[0]['id']},
        
        # Dried Foods
        {"name": "Egusi (Melon Seeds)", "brand": "Premium Seeds", "category": "Dried & Preserved Foods", "price": 8.99, "image": "https://images.unsplash.com/photo-1515543904323-712af97fa435?w=400", "description": "Ground melon seeds for soup", "weight": "500g", "vendor_id": created_vendors[1]['id']},
        {"name": "Ogbono Seeds", "brand": "Forest Harvest", "category": "Dried & Preserved Foods", "price": 9.99, "image": "https://images.unsplash.com/photo-1515543904323-712af97fa435?w=400", "description": "Wild mango seeds for soup", "weight": "400g", "vendor_id": created_vendors[2]['id']},
        {"name": "Dried Bitter Leaf", "brand": "Herbal Plus", "category": "Dried & Preserved Foods", "price": 4.99, "image": "https://images.unsplash.com/photo-1515543904323-712af97fa435?w=400", "description": "Dried bitter leaf for soup", "weight": "100g", "vendor_id": created_vendors[0]['id']},
        {"name": "Uziza Leaves (Dried)", "brand": "Spice Garden", "category": "Dried & Preserved Foods", "price": 5.49, "image": "https://images.unsplash.com/photo-1515543904323-712af97fa435?w=400", "description": "Aromatic pepper leaves", "weight": "50g", "vendor_id": created_vendors[1]['id']},
        
        # Beauty
        {"name": "African Black Soap", "brand": "Dudu-Osun", "category": "Beauty & Household", "price": 4.99, "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400", "description": "Natural black soap", "weight": "150g", "vendor_id": created_vendors[2]['id']},
        {"name": "Shea Butter (Raw)", "brand": "Ghana Gold", "category": "Beauty & Household", "price": 7.99, "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400", "description": "Pure unrefined shea butter", "weight": "500g", "vendor_id": created_vendors[0]['id']},
        {"name": "Chewing Stick (Pako)", "brand": "Natural Care", "category": "Beauty & Household", "price": 1.99, "image": "https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400", "description": "Natural teeth cleaning sticks", "weight": "Pack of 5", "vendor_id": created_vendors[1]['id']},
    ]
    
    for product_data in products_data:
        product_data['in_stock'] = True
        product_data['stock_quantity'] = 100
        product_data['rating'] = round(4.0 + (hash(product_data['name']) % 10) / 10, 1)
        product_data['review_count'] = hash(product_data['name']) % 50 + 5
        await db.create_product(product_data)
    
    logger.info(f"Seeded {len(products_data)} products to Firestore")
    logger.info("Firestore data seeding completed!")
