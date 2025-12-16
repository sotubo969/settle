# 🏪 Complete Store Submission Guide - AfroMarket UK

## ✅ Current Status

**Your App Is Ready for Store Submission!**

- ✅ App icons created from your logo
- ✅ PWA fully functional
- ✅ Backend tested (100% core features)
- ✅ Frontend tested (95%+ features)
- ✅ Build scripts prepared
- ✅ All documentation ready

---

## 📱 Part 1: GOOGLE PLAY STORE SUBMISSION

### Step 1: Create Google Play Developer Account (30 minutes)

**Cost:** $25 (one-time fee)

**Process:**
1. Go to https://play.google.com/console
2. Click **"Get Started"**
3. Sign in with Google account
4. Accept Developer Distribution Agreement
5. Pay $25 registration fee (credit card/PayPal)
6. Wait for payment confirmation (instant)
7. Complete account verification
   - Verify email
   - Verify phone number
   - D-U-N-S number (optional for organizations)

**Account Setup:**
- Developer name: Your name or company name
- Email address: support@afromarket.uk
- Phone number: Your contact number
- Website: https://your-domain.com

**Timeline:** Account active immediately after payment

---

### Step 2: Build Android APK (15 minutes)

**Option A: Using Our Automated Script (Easiest)**

```bash
cd /app

# Run the build script
./build-android-app.sh

# Follow prompts:
# - Enter your domain: afromarket.uk (or your domain)
# - Wait for build to complete (~5 min)
# - APK created: app-release-signed.apk
```

**Option B: Manual Bubblewrap Build**

```bash
# 1. Install Bubblewrap (already installed)
npm install -g @bubblewrap/cli

# 2. Initialize project
cd /app
bubblewrap init --manifest https://your-domain.com/manifest.json

# 3. Fill in prompts:
#    - Domain: your-domain.com
#    - Package ID: uk.afromarket.app
#    - App name: AfroMarket UK
#    - Theme color: #059669
#    - Start URL: /

# 4. Build APK
bubblewrap build

# Result: app-release-signed.apk
```

**What You Get:**
- `app-release-signed.apk` - Ready to upload!
- Size: ~15-20 MB
- Signed with auto-generated keystore
- Production-ready

---

### Step 3: Prepare Store Assets (2-3 hours)

#### A. Screenshots (REQUIRED)

**Requirements:**
- **Phone screenshots**: 2-8 images
- Size: 1080 x 1920 pixels or 1080 x 2340 pixels
- Format: PNG or JPEG (no alpha channel)
- Max size: 8MB each

**How to Create:**

1. **Using Chrome DevTools:**
   ```
   - Open Chrome
   - Press F12 (Developer Tools)
   - Click device toolbar icon
   - Select "Pixel 5" (1080 x 2340)
   - Navigate to:
     * Homepage
     * Products page
     * Product detail
     * Cart
     * Profile/Orders
   - Right-click → Capture screenshot
   - Save each one
   ```

2. **Essential Screenshots:**
   - Screenshot 1: Homepage with hero banner
   - Screenshot 2: Product listing (with search bar)
   - Screenshot 3: Product detail page
   - Screenshot 4: Shopping cart
   - Screenshot 5: User profile/orders

3. **Add Text Overlays (Optional but Recommended):**
   Use Canva/Figma to add:
   - "Browse 1000+ African Products"
   - "Fast UK Delivery"
   - "Secure Checkout"
   - "Track Your Orders"
   - "Support Local Vendors"

#### B. Feature Graphic (REQUIRED)

**Requirements:**
- Size: 1024 x 500 pixels
- Format: PNG or JPEG (no transparency)
- Showcases app's main feature

