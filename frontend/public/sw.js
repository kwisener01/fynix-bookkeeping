const CACHE_VERSION = 'v1';
const STATIC_CACHE = `fynix-static-${CACHE_VERSION}`;
const API_CACHE = `fynix-api-${CACHE_VERSION}`;
const OFFLINE_RECEIPTS_DB = 'fynix-offline-receipts';

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  event.waitUntil(
    caches.open(STATIC_CACHE).then((cache) => {
      return cache.addAll([
        '/',
        '/manifest.json',
      ]).catch(err => {
        console.log('Cache addAll error:', err);
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName.startsWith('fynix-') && cacheName !== STATIC_CACHE && cacheName !== API_CACHE) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network-first strategy with offline fallback
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-HTTP requests
  if (!request.url.startsWith('http')) {
    return;
  }

  // API calls: network-first, with offline handling
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          // Clone and cache successful responses
          if (response.ok) {
            const responseClone = response.clone();
            caches.open(API_CACHE).then(cache => {
              cache.put(request, responseClone);
            });
          }
          return response;
        })
        .catch(async (error) => {
          console.log('Fetch failed, checking cache:', url.pathname);

          // For receipt uploads, queue for later
          if (request.method === 'POST' && url.pathname.includes('/receipts/capture')) {
            // Send message to client about offline status
            const clients = await self.clients.matchAll();
            clients.forEach(client => {
              client.postMessage({
                type: 'OFFLINE_RECEIPT',
                message: 'Receipt queued for upload when online'
              });
            });

            // Return a custom offline response
            return new Response(
              JSON.stringify({
                status: 'queued',
                message: 'Receipt will be uploaded when online',
                offline: true
              }),
              {
                status: 202,
                headers: { 'Content-Type': 'application/json' }
              }
            );
          }

          // Try cache for other requests
          const cachedResponse = await caches.match(request);
          if (cachedResponse) {
            return cachedResponse;
          }

          // Return offline page or error
          return new Response(
            JSON.stringify({ error: 'Offline and no cached data available' }),
            {
              status: 503,
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
    );
  }
  // Static assets and pages: cache-first
  else {
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }

        return fetch(request).then((response) => {
          // Cache successful responses
          if (response.ok && request.method === 'GET') {
            const responseClone = response.clone();
            caches.open(STATIC_CACHE).then((cache) => {
              cache.put(request, responseClone);
            });
          }
          return response;
        }).catch(err => {
          console.log('Fetch error:', err);
          // Return a basic offline page
          return new Response('Offline', { status: 503 });
        });
      })
    );
  }
});

// Background sync for offline receipts
self.addEventListener('sync', (event) => {
  console.log('Background sync event:', event.tag);

  if (event.tag === 'sync-receipts') {
    event.waitUntil(syncOfflineReceipts());
  }
});

// Function to sync offline receipts (to be implemented with IndexedDB)
async function syncOfflineReceipts() {
  console.log('Syncing offline receipts...');

  // This will be enhanced when IndexedDB helper is integrated
  const clients = await self.clients.matchAll();
  clients.forEach(client => {
    client.postMessage({
      type: 'SYNC_RECEIPTS',
      message: 'Attempting to sync offline receipts'
    });
  });
}

// Handle messages from clients
self.addEventListener('message', (event) => {
  console.log('Service Worker received message:', event.data);

  if (event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (cacheName.startsWith('fynix-')) {
              return caches.delete(cacheName);
            }
          })
        );
      })
    );
  }
});
