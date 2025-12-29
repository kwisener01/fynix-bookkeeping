import { useEffect, useState, useCallback } from 'react';
import { offlineDB } from '@/lib/offline-db';
import { api } from '@/lib/api';

export function useOfflineSync() {
  const [pendingCount, setPendingCount] = useState(0);
  const [syncing, setSyncing] = useState(false);
  const [isOnline, setIsOnline] = useState(true);

  const checkPending = useCallback(async () => {
    try {
      const pending = await offlineDB.getPendingReceipts();
      setPendingCount(pending.length);
    } catch (error) {
      console.error('Error checking pending receipts:', error);
    }
  }, []);

  const syncPendingReceipts = useCallback(async () => {
    if (syncing || !navigator.onLine) {
      console.log('Cannot sync: syncing=' + syncing + ', online=' + navigator.onLine);
      return;
    }

    console.log('Starting sync of pending receipts...');
    setSyncing(true);

    try {
      const pending = await offlineDB.getPendingReceipts();
      console.log(`Found ${pending.length} pending receipts to sync`);

      for (const receipt of pending) {
        try {
          // Convert Blob back to File
          const file = new File([receipt.file], `receipt_${receipt.id}.jpg`, {
            type: 'image/jpeg',
          });

          console.log(`Uploading receipt ${receipt.id}...`);
          await api.uploadReceipt(file, receipt.clientId);

          // Success - remove from queue
          await offlineDB.removeReceipt(receipt.id);
          console.log(`Receipt ${receipt.id} synced successfully`);
        } catch (error) {
          console.error(`Failed to sync receipt ${receipt.id}:`, error);

          // Update retry count
          await offlineDB.updateRetryCount(receipt.id);

          // If too many retries, remove from queue
          if (receipt.retryCount >= 3) {
            console.warn(`Receipt ${receipt.id} exceeded retry limit, removing`);
            await offlineDB.removeReceipt(receipt.id);
          }
        }
      }
    } catch (error) {
      console.error('Error during sync:', error);
    } finally {
      setSyncing(false);
      await checkPending();
    }
  }, [syncing, checkPending]);

  useEffect(() => {
    // Initial check
    checkPending();

    // Set up online/offline listeners
    const handleOnline = () => {
      console.log('Network online');
      setIsOnline(true);
      syncPendingReceipts();
    };

    const handleOffline = () => {
      console.log('Network offline');
      setIsOnline(false);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    // Check initial online status
    setIsOnline(navigator.onLine);

    // Set up periodic sync check (every 30 seconds when online)
    const syncInterval = setInterval(() => {
      if (navigator.onLine && pendingCount > 0 && !syncing) {
        syncPendingReceipts();
      }
    }, 30000);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      clearInterval(syncInterval);
    };
  }, [pendingCount, syncing, syncPendingReceipts, checkPending]);

  return {
    pendingCount,
    syncing,
    isOnline,
    syncNow: syncPendingReceipts,
    refreshCount: checkPending,
  };
}
