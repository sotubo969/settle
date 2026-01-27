# AfroMarket UK - Product Requirements Document

## Project Overview
**Name:** AfroMarket UK  
**Type:** E-commerce marketplace for African groceries  
**Target Market:** UK customers seeking authentic African food products  
**GitHub Source:** https://github.com/sotubo969/last_bit

---

## User Personas

### 1. Customer (Shopper)
- UK residents seeking authentic African groceries
- Nigerian, Ghanaian, Kenyan diaspora communities
- Food enthusiasts interested in African cuisine

### 2. Vendor (Seller)
- African grocery store owners
- Food importers/distributors
- Local producers of African products

### 3. Admin/Owner
- Platform administrators
- Customer service representatives

---

## Core Requirements (Static)

### Authentication
- [x] Email/Password registration and login
- [x] Firebase Authentication (Google Sign-In) ✅ CONFIGURED
- [x] JWT token-based session management
- [x] Password reset functionality
- [x] Email verification

### Product Management
- [x] Product catalog with categories
- [x] Product search and filtering
- [x] Product detail pages
- [x] Stock management
- [x] Featured products

### Shopping Experience
- [x] Shopping cart
- [x] Wishlist
- [x] Checkout flow
- [x] Stripe payment integration
- [x] Order confirmation

### Vendor Features
- [x] Vendor registration with email notification ✅ WORKING
- [x] Vendor dashboard
- [x] **Real-time notifications** ✅ NEW
- [x] Product management
- [x] Order management
- [x] Sales analytics
- [x] Advertising wallet

### Admin Features
- [x] Admin dashboard
- [x] User management
- [x] **Vendor approval with notifications** ✅ ENHANCED
- [x] Order oversight
- [x] Analytics

---

## What's Been Implemented

### January 27, 2026 - Session 3 (Notification System)
1. ✅ **VendorNotification Database Model** - Stores notifications in SQLite
2. ✅ **Notification API Endpoints**:
   - `GET /api/vendor/notifications` - Get vendor's notifications
   - `GET /api/vendor/notifications/by-email/{email}` - Get by email (no auth)
   - `PUT /api/vendor/notifications/{id}/read` - Mark as read
   - `PUT /api/vendor/notifications/mark-all-read` - Mark all read
3. ✅ **Enhanced Vendor Approval** - Creates notification + sends email
4. ✅ **VendorNotifications Component** - Bell icon with dropdown, polling every 30s
5. ✅ **VendorNotificationsPage** - Full notifications management page
6. ✅ **Dashboard Integration** - Notification bell in vendor dashboard header

### January 27, 2026 - Session 2
1. ✅ **Vendor Email Notifications** - Admin receives email when vendor registers
2. ✅ **Firebase Google Sign-In** - Configured with user's Firebase project
3. ✅ **SMTP Email Service** - Gmail SMTP configured and working
4. ✅ **Public Vendor Registration** - Non-authenticated vendor registration endpoint

### January 27, 2026 - Session 1
1. ✅ **GitHub Code Pull** - Repository cloned and set up
2. ✅ **Database Seeding** - 32 products from 3 vendors
3. ✅ **Environment Configuration** - Backend and frontend .env files
4. ✅ **Website Audit** - Comprehensive comparison to Amazon/eBay/Vinted

---

## Notification System Architecture

### Flow
```
1. Vendor Registers → Admin receives email notification
2. Admin Reviews in Owner Dashboard → Clicks Approve/Reject
3. System Creates:
   - In-app notification (stored in VendorNotification table)
   - Email notification (sent via SMTP)
4. Vendor sees notification:
   - Bell icon shows unread count
   - Click opens dropdown with notifications
   - Click notification → marked as read, redirects to link
```

### Notification Types
- `approval` - Vendor application approved
- `rejection` - Vendor application rejected
- `order` - New order received (future)
- `message` - New message received (future)
- `system` - System announcements (future)

### Polling Interval
- Frontend polls every 30 seconds for new notifications
- Can be upgraded to WebSockets for true real-time

---

## Configuration Status

| Service | Status | Details |
|---------|--------|---------|
| SMTP Email | ✅ Working | Gmail SMTP with app password |
| Firebase Auth | ✅ Configured | Google Sign-In enabled |
| Notifications | ✅ Working | SQLite + polling |
| Stripe | ⚠️ Test Mode | Using test keys |
| Database | ✅ Seeded | SQLite with 32 products |

---

## Key Files

### Notification System
- `/app/backend/database.py` - VendorNotification model
- `/app/backend/server.py` - Notification endpoints
- `/app/frontend/src/components/VendorNotifications.js` - Bell component
- `/app/frontend/src/pages/VendorNotificationsPage.js` - Full page

### Email & Auth
- `/app/backend/email_service.py` - SMTP email service
- `/app/backend/firebase_auth.py` - Firebase Admin SDK
- `/app/frontend/src/lib/firebase.js` - Firebase client config

### Vendor Management
- `/app/frontend/src/pages/VendorRegister.js` - Registration form
- `/app/frontend/src/pages/VendorDashboard.js` - Dashboard with bell

---

## Prioritized Backlog

### P0 - Critical (Completed ✅)
1. [x] Vendor email notifications
2. [x] Firebase Google Sign-In
3. [x] Real-time in-app notifications
4. [x] Vendor approval workflow

### P1 - Production Ready
1. [ ] Replace Stripe test keys with live keys
2. [ ] Add production domain to Firebase authorized domains
3. [ ] Set production CORS origins

### P2 - Enhancements
1. [ ] WebSocket for true real-time notifications
2. [ ] Order notifications for vendors
3. [ ] Push notifications (PWA)
4. [ ] Multiple product images

### P3 - Future
1. [ ] Multi-language support
2. [ ] Dark mode
3. [ ] SMS notifications

---

## Testing Summary

### Session 3 Test Results
- Backend: 88.2% pass rate
- Frontend: 85% pass rate
- Overall: 87% pass rate

### Passed Tests
- Vendor registration creates vendor in database
- Admin vendor approval creates notification and sends email
- Vendor notifications endpoints work correctly
- Full workflow: register → approve → notification created
- Frontend security: proper redirects for unauthenticated users

---

## Next Session Tasks
1. Upgrade to WebSockets for real-time notifications
2. Add order notifications for vendors
3. Implement push notifications via PWA
4. Add notification preferences settings
