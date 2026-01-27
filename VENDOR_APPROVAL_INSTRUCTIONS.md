# AfroMarket UK - Vendor Approval Instructions

## How to Approve Vendors

When a vendor submits a registration form, you will receive an email notification at **sotubodammy@gmail.com** with all their details.

### Method 1: Admin Dashboard (Recommended)

1. **Login as Admin**
   - Go to https://github-code-pull.preview.emergentagent.com/login
   - Use your admin credentials
   
2. **Access Owner Dashboard**
   - Navigate to https://github-code-pull.preview.emergentagent.com/owner
   - Or click "Account & Lists" → "Owner Dashboard"

3. **Review Pending Vendors**
   - In the dashboard, find the "Vendors" or "Pending Approvals" section
   - You'll see all vendors with status "pending"

4. **Approve or Reject**
   - Click on a vendor to view their details
   - Click "Approve" to activate their account
   - Click "Reject" to deny the application

### Method 2: API (For Developers)

```bash
# Get list of all vendors
curl -X GET https://github-code-pull.preview.emergentagent.com/api/vendors

# Approve a vendor (requires admin auth)
curl -X PUT https://github-code-pull.preview.emergentagent.com/api/vendors/{vendor_id}/approve \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Reject a vendor
curl -X PUT https://github-code-pull.preview.emergentagent.com/api/vendors/{vendor_id}/reject \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

---

## Email Notification Content

When a vendor registers, you'll receive an email like this:

**Subject:** 🎉 New Vendor Registration: [Business Name]

**Content includes:**
- Business Name
- Owner Name
- Email Address
- Phone Number
- Business Address
- City & Postcode
- Business Description
- Registration Date
- Vendor ID

---

## Vendor Status Flow

```
PENDING → APPROVED → ACTIVE
       ↘ REJECTED
```

1. **Pending**: New registration, awaiting your review
2. **Approved**: You've approved, vendor can access dashboard
3. **Active**: Vendor is live and selling
4. **Rejected**: Application denied

---

## Automatic Emails to Vendors

The system will automatically send emails to vendors:
- ✅ Registration confirmation
- ✅ Approval notification
- ✅ Rejection notification (if applicable)

---

## Best Practices

1. **Review within 2-3 business days** - Keep vendors engaged
2. **Verify business details** - Check if the business is legitimate
3. **Contact vendor if needed** - Use provided phone/email
4. **Document rejection reasons** - Help vendors improve

---

## Troubleshooting

### Not receiving emails?
1. Check spam/junk folder
2. Verify SMTP credentials in `/app/backend/.env`
3. Check backend logs: `tail -f /var/log/supervisor/backend.err.log`

### Can't approve vendors?
1. Ensure you're logged in as admin
2. Check if the vendor exists: `GET /api/vendors`
3. Verify your admin token is valid

---

## Support

If you need help:
1. Check the console logs for errors
2. Verify environment variables are set
3. Test email sending manually:
   ```python
   from email_service import EmailService
   es = EmailService()
   es.send_email("test@example.com", "Test", "<h1>Test</h1>")
   ```
