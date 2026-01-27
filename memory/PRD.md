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
- [x] Firebase Authentication (Google Sign-In)
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
- [x] Vendor registration
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

### January 27, 2026
1. ✅ **GitHub Code Pull** - Repository cloned and set up
2. ✅ **Database Seeding** - 32 products from 3 vendors
3. ✅ **Environment Configuration** - Backend and frontend .env files
4. ✅ **Stripe Integration** - Test keys configured
5. ✅ **Website Audit** - Comprehensive comparison to Amazon/eBay/Vinted
6. ✅ **Firebase Documentation** - Domain authorization guide created
7. ✅ **All Tests Passed** - 100% backend and frontend tests passing

### Database Status
- **Products:** 32 African grocery items
- **Vendors:** 3 (Mama Nkechi's, Wosiwosi Foods, African Food Warehouse)
- **Categories:** 8 (Fresh, Grains, Condiments, Frozen, Snacks, Drinks, Dried, Beauty)
- **Promo Codes:** 4 (WELCOME10, AFRO20, FREEDELIVERY, NEWCUSTOMER)

---

## Prioritized Backlog

### P0 - Critical (Before Production)
1. [ ] Configure SMTP for email notifications
2. [ ] Add production domain to Firebase authorized domains
3. [ ] Replace Stripe test keys with live keys
4. [ ] Set production CORS origins

### P1 - High Priority (Post-Launch Week 1)
1. [ ] Multiple product images
2. [ ] Image zoom/gallery
3. [ ] Product recommendations
4. [ ] Google Analytics setup

### P2 - Medium Priority (Month 1)
1. [ ] Search autocomplete
2. [ ] Recently viewed products
3. [ ] Stock alerts
4. [ ] Push notifications

### P3 - Low Priority (Future)
1. [ ] Multi-language support
2. [ ] Dark mode
3. [ ] Gift cards
4. [ ] Price alerts

---

## Technical Stack

### Frontend
- React 19
- Tailwind CSS
- Shadcn/UI components
- Axios for API calls
- React Router v7

### Backend
- FastAPI (Python)
- SQLAlchemy + SQLite
- MongoDB (optional)
- JWT authentication
- Stripe SDK

### Infrastructure
- Preview: Emergent Platform
- Database: SQLite/MongoDB
- Payments: Stripe
- Auth: Firebase + JWT

---

## Files Modified/Created (Jan 27, 2026)
- `/app/backend/.env` - Created
- `/app/frontend/.env` - Created with Stripe key
- `/app/WEBSITE_AUDIT_REPORT_UPDATED.md` - Comprehensive audit
- `/app/FIREBASE_DOMAIN_FIX.md` - Firebase configuration guide
- `/app/memory/PRD.md` - This document

---

## Next Session Tasks
1. Configure SMTP for transactional emails
2. Help user add Firebase authorized domain
3. Implement multiple product images
4. Add image zoom functionality
5. Set up Google Analytics
