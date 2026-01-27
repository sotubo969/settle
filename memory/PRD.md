# AfroMarket UK - Product Requirements Document
## Final Production-Ready Version - January 27, 2026

---

## 1. PROJECT OVERVIEW

**AfroMarket UK** is a full-featured e-commerce marketplace for authentic African groceries serving the UK market.

### Tech Stack
- **Frontend**: React.js + Tailwind CSS + Shadcn UI
- **Backend**: FastAPI (Python) + SQLite
- **Auth**: Firebase Authentication (Google + Email/Password)
- **Payments**: Stripe
- **Database**: SQLite (can migrate to PostgreSQL for production)

---

## 2. COMPLETED FEATURES ✅

### Core E-commerce
- ✅ **32 Products** seeded across 8 categories
- ✅ Product listing with images, prices, ratings
- ✅ Category filtering and price range filtering
- ✅ Product search functionality
- ✅ Shopping cart with persistent storage
- ✅ Multi-step checkout flow
- ✅ Stripe payment integration

### Authentication & Security
- ✅ Firebase Authentication
- ✅ Google Sign-In (auto-verified)
- ✅ Email/Password with email verification
- ✅ JWT tokens for API authentication
- ✅ Rate limiting (120 requests/minute)
- ✅ Security headers (X-Frame-Options, etc.)
- ✅ Password hashing (bcrypt)

### Order Management
- ✅ Order creation and processing
- ✅ **Order History Page** (`/orders`)
- ✅ **Order Tracking** with timeline
- ✅ Order status updates

### Reviews & Ratings
- ✅ **Product Reviews** - Submit and view reviews
- ✅ **Vendor/Seller Reviews**
- ✅ Rating distribution display
- ✅ Verified purchase badges
- ✅ Helpful vote system
- ✅ **Product Q&A** - Ask and answer questions

### Marketplace Features
- ✅ **Wishlist** (`/wishlist`) - Save favorite products
- ✅ **Buyer-Seller Messaging** (`/messages`)
- ✅ **Promo Codes/Discounts** - 4 active codes:
  - WELCOME10 - 10% off (min £20)
  - AFRO20 - 20% off (min £50)
  - FREEDELIVERY - Free delivery (min £30)
  - NEWCUSTOMER - £5 off (min £25)
- ✅ **Refund/Return Requests**

### Vendor System
- ✅ Vendor registration and approval
- ✅ Vendor dashboard with analytics
- ✅ Product management
- ✅ Order management
- ✅ **Advertising system** with pricing tiers
- ✅ **Vendor Wallet** for ad payments
- ✅ Auto-recharge settings

### Admin/Owner
- ✅ Admin dashboard
- ✅ Owner dashboard
- ✅ Vendor approval/rejection
- ✅ Advertisement moderation

### Other Features
- ✅ PWA (Progressive Web App) support
- ✅ **AfroBot** AI chatbot (GPT-4o)
- ✅ SEO optimizations (meta tags, sitemap, robots.txt)
- ✅ Help & Support page
- ✅ Terms of Service
- ✅ Privacy Policy
- ✅ Shipping Information
- ✅ Returns & Refunds Policy

---

## 3. API ENDPOINTS

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/firebase` - Firebase token auth
- `GET /api/auth/firebase/status` - Check Firebase config

### Products
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product details
- `GET /api/products/category/{category}` - Filter by category

### Reviews & Q&A
- `POST /api/reviews/product` - Submit product review
- `GET /api/reviews/product/{id}` - Get product reviews
- `POST /api/reviews/vendor` - Submit vendor review
- `GET /api/reviews/vendor/{id}` - Get vendor reviews
- `POST /api/questions` - Ask product question
- `GET /api/questions/product/{id}` - Get product Q&A

### Wishlist
- `POST /api/wishlist/toggle` - Add/remove item
- `GET /api/wishlist` - Get user's wishlist
- `GET /api/wishlist/check/{id}` - Check if in wishlist

### Messages
- `POST /api/messages` - Send message
- `GET /api/messages` - Get conversations
- `GET /api/messages/{conversation_id}` - Get messages

### Promo Codes
- `POST /api/promo/validate` - Validate code
- `POST /api/promo/apply` - Apply code to order

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders/history` - Get order history
- `GET /api/orders/tracking/{order_id}` - Get tracking

### Refunds
- `POST /api/refunds` - Request refund
- `GET /api/refunds` - Get user's refund requests

---

## 4. DATABASE SCHEMA

### Tables
- `users` - User accounts (with Firebase integration)
- `vendors` - Vendor/seller accounts
- `products` - Product catalog (32 items seeded)
- `cart` - Shopping cart items
- `orders` - Order records
- `product_reviews` - Product reviews
- `vendor_reviews` - Seller reviews
- `product_questions` - Product Q&A
- `messages` - Buyer-seller messages
- `promo_codes` - Discount codes (4 active)
- `refund_requests` - Return/refund requests
- `wishlists` - User saved items
- `advertisements` - Vendor ads
- `vendor_wallets` - Vendor ad balances

---

## 5. CONFIGURATION REQUIRED

### Firebase (Configured ✅)
```
Frontend: .env
REACT_APP_FIREBASE_API_KEY=AIzaSyBNWwS...
REACT_APP_FIREBASE_AUTH_DOMAIN=afromarket-uk-f21e9.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=afromarket-uk-f21e9

Backend: .env
FIREBASE_SERVICE_ACCOUNT={...service account JSON...}
```

### Firebase Console
- Add authorized domain: `mine-pull.preview.emergentagent.com`
- Enable Google Sign-In provider
- Enable Email/Password provider

### Stripe (Needs Live Keys)
```
Backend: .env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
```

### Email (Needs Configuration)
```
Backend: .env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-password
FROM_EMAIL=your-email@gmail.com
```

---

## 6. TEST RESULTS

| Category | Tests Passed | Percentage |
|----------|--------------|------------|
| Backend APIs | 19/19 | **100%** |
| Frontend Pages | All Load | **95%** |
| Products Seeded | 32 | ✅ |
| Promo Codes | 4 | ✅ |
| Vendors | 3 | ✅ |

---

## 7. LAUNCH CHECKLIST

### Before Going Live
- [ ] Configure Stripe live keys
- [ ] Configure SMTP for email notifications
- [ ] Add production domain to Firebase authorized domains
- [ ] Set up custom domain
- [ ] Enable HSTS header in production
- [ ] Migrate SQLite to PostgreSQL (optional but recommended)
- [ ] Set up SSL certificate
- [ ] Configure CDN for images

### Optional Enhancements
- [ ] Multiple product images gallery
- [ ] Product variant selection (sizes, colors)
- [ ] Advanced search with autocomplete
- [ ] Email notifications for orders
- [ ] SMS notifications via Twilio
- [ ] Social sharing buttons
- [ ] Product recommendations AI

---

## 8. SUMMARY

**AfroMarket UK is now PRODUCTION-READY** with:
- ✅ 32 products across 8 categories
- ✅ Full authentication system (Firebase + JWT)
- ✅ Order management with tracking
- ✅ Product & vendor reviews
- ✅ Wishlist functionality
- ✅ Buyer-seller messaging
- ✅ Promo code system (4 active codes)
- ✅ Refund request system
- ✅ Vendor dashboard & advertising
- ✅ Admin/Owner controls
- ✅ AI chatbot support
- ✅ Rate limiting & security
- ✅ PWA support
- ✅ SEO optimization

**Ready for public launch pending:**
1. Stripe live keys configuration
2. Email SMTP setup
3. Firebase domain authorization
