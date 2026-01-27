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
- [x] Product management
- [x] Order management
- [x] Sales analytics
- [x] Advertising wallet

### Admin Features
- [x] Admin dashboard
- [x] User management
- [x] Vendor approval
- [x] Order oversight
- [x] Analytics

---

## What's Been Implemented

### January 27, 2026 - Session 2
1. ✅ **Vendor Email Notifications** - Admin receives email when vendor registers
2. ✅ **Firebase Google Sign-In** - Configured with user's Firebase project
3. ✅ **SMTP Email Service** - Gmail SMTP configured and working
4. ✅ **Public Vendor Registration** - Non-authenticated vendor registration endpoint
5. ✅ **Google Sign-In on Vendor Form** - Pre-fill email from Google account
6. ✅ **Approval Instructions** - Documentation for vendor approval process

### January 27, 2026 - Session 1
1. ✅ **GitHub Code Pull** - Repository cloned and set up
2. ✅ **Database Seeding** - 32 products from 3 vendors
3. ✅ **Environment Configuration** - Backend and frontend .env files
4. ✅ **Stripe Integration** - Test keys configured
5. ✅ **Website Audit** - Comprehensive comparison to Amazon/eBay/Vinted

### Database Status
- **Products:** 32 African grocery items
- **Vendors:** 4+ (including test registrations)
- **Categories:** 8 (Fresh, Grains, Condiments, Frozen, Snacks, Drinks, Dried, Beauty)

---

## Configuration Status

| Service | Status | Details |
|---------|--------|---------|
| SMTP Email | ✅ Working | Gmail SMTP with app password |
| Firebase Auth | ✅ Configured | Google Sign-In enabled |
| Stripe | ⚠️ Test Mode | Using test keys |
| Database | ✅ Seeded | SQLite with 32 products |

---

## Prioritized Backlog

### P0 - Critical (Completed ✅)
1. [x] Vendor email notifications
2. [x] Firebase Google Sign-In
3. [x] Vendor approval workflow documentation

### P1 - Production Ready
1. [ ] Replace Stripe test keys with live keys
2. [ ] Add production domain to Firebase authorized domains
3. [ ] Set production CORS origins

### P2 - Enhancements
1. [ ] Multiple product images
2. [ ] Image zoom/gallery
3. [ ] Product recommendations
4. [ ] Google Analytics setup

### P3 - Future
1. [ ] Multi-language support
2. [ ] Push notifications
3. [ ] Price alerts

---

## Technical Stack

### Frontend
- React 19
- Tailwind CSS
- Shadcn/UI components
- Firebase SDK (Google Sign-In)

### Backend
- FastAPI (Python)
- SQLAlchemy + SQLite
- JWT + Firebase Authentication
- Gmail SMTP for emails

### Infrastructure
- Preview: Emergent Platform
- Email: Gmail SMTP
- Auth: Firebase + JWT
- Payments: Stripe

---

## Key Files

### Email & Auth
- `/app/backend/email_service.py` - SMTP email service
- `/app/backend/firebase_auth.py` - Firebase Admin SDK
- `/app/frontend/src/lib/firebase.js` - Firebase client config
- `/app/frontend/src/context/AuthContext.js` - Auth state management

### Vendor Registration
- `/app/frontend/src/pages/VendorRegister.js` - Vendor form with Google Sign-In
- `/app/backend/server.py` - Vendor registration endpoints

### Documentation
- `/app/VENDOR_APPROVAL_INSTRUCTIONS.md` - How to approve vendors
- `/app/FIREBASE_DOMAIN_FIX.md` - Firebase configuration guide
- `/app/WEBSITE_AUDIT_REPORT_UPDATED.md` - Comprehensive audit

---

## Next Session Tasks
1. Test Google Sign-In on production domain
2. Set up email templates with better branding
3. Add order notification emails
4. Configure Google Analytics
