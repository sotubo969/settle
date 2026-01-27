# AfroMarket UK - Product Requirements Document

## Project Overview
**Name:** AfroMarket UK  
**Type:** E-commerce marketplace for African groceries  
**Target Market:** UK customers seeking authentic African food products  
**GitHub Source:** https://github.com/sotubo969/last_bit

---

## What's Been Implemented

### January 27, 2026 - Session 4 (Real-Time Notifications)
1. ✅ **WebSocket Notifications** - Real-time updates via WebSocket (`/ws/vendor/{vendor_id}`)
2. ✅ **PWA Push Notifications** - Browser push notifications with VAPID keys
3. ✅ **Order Notifications** - Vendors receive instant notifications when orders placed
4. ✅ **Notification Preferences** - Full control over email/in-app/push notifications
5. ✅ **Notification Settings Page** - `/vendor/notifications/settings` for preference management

### Session 3 - Notification System
- VendorNotification database model
- Basic notification endpoints
- In-app notification bell

### Session 2 - Email & Auth
- Vendor email notifications (SMTP)
- Firebase Google Sign-In
- Public vendor registration

### Session 1 - Initial Setup
- GitHub code pull
- Database seeding (32 products)
- Environment configuration

---

## Notification System Architecture

### Channels
1. **WebSocket** - Real-time in-app updates
   - Endpoint: `wss://domain/ws/vendor/{vendor_id}`
   - Auto-reconnect with exponential backoff
   - Ping/pong heartbeat every 30s

2. **PWA Push** - Browser notifications
   - Works even when browser is closed
   - VAPID authentication
   - Service worker: `/sw-push.js`

3. **Email** - Traditional email notifications
   - Gmail SMTP configured
   - HTML templates for each type

4. **In-App** - Dashboard notifications
   - Bell icon with unread count
   - Notification panel with types

### Notification Types
- `order` - New order placed
- `approval` - Vendor approved
- `rejection` - Vendor rejected
- `message` - Customer message
- `review` - Product review
- `system` - Admin alerts

### Preferences Schema
```json
{
  "email": {
    "orders": true,
    "messages": true,
    "reviews": true,
    "adminAlerts": true,
    "marketing": false
  },
  "inapp": {
    "orders": true,
    "messages": true,
    "reviews": true,
    "adminAlerts": true,
    "marketing": true
  },
  "push": {
    "enabled": true,
    "orders": true,
    "messages": true,
    "reviews": false,
    "adminAlerts": true
  }
}
```

---

## API Endpoints

### WebSocket
- `WS /ws/vendor/{vendor_id}` - Real-time notifications

### Notification Preferences
- `GET /api/vendor/notifications/preferences` - Get preferences
- `PUT /api/vendor/notifications/preferences` - Update preferences

### Push Notifications
- `GET /api/push/vapid-key` - Get VAPID public key
- `POST /api/vendor/push/subscribe` - Subscribe to push
- `DELETE /api/vendor/push/unsubscribe` - Unsubscribe from push
- `POST /api/vendor/push/test` - Send test push

### Status
- `GET /api/ws/status` - WebSocket connection status

---

## Configuration Status

| Service | Status | Details |
|---------|--------|---------|
| WebSocket | ✅ Working | Real-time via FastAPI |
| PWA Push | ✅ Configured | VAPID keys generated |
| SMTP Email | ✅ Working | Gmail SMTP |
| Firebase | ✅ Configured | Google Sign-In |
| Stripe | ⚠️ Test Mode | Using test keys |

---

## Key Files

### Backend
- `/app/backend/notification_service.py` - WebSocket manager & push service
- `/app/backend/database.py` - VendorNotificationPreferences, PushSubscription models
- `/app/backend/server.py` - WebSocket endpoint, preference APIs

### Frontend
- `/app/frontend/src/hooks/useWebSocket.js` - WebSocket connection hook
- `/app/frontend/src/hooks/usePushNotifications.js` - Push notification hook
- `/app/frontend/src/components/VendorNotifications.js` - Notification bell
- `/app/frontend/src/pages/VendorNotificationSettings.js` - Settings page
- `/app/frontend/public/sw-push.js` - Service worker for push

---

## Test Results

### Session 4
- Backend: 96.2% pass rate
- Frontend: 75% pass rate
- Note: Frontend requires vendor approval workflow for dashboard access

### Passed Tests
- WebSocket status endpoint
- VAPID key endpoint
- Notification preferences GET/PUT
- Push subscription endpoint
- Admin vendor approval creates notification
- Order notifications sent on order creation
- Email notification preferences
- In-app notification preferences

---

## Prioritized Backlog

### P0 - Completed ✅
1. [x] WebSocket real-time notifications
2. [x] PWA push notifications
3. [x] Order notifications for vendors
4. [x] Notification preferences

### P1 - Production Ready
1. [ ] Replace Stripe test keys with live keys
2. [ ] Add production domain to Firebase
3. [ ] SSL/TLS for WebSocket in production

### P2 - Enhancements
1. [ ] Message notifications for buyer-seller chat
2. [ ] Review notifications
3. [ ] Low stock alerts for vendors
4. [ ] Daily/weekly summary emails

### P3 - Future
1. [ ] Mobile app push notifications
2. [ ] SMS notifications via Twilio
3. [ ] Webhook integrations

---

## Next Session Tasks
1. Test full order -> notification flow with real user
2. Add review notifications
3. Implement message notifications for chat
4. Add notification sound toggle
