// Service worker: lets the site open offline once it has been visited.
// Network first (so a fresh deploy shows up right away), falling back to the cache when offline.
// Bump CACHE_VERSION only if you want to force-clear old cached files.
const CACHE_VERSION = 'v1';
const CACHE = 'brian-toolbox-' + CACHE_VERSION;
const PRECACHE = [
  'home_page.html', 'tools.html', 'trading_position.html', 'valuation_analysis.html', 'dividend_cashflow.html',
  'etf_calculator.html', 'stock_calculator.html', 'target_price_calculator.html', 'avg_cost_calculator.html', 'dca_calculator.html',
  'styles.css', 'nav.js', 'stepper.js', 'calc.js', 'trade_math.js', 'manifest.json', 'icon-192.png'
];

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
    }).catch(() => caches.match(req).then(hit => hit || caches.match('home_page.html')))
  );
});
