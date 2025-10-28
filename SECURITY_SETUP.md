# Настройка безопасности проекта

## 1. Подключение Middleware

Добавьте в `finquest/settings.py` в раздел `MIDDLEWARE`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
    # НОВЫЕ MIDDLEWARE ДЛЯ БЕЗОПАСНОСТИ
    'game.middleware.RateLimitMiddleware',           # Rate limiting
    'game.middleware.SecurityHeadersMiddleware',     # Security headers
]
```

## 2. Настройка кэша (для rate limiting)

Добавьте в `settings.py`:

```python
# Кэш для rate limiting (используем локальную память для разработки)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Для production рекомендуется Redis:
# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {
#             'CLIENT_CLASS': 'django_redis.client.DefaultClient',
#         }
#     }
# }
```

## 3. Дополнительные настройки безопасности

Добавьте/обновите в `settings.py`:

```python
# HTTPS/SSL настройки (для production)
SECURE_SSL_REDIRECT = True if not DEBUG else False
SESSION_COOKIE_SECURE = True if not DEBUG else False
CSRF_COOKIE_SECURE = True if not DEBUG else False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Session security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# Password validation (уже должно быть)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Allowed hosts (обязательно настроить для production!)
ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Добавьте ваш домен

# CSRF настройки
CSRF_COOKIE_AGE = 31449600  # 1 год
CSRF_USE_SESSIONS = False

# Security timeout
SESSION_COOKIE_AGE = 1209600  # 2 недели

# Логирование безопасности
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': 'logs/security.log',
        },
    },
    'loggers': {
        'django.security': {
            'handlers': ['file'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
```

## 4. Использование валидаторов

В `game/views.py` используйте валидаторы:

```python
from game.validators import (
    validate_quiz_answer,
    validate_question_index,
    validate_completion_time,
    sanitize_user_input
)
from django.core.exceptions import ValidationError

# Пример использования:
def level_play(request, level_id):
    # ...
    if request.method == "POST":
        try:
            # Валидируем индекс вопроса
            question_index = validate_question_index(
                request.POST.get('question_index', 0),
                len(level.content['questions'])
            )
            
            # Валидируем время
            completion_time = validate_completion_time(
                request.POST.get('completion_time', 0)
            )
            
            # Валидируем ответ
            question = level.content['questions'][question_index]
            answer_data = validate_quiz_answer(request.POST, question)
            
        except ValidationError as e:
            messages.error(request, f"Ошибка валидации: {e}")
            return redirect('level_play', level_id=level.id)
```

## 5. Проверка безопасности

### Автоматическая проверка
```bash
# Установка инструментов
pip install bandit safety

# Проверка кода на уязвимости
bandit -r . -x ./venv/

# Проверка зависимостей
safety check

# Django security check
python manage.py check --deploy
```

### Ручная проверка
1. ✅ Все формы имеют `{% csrf_token %}`
2. ✅ Используется `@login_required` на всех защищенных views
3. ✅ Валидация всех пользовательских данных
4. ✅ Экранирование HTML в шаблонах (Django делает автоматически)
5. ✅ Rate limiting на аутентификации
6. ✅ Security headers

## 6. Регулярное обновление

```bash
# Обновление зависимостей
pip list --outdated
pip install --upgrade django

# Проверка CVE
safety check --json
```

## 7. Production Checklist

- [ ] DEBUG = False
- [ ] SECRET_KEY в переменных окружения
- [ ] ALLOWED_HOSTS настроен
- [ ] HTTPS включен
- [ ] SECURE_* настройки включены
- [ ] Настроен Redis для кэша
- [ ] Логирование настроено
- [ ] Резервное копирование БД
- [ ] Мониторинг ошибок (Sentry)
- [ ] Rate limiting протестирован
- [ ] CSRF protection протестирован

## 8. Мониторинг

Рекомендуемые инструменты:
- **Sentry** - мониторинг ошибок
- **New Relic** - мониторинг производительности
- **Cloudflare** - DDoS защита
- **Let's Encrypt** - SSL сертификаты

## Контакты для вопросов

При обнаружении уязвимостей сообщите разработчикам.

