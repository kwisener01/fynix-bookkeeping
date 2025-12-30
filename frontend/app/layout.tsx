'use client';

import { useEffect } from 'react';
import './globals.css';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  useEffect(() => {
    // Clear old cached data on first load
    const clearOldData = () => {
      try {
        // Clear old localStorage data
        const keysToKeep = ['demoUser']; // Keep current demo session
        const keysToRemove: string[] = [];

        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && !keysToKeep.includes(key)) {
            keysToRemove.push(key);
          }
        }

        keysToRemove.forEach(key => {
          console.log('Clearing old data:', key);
          localStorage.removeItem(key);
        });

        console.log('Old data cleared');
      } catch (error) {
        console.error('Error clearing old data:', error);
      }
    };

    clearOldData();

    // Register service worker
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered:', registration);

          // Check for updates periodically
          setInterval(() => {
            registration.update();
          }, 60000); // Check every minute
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });

      // Listen for service worker messages
      navigator.serviceWorker.addEventListener('message', (event) => {
        console.log('Message from SW:', event.data);

        if (event.data.type === 'OFFLINE_RECEIPT') {
          // Could show a toast notification here
          console.log(event.data.message);
        }
      });
    }

    // Handle PWA install prompt
    let deferredPrompt: any;

    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      console.log('PWA install prompt available');

      // Could show custom install button here
    });

    window.addEventListener('appinstalled', () => {
      console.log('PWA installed successfully');
      deferredPrompt = null;
    });
  }, []);

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />

        {/* PWA Meta Tags */}
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#2563eb" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="Fynix" />

        {/* Icons */}
        <link rel="apple-touch-icon" href="/ios/180.png" />
        <link rel="icon" type="image/png" sizes="192x192" href="/android/android-launchericon-192-192.png" />
        <link rel="icon" type="image/png" sizes="512x512" href="/android/android-launchericon-512-512.png" />

        {/* SEO */}
        <title>Fynix Receipt Capture - AI-Powered Receipt Scanning for Contractors</title>
        <meta
          name="description"
          content="Mobile camera receipt capture with Claude Vision AI. Instant extraction and job matching for contractors."
        />

        {/* Open Graph */}
        <meta property="og:title" content="Fynix Receipt Capture" />
        <meta
          property="og:description"
          content="AI-powered receipt scanning for contractors"
        />
        <meta property="og:type" content="website" />
      </head>
      <body>{children}</body>
    </html>
  );
}