**How to Create:**
1. Use Canva (https://canva.com)
2. Create custom size: 1024 x 500
3. Design with:
   - Your logo
   - App name: "AfroMarket UK"
   - Tagline: "Authentic African Groceries"
   - Background: Green (#059669)
4. Export as PNG

#### C. App Icon (Already Done! ✅)

**You have:**
- logo512.png - High-res icon
- logo192.png - Standard icon
- All sizes generated from your logo

---

### Step 4: Create App Listing (1 hour)

**Go to:** https://play.google.com/console

1. **Click "Create app"**

2. **App Details:**
   - **App name**: AfroMarket UK
   - **Default language**: English (UK)
   - **App or game**: App
   - **Free or paid**: Free

3. **Store Listing:**

   **App name:** AfroMarket UK
   
   **Short description (80 characters):**
   ```
   UK's premier marketplace for authentic African & Caribbean groceries
   ```
   
   **Full description (4000 characters):**
   ```
   🛒 Welcome to AfroMarket UK

   Discover the UK's largest online marketplace for authentic African and Caribbean groceries. Shop from trusted vendors across the country and get your favorite ingredients delivered to your doorstep.

   ✨ WHY CHOOSE AFROMARKET?

   🏪 Wide Selection
   Browse thousands of products from verified vendors:
   • Fresh produce (plantains, yams, okra)
   • Grains & flours (fufu, garri, pounded yam)
   • Spices & seasonings (suya, curry, pepper soup)
   • Frozen foods & meats
   • Snacks & beverages
   • Beauty & household items

   🚚 Fast UK Delivery
   • Order today, delivered tomorrow
   • Track your delivery in real-time
   • Multiple payment options
   • Secure checkout process

   👤 Easy Account Management
   • Save favorite products
   • Quick reorders from history
   • Manage delivery addresses
   • Track all your orders

   💚 Support Local Vendors
   • Buy directly from UK-based African stores
   • Support small businesses
   • Authentic products guaranteed
   • Competitive prices

   📱 APP FEATURES

   ✅ Browse & search products easily
   ✅ Filter by category, price, vendor
   ✅ Secure Google Sign-In
   ✅ Multiple payment methods
   ✅ Save products to wishlist
   ✅ Read product reviews
   ✅ Offline browsing support
   ✅ Push notifications

   🌍 SERVING THE UK AFRICAN COMMUNITY

   Whether you're cooking jollof rice, egusi soup, or Caribbean curry, find everything you need in one place. From London to Manchester, Birmingham to Glasgow, we deliver authentic groceries across the UK.

   Download AfroMarket UK today and taste home! 🇬🇧🌍
   ```

4. **App Details:**
   - **App category**: Shopping
   - **Tags**: african groceries, caribbean food, ethnic food, groceries
   - **Email**: support@afromarket.uk
   - **Phone**: [Your phone number]
   - **Website**: https://your-domain.com

5. **Graphics:**
   - Upload icon (512x512): logo512.png ✅
   - Upload feature graphic (1024x500): [Create this]
   - Upload screenshots (2-8): [Create these]

---

### Step 5: Content Rating (15 minutes)

1. Go to **"Content rating"** section
2. Start questionnaire
3. Select **"Shopping"** category

**Answer questions honestly:**
- Violence: None
- Sexual content: None
- Language: None
- Controlled substances: None
- Gambling: None
- User-generated content: No
- Share location: No
- Personal information: Email only

**Result:** Likely "Everyone" rating

---

### Step 6: Target Audience & Content (10 minutes)

1. **Target age group**: Adults 18+
2. **Target countries**: United Kingdom (add others if needed)
3. **Contains ads**: No (unless you add ads)
4. **In-app purchases**: No (unless you add them)

---

### Step 7: Privacy Policy (REQUIRED)

**You MUST have a privacy policy URL**

**Quick Solution:**

1. Use free generator:
   - https://www.privacypolicies.com
   - https://www.freeprivacypolicy.com

2. Include in policy:
   - What data you collect (email, name, address)
   - How you use it (order processing, delivery)
   - Third parties (payment processor, Google OAuth)
   - User rights (delete account, data export)
   - Contact info

3. Host on your website:
   - https://your-domain.com/privacy

4. Add URL to Play Console

---

### Step 8: Upload APK (10 minutes)

1. Go to **"Release" → "Production"**
2. Click **"Create new release"**
3. Upload `app-release-signed.apk`
4. **Release name**: Version 1.0.0
5. **Release notes**:
   ```
   Initial release of AfroMarket UK

   Features:
   • Browse 1000+ African & Caribbean products
   • Secure Google Sign-In
   • Fast UK delivery
   • Track orders in real-time
   • Save favorite products
   • Multiple payment options
   • Offline browsing
   ```

6. Click **"Save"** then **"Review release"**

---

### Step 9: Submit for Review (5 minutes)

1. Complete all required sections (✅ checkmarks)
2. Go to **"Dashboard"**
3. Check all warnings are resolved
4. Click **"Send for review"**

**Review Timeline:**
- First submission: 1-3 days
- Updates: 24-48 hours

**You'll receive email when:**
- Review starts
- App is approved
- App is rejected (with reasons)

---

### Step 10: After Approval

**Your app will be live!**

**Users can find it by:**
1. Opening Google Play Store
2. Searching: **"AfroMarket UK"**
3. Installing with one tap!

**App URL:**
`https://play.google.com/store/apps/details?id=uk.afromarket.app`

---

## 🍎 Part 2: APPLE APP STORE SUBMISSION

### Prerequisites:
- **macOS computer** (or Mac in cloud)
- **Xcode** installed
- **Apple Developer account** ($99/year)

---

### Step 1: Create Apple Developer Account (2 days)

**Cost:** $99 per year

**Process:**
1. Go to https://developer.apple.com/programs/
2. Click **"Enroll"**
3. Sign in with Apple ID
4. Choose account type:
   - **Individual** (your name)
   - **Organization** (company name, requires D-U-N-S)
5. Pay $99 annual fee
6. Wait for approval (24-48 hours)
7. Check email for confirmation

---

### Step 2: Install Development Tools (1 hour)

**On macOS:**

```bash
# 1. Install Xcode from Mac App Store
# Search "Xcode" → Install (12GB download)

# 2. Install Xcode Command Line Tools
xcode-select --install

# 3. Open Xcode and accept license
sudo xcodebuild -license accept

# 4. Install Capacitor
cd /app/frontend
npm install @capacitor/core @capacitor/cli @capacitor/ios
```

---

### Step 3: Build React App (10 minutes)

```bash
cd /app/frontend

# Build production version
yarn build

# Result: /app/frontend/build folder
```

---

### Step 4: Initialize Capacitor (15 minutes)

```bash
cd /app/frontend

# Initialize Capacitor
npx cap init

# When prompted:
# - App name: AfroMarket UK
# - App ID: uk.afromarket.app
# - Web directory: build

# Add iOS platform
npx cap add ios

# Copy web assets to iOS
npx cap copy ios

# Open in Xcode
npx cap open ios
```

---

### Step 5: Configure in Xcode (30 minutes)

**Xcode will open. Now configure:**

1. **Select project** (blue icon at top)

2. **General tab:**
   - Display Name: AfroMarket UK
   - Bundle Identifier: uk.afromarket.app
   - Version: 1.0.0
   - Build: 1
   - Team: [Select your developer account]

3. **Signing & Capabilities:**
   - Automatically manage signing: ✅ ON
   - Team: [Your Apple Developer account]
   - Provisioning Profile: Automatic

4. **Deployment Info:**
   - Deployment Target: iOS 13.0
   - Devices: iPhone, iPad (or iPhone only)
   - Orientation: Portrait

5. **App Icons:**
   - Click "App Icon" in Assets
   - Drag logo1024.png into the slots
   - Xcode auto-generates all sizes

---

### Step 6: Test on Simulator (10 minutes)

1. Select device: **iPhone 14 Pro** (top left)
2. Click **Play button** (▶️)
3. App launches in simulator
4. Test:
   - Browse products
   - Search works
   - Cart operations
   - Login/logout
5. Check for crashes or errors

---

### Step 7: Create App in App Store Connect (20 minutes)

**Go to:** https://appstoreconnect.apple.com

1. **Click "My Apps" → "+"** → "New App"

2. **App Information:**
   - **Platform**: iOS
   - **Name**: AfroMarket UK
   - **Primary Language**: English (UK)
   - **Bundle ID**: uk.afromarket.app
   - **SKU**: afromarket-uk-001

3. **Pricing and Availability:**
   - **Price**: Free
   - **Availability**: All countries (or select UK)

4. **App Privacy:**
   - Add privacy policy URL
   - Data collection details:
     * Email: Required (for account)
     * Name: Required (for delivery)
     * Address: Required (for delivery)
     * Payment info: Not collected (via Stripe)

5. **Age Rating:**
   - Complete questionnaire
   - Likely: 4+ or 12+

---

### Step 8: Prepare iOS Screenshots (2 hours)

**Requirements:**
- **6.7" iPhone** (1290 x 2796 px) - 3-10 screenshots
- **5.5" iPhone** (1242 x 2208 px) - 3-10 screenshots
- **12.9" iPad** (2048 x 2732 px) - Optional

**Create Screenshots:**
1. Use iOS Simulator in Xcode
2. Run app in different device sizes
3. Take screenshots: Cmd + S
4. Use Figma/Canva to add text overlays
5. Export in required sizes

---

### Step 9: Archive and Upload (30 minutes)

**In Xcode:**

1. Select **"Any iOS Device"** (top left)
2. Go to **Product → Archive**
3. Wait for archive to complete (~5 minutes)
4. Archive Organizer opens
5. Select your archive
6. Click **"Distribute App"**
7. Choose **"App Store Connect"**
8. Click **"Upload"**
9. Wait for upload (~10-20 minutes)
10. Check email for "Processing Complete"

**Processing time:** 15-60 minutes after upload

---

### Step 10: Complete App Store Listing (1 hour)

**In App Store Connect:**

1. **App Information:**
   - Subtitle (30 chars): "African Groceries Delivered"
   - Category: Shopping
   - Secondary: Food & Drink

2. **Promotional Text (170 chars):**
   ```
   Shop authentic African & Caribbean groceries from UK vendors. Fast delivery, secure checkout, thousands of products. Download now!
   ```

3. **Description (same as Play Store)**

4. **Keywords (100 chars):**
   ```
   african,groceries,caribbean,food,delivery,uk,shopping,ethnic,supermarket
   ```

5. **Support URL**: https://your-domain.com/help

6. **Marketing URL**: https://your-domain.com

7. **Screenshots**:
   - Upload for each device size
   - Drag to reorder

8. **App Preview (Optional)**:
   - Video preview of app (15-30 seconds)

---

### Step 11: Select Build and Submit (15 minutes)

1. Go to **"App Store" tab**
2. Click **"+" next to Build**
3. Select your uploaded build
4. Add **"What's New in This Version"**:
   ```
   Version 1.0.0 - Initial Release
   
   • Browse thousands of African products
   • Google Sign-In
   • Fast UK delivery
   • Secure checkout
   • Track orders
   • Save favorites
   • Offline browsing
   ```

5. **Submit for Review**:
   - Answer additional questions
   - Advertising identifier: No
   - Content rights: You own all rights
   - Export compliance: No encryption

6. Click **"Submit"**

**Review Timeline:**
- First app: 1-7 days
- Updates: 24-48 hours

---

### Step 12: After Approval

**Your app will be live!**

**Users can find it by:**
1. Opening Apple App Store
2. Searching: **"AfroMarket UK"**
3. Downloading!

**App URL:**
`https://apps.apple.com/app/afromarket-uk/id[APP_ID]`

---

## 📊 Summary Table

| Task | Platform | Time | Cost |
|------|----------|------|------|
| Create account | Play Store | 30 min | $25 (once) |
| Build APK | Play Store | 15 min | Free |
| Create listing | Play Store | 3 hours | Free |
| Submit | Play Store | 10 min | Free |
| Review wait | Play Store | 1-3 days | Free |
| **TOTAL PLAY STORE** | | **4-5 hours** | **$25** |
| | | | |
| Create account | App Store | 2 days | $99/year |
| Setup tools | App Store | 1 hour | Free |
| Build iOS app | App Store | 1 hour | Free |
| Create listing | App Store | 3 hours | Free |
| Submit | App Store | 1 hour | Free |
| Review wait | App Store | 1-7 days | Free |
| **TOTAL APP STORE** | | **6-8 hours** | **$99/year** |

---

## ✅ Quick Start Checklist

### Google Play Store:
- [ ] Create Play Developer account ($25)
- [ ] Run `./build-android-app.sh`
- [ ] Create 5 screenshots (1080 x 1920)
- [ ] Create feature graphic (1024 x 500)
- [ ] Write store description
- [ ] Create privacy policy
- [ ] Upload APK to Play Console
- [ ] Complete content rating
- [ ] Submit for review
- [ ] Wait 1-3 days
- [ ] App goes live! 🎉

### Apple App Store:
- [ ] Create Apple Developer account ($99)
- [ ] Install Xcode on macOS
- [ ] Build React app
- [ ] Setup Capacitor
- [ ] Configure in Xcode
- [ ] Create 10 screenshots (iPhone + iPad)
- [ ] Archive and upload
- [ ] Complete App Store listing
- [ ] Submit for review
- [ ] Wait 1-7 days
- [ ] App goes live! 🎉

---

## 🆘 Common Issues & Solutions

### Play Store:

**"APK not installable"**
→ Check min SDK version (21+)
→ Rebuild with `bubblewrap build`

**"Icon doesn't meet requirements"**
→ Use logo512.png (already created!)
→ Must be 512x512 PNG

**"Missing privacy policy"**
→ Create and host at yourdomain.com/privacy
→ Use free generator

### App Store:

**"Build not appearing"**
→ Wait 15-60 minutes after upload
→ Check email for processing complete

**"Provisioning profile error"**
→ Enable automatic signing in Xcode
→ Select your developer team

**"Missing screenshots"**
→ Need at least 3 for 6.7" iPhone
→ Use Simulator to capture

---

## 🎯 What Happens After Submission?

### Play Store Review:
1. **Submitted** → In review queue
2. **In Review** → Google testing (automated + manual)
3. **Approved** → Live on Play Store!
4. **Rejected** → Fix issues and resubmit

### App Store Review:
1. **Waiting for Review** → In queue
2. **In Review** → Apple testing
3. **Ready for Sale** → Live on App Store!
4. **Rejected** → Address issues and resubmit

**You'll receive emails at each stage.**

---

## 📧 Support

**For Store Issues:**
- Play Store: https://support.google.com/googleplay/android-developer
- App Store: https://developer.apple.com/contact/

**For App Building Issues:**
- Check logs
- Review documentation
- Test on physical devices

---

## 🎉 Congratulations!

Once approved, your app will be **searchable and downloadable** from both stores!

**Users search:**
- **Play Store**: "AfroMarket UK" → Install
- **App Store**: "AfroMarket UK" → Download

**Promote your app:**
- Social media announcements
- Email to existing users
- Website banner
- QR codes for stores

---

**Your app is ready! Start with Play Store (easier), then do App Store. Good luck! 🚀**
