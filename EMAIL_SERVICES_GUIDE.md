# Complete Email Setup Guide - All Options

## 📧 Available Email Services (NOT Twilio - that's for SMS)

You have 4 main options to send vendor notification emails:

---

## ✅ Option 1: Gmail (EASIEST - Recommended)

### Setup Time: 5 minutes
### Cost: FREE
### Limit: 500 emails/day

### Steps:

1. **Get App Password:**
   - Go to: https://myaccount.google.com/security
   - Enable "2-Step Verification" (if not already on)
   - Click "App passwords" (or search for it)
   - Select: Mail → Other (custom name) → "AfroMarket UK"
   - Click Generate
   - Copy the 16-character password

2. **Add to .env:**
   ```bash
   nano /app/backend/.env
   ```
   
   Add these lines:
   ```env
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT="587"
   SMTP_EMAIL="sotubodammy@gmail.com"
   SMTP_PASSWORD="abcd efgh ijkl mnop"  # Your 16-char app password
   ```

3. **Restart:**
   ```bash
   sudo supervisorctl restart backend
   ```

4. **Test:**
   - Have someone register as vendor
   - Check inbox: sotubodammy@gmail.com

---

## ✅ Option 2: SendGrid (Best for Scale)

### Setup Time: 10 minutes
### Cost: FREE tier (100 emails/day), Paid starts at $19.95/month
### Limit: 100 emails/day (free), unlimited (paid)

### Steps:

1. **Create Account:**
   - Go to: https://signup.sendgrid.com/
   - Sign up for free account
   - Verify your email

