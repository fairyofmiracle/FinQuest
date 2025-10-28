# ⚡ Быстрая настройка безопасности (5 минут)

## Шаг 1: Обновите settings.py

Откройте `finquest/settings.py` и добавьте:

### 1.1 Middleware (добавьте в конец списка MIDDLEWARE)
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # 👇 ДОБАВЬТЕ ЭТИ ДВЕ СТРОКИ
    'game.middleware.RateLimitMiddleware',
    'game.middleware.SecurityHeadersMiddleware',
]
```

### 1.2 Кэш (добавьте в конец файла)
```python
# Кэш для rate limiting
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### 1.3 Дополнительные настройки безопасности (добавьте в конец)
```python
# Session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## Шаг 2: Примените миграцию

Откройте терминал и выполните:

```bash
python manage.py migrate
```

Эта команда добавит индексы в БД для ускорения запросов.

---

## Шаг 3: Запустите тесты

```bash
python manage.py test game.test_security
```

Если все тесты прошли ✅ - поздравляем, безопасность настроена!

---

## Шаг 4: Проверка

```bash
python manage.py check --deploy
```

Эта команда проверит, готов ли проект к production.

---

## ✅ Готово!

Теперь ваше приложение защищено от:
- ✅ Brute-force атак (rate limiting)
- ✅ XSS атак
- ✅ CSRF атак
- ✅ Clickjacking
- ✅ SQL инъекций
- ✅ MIME sniffing

---

## 📚 Дополнительно

Для более детальной настройки см. `SECURITY_SETUP.md`

---

## ⚠️ Важно для Production

Перед запуском на production также настройте:
1. `DEBUG = False`
2. `SECRET_KEY` в переменных окружения
3. `ALLOWED_HOSTS = ['ваш-домен.com']`
4. HTTPS (Let's Encrypt)
5. Redis вместо LocMemCache

Подробнее в `SECURITY_SETUP.md` раздел "Production Checklist"

