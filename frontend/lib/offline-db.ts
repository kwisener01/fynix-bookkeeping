const DB_NAME = 'fynix-offline';
const DB_VERSION = 1;
const RECEIPTS_STORE = 'pending-receipts';

export interface PendingReceipt {
  id: string;
  file: Blob;
  clientId: string;
  timestamp: number;
  retryCount: number;
}

class OfflineDB {
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    if (this.db) return;

    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => {
        console.error('IndexedDB error:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('IndexedDB initialized');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        if (!db.objectStoreNames.contains(RECEIPTS_STORE)) {
          const store = db.createObjectStore(RECEIPTS_STORE, { keyPath: 'id' });
          store.createIndex('timestamp', 'timestamp', { unique: false });
          store.createIndex('clientId', 'clientId', { unique: false });
          console.log('Created receipts object store');
        }
      };
    });
  }

  async addReceipt(receipt: PendingReceipt): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([RECEIPTS_STORE], 'readwrite');
      const store = transaction.objectStore(RECEIPTS_STORE);
      const request = store.add(receipt);

      request.onsuccess = () => {
        console.log('Receipt added to offline queue:', receipt.id);
        resolve();
      };

      request.onerror = () => {
        console.error('Error adding receipt:', request.error);
        reject(request.error);
      };
    });
  }

  async getPendingReceipts(): Promise<PendingReceipt[]> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([RECEIPTS_STORE], 'readonly');
      const store = transaction.objectStore(RECEIPTS_STORE);
      const request = store.getAll();

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        console.error('Error getting receipts:', request.error);
        reject(request.error);
      };
    });
  }

  async getReceiptById(id: string): Promise<PendingReceipt | null> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([RECEIPTS_STORE], 'readonly');
      const store = transaction.objectStore(RECEIPTS_STORE);
      const request = store.get(id);

      request.onsuccess = () => {
        resolve(request.result || null);
      };

      request.onerror = () => {
        console.error('Error getting receipt:', request.error);
        reject(request.error);
      };
    });
  }

  async removeReceipt(id: string): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([RECEIPTS_STORE], 'readwrite');
      const store = transaction.objectStore(RECEIPTS_STORE);
      const request = store.delete(id);

      request.onsuccess = () => {
        console.log('Receipt removed from offline queue:', id);
        resolve();
      };

      request.onerror = () => {
        console.error('Error removing receipt:', request.error);
        reject(request.error);
      };
    });
  }

  async updateRetryCount(id: string): Promise<void> {
    if (!this.db) await this.init();

    const receipt = await this.getReceiptById(id);
    if (!receipt) return;

    receipt.retryCount += 1;

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([RECEIPTS_STORE], 'readwrite');
      const store = transaction.objectStore(RECEIPTS_STORE);
      const request = store.put(receipt);

      request.onsuccess = () => {
        resolve();
      };

      request.onerror = () => {
        console.error('Error updating retry count:', request.error);
        reject(request.error);
      };
    });
  }

  async clearAll(): Promise<void> {
    if (!this.db) await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([RECEIPTS_STORE], 'readwrite');
      const store = transaction.objectStore(RECEIPTS_STORE);
      const request = store.clear();

      request.onsuccess = () => {
        console.log('All receipts cleared from offline queue');
        resolve();
      };

      request.onerror = () => {
        console.error('Error clearing receipts:', request.error);
        reject(request.error);
      };
    });
  }
}

// Singleton instance
export const offlineDB = new OfflineDB();
