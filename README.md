<p align="center">
  <img src="docs/screenshots/banner.png" alt="FinQuest" width="800" />
</p>

<p align="center">
  <a href="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white"><img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" /></a>
  <a href="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white"><img src="https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white" /></a>
  <a href="https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white"><img src="https://img.shields.io/badge/Bootstrap-5-7952B3?logo=bootstrap&logoColor=white" /></a>
</p>

<h1 align="center">FinQuest</h1>

FinQuest — обучающий веб‑сервис в формате коротких игровых уровней по темам личных финансов: накопления, базовая безопасность, противодействие мошенничеству, финансовые цели. Пользователь проходит уровни, получает мгновенную обратную связь, зарабатывает очки/монеты и достижения. Проект спроектирован как встраиваемый модуль для мобильного приложения (адаптивная вёрстка).

## Возможности
- Темы и уровни с карточками: тема, сложность, награды
- Прохождение уровней (викторина) с мгновенной обратной связью
- Подсказки на уровне (покупка за монеты)
- Прогресс по уровням, лучшая попытка (best score), число попыток
- Достижения (например, «Мастер темы»), серии (streak) по дням
- Уведомления: получение при достижении и при разрыве серии; лента уведомлений
- Профиль пользователя: аватар, очки, монеты, прогресс по темам, достижения
- Раздел «Медиа»: статьи по темам

## Технологии
- Django 5, Bootstrap 5
- Кастомная модель пользователя `accounts.User`
- PostgreSQL по умолчанию (перенастраивается через переменные окружения)

## Скриншоты

> Поместите изображения в `docs/screenshots/` (названия ниже), чтобы превью отобразились.

| Дашборд | Уровни по теме |
|---|---|
| <img src="docs/screenshots/dashboard.png" alt="Dashboard" width="400" /> | <img src="docs/screenshots/topic.png" alt="Topic Levels" width="400" /> |

| Прохождение уровня | Результат уровня |
|---|---|
| <img src="docs/screenshots/level.png" alt="Level Play" width="400" /> | <img src="docs/screenshots/result.png" alt="Level Result" width="400" /> |

| Уведомления | Профиль |
|---|---|
| <img src="docs/screenshots/notifications.png" alt="Notifications" width="400" /> | <img src="docs/screenshots/profile.png" alt="Profile" width="400" /> |

## Быстрый старт (локально)

### 1) Клонирование и окружение
```bash
git clone <repo-url>
cd FinQuest
python -m venv .venv
# Windows PowerShell
. .venv\Scripts\Activate.ps1
# macOS/Linux
# source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Переменные окружения
Создайте файл `.env` (или задайте переменные в среде):
```env
DJANGO_SECRET_KEY=dev-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=finquest
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
```
> Примечание: `finquest/settings.py` читает параметры из окружения; при их отсутствии используются dev-значения.

### 3) Миграции и демо-данные
```bash
python manage.py migrate
# Опционально: загрузка фикстур с демо-данными
python manage.py loaddata game/fixtures/finquest_full.json
```

### 4) Запуск dev‑сервера
```bash
python manage.py runserver
```
Откройте `http://127.0.0.1:8000/`.

### 6) Скриншоты (опционально)
Сделайте скриншоты ключевых экранов и положите их в `docs/screenshots/` под именами:
`banner.png`, `dashboard.png`, `topic.png`, `level.png`, `result.png`, `notifications.png`, `profile.png`.

### 5) Суперпользователь
```bash
python manage.py createsuperuser
```

## Основные URL
- `/` — дашборд (после логина)
- `/accounts/login`, `/accounts/register` — аутентификация
- `/topic/<id>` — уровни по теме
- `/level/<id>` — прохождение уровня
- `/notifications/` — лента уведомлений
- `/media/` — статьи
- `/accounts/profile/` — профиль

## Заметки по продукту
- Награды начисляются один раз за уровень при первом успешном прохождении
- «Лучшая попытка» обновляется при каждом улучшении результата
- Подсказки покупаются за монеты в пределах текущей сессии (для демо); можно расширить до истории покупок
- Уведомления простые, без фоновых задач; для продакшена стоит использовать Celery/CRON

## Дальнейшее развитие
- Расширить типы уровней (квест/симуляция/сортировка) с UI
- Добавить фоновые напоминания (серии, новые уровни) через Celery
- Улучшить магазин аватаров/косметики
- i18n для мультиязычной версии
