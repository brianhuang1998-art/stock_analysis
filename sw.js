// Service worker: lets the site open offline once it has been visited.
// Network first (so a fresh deploy shows up right away), falling back to the cache when offline.
// Bump CACHE_VERSION only if you want to force-clear old cached files.
const CACHE_VERSION = 'v1';
const CACHE = 'brian-toolbox-' + CACHE_VERSION;

// The page list comes from site-config.js, so a new page is cached automatically
importScripts('config/site-config.js');
const PAGES = [self.SITE.home.href];
self.SITE.categories.forEach(c => {
  PAGES.push(c.href);
  c.tools.forEach(t => { if(!t.soon && t.href) PAGES.push(t.href); });
});
const PRECACHE = PAGES.concat([
  'config/site-config.js', 'assets/js/util.js', 'assets/js/nav.js', 'assets/js/stepper.js',
  'assets/js/calc.js', 'assets/js/trade_math.js', 'assets/js/chart.js', 'assets/js/mc.js', 'assets/css/styles.css',
  'manifest.json', 'assets/icons/favicon.svg', 'assets/icons/icon-192.png'
]);

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('brian-toolbox-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if(req.method !== 'GET' || new URL(req.url).origin !== location.origin) return; // skip GitHub API etc.
  e.respondWith(
    fetch(req).then(res => {
      if(res.ok){
        const copy = res.clone();
        caches.open(CACHE).then(c => c.put(req, copy));
      }
      return res;
    }).catch(() => caches.match(req).then(hit => hit || caches.match('./')))
  );
});
