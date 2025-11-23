// Service Worker для PWA
const CACHE_NAME = 'finquest-v1';
const urlsToCache = [
  '/',
  '/static/css/bootstrap.min.css',
  '/static/css/finquest.css',
  '/static/css/mobile.css',
  '/static/css/mobile-app.css',
  '/static/js/bootstrap.bundle.min.js',
  '/static/js/finquest.js',
];

// Установка Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Обслуживание кешированного контента
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Возвращаем кешированный ответ или делаем запрос к сети
        return response || fetch(event.request);
      })
  );
});

// Обновление Service Worker
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

