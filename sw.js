const CACHE = 'luftfahrt-v27';

const SHELL = [
  './',
  './index.html',
  './icon.svg',
  './manifest.json',
];

// Live-API-Domains → immer Netzwerk, nie cachen
const NETWORK_ONLY = [
  'aviationweather.gov',
  'api.adsb.fi',
  'globe.adsbexchange.com',
  'opensky-network.org',
  'api.brightsky.dev',
  'allorigins.win',
  'corsproxy.io',
  'codetabs.com',
  'overpass-api.de',
  'opentopodata.org',
];

// ── Install ────────────────────────────────────────────────────────────────
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(SHELL))
      .then(() => self.skipWaiting())
  );
});

// ── Activate: alte Caches löschen ─────────────────────────────────────────
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ── Fetch ──────────────────────────────────────────────────────────────────
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);

  // Nur GET cachen
  if (e.request.method !== 'GET') return;

  // Live-APIs: immer Netzwerk
  if (NETWORK_ONLY.some(h => url.hostname.includes(h))) return;

  // HTML-Seiten (Navigationen): IMMER zuerst Netzwerk → Updates sofort sichtbar,
  // Cache nur als Offline-Fallback.
  if (e.request.mode === 'navigate' ||
      (url.origin === self.location.origin && url.pathname.endsWith('.html'))) {
    e.respondWith(networkFirst(e.request));
    return;
  }

  // GitHub Raw JSON (Katalogdaten): Stale-While-Revalidate
  if (url.hostname === 'raw.githubusercontent.com') {
    e.respondWith(staleWhileRevalidate(e.request));
    return;
  }

  // CDN-Assets (Leaflet, Globe.gl, Fonts): Cache-First
  if (['unpkg.com', 'fonts.googleapis.com', 'fonts.gstatic.com'].some(h => url.hostname.includes(h))) {
    e.respondWith(cacheFirst(e.request));
    return;
  }

  // Same-Origin (Shell): Stale-While-Revalidate – sofort aus Cache, im Hintergrund aktualisieren
  if (url.origin === self.location.origin) {
    e.respondWith(staleWhileRevalidate(e.request));
  }
});

// ── Strategien ─────────────────────────────────────────────────────────────
async function cacheFirst(req) {
  const cached = await caches.match(req);
  if (cached) return cached;
  const res = await fetch(req);
  if (res.ok) {
    const cache = await caches.open(CACHE);
    cache.put(req, res.clone());
  }
  return res;
}

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    const res = await fetch(req);
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch (e) {
    const cached = await cache.match(req);
    return cached || Response.error();
  }
}

async function staleWhileRevalidate(req) {
  const cache = await caches.open(CACHE);
  const cached = await cache.match(req);
  const fetchPromise = fetch(req).then(res => {
    if (res.ok) cache.put(req, res.clone());
    return res;
  }).catch(() => null);
  return cached || await fetchPromise;
}
