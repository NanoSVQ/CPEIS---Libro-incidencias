/* Libro de incidencias — Service worker
 * Permite abrir la app sin cobertura (guarda una copia de index.html y del icono).
 * Estrategia "red primero": si hay conexión siempre carga la última versión publicada.
 * Las peticiones a Google Apps Script NO pasan por aquí (son de otro dominio).
 */
const CACHE = 'libro-incidencias-v1';
const ARCHIVOS = ['./', './index.html', './apple-touch-icon.png'];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE).then((c) => c.addAll(ARCHIVOS)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;

  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      const ctrl = new AbortController();
      const t = setTimeout(() => ctrl.abort(), 5000);
      const res = await fetch(url.href, { signal: ctrl.signal, cache: 'no-store', credentials: 'same-origin' });
      clearTimeout(t);
      if (res && res.ok) cache.put(req, res.clone());
      return res;
    } catch (err) {
      const hit = (await cache.match(req, { ignoreSearch: true })) ||
        (req.mode === 'navigate' ? await cache.match('./index.html') : null);
      if (hit) return hit;
      throw err;
    }
  })());
});
