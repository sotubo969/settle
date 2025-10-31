# AfroMarket UK - API Contracts & Integration Plan

## Overview
This document outlines the API contracts and integration strategy for the African grocery marketplace platform.

## 1. Data Models

### User Model
```python
{
    "_id": ObjectId,
    "name": str,
    "email": str (unique),
    "password": str (hashed),
    "role": str (enum: "customer", "vendor", "admin"),
    "avatar": str (optional),
    "phone": str (optional),
    "addresses": [
        {
            "fullName": str,
            "address": str,
            "city": str,
            "postcode": str,
            "phone": str,
            "isDefault": bool
        }
    ],
    "createdAt": datetime,
    "updatedAt": datetime
}
```

### Vendor Model
```python
{
    "_id": ObjectId,
    "userId": ObjectId (ref: User),
    "businessName": str,
    "description": str,
    "email": str,
    "phone": str,
    "address": str,
    "city": str,
    "postcode": str,
    "location": str,
    "verified": bool,
    "rating": float,
    "totalSales": int,
    "commission": float (default: 1.0),
    "status": str (enum: "pending", "approved", "rejected"),
    "createdAt": datetime,
    "updatedAt": datetime
}
```

### Product Model
```python
{
    "_id": ObjectId,
    "name": str,
    "brand": str,
    "description": str,
    "price": float,
    "originalPrice": float (optional),
    "image": str (URL),
    "images": [str],
    "category": str,
    "categoryId": int,
    "vendorId": ObjectId (ref: Vendor),
    "vendor": {
        "name": str,
        "rating": float,
        "location": str
    },
    "rating": float,
    "reviews": int,
    "stock": int,
    "weight": str,
    "inStock": bool,
    "featured": bool,
    "createdAt": datetime,
    "updatedAt": datetime
}
```

### Order Model
```python
{
    "_id": ObjectId,
    "orderId": str (unique, format: ORD-YYYY-####),
    "userId": ObjectId (ref: User),
    "items": [
        {
            "productId": ObjectId (ref: Product),
            "name": str,
            "brand": str,
            "image": str,
            "price": float,
            "quantity": int,
            "vendorId": ObjectId (ref: Vendor),
            "vendorName": str
        }
    ],
    "shippingInfo": {
        "fullName": str,
        "email": str,
        "phone": str,
        "address": str,
        "city": str,
        "postcode": str
    },
    "paymentInfo": {
        "method": str (enum: "stripe", "paypal"),
        "transactionId": str,
        "status": str (enum: "pending", "completed", "failed")
    },
    "subtotal": float,
    "deliveryFee": float,
    "commission": float (£1 per item),
    "total": float,
    "status": str (enum: "pending", "processing", "shipped", "delivered", "cancelled"),
    "createdAt": datetime,
    "updatedAt": datetime
}
```

### Cart Model (Session-based)
```python
{
    "_id": ObjectId,
    "userId": ObjectId (ref: User),
    "items": [
        {
            "productId": ObjectId (ref: Product),
            "quantity": int
        }
    ],
    "updatedAt": datetime
}
```

## 2. API Endpoints

### Authentication APIs
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login (returns JWT token)
- `POST /api/auth/google` - Google OAuth login
- `GET /api/auth/me` - Get current user (protected)
- `POST /api/auth/logout` - Logout

### Product APIs
- `GET /api/products` - Get all products (with filters: category, vendor, price range, search)
- `GET /api/products/:id` - Get product by ID
- `POST /api/products` - Create product (vendor only)
- `PUT /api/products/:id` - Update product (vendor only)
- `DELETE /api/products/:id` - Delete product (vendor only)
- `GET /api/products/featured` - Get featured products

### Category APIs
- `GET /api/categories` - Get all categories

### Vendor APIs
- `POST /api/vendors/register` - Vendor registration
- `GET /api/vendors` - Get all vendors
- `GET /api/vendors/:id` - Get vendor by ID
- `GET /api/vendors/:id/products` - Get vendor's products
- `PUT /api/vendors/:id` - Update vendor (vendor only)
- `GET /api/vendors/dashboard/stats` - Get vendor dashboard stats (vendor only)

