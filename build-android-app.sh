#!/bin/bash

# AfroMarket UK - Android APK Build Script
# This script automates the Android app build process using Bubblewrap

echo "🚀 AfroMarket UK - Android APK Builder"
echo "======================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Bubblewrap is installed
if ! command -v bubblewrap &> /dev/null; then
    echo -e "${RED}❌ Bubblewrap not found${NC}"
    echo "Installing Bubblewrap CLI..."
    npm install -g @bubblewrap/cli
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to install Bubblewrap${NC}"
        exit 1
    fi
fi

# Check if JDK is installed
if ! command -v java &> /dev/null; then
    echo -e "${YELLOW}⚠️  JDK not found${NC}"
    echo "Please install JDK 17:"
    echo "  Ubuntu/Debian: sudo apt install openjdk-17-jdk"
    echo "  macOS: brew install openjdk@17"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Configuration
echo "📝 Configuration:"
echo "   App Name: AfroMarket UK"
echo "   Package ID: uk.afromarket.app"
echo "   Domain: [YOUR_DOMAIN_HERE]"
echo ""

read -p "Enter your domain (e.g., afromarket.uk): " DOMAIN

if [ -z "$DOMAIN" ]; then
    echo -e "${RED}Domain cannot be empty${NC}"
    exit 1
fi

MANIFEST_URL="https://$DOMAIN/manifest.json"

echo ""
echo "🔨 Building Android app..."
echo ""

# Create twa-manifest.json if it doesn't exist
if [ ! -f "twa-manifest.json" ]; then
    echo "Creating twa-manifest.json..."
    
    cat > twa-manifest.json << EOF
{
  "packageId": "uk.afromarket.app",
  "host": "$DOMAIN",
  "name": "AfroMarket UK",
  "launcherName": "AfroMarket",
  "display": "standalone",
  "themeColor": "#059669",
  "backgroundColor": "#ffffff",
  "startUrl": "/",
  "iconUrl": "https://$DOMAIN/logo512.png",
  "maskableIconUrl": "https://$DOMAIN/logo512.png",
  "shortcuts": [
    {
      "name": "Browse Products",
      "short_name": "Products",
      "url": "/products",
      "icon": "https://$DOMAIN/logo192.png"
    },
    {
      "name": "My Cart",
      "short_name": "Cart",
      "url": "/cart",
      "icon": "https://$DOMAIN/logo192.png"
    }
  ],
  "generatorApp": "bubblewrap-cli",
  "webManifestUrl": "$MANIFEST_URL",
  "fallbackType": "customtabs",
  "enableNotifications": true,
  "enableSiteSettingsShortcut": true,
  "isChromeOSOnly": false,
  "orientation": "default",
  "fingerprints": [],
  "additionalTrustedOrigins": [],
  "appVersionName": "1.0.0",
  "appVersionCode": 1,
  "splashScreenFadeOutDuration": 300,
  "minSdkVersion": 21,
  "targetSdkVersion": 33
}
EOF
    
    echo -e "${GREEN}✅ Created twa-manifest.json${NC}"
fi

# Build the APK
echo ""
echo "Building APK... (this may take 5-10 minutes)"
echo ""

bubblewrap build --skipPwaValidation

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 SUCCESS! Android app built successfully!${NC}"
    echo ""
    echo "📦 APK Location:"
    echo "   ./app-release-signed.apk"
    echo ""
    echo "📱 Next Steps:"
    echo "   1. Test on Android device:"
    echo "      adb install app-release-signed.apk"
    echo ""
    echo "   2. Upload to Google Play Console:"
    echo "      https://play.google.com/console"
    echo ""
    echo "   3. Create store listing:"
    echo "      - Add screenshots"
    echo "      - Write description"
    echo "      - Submit for review"
    echo ""
    
    # Show file size
    APK_SIZE=$(du -h app-release-signed.apk | cut -f1)
    echo "   APK Size: $APK_SIZE"
    echo ""
else
    echo -e "${RED}❌ Build failed${NC}"
    echo "Check the errors above and try again"
    exit 1
fi
