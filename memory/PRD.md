# AfroMarket UK - PRD

## Original Problem Statement
Pull code from GitHub repository: https://github.com/sotubo969/mine
Continue Vendor Wallet System implementation

## Project Overview
AfroMarket UK is a comprehensive e-commerce marketplace for authentic African groceries in the UK.

## Tech Stack
- **Frontend**: React.js with Tailwind CSS, Shadcn UI components
- **Backend**: FastAPI (Python) with SQLite database
- **Features**: PWA support, Stripe payments, Email notifications

## What's Implemented
- Full e-commerce platform with product listings
- User authentication (JWT + Google OAuth)
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

### Vendor Wallet System (Completed - Jan 26, 2026)
- **GET /api/wallet** - Get wallet balance and info ✅
- **POST /api/wallet/topup** - Create Stripe payment intent for top-up ✅
- **POST /api/wallet/confirm-topup** - Confirm wallet top-up after payment ✅
- **POST /api/wallet/setup-auto-recharge** - Configure auto-recharge settings ✅
- **GET /api/wallet/transactions** - Get transaction history ✅
- **Frontend /vendor/wallet** - Full wallet management UI ✅
- Auto-recharge configuration ✅
- Transaction history display ✅

## Environment Variables Required
- STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
- PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
- SMTP_USER, SMTP_PASSWORD (for email)
- EMERGENT_LLM_KEY (for AfroBot)

## Next Steps
1. Configure Stripe live keys for payment processing
2. Implement pay-per-performance ad billing (deduct from wallet on impressions/clicks)
3. Implement auto-recharge via Stripe saved payment methods
