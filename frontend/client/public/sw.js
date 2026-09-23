// ShikshaSetu Service Worker for offline support and faster repeat visits
// Version 1.0.0

const CACHE_NAME = 'shikshasetu-v1';
const RUNTIME_CACHE = 'shikshasetu-runtime-v1';

// Assets to cache on install
const PRECACHE_ASSETS = [
  '/',
  '/assets/shikshasetu-logo.png',
  '/assets/shikshasetu-icon.png',
  '/shikshasetu-square.svg',
  '/shikshasetu-icon.svg',
  '/favicon.ico',
];

// Cache strategies
const CACHE_STRATEGIES = {
  // Images: Cache first, network fallback
  images: /\.(png|jpg|jpeg|gif|svg|webp|ico)$/i,
  // Fonts: Cache first
  fonts: /\.(woff|woff2|ttf|eot)$/i,
  // Scripts and styles: Network first, cache fallback
  assets: /\.(js|css)$/i,
  // API calls: Network only
  api: /\/api\//i,
};

// Install event - cache critical assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches
      .open(CACHE_NAME)
      .then((cache) => {
        console.log('[SW] Precaching assets');
        return cache.addAll(PRECACHE_ASSETS);
      })
      .then(() => self.skipWaiting())
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches
      .keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE)
            .map((name) => {
              console.log('[SW] Deleting old cache:', name);
              return caches.delete(name);
            })
        );
      })
      .then(() => self.clients.claim())
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip cross-origin requests
  if (url.origin !== self.location.origin) {
    return;
  }

  // API requests: Network only (always fresh data)
  if (CACHE_STRATEGIES.api.test(url.pathname)) {
    event.respondWith(fetch(request));
    return;
  }

  // Images and fonts: Cache first, network fallback
  if (
    CACHE_STRATEGIES.images.test(url.pathname) ||
    CACHE_STRATEGIES.fonts.test(url.pathname)
  ) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Scripts and styles: Network first, cache fallback
  if (CACHE_STRATEGIES.assets.test(url.pathname)) {
    event.respondWith(networkFirst(request));
    return;
  }

  // HTML pages: Network first, cache fallback
  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request));
    return;
  }

  // Default: Network first
  event.respondWith(networkFirst(request));
});

// Cache first strategy
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    console.error('[SW] Cache first failed:', error);
    throw error;
  }
}

// Network first strategy
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await caches.match(request);
    if (cached) {
      console.log('[SW] Serving from cache:', request.url);
      return cached;
    }
    throw error;
  }
}

// Listen for messages from the main thread
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
