# AfroMarket UK - PRD

## Original Problem Statement
Pull code from GitHub repository: https://github.com/sotubo969/mine
Continue Vendor Wallet System implementation
Enhance authentication with Firebase Authentication

## Project Overview
AfroMarket UK is a comprehensive e-commerce marketplace for authentic African groceries in the UK.

## Tech Stack
- **Frontend**: React.js with Tailwind CSS, Shadcn UI components
- **Backend**: FastAPI (Python) with SQLite database
- **Auth**: Firebase Authentication (with legacy JWT fallback)
- **Features**: PWA support, Stripe payments, Email notifications

## What's Implemented

### Core Features
- Full e-commerce platform with product listings
- Shopping cart and checkout
- Vendor registration and dashboard
- Owner/Admin dashboards
- AfroBot AI chatbot (GPT-4o)
- Vendor advertising system (fixed pricing)
- Stripe payment integration
- Email notifications (SMTP)
- Password reset flow
- SEO optimizations (robots.txt, sitemap, meta tags)
- PWA (Progressive Web App)

### Authentication System (Completed - Jan 26, 2026)
**Firebase Authentication:**
- Google Sign-In via Firebase (auto-verified, no email confirmation) ✅
- Email/Password with Firebase email verification ✅
- Backend Firebase token verification (`/api/auth/firebase`) ✅
- Firebase status check endpoint (`/api/auth/firebase/status`) ✅
- Graceful fallback to legacy JWT auth when Firebase not configured ✅

**Verification Logic:**
- Google users → always verified ✅
- Email users → must verify email first ✅
- Unverified users blocked from checkout ✅
- Session persistence via Firebase + localStorage ✅

**Database Schema Updated:**
- `firebase_uid` - Firebase user ID
- `auth_provider` - 'email', 'google', 'apple', 'firebase'
- `email_verified` - Boolean verification status

### Vendor Wallet System (Completed - Jan 26, 2026)
- `GET /api/wallet` - Wallet balance and info ✅
- `POST /api/wallet/topup` - Stripe payment intent ✅
- `POST /api/wallet/confirm-topup` - Confirm top-up ✅
- `POST /api/wallet/setup-auto-recharge` - Auto-recharge settings ✅
- `GET /api/wallet/transactions` - Transaction history ✅
- Frontend `/vendor/wallet` page ✅

## Configuration Required

### Firebase Setup (Required for Google Sign-In)
Frontend (`/app/frontend/.env`):
```
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
```

Backend (`/app/backend/.env`):
```
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}
# OR
FIREBASE_SERVICE_ACCOUNT_PATH=firebase-admin.json
```

### Other Configuration
- STRIPE_SECRET_KEY, REACT_APP_STRIPE_PUBLISHABLE_KEY
- SMTP credentials for email

## Next Steps
1. Configure Firebase credentials from Firebase Console
2. Add authorized domains in Firebase (Google Sign-In)
3. Test Firebase email verification flow
4. Implement pay-per-performance ad billing