### Cart APIs
- `GET /api/cart` - Get user's cart
- `POST /api/cart/add` - Add item to cart
- `PUT /api/cart/update/:productId` - Update cart item quantity
- `DELETE /api/cart/remove/:productId` - Remove item from cart
- `DELETE /api/cart/clear` - Clear cart

### Order APIs
- `POST /api/orders` - Create order
- `GET /api/orders` - Get user's orders
- `GET /api/orders/:id` - Get order by ID
- `PUT /api/orders/:id/status` - Update order status (vendor/admin)

### Payment APIs
- `POST /api/payment/stripe/create-intent` - Create Stripe payment intent
- `POST /api/payment/stripe/confirm` - Confirm Stripe payment
- `POST /api/payment/paypal/create` - Create PayPal order
- `POST /api/payment/paypal/capture` - Capture PayPal payment

## 3. Mock Data to Replace

### In mock.js:
- `categories` → Keep as static data (no backend needed)
- `vendors` → Replace with GET /api/vendors
- `products` → Replace with GET /api/products
- `banners` → Keep as static data
- `getCart()` → Replace with GET /api/cart
- `addToCart()` → Replace with POST /api/cart/add
- `removeFromCart()` → Replace with DELETE /api/cart/remove/:productId
- `updateCartQuantity()` → Replace with PUT /api/cart/update/:productId
- `clearCart()` → Replace with DELETE /api/cart/clear
- `mockLogin()` → Replace with POST /api/auth/login
- `mockRegister()` → Replace with POST /api/auth/register
- `mockVendorRegister()` → Replace with POST /api/vendors/register
- `mockOrders` → Replace with GET /api/orders

## 4. Frontend-Backend Integration Changes

### Files to Update:

1. **src/context/AuthContext.js**
   - Replace mockLogin/mockRegister with actual API calls
   - Add JWT token storage
   - Add API interceptor for auth headers

2. **src/context/CartContext.js**
   - Replace localStorage cart with backend API calls
   - Sync cart with server

3. **src/pages/Home.js**
   - Fetch products from API
   - Fetch vendors from API

4. **src/pages/Products.js**
   - Fetch products with filters from API

5. **src/pages/ProductDetail.js**
   - Fetch product details from API

6. **src/pages/Cart.js**
   - Use cart API

7. **src/pages/Checkout.js**
   - Integrate Stripe & PayPal payment APIs
   - Create order via API

8. **src/pages/Login.js & Register.js**
   - Use auth APIs

9. **src/pages/VendorRegister.js**
   - Use vendor registration API

10. **src/pages/VendorDashboard.js**
    - Fetch vendor stats and products from API

11. **src/pages/Profile.js**
    - Fetch user orders from API

## 5. Authentication Flow

1. User registers/logs in → Backend returns JWT token
2. Frontend stores token in localStorage
3. All protected API calls include token in Authorization header
4. Backend validates token and extracts user info
5. Google OAuth: Frontend gets Google token → Send to backend → Backend validates → Returns JWT

## 6. Payment Flow

### Stripe:
1. User fills checkout form
2. Frontend calls POST /api/payment/stripe/create-intent
3. Backend creates PaymentIntent and returns client_secret
4. Frontend uses Stripe.js to confirm payment
5. On success, frontend calls POST /api/orders to create order
6. Backend stores order with payment details

### PayPal:
1. User selects PayPal
2. Frontend calls POST /api/payment/paypal/create
3. Backend creates PayPal order and returns approval URL
4. User approves on PayPal
5. Frontend calls POST /api/payment/paypal/capture
6. Backend captures payment and creates order

## 7. Commission Tracking

- Platform commission: £1 per item sold
- Calculated at order creation: `commission = total_items * 1.0`
- Stored in Order model
- Vendor dashboard shows net revenue (total - commission)

## 8. Next Steps

1. ✅ Install required Python packages
2. ✅ Create MongoDB models
3. ✅ Implement authentication endpoints
4. ✅ Implement product CRUD endpoints
5. ✅ Implement cart endpoints
6. ✅ Implement order endpoints
7. ✅ Implement vendor endpoints
8. ✅ Integrate payment APIs (Stripe & PayPal)
9. ✅ Update frontend to use backend APIs
10. ✅ Test all flows
11. ✅ Remove mock.js references
