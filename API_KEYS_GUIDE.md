# AfroMarket UK - API Keys Configuration Guide

## 🚀 Quick Start

Your AfroMarket UK application is now running with **SQL database (SQLite)** and ready for payment + OAuth integrations!

## 📝 Where to Add Your API Keys

All API keys should be added to `/app/backend/.env` file.

### Current Status:
- ✅ **Database**: SQLite (production-ready, can migrate to MySQL anytime)
- ✅ **Backend API**: Fully functional
- ✅ **Frontend**: Complete UI with mock data
- ⏳ **Integrations**: Waiting for your API keys

---

## 1️⃣ Stripe Integration (Payment + Apple Pay)

**File:** `/app/backend/.env`

```env
# Get keys from: https://dashboard.stripe.com/apikeys
STRIPE_PUBLISHABLE_KEY="pk_test_YOUR_KEY_HERE"  # Replace with your publishable key
STRIPE_SECRET_KEY="sk_test_YOUR_KEY_HERE"       # Replace with your secret key
STRIPE_WEBHOOK_SECRET="whsec_YOUR_SECRET_HERE"   # For webhooks (optional)
```

**How to get Stripe keys:**
1. Go to https://dashboard.stripe.com/register
2. Complete registration
3. Navigate to Developers → API keys
4. Copy Publishable key and Secret key
5. Paste them in `.env` file

**Apple Pay:** Works automatically through Stripe once Stripe keys are added! No separate Apple Pay keys needed.

---

## 2️⃣ PayPal Integration

**File:** `/app/backend/.env`

```env
# Get keys from: https://developer.paypal.com/dashboard/applications
PAYPAL_CLIENT_ID="YOUR_PAYPAL_CLIENT_ID_HERE"        # Replace with your client ID
PAYPAL_CLIENT_SECRET="YOUR_PAYPAL_CLIENT_SECRET_HERE" # Replace with your secret
PAYPAL_MODE="sandbox"  # Use "live" for production
```

**How to get PayPal keys:**
1. Go to https://developer.paypal.com/dashboard/
2. Create an app
3. Get Client ID and Secret from app credentials
4. Paste them in `.env` file

---

## 3️⃣ Google OAuth (Sign in with Google)

**File:** `/app/backend/.env`

```env
# Get keys from: https://console.cloud.google.com/apis/credentials
GOOGLE_CLIENT_ID="YOUR_CLIENT_ID.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
GOOGLE_REDIRECT_URI="https://sourcecode-fetch.preview.emergentagent.com/api/auth/google/callback"
```

**How to get Google OAuth keys:**
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable Google+ API
4. Go to Credentials → Create Credentials → OAuth 2.0 Client ID
5. Application type: Web application
6. Add authorized redirect URI: `https://sourcecode-fetch.preview.emergentagent.com/api/auth/google/callback`
7. Copy Client ID and Client Secret
8. Paste them in `.env` file

---

## 4️⃣ Apple Sign In (Sign in with Apple)

**File:** `/app/backend/.env`

```env
# Get keys from: https://developer.apple.com/account/resources/identifiers/list/serviceId
APPLE_SERVICE_ID="com.yourcompany.afromarket"
APPLE_TEAM_ID="YOUR_TEAM_ID_HERE"
APPLE_KEY_ID="YOUR_KEY_ID_HERE"
```

**Additional file needed:** `/app/backend/apple_private_key.p8`

**How to get Apple Sign In credentials:**
1. Go to https://developer.apple.com/account/
2. Requires Apple Developer Program membership ($99/year)
3. Create an App ID
4. Create a Services ID
5. Create a Sign in with Apple Key
6. Download the .p8 private key file
7. Place it at `/app/backend/apple_private_key.p8`
8. Copy Service ID, Team ID, and Key ID to `.env`

**Note:** Apple Sign In requires a paid Apple Developer account. You can skip this for now and add it later.

---

## ✅ After Adding Keys

1. **Restart the backend:**
   ```bash
   sudo supervisorctl restart backend
   ```

2. **Test the integrations:**
   - Go to your application
   - Try signing in with Google
   - Try making a payment with Stripe/PayPal
   - Try Apple Pay (if Stripe is configured)

---

## 🗄️ Database Information

### Current Setup: SQLite
- **File:** `/app/backend/afromarket.db`
- **Status:** Production-ready, automatically created
- **Pros:** Zero configuration, fast, perfect for MVP
- **Data:** 12 products, 5 vendors already seeded

### Migrating to MySQL (Optional)

When you want to use MySQL instead:

1. Install MySQL (if not installed)
2. Create database:
   ```sql
   CREATE DATABASE afromarket;
   CREATE USER 'afromarket'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON afromarket.* TO 'afromarket'@'localhost';
   ```

3. Update `.env`:
   ```env
   DATABASE_URL="mysql+aiomysql://afromarket:your_password@localhost/afromarket"
   ```

4. Restart backend:
   ```bash
   sudo supervisorctl restart backend
   ```

5. Run seed script:
   ```bash
   cd /app/backend && python seed_sql_data.py
   ```

---

## 📊 API Endpoints

All endpoints are prefixed with `/api`:

### Authentication
- `POST /api/auth/register` - Register with email
- `POST /api/auth/login` - Login with email
- `POST /api/auth/google` - Sign in with Google
- `POST /api/auth/apple` - Sign in with Apple
- `GET /api/auth/me` - Get current user

### Products
- `GET /api/products` - Get all products (with filters)
- `GET /api/products/:id` - Get product details

### Cart
- `GET /api/cart` - Get user cart
- `POST /api/cart/add` - Add to cart
- `DELETE /api/cart/clear` - Clear cart

### Orders
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user orders

### Payments
- `POST /api/payment/stripe/create-intent` - Create Stripe payment
- `POST /api/payment/stripe/confirm/:id` - Confirm payment
- `POST /api/payment/stripe/apple-pay` - Process Apple Pay
- `POST /api/payment/paypal/create` - Create PayPal payment
- `POST /api/payment/paypal/execute` - Execute PayPal payment

### Vendors
- `POST /api/vendors/register` - Register as vendor
- `GET /api/vendors` - Get all vendors

---

## 🔐 Security Notes

1. **Never commit `.env` file to Git**
2. **Use test/sandbox keys for development**
3. **Switch to production keys only when going live**
4. **Regenerate keys if they're exposed**
5. **Keep your private keys secure**

---

## 🆘 Need Help?

### Testing without real keys:
The application will work with placeholder keys, but payment/OAuth features will show errors. Add real keys when ready to test those features.

### Common Issues:

**"Invalid Stripe key"**
→ Make sure you're using test keys (pk_test_... and sk_test_...)

**"Google OAuth error"**
→ Check that redirect URI matches exactly in Google Console

**"PayPal error"**
→ Ensure you're using sandbox credentials with PAYPAL_MODE="sandbox"

---

## 📞 Support

If you need help:
1. Check the error logs: `tail -f /var/log/supervisor/backend.err.log`
2. Verify your keys are correctly formatted in `.env`
3. Restart backend after changing keys
4. Test with curl or Postman first before testing in browser

---

**🎉 Your marketplace is ready! Add your API keys to unlock all features.**
