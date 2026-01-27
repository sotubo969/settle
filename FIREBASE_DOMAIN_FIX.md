# Firebase Domain Authorization Guide
## Fix "auth/network-request-failed" Error

---

## THE PROBLEM

When using Firebase Authentication (Google Sign-In or Email/Password), you may see this error:
```
Firebase: Error (auth/network-request-failed)
```

This happens because the preview/production domain is **not authorized** in your Firebase Console.

---

## THE SOLUTION

### Step 1: Go to Firebase Console
1. Open https://console.firebase.google.com/
2. Select your project (the one configured for AfroMarket UK)

### Step 2: Navigate to Authentication Settings
1. In the left sidebar, click **"Authentication"**
2. Click on the **"Settings"** tab at the top
3. Click on **"Authorized domains"** section

### Step 3: Add the Domain
1. Click **"Add domain"** button
2. Add this domain:
   ```
   github-code-pull.preview.emergentagent.com
   ```
3. Click **"Add"**

### Step 4: Verify
The domain should now appear in your authorized domains list alongside:
- localhost
- your-project-id.firebaseapp.com
- your-project-id.web.app

---

## CURRENT DOMAINS TO AUTHORIZE

For AfroMarket UK, add these domains:
1. `github-code-pull.preview.emergentagent.com` (Current preview)
2. Your production domain (when ready)

---

## ALTERNATIVE: Use Legacy Auth

If Firebase configuration is not available, the platform has a fallback:
- **JWT-based Email/Password authentication** works without Firebase
- Users can register and login with email/password using the legacy system

---

## TESTING AFTER FIX

1. Go to https://github-code-pull.preview.emergentagent.com/login
2. Click "Sign in with Google"
3. Complete the Google OAuth flow
4. You should be logged in successfully

---

## TROUBLESHOOTING

### If still getting errors:
1. **Clear browser cache** - Firebase caches auth state
2. **Check Firebase config** - Ensure API keys are correct in frontend/.env
3. **Check console logs** - Look for specific error messages

### Firebase Environment Variables Needed:
```env
# In frontend/.env
REACT_APP_FIREBASE_API_KEY=your_api_key
REACT_APP_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your_project_id
```

### Backend Firebase Service Account:
```env
# In backend/.env
FIREBASE_SERVICE_ACCOUNT={"type":"service_account",...}
```

---

## FIREBASE STATUS CHECK

You can check if Firebase is configured by visiting:
```
GET https://github-code-pull.preview.emergentagent.com/api/auth/firebase/status
```

Response:
- `{"configured": true}` - Firebase is ready
- `{"configured": false}` - Firebase needs configuration

---

## CONTACT

If you need help configuring Firebase:
1. Share your Firebase project ID
2. I can help verify the configuration
3. The legacy JWT auth system works as a backup
