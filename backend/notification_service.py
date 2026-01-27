"""
WebSocket and Push Notification Service for AfroMarket UK
Real-time notifications for vendors
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, field
import os

# Web Push imports
try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    print("pywebpush not installed. Push notifications will be disabled.")

logger = logging.getLogger(__name__)

# VAPID keys for Web Push (generate once and store securely)
VAPID_PRIVATE_KEY = os.environ.get('VAPID_PRIVATE_KEY', '')
VAPID_PUBLIC_KEY = os.environ.get('VAPID_PUBLIC_KEY', '')
VAPID_CLAIMS = {
    "sub": "mailto:sotubodammy@gmail.com"
}


@dataclass
class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    # vendor_id -> set of WebSocket connections
    active_connections: Dict[int, Set[WebSocket]] = field(default_factory=dict)
    # WebSocket -> vendor_id mapping for cleanup
    connection_to_vendor: Dict[WebSocket, int] = field(default_factory=dict)
    
    async def connect(self, websocket: WebSocket, vendor_id: int):
        """Accept a new WebSocket connection for a vendor"""
        await websocket.accept()
        
        if vendor_id not in self.active_connections:
            self.active_connections[vendor_id] = set()
        
        self.active_connections[vendor_id].add(websocket)
        self.connection_to_vendor[websocket] = vendor_id
        
        logger.info(f"WebSocket connected for vendor {vendor_id}. Total connections: {len(self.active_connections[vendor_id])}")
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "vendor_id": vendor_id,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        vendor_id = self.connection_to_vendor.get(websocket)
        
        if vendor_id and vendor_id in self.active_connections:
            self.active_connections[vendor_id].discard(websocket)
            if not self.active_connections[vendor_id]:
                del self.active_connections[vendor_id]
        
        if websocket in self.connection_to_vendor:
            del self.connection_to_vendor[websocket]
        
        logger.info(f"WebSocket disconnected for vendor {vendor_id}")
    
    async def send_to_vendor(self, vendor_id: int, message: dict):
        """Send a message to all connections for a specific vendor"""
        if vendor_id not in self.active_connections:
            logger.debug(f"No active connections for vendor {vendor_id}")
            return False
        
        disconnected = set()
        sent_count = 0
        
        for websocket in self.active_connections[vendor_id]:
            try:
                await websocket.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send to websocket: {e}")
                disconnected.add(websocket)
        
        # Clean up disconnected sockets
        for ws in disconnected:
            self.disconnect(ws)
        
        logger.info(f"Sent notification to {sent_count} connections for vendor {vendor_id}")
        return sent_count > 0
    
    async def broadcast(self, message: dict, exclude_vendors: Set[int] = None):
        """Broadcast a message to all connected vendors"""
        exclude_vendors = exclude_vendors or set()
        
        for vendor_id in list(self.active_connections.keys()):
            if vendor_id not in exclude_vendors:
                await self.send_to_vendor(vendor_id, message)
    
    def get_connected_vendors(self) -> List[int]:
        """Get list of currently connected vendor IDs"""
        return list(self.active_connections.keys())
    
    def is_vendor_connected(self, vendor_id: int) -> bool:
        """Check if a vendor has any active connections"""
        return vendor_id in self.active_connections and len(self.active_connections[vendor_id]) > 0


# Global connection manager instance
ws_manager = ConnectionManager()


class PushNotificationService:
    """Service for sending Web Push notifications"""
    
    @staticmethod
    def is_configured() -> bool:
        """Check if push notifications are configured"""
        return WEBPUSH_AVAILABLE and bool(VAPID_PRIVATE_KEY) and bool(VAPID_PUBLIC_KEY)
    
    @staticmethod
    def get_public_key() -> str:
        """Get the VAPID public key for client subscription"""
        return VAPID_PUBLIC_KEY
    
    @staticmethod
    async def send_push(subscription_info: dict, title: str, body: str, 
                        icon: str = None, url: str = None, tag: str = None,
                        data: dict = None) -> bool:
        """Send a push notification to a subscription"""
        if not PushNotificationService.is_configured():
            logger.warning("Push notifications not configured")
            return False
        
        try:
            payload = {
                "title": title,
                "body": body,
                "icon": icon or "/logo192.png",
                "badge": "/logo192.png",
                "tag": tag or "afromarket-notification",
                "requireInteraction": True,
                "data": {
                    "url": url or "/vendor/notifications",
                    **(data or {})
                }
            }
            
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims=VAPID_CLAIMS
            )
            
            logger.info(f"Push notification sent: {title}")
            return True
            
        except WebPushException as e:
            logger.error(f"Push notification failed: {e}")
            if e.response and e.response.status_code == 410:
                # Subscription expired/invalid
                return None  # Signal to remove subscription
            return False
        except Exception as e:
            logger.error(f"Unexpected push error: {e}")
            return False
    
    @staticmethod
    async def send_to_vendor_subscriptions(db_session, vendor_id: int, 
                                           title: str, body: str, 
                                           notification_type: str,
                                           url: str = None, data: dict = None):
        """Send push notification to all active subscriptions for a vendor"""
        from database import PushSubscription, VendorNotificationPreferences
        from sqlalchemy import select
        
        # Check if vendor has push enabled
        prefs_result = await db_session.execute(
            select(VendorNotificationPreferences).where(
                VendorNotificationPreferences.vendor_id == vendor_id
            )
        )
        prefs = prefs_result.scalar_one_or_none()
        
        if prefs:
            # Check type-specific push preferences
            if notification_type == 'order' and not prefs.push_orders:
                return 0
            elif notification_type == 'message' and not prefs.push_messages:
                return 0
            elif notification_type == 'review' and not prefs.push_reviews:
                return 0
            elif notification_type in ['approval', 'rejection', 'system'] and not prefs.push_admin_alerts:
                return 0
            elif not prefs.push_enabled:
                return 0
        
        # Get all active subscriptions
        result = await db_session.execute(
            select(PushSubscription).where(
                PushSubscription.vendor_id == vendor_id,
                PushSubscription.is_active == True
            )
        )
        subscriptions = result.scalars().all()
        
        sent_count = 0
        expired_subs = []
        
        for sub in subscriptions:
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": sub.p256dh_key,
                    "auth": sub.auth_key
                }
            }
            
            result = await PushNotificationService.send_push(
                subscription_info=subscription_info,
                title=title,
                body=body,
                url=url,
                tag=f"afromarket-{notification_type}-{vendor_id}",
                data=data
            )
            
            if result is True:
                sent_count += 1
                sub.last_used_at = datetime.utcnow()
            elif result is None:
                # Subscription is invalid/expired
                expired_subs.append(sub)
        
        # Remove expired subscriptions
        for sub in expired_subs:
            sub.is_active = False
        
        await db_session.flush()
        
        logger.info(f"Sent {sent_count} push notifications to vendor {vendor_id}")
        return sent_count


class NotificationService:
    """Unified notification service - handles WebSocket, Push, and Email"""
    
    @staticmethod
    async def notify_vendor(db_session, vendor_id: int, notification_type: str,
                           title: str, message: str, link: str = None,
                           data: dict = None, send_email: bool = True):
        """
        Send notification to vendor via all enabled channels:
        1. Create in-app notification
        2. Send via WebSocket if connected
        3. Send push notification if enabled
        4. Send email if enabled in preferences
        """
        from database import VendorNotification, VendorNotificationPreferences, Vendor
        from email_service import email_service
        from sqlalchemy import select
        
        # Get vendor preferences
        prefs_result = await db_session.execute(
            select(VendorNotificationPreferences).where(
                VendorNotificationPreferences.vendor_id == vendor_id
            )
        )
        prefs = prefs_result.scalar_one_or_none()
        
        # Get vendor info for email
        vendor_result = await db_session.execute(
            select(Vendor).where(Vendor.id == vendor_id)
        )
        vendor = vendor_result.scalar_one_or_none()
        
        results = {
            "inapp": False,
            "websocket": False,
            "push": False,
            "email": False
        }
        
        # Check if in-app notification should be created
        should_create_inapp = True
        if prefs:
            if notification_type == 'order' and not prefs.inapp_orders:
                should_create_inapp = False
            elif notification_type == 'message' and not prefs.inapp_messages:
                should_create_inapp = False
            elif notification_type == 'review' and not prefs.inapp_reviews:
                should_create_inapp = False
            elif notification_type in ['approval', 'rejection', 'system'] and not prefs.inapp_admin_alerts:
                should_create_inapp = False
        
        # 1. Create in-app notification
        if should_create_inapp:
            notification = VendorNotification(
                vendor_id=vendor_id,
                type=notification_type,
                title=title,
                message=message,
                link=link,
                data=data or {}
            )
            db_session.add(notification)
            await db_session.flush()
            await db_session.refresh(notification)
            results["inapp"] = True
            
            # 2. Send via WebSocket
            ws_message = {
                "type": "notification",
                "notification": {
                    "id": notification.id,
                    "type": notification_type,
                    "title": title,
                    "message": message,
                    "link": link,
                    "data": data or {},
                    "createdAt": notification.created_at.isoformat(),
                    "isRead": False
                }
            }
            results["websocket"] = await ws_manager.send_to_vendor(vendor_id, ws_message)
        
        # 3. Send push notification
        push_count = await PushNotificationService.send_to_vendor_subscriptions(
            db_session, vendor_id, title, message, notification_type, link, data
        )
        results["push"] = push_count > 0
        
        # 4. Send email notification
        if send_email and vendor:
            should_send_email = True
            if prefs:
                if notification_type == 'order' and not prefs.email_orders:
                    should_send_email = False
                elif notification_type == 'message' and not prefs.email_messages:
                    should_send_email = False
                elif notification_type == 'review' and not prefs.email_reviews:
                    should_send_email = False
                elif notification_type in ['approval', 'rejection', 'system'] and not prefs.email_admin_alerts:
                    should_send_email = False
            
            if should_send_email:
                try:
                    email_service.send_vendor_notification_email(
                        vendor.email, vendor.business_name, 
                        notification_type, title, message, link
                    )
                    results["email"] = True
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")
        
        logger.info(f"Notification sent to vendor {vendor_id}: {results}")
        return results
    
    @staticmethod
    async def notify_order(db_session, vendor_id: int, order_data: dict):
        """Send order notification to vendor"""
        order_id = order_data.get('order_id', 'N/A')
        total = order_data.get('total', 0)
        items_count = order_data.get('items_count', 0)
        buyer_name = order_data.get('buyer_name', 'Customer')
        
        title = f"🛒 New Order #{order_id}!"
        message = f"You have a new order from {buyer_name}. {items_count} item(s) totaling £{total:.2f}. Please process it promptly!"
        
        return await NotificationService.notify_vendor(
            db_session=db_session,
            vendor_id=vendor_id,
            notification_type="order",
            title=title,
            message=message,
            link=f"/vendor/dashboard?tab=orders&order={order_id}",
            data=order_data
        )


# Generate VAPID keys if not set
def generate_vapid_keys():
    """Generate VAPID keys for Web Push"""
    try:
        from py_vapid import Vapid
        vapid = Vapid()
        vapid.generate_keys()
        print("\n=== VAPID Keys Generated ===")
        print(f"Public Key: {vapid.public_key}")
        print(f"Private Key: {vapid.private_key}")
        print("Add these to your .env file:")
        print(f"VAPID_PUBLIC_KEY={vapid.public_key}")
        print(f"VAPID_PRIVATE_KEY={vapid.private_key}")
        print("============================\n")
        return vapid.public_key, vapid.private_key
    except ImportError:
        print("py_vapid not installed. Run: pip install py-vapid")
        return None, None
