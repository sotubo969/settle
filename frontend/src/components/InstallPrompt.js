import React, { useState, useEffect } from 'react';
import { Download, X } from 'lucide-react';
import { Button } from './ui/button';
import { Card } from './ui/card';

/**
 * InstallPrompt Component
 * Shows a prompt to install the PWA app on user's device
 */
function InstallPrompt() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
      return;
    }

    // Check if iOS
    const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    setIsIOS(iOS);

    // Handle beforeinstallprompt event (Android/Desktop)
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      
      // Check if user dismissed before
      const dismissed = localStorage.getItem('pwa-prompt-dismissed');
      if (!dismissed) {
        setTimeout(() => setShowPrompt(true), 3000); // Show after 3 seconds
      }
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);

    // Handle app installed
    const handleAppInstalled = () => {
      setShowPrompt(false);
      setDeferredPrompt(null);
      setIsInstalled(true);
      localStorage.removeItem('pwa-prompt-dismissed');
    };

    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (!deferredPrompt) return;

    // Show the install prompt
    deferredPrompt.prompt();

    // Wait for the user's response
    const { outcome } = await deferredPrompt.userChoice;
    
    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
    } else {
      console.log('User dismissed the install prompt');
    }

    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-prompt-dismissed', 'true');
    // Auto-show again after 7 days
    setTimeout(() => {
      localStorage.removeItem('pwa-prompt-dismissed');
    }, 7 * 24 * 60 * 60 * 1000);
  };

  // Don't show if already installed
  if (isInstalled) return null;

  // iOS Install Instructions
  if (isIOS && showPrompt) {
    return (
      <div className="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-4 md:w-96">
        <Card className="p-4 shadow-2xl border-2 border-green-600 bg-white">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="bg-green-100 p-2 rounded-lg">
                <Download className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="font-bold text-lg">Install AfroMarket App</h3>
            </div>
            <button 
              onClick={handleDismiss}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <div className="text-sm text-gray-600 space-y-2 mb-4">
            <p>Install our app for a better experience!</p>
            <div className="bg-blue-50 p-3 rounded-lg space-y-1">
              <p className="font-semibold text-blue-900">To install on iOS:</p>
              <ol className="list-decimal list-inside space-y-1 text-blue-800">
                <li>Tap the Share button <span className="inline-block px-2 py-1 bg-blue-200 rounded">⎋</span></li>
                <li>Scroll down and tap "Add to Home Screen"</li>
                <li>Tap "Add" to confirm</li>
              </ol>
            </div>
          </div>
          
          <Button 
            onClick={handleDismiss}
            className="w-full"
            variant="outline"
          >
            Got it!
          </Button>
        </Card>
      </div>
    );
  }

  // Android/Desktop Install Prompt
  if (showPrompt && deferredPrompt) {
    return (
      <div className="fixed bottom-4 left-4 right-4 z-50 md:left-auto md:right-4 md:w-96">
        <Card className="p-4 shadow-2xl border-2 border-green-600 bg-white">
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="bg-green-100 p-2 rounded-lg">
                <Download className="h-5 w-5 text-green-600" />
              </div>
              <h3 className="font-bold text-lg">Install AfroMarket App</h3>
            </div>
            <button 
              onClick={handleDismiss}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          <p className="text-sm text-gray-600 mb-4">
            Install our app for faster access, offline browsing, and push notifications!
          </p>
          
          <div className="flex gap-2">
            <Button 
              onClick={handleInstallClick}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              <Download className="h-4 w-4 mr-2" />
              Install App
            </Button>
            <Button 
              onClick={handleDismiss}
              variant="outline"
            >
              Later
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return null;
}

export default InstallPrompt;
