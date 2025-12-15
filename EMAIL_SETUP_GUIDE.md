# Email Notification Setup Guide

## 📧 Vendor Registration Email Notifications

When a vendor registers on your platform, an email notification will be automatically sent to **sotubodammy@gmail.com** with all the vendor details.

---

## ✅ Current Status

- ✅ **Email service implemented**
- ✅ **Vendor registration notifications configured**
- ✅ **Admin email set to: sotubodammy@gmail.com**
- ⏳ **Waiting for SMTP credentials to actually send emails**

---

## 🔧 How to Enable Email Sending

### Option 1: Using Gmail (Recommended for Testing)

**Step 1:** Enable 2-Factor Authentication on your Gmail
- Go to https://myaccount.google.com/security
- Enable 2-Step Verification

**Step 2:** Generate App Password
- Go to https://myaccount.google.com/apppasswords
- Select "Mail" and your device
- Copy the 16-character password

**Step 3:** Update `/app/backend/.env`
```env
SMTP_HOST="smtp.gmail.com"
SMTP_PORT="587"
SMTP_USER="your-gmail@gmail.com"          # Your Gmail address
SMTP_PASSWORD="xxxx xxxx xxxx xxxx"        # The 16-char App Password
FROM_EMAIL="noreply@afromarket.uk"
ADMIN_EMAIL="sotubodammy@gmail.com"        # Already configured!
```

**Step 4:** Restart backend
```bash
sudo supervisorctl restart backend
```

---

## 📬 What Emails Are Sent?

### Vendor Registration Notification (to Admin)
**Recipient:** sotubodammy@gmail.com  
**Triggered:** When a vendor registers  
**Contains:**
- Business name, email, phone
- Address details
- Business description
- Registration timestamp

---

## 🧪 Testing

**Test vendor registration:**
```bash
curl -X POST https://sourcecode-fetch.preview.emergentagent.com/api/vendors/register \
  -H 'Content-Type: application/json' \
  -d '{
    "businessName": "Test Store",
    "description": "Testing email",
    "email": "test@example.com",
    "phone": "+44 20 1234 5678",
    "address": "123 Test St",
    "city": "London",
    "postcode": "E1 1AA"
  }'
```

**Without SMTP credentials:** Emails are logged to console  
**With SMTP credentials:** Real emails sent to sotubodammy@gmail.com

---

## ⚠️ Important

- Add SMTP credentials to `/app/backend/.env` to enable email sending
- Currently emails are logged (development mode)
- Admin email: **sotubodammy@gmail.com** (already configured!)
