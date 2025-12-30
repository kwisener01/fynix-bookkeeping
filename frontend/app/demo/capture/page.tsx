'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { LogOut, Wifi, WifiOff, RefreshCw } from 'lucide-react';
import ReceiptUpload from '@/components/ReceiptUpload';
import { getDemoUser, clearDemoUser, getTimeRemaining } from '@/lib/demo-session';
import { useOfflineSync } from '@/hooks/useOfflineSync';
import type { ReceiptUploadResponse } from '@/types';

export default function DemoCapturePage() {
  const router = useRouter();
  const { pendingCount, syncing, isOnline, syncNow } = useOfflineSync();
  const [demoUser, setDemoUser] = useState(getDemoUser());
  const [timeRemaining, setTimeRemaining] = useState('');

  useEffect(() => {
    if (!demoUser) {
      router.push('/');
      return;
    }

    // Update time remaining every minute
    const updateTime = () => setTimeRemaining(getTimeRemaining());
    updateTime();
    const interval = setInterval(updateTime, 60000);

    return () => clearInterval(interval);
  }, [demoUser, router]);

  const handleExitDemo = () => {
    if (confirm('Exit demo? Your session will be cleared.')) {
      clearDemoUser();
      router.push('/');
    }
  };

  const handleSuccess = (response: ReceiptUploadResponse) => {
    console.log('Receipt uploaded successfully:', response);
    // Store result in localStorage for result page
    localStorage.setItem('lastReceiptResult', JSON.stringify(response));
    router.push(`/demo/result?id=${response.receipt_id}`);
  };

  if (!demoUser) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Receipt Capture Demo</h1>
              <p className="text-sm text-gray-500 mt-1">
                Session expires in {timeRemaining}
              </p>
            </div>
            <button
              onClick={handleExitDemo}
              className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Exit Demo
            </button>
          </div>
        </div>
      </header>

      {/* Status Bar */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 py-3">
          <div className="flex items-center justify-between flex-wrap gap-4">
            {/* Network Status */}
            <div className="flex items-center gap-2">
              {isOnline ? (
                <>
                  <Wifi className="w-5 h-5 text-green-500" />
                  <span className="text-sm text-green-600 font-medium">Online</span>
                </>
              ) : (
                <>
                  <WifiOff className="w-5 h-5 text-orange-500" />
                  <span className="text-sm text-orange-600 font-medium">Offline</span>
                </>
              )}
            </div>

            {/* Pending Receipts */}
            {pendingCount > 0 && (
              <div className="flex items-center gap-3">
                <span className="text-sm text-gray-600">
                  {pendingCount} receipt{pendingCount > 1 ? 's' : ''} queued
                </span>
                {isOnline && !syncing && (
                  <button
                    onClick={syncNow}
                    className="flex items-center gap-1 px-3 py-1 text-sm text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Sync Now
                  </button>
                )}
                {syncing && (
                  <span className="flex items-center gap-2 text-sm text-blue-600">
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Syncing...
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8">
        {/* Offline Warning */}
        {!isOnline && (
          <div className="bg-orange-50 border-l-4 border-orange-400 p-4 mb-6 rounded">
            <div className="flex">
              <div className="flex-shrink-0">
                <WifiOff className="h-5 w-5 text-orange-400" />
              </div>
              <div className="ml-3">
                <p className="text-sm text-orange-700">
                  You're offline. Receipts will be saved locally and uploaded automatically when you're back online.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Upload Section */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-gray-900">Upload Receipt</h2>
          <ReceiptUpload clientId={demoUser.id} onSuccess={handleSuccess} />
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3">How it works:</h3>
          <ol className="space-y-2 text-sm text-blue-800">
            <li className="flex gap-2">
              <span className="font-bold">1.</span>
              <span>Tap "Open Camera" (mobile) or drag & drop a receipt image</span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold">2.</span>
              <span>Claude Vision extracts vendor, date, line items, and total</span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold">3.</span>
              <span>AI matches the receipt to active jobs automatically</span>
            </li>
            <li className="flex gap-2">
              <span className="font-bold">4.</span>
              <span>View results and job suggestions instantly</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
