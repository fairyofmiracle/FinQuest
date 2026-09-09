# FinQuest — финансовая грамотность в игровой форме

<div align="center">

![FinQuest Logo](static/images/topics/basics.svg)

**Образовательная платформа с геймификацией** · Django · PWA  
Команда **«Джунцы»** · IT-Sprint 2025

[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PWA](https://img.shields.io/badge/PWA-Ready-purple.svg)](https://web.dev/progressive-web-apps/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## Возможности

- XP, уровни, достижения, рейтинг, ежедневные задания
- Статьи, тесты, прогресс по темам
- PWA: мобильная вёрстка, тёмная тема, офлайн (Service Worker)
- Светлая / тёмная тема

---

## Быстрый старт

```bash
git clone https://github.com/fairyofmiracle/FinQuest.git
cd FinQuest

python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py create_new_structure
python manage.py create_daily_quests
python manage.py createsuperuser
python manage.py runserver
```

### Подробный запуск: [SETUP.md](SETUP.md)
