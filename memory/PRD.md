# AfroMarket UK - PRD

## Original Problem Statement
Pull code from GitHub repository: https://github.com/sotubo969/mine

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
- Vendor advertising system
- Stripe payment integration
- Email notifications (SMTP)
- Password reset flow
- SEO optimizations (robots.txt, sitemap, meta tags)
- PWA (Progressive Web App)

## Status: Codebase Pulled Successfully
- Repository cloned: ✅
- Backend running: ✅ (port 8001)
- Frontend running: ✅ (port 3000)
- Environment files created: ✅

## Environment Variables Required
- STRIPE_SECRET_KEY, STRIPE_PUBLISHABLE_KEY
- PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
- SMTP_USER, SMTP_PASSWORD (for email)
- EMERGENT_LLM_KEY (for AfroBot)

## Next Steps
1. Configure Stripe live keys
2. Configure email SMTP credentials
3. Complete Vendor Wallet System implementation
