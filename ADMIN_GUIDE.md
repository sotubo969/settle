# AfroMarket UK - Admin Guide

## 🎯 New Features Implemented

### 1. Wishlist Functionality
- Users can add products to wishlist from product detail page
- Wishlist accessible from Profile page
- Remove items from wishlist

### 2. Profile Management
- Edit name and phone number
- View and manage account details
- All changes saved to database

### 3. Address Management
- Add multiple delivery addresses
- Set default address
- Edit and delete addresses
- Used during checkout

### 4. Payment Methods
- Add and save payment methods
- Card details securely masked
- Delete payment methods
- Set default payment method

### 5. Vendor Registration Email Notifications
- **Admin Email:** sotubodammy@gmail.com
- When a vendor registers, you'll receive a console notification (email setup pending)
- Check backend logs for vendor registration details

### 6. Vendor Approval & Product Management
- Approve vendors through API
- Approved vendors can add their own products
- Vendors can edit and delete their products
- Full product management dashboard

### 7. Order History
- Real order tracking
- Order status updates
- Complete order details

### 8. Footer Update
- Added "GOD IS GOOD" message
- © 2025 AfroMarket UK

---

## 📧 Vendor Registration Workflow

### When a New Vendor Registers:

1. **Notification Logged to Console**
   - Check backend logs: `tail -f /var/log/supervisor/backend.err.log`
   - Look for "VENDOR REGISTRATION NOTIFICATION"

2. **Review Vendor Details**
   ```bash
   # Get pending vendors
   curl -s http://localhost:8001/api/admin/vendors/pending | jq '.'
   ```

3. **Approve or Reject Vendor**
   ```bash
   # Approve vendor
   curl -X POST http://localhost:8001/api/admin/vendors/approve \
     -H "Content-Type: application/json" \
     -d '{"vendorId": 1, "status": "approved"}'
   
   # Reject vendor
   curl -X POST http://localhost:8001/api/admin/vendors/approve \
     -H "Content-Type: application/json" \
     -d '{"vendorId": 1, "status": "rejected"}'
   ```

4. **After Approval**
   - Vendor receives notification
   - Vendor can log in and add products
   - Products appear in marketplace immediately

---

## 🛍️ Vendor Product Management

### Approved vendors can:

1. **Add Products**
   - Access vendor dashboard
   - Click "Add Product"
   - Fill in product details
   - Upload product image
   - Set price, stock, category

2. **Edit Products**
   - Update product details
   - Change pricing
   - Adjust stock levels

3. **Delete Products**
   - Remove products from marketplace
   - Instant removal

### API Endpoints for Vendors:

```bash
# Get vendor's products
GET /api/vendor/my-products

# Create new product
POST /api/vendor/products

# Update product
PUT /api/vendor/products/{id}

# Delete product
DELETE /api/vendor/products/{id}
```

---

## 🔧 Admin Tasks

### Check Pending Vendors
```bash
curl -s http://localhost:8001/api/admin/vendors/pending | jq '.'
```

### Approve Vendor
```bash
curl -X POST http://localhost:8001/api/admin/vendors/approve \
  -H "Content-Type: application/json" \
  -d '{
    "vendorId": INSERT_VENDOR_ID_HERE,
    "status": "approved"
  }'
```

### Monitor Vendor Registrations
```bash
# Watch backend logs in real-time
tail -f /var/log/supervisor/backend.err.log | grep "VENDOR"
```

---

## 📱 User Features

### Profile Management
- **URL:** https://code-fetcher-23.preview.emergentagent.com/profile
- Edit profile information
- Manage addresses
- Add payment methods
- View order history
- Access wishlist

### Wishlist
- Add products from product detail page
- View all wishlist items in profile
- Remove items as needed
- Quick access to favorite products

### Order Tracking
- View all orders
- Track order status
- See order details
- Reorder functionality

---

## 🔄 Database Schema Updates

### User Table - New Fields:
- `wishlist` - JSON array of product IDs
- `payment_methods` - JSON array of payment methods
- `addresses` - JSON array (already existed, now functional)

### All Changes:
- SQLite database automatically updated
- No manual migration needed
- All data preserved

---

## 🚀 Testing the New Features

### Test Wishlist:
1. Go to any product page
2. Click "Add to Wishlist"
3. Go to Profile → Wishlist tab
4. Verify product appears

### Test Profile Edit:
1. Go to Profile → Profile tab
2. Click "Edit Profile"
3. Change name or phone
4. Click "Save Changes"

### Test Addresses:
1. Go to Profile → Addresses tab
2. Click "Add Address"
3. Fill in details
4. Save and verify

### Test Vendor Registration:
1. Go to "Become a Vendor"
2. Fill in business details
3. Submit
4. Check backend logs for notification
5. Approve via API
6. Vendor can now add products

---

## 📝 Notes

- **Email Configuration:** To enable actual email sending, configure SMTP settings in `email_service.py`
- **Admin Panel:** Currently using API endpoints. Can build admin UI later
- **Vendor Dashboard:** Already implemented at `/vendor/dashboard`
- **All features are live and functional**

---

## 🎉 Summary

✅ Wishlist working
✅ Profile management functional
✅ Address management live
✅ Payment methods working
✅ Vendor email notifications (console)
✅ Vendor approval system ready
✅ Vendor product management complete
✅ Order history accurate
✅ Footer updated with "GOD IS GOOD"

**Everything is ready to use!**