2. **Get API Key:**
   - Go to Settings → API Keys
   - Click "Create API Key"
   - Name: "AfroMarket UK"
   - Select "Full Access"
   - Copy the API key (save it - you won't see it again)

3. **Add to .env:**
   ```bash
   nano /app/backend/.env
   ```
   
   Add these lines:
   ```env
   SMTP_SERVER="smtp.sendgrid.net"
   SMTP_PORT="587"
   SMTP_EMAIL="apikey"
   SMTP_PASSWORD="SG.your-actual-sendgrid-api-key-here"
   ```

4. **Verify Sender:**
   - In SendGrid dashboard: Settings → Sender Authentication
   - Verify your email: sotubodammy@gmail.com
   - Click verification link sent to your email

5. **Restart:**
   ```bash
   sudo supervisorctl restart backend
   ```

---

## ✅ Option 3: Mailgun (Developer Friendly)

### Setup Time: 10 minutes
### Cost: FREE tier (5,000 emails/month for 3 months), then $35/month
### Limit: 5,000 emails/month (trial)

### Steps:

1. **Create Account:**
   - Go to: https://www.mailgun.com/
   - Sign up for free trial
   - Verify your email

2. **Get SMTP Credentials:**
   - Go to Sending → Domain Settings
   - Select your domain (sandbox or custom)
   - Click "SMTP credentials"
   - Copy username and password

3. **Add to .env:**
   ```bash
   nano /app/backend/.env
   ```
   
   Add these lines:
   ```env
   SMTP_SERVER="smtp.mailgun.org"
   SMTP_PORT="587"
   SMTP_EMAIL="postmaster@sandboxXXXX.mailgun.org"  # Your mailgun username
   SMTP_PASSWORD="your-mailgun-password-here"
   ```

4. **Add Authorized Recipients (Sandbox mode):**
   - Go to Sending → Domains → Authorized Recipients
   - Add: sotubodammy@gmail.com
   - Verify the email

5. **Restart:**
   ```bash
   sudo supervisorctl restart backend
   ```

---

## ✅ Option 4: Outlook/Hotmail (Alternative to Gmail)

### Setup Time: 5 minutes
### Cost: FREE
### Limit: 300 emails/day

### Steps:

1. **Enable App Password:**
   - Go to: https://account.microsoft.com/security
   - Turn on "Two-step verification"
   - Generate app password

2. **Add to .env:**
   ```bash
   nano /app/backend/.env
   ```
   
   Add these lines:
   ```env
   SMTP_SERVER="smtp-mail.outlook.com"
   SMTP_PORT="587"
   SMTP_EMAIL="your-email@outlook.com"
   SMTP_PASSWORD="your-app-password-here"
   ```

3. **Restart:**
   ```bash
   sudo supervisorctl restart backend
   ```

---

## 📊 Comparison Table

| Service | Setup | Cost | Limit | Best For |
|---------|-------|------|-------|----------|
| **Gmail** | Easy | FREE | 500/day | Quick start, personal |
| **SendGrid** | Medium | FREE/Paid | 100/day (free) | Professional, scalable |
| **Mailgun** | Medium | Trial | 5,000/month | Developers, APIs |
| **Outlook** | Easy | FREE | 300/day | Alternative to Gmail |

---

## 🎯 Which Should You Choose?

### Choose Gmail if:
- ✅ You want to start immediately
- ✅ You already have Gmail account
- ✅ You expect < 500 emails/day
- ✅ You want simplest setup

### Choose SendGrid if:
- ✅ You want professional email service
- ✅ You need email analytics
- ✅ You might send 100+ emails/day
- ✅ You want better deliverability

### Choose Mailgun if:
- ✅ You're technical/developer
- ✅ You want detailed logs
- ✅ You need API access
- ✅ You want webhooks

### Choose Outlook if:
- ✅ You don't want to use Gmail
- ✅ You have Outlook account
- ✅ Simple personal use

---

## 🚀 Recommended Setup (3 Steps)

**For most users, Gmail is the fastest:**

1. **Get App Password (2 min):**
   ```
   Google Account → Security → App Passwords → Generate
   ```

2. **Update .env (1 min):**
   ```bash
   nano /app/backend/.env
   ```
   Add:
   ```env
   SMTP_SERVER="smtp.gmail.com"
   SMTP_PORT="587"
   SMTP_EMAIL="sotubodammy@gmail.com"
   SMTP_PASSWORD="your-16-char-password"
   ```

3. **Restart (30 sec):**
   ```bash
   sudo supervisorctl restart backend
   ```

---

## ✅ Testing Your Setup

After configuration, test it:

```bash
# Watch logs in real-time
tail -f /var/log/supervisor/backend.out.log | grep "Email"

# In another terminal, test vendor registration:
curl -X POST http://localhost:8001/api/vendors/register \
  -H 'Content-Type: application/json' \
  -d '{
    "businessName": "Test Store",
    "description": "Testing email",
    "email": "test@example.com",
    "phone": "+44 20 1234 5678",
    "address": "123 Test St",
    "city": "Manchester",
    "postcode": "M1 1BB"
  }'
```

**Look for:**
```
✅ Email sent successfully to sotubodammy@gmail.com
```

**Or if not configured:**
```
⚠️ SMTP not configured. Add SMTP_EMAIL and SMTP_PASSWORD to .env
```

---

## 🔧 Troubleshooting

### Gmail: "Authentication failed"
- ❌ Using regular password → ✅ Use App Password
- ❌ 2FA not enabled → ✅ Enable 2-Step Verification first
- ❌ Wrong app password → ✅ Generate new one

### SendGrid: "Sender not verified"
- Go to Settings → Sender Authentication
- Verify your email address
- Check spam for verification email

### Mailgun: "Recipient not authorized"
- In sandbox mode, add recipient to authorized list
- Or upgrade to paid plan for unlimited recipients

### All Services: "Connection refused"
- Check SMTP_PORT is "587" (not 465 or 25)
- Check SMTP_SERVER spelling
- Check firewall settings

---

## 🔐 Security Best Practices

✅ **Do:**
- Use App Passwords (not main passwords)
- Keep .env file private
- Don't commit .env to Git
- Rotate passwords if exposed

❌ **Don't:**
- Share SMTP credentials
- Use your main email password
- Hardcode credentials in code
- Expose credentials in logs

---

## 📱 What About Twilio?

**Twilio is for SMS, not emails!**

If you want SMS notifications instead:
```env
TWILIO_ACCOUNT_SID="your-account-sid"
TWILIO_AUTH_TOKEN="your-auth-token"
TWILIO_PHONE_NUMBER="+1234567890"
```

But for vendor registration notifications, **email is recommended** because:
- ✅ More professional
- ✅ Can include rich formatting
- ✅ Better for detailed information
- ✅ Free or very cheap
- ✅ No international SMS costs

---

## 📞 Need Help?

After setup, if you still don't receive emails:

1. Check .env file has correct credentials
2. Check backend logs for errors
3. Verify email isn't in spam folder
4. Test with curl command above
5. Check sender verification (SendGrid/Mailgun)

---

## Summary

**Quickest Setup:** Gmail (5 minutes)  
**Most Professional:** SendGrid (10 minutes)  
**Best for Developers:** Mailgun (10 minutes)  

**Recommended:** Start with Gmail, upgrade to SendGrid later if needed.

**Current Status:** Email notifications are working but waiting for your SMTP credentials!
