# How to Get Gmail SMTP Password (App Password)

## Quick Steps:

### 1. Enable 2-Factor Authentication
1. Go to https://myaccount.google.com/security
2. Find "2-Step Verification" 
3. Click "Get Started" and follow the setup

### 2. Generate App Password
1. Go to https://myaccount.google.com/apppasswords
2. If you don't see "App passwords", make sure 2FA is enabled first
3. Select app: **Mail**
4. Select device: **Other (Custom name)**
5. Type: **AfroMarket UK**
6. Click **Generate**
7. You'll get a 16-character password like: `abcd efgh ijkl mnop`
8. **Copy this password** (you won't see it again!)

### 3. Add to Your .env File
Open `/app/backend/.env` and update:
```env
SMTP_USER="your-email@gmail.com"           # Your Gmail address
SMTP_PASSWORD="abcd efgh ijkl mnop"        # The 16-char password from step 2
```

### 4. Restart Backend
```bash
sudo supervisorctl restart backend
```

### 5. Test It!
Register a vendor and check **sotubodammy@gmail.com** for the notification email!

---

## Troubleshooting:

**"App passwords option not showing"**
→ Make sure 2FA is fully enabled and wait a few minutes

**"Invalid credentials" error**
→ Use the App Password, NOT your regular Gmail password

**Still not working?**
→ Check if "Less secure app access" is off (it should be)
→ Make sure you copied the full 16-character password
→ Remove any spaces between characters in .env file

---

**Need help?** Contact support or check backend logs:
```bash
tail -f /app/backend/logs/backend.err.log
```
