# 📧 Why Am I Not Receiving Vendor Registration Emails?

## Quick Answer

**You need to configure Gmail App Password in your backend settings.**

Emails are currently being **logged to the console only** because SMTP credentials are not set up. This is intentional for security - we don't want to store your email password without your explicit setup.

---

## 5-Minute Setup to Enable Emails

### Step 1: Get Gmail App Password

1. Go to: https://myaccount.google.com/security
2. Turn on **2-Step Verification** (if not already on)
3. Search for "App passwords" or scroll down to find it
4. Click **App passwords**
5. Select:
   - **App:** Mail
   - **Device:** Other (custom name)
   - Name it: **AfroMarket UK**
6. Click **Generate**
7. **COPY the 16-character password** that appears (spaces don't matter)
   - Example: `abcd efgh ijkl mnop`

### Step 2: Add to Backend

```bash
# Open the .env file
nano /app/backend/.env

# Add these 4 lines at the bottom:
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"
SMTP_EMAIL="sotubodammy@gmail.com"
SMTP_PASSWORD="your-16-character-app-password-here"

# Save and exit (Ctrl+X, then Y, then Enter)
```

### Step 3: Restart Backend

```bash
sudo supervisorctl restart backend
```

### Step 4: Test It!

1. Have someone register as a vendor on your site
2. Check your email: **sotubodammy@gmail.com**
3. You should receive: "🎉 New Vendor Registration - [Business Name]"

---

## What You'll Receive

When someone applies to become a vendor, you'll get an email with:

✅ Business name  
✅ Contact email  
✅ Phone number  
✅ Location  
✅ Business description  
✅ Instructions on how to approve them

---

## Checking If It's Working

### Option 1: Check Backend Logs
```bash
tail -f /var/log/supervisor/backend.out.log | grep "VENDOR"
```

**If configured correctly, you'll see:**
```
✅ Email sent successfully to sotubodammy@gmail.com
```

**If not configured, you'll see:**
```
⚠️ SMTP not configured. Add SMTP_EMAIL and SMTP_PASSWORD to .env
```

### Option 2: Test Vendor Registration

Go to: https://code-fetcher-23.preview.emergentagent.com/vendor/register

Fill in the form and submit. Check:
1. Backend logs (as above)
2. Your email inbox
3. Spam/junk folder (just in case)

---

## Troubleshooting

### "Authentication failed"
- ❌ Using regular Gmail password
- ✅ Must use App Password (16 characters)
- ❌ 2-Step Verification not enabled
- ✅ Enable 2-Step Verification first

### "Still not receiving emails"
```bash
# Verify credentials are loaded
cd /app/backend
python -c "import os; from dotenv import load_dotenv; load_dotenv('.env'); print('SMTP_EMAIL:', os.environ.get('SMTP_EMAIL')); print('SMTP configured:', bool(os.environ.get('SMTP_PASSWORD')))"
```

**Expected output:**
```
SMTP_EMAIL: sotubodammy@gmail.com
SMTP configured: True
```

### "Can't find App Passwords in Google"
- You need 2-Step Verification enabled first
- Direct link: https://myaccount.google.com/apppasswords
- Or search "app passwords" in your Google Account

---

## Current Behavior (Without Setup)

**Console Logs Only:**
```
============================================================
📧 VENDOR REGISTRATION NOTIFICATION
============================================================
To: sotubodammy@gmail.com
Business: Test African Store
Email: vendor@example.com
Phone: +44 20 1234 5678
Location: Manchester, M1 1BB
============================================================
```

You can see these by running:
```bash
tail -f /var/log/supervisor/backend.out.log
```

---

## Security Notes

✅ **Safe:** App passwords are for specific apps only  
✅ **Secure:** Not your main Gmail password  
✅ **Revocable:** Can be deleted anytime from Google Account  
✅ **Limited:** Only has email sending permission  

❌ **Don't:** Share the app password  
❌ **Don't:** Commit .env file to Git  
❌ **Don't:** Use your regular Gmail password  

---

## Alternative: Use a Different Email Service

If you don't want to use Gmail, you can use:

### SendGrid (Free tier: 100 emails/day)
```env
SMTP_SERVER="smtp.sendgrid.net"
SMTP_PORT="587"
SMTP_EMAIL="apikey"
SMTP_PASSWORD="your-sendgrid-api-key"
```

### Mailgun
```env
SMTP_SERVER="smtp.mailgun.org"
SMTP_PORT="587"
SMTP_EMAIL="postmaster@your-domain.mailgun.org"
SMTP_PASSWORD="your-mailgun-smtp-password"
```

---

## Summary

| Step | What to Do | Time |
|------|-----------|------|
| 1 | Get Gmail App Password | 2 min |
| 2 | Add to .env file | 1 min |
| 3 | Restart backend | 30 sec |
| 4 | Test | 1 min |

**Total: ~5 minutes to enable email notifications!**

After setup, you'll automatically receive emails whenever someone wants to become a vendor.

---

## Need Help?

If emails still don't work after setup:
1. Check the troubleshooting section above
2. Verify credentials in .env are correct
3. Check backend logs for error messages
4. Ensure no typos in email address

**The system is working - it just needs your email credentials!** 📧
