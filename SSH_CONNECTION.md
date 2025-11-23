# 🔐 Подключение к серверу по SSH

## 📋 Что вам нужно:

1. **IP адрес сервера** (например: 192.168.1.100)
2. **Логин** (обычно: `root` или `ubuntu`)
3. **Пароль** или **SSH ключ**
4. **SSH клиент** (уже есть в Windows 10+, Linux, Mac)

---

## 🖥️ Подключение из Windows

### Способ 1: PowerShell/CMD (встроенный SSH)

```powershell
# Базовое подключение
ssh root@ваш-ip-адрес                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                

# Пример:
ssh root@192.168.1.100
```

При первом подключении увидите:
```
The authenticity of host '192.168.1.100 (192.168.1.100)' can't be established.
Are you sure you want to continue connecting (yes/no)?
```
Напишите `yes` и нажмите Enter.

Затем введите пароль (символы не будут видны при вводе - это нормально).

### Способ 2: PuTTY (если SSH не работает)

1. Скачайте PuTTY: https://www.putty.org/
2. Запустите `putty.exe`
3. В поле "Host Name" введите IP адрес
4. Port: `22`
5. Connection type: `SSH`
6. Нажмите "Open"
7. Введите логин и пароль

---

## 🍎 Подключение из macOS/Linux

### Терминал (встроенный SSH)

```bash
# Базовое подключение
ssh root@ваш-ip-адрес

# С указанием порта (если не 22)
ssh -p 2222 root@ваш-ip-адрес

# С SSH ключом
ssh -i путь/к/ключу.pem root@ваш-ip-адрес
```

---

## 🔑 Если используете SSH ключ

### Windows (PowerShell):
```powershell
# 1. Сохраните ключ (например: server_key.pem) в папку
# C:\Users\ВашеИмя\.ssh\

# 2. Установите права (если требуется)
icacls "C:\Users\ВашеИмя\.ssh\server_key.pem" /inheritance:r
icacls "C:\Users\ВашеИмя\.ssh\server_key.pem" /grant:r "%USERNAME%:R"

# 3. Подключитесь
ssh -i C:\Users\ВашеИмя\.ssh\server_key.pem root@ваш-ip
```

### Linux/Mac:
```bash
# 1. Установите права на ключ
chmod 600 ~/.ssh/server_key.pem

# 2. Подключитесь
ssh -i ~/.ssh/server_key.pem root@ваш-ip
```

---

## 📝 Полный процесс установки FinQuest на сервер

### 1. Подключаемся к серверу

```bash
ssh root@ваш-ip
```

### 2. Обновляем систему

```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

### 3. Устанавливаем необходимое ПО

```bash
# Устанавливаем Python, pip, git, nginx
sudo apt install python3 python3-pip python3-venv nginx git -y

# Проверяем версии
python3 --version
git --version
nginx -v
```

### 4. Клонируем проект

```bash
# Переходим в директорию
cd /var/www

# Клонируем репозиторий
sudo git clone https://github.com/ваш-username/fin_project.git

# Даем права
sudo chown -R $USER:$USER /var/www/fin_project

# Переходим в проект
cd fin_project
```

### 5. Создаем виртуальное окружение

```bash
# Создаем venv
python3 -m venv venv

# Активируем
source venv/bin/activate

# Проверяем активацию (должно быть (venv) в начале строки)
which python
```

### 6. Устанавливаем зависимости

```bash
# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости проекта
pip install -r requirements.txt

# Устанавливаем дополнительно для production
pip install gunicorn
```

### 7. Настраиваем Django

```bash
# Создаем .env файл для секретных данных
nano .env
```

Добавьте в `.env`:
```env
DEBUG=False
SECRET_KEY=ваш-супер-секретный-ключ-тут-минимум-50-символов
ALLOWED_HOSTS=ваш-ip,ваш-домен.ru
```

Для генерации SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 8. Применяем миграции и загружаем данные

```bash
# Миграции базы данных
python manage.py migrate

# Создаем суперпользователя
python manage.py createsuperuser
# Введите логин, email, пароль

# Загружаем категории и уровни
python manage.py create_new_structure

# Загружаем ежедневные задания
python manage.py create_daily_quests

# Собираем статические файлы
python manage.py collectstatic --noinput
```

### 9. Настраиваем Gunicorn (сервер приложения)

```bash
# Создаем systemd сервис
sudo nano /etc/systemd/system/finquest.service
```

Вставьте:
```ini
[Unit]
Description=FinQuest Django Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/fin_project
Environment="PATH=/var/www/fin_project/venv/bin"
ExecStart=/var/www/fin_project/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/fin_project/finquest.sock \
          finquest.wsgi:application

[Install]
WantedBy=multi-user.target
```

Сохраните (Ctrl+X, Y, Enter) и запустите:
```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Запускаем сервис
sudo systemctl start finquest

# Добавляем в автозагрузку
sudo systemctl enable finquest

# Проверяем статус
sudo systemctl status finquest
```

### 10. Настраиваем Nginx (веб-сервер)

```bash
# Создаем конфигурацию
sudo nano /etc/nginx/sites-available/finquest
```

Вставьте:
```nginx
server {
    listen 80;
    server_name ваш-ip ваш-домен.ru;

    client_max_body_size 10M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /var/www/fin_project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        alias /var/www/fin_project/media/;
        expires 30d;
    }

    # Service Worker для PWA
    location = /static/sw.js {
        alias /var/www/fin_project/staticfiles/sw.js;
        add_header Cache-Control "no-cache";
        add_header Service-Worker-Allowed "/";
    }

    # Manifest для PWA
    location = /static/manifest.json {
        alias /var/www/fin_project/staticfiles/manifest.json;
        add_header Cache-Control "no-cache";
    }

    location / {
        proxy_pass http://unix:/var/www/fin_project/finquest.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Активируем конфигурацию:
```bash
# Создаем ссылку
sudo ln -s /etc/nginx/sites-available/finquest /etc/nginx/sites-enabled/

# Удаляем дефолтную конфигурацию
sudo rm /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
sudo nginx -t

# Перезапускаем Nginx
sudo systemctl restart nginx

# Добавляем в автозагрузку
sudo systemctl enable nginx
```

### 11. Настраиваем Firewall

```bash
# Разрешаем SSH (чтобы не потерять доступ!)
sudo ufw allow OpenSSH

# Разрешаем HTTP и HTTPS
sudo ufw allow 'Nginx Full'

# Включаем firewall
sudo ufw enable

# Проверяем статус
sudo ufw status
```

### 12. Настраиваем HTTPS (SSL сертификат)

```bash
# Устанавливаем Certbot
sudo apt install certbot python3-certbot-nginx -y

# Получаем бесплатный SSL сертификат
sudo certbot --nginx -d ваш-домен.ru -d www.ваш-домен.ru

# Следуйте инструкциям на экране
# Введите email
# Согласитесь с условиями
# Выберите "Redirect" для автоматического редиректа на HTTPS

# Проверяем автообновление сертификата
sudo systemctl status certbot.timer
```

---

## ✅ Проверка работы

### 1. Откройте браузер

```
http://ваш-ip
или
https://ваш-домен.ru
```

### 2. Проверьте админку

```
http://ваш-ip/admin/
```

### 3. Проверьте логи

```bash
# Логи Gunicorn
sudo journalctl -u finquest -f

# Логи Nginx
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

---

## 🔄 Обновление проекта

```bash
# 1. Подключаемся к серверу
ssh root@ваш-ip

# 2. Переходим в проект
cd /var/www/fin_project

# 3. Получаем изменения
git pull origin main

# 4. Активируем venv
source venv/bin/activate

# 5. Обновляем зависимости
pip install -r requirements.txt --upgrade

# 6. Применяем миграции
python manage.py migrate

# 7. Собираем статику
python manage.py collectstatic --noinput

# 8. Перезапускаем Gunicorn
sudo systemctl restart finquest

# 9. Перезапускаем Nginx (если менялась конфигурация)
sudo systemctl restart nginx

# 10. Готово!
```

---

## 🐛 Решение проблем

### Не могу подключиться по SSH

```bash
# Проверьте что SSH запущен на сервере (если есть консоль)
sudo systemctl status ssh
sudo systemctl start ssh
sudo systemctl enable ssh

# Проверьте firewall
sudo ufw status
sudo ufw allow 22/tcp
```

### Gunicorn не запускается

```bash
# Проверяем статус
sudo systemctl status finquest

# Смотрим логи
sudo journalctl -u finquest -n 50

# Проверяем права
sudo chown -R www-data:www-data /var/www/fin_project
```

### 502 Bad Gateway

```bash
# Проверяем запущен ли Gunicorn
sudo systemctl status finquest
sudo systemctl restart finquest

# Проверяем socket файл
ls -la /var/www/fin_project/finquest.sock

# Проверяем логи Nginx
sudo tail -f /var/log/nginx/error.log
```

### Статические файлы не загружаются

```bash
# Собираем статику заново
cd /var/www/fin_project
source venv/bin/activate
python manage.py collectstatic --noinput --clear

# Проверяем права
sudo chmod -R 755 /var/www/fin_project/staticfiles
sudo chown -R www-data:www-data /var/www/fin_project/staticfiles
```

---

## 📊 Мониторинг сервера

```bash
# Использование CPU и памяти
htop

# Использование диска
df -h

# Использование памяти
free -h

# Активные процессы
ps aux | grep python

# Открытые порты
sudo netstat -tulpn
```

---

## 🔐 Повышение безопасности

### 1. Отключение входа по паролю (только SSH ключи)

```bash
sudo nano /etc/ssh/sshd_config

# Измените:
PasswordAuthentication no
PubkeyAuthentication yes

# Перезапустите SSH
sudo systemctl restart ssh
```

### 2. Изменение SSH порта

```bash
sudo nano /etc/ssh/sshd_config

# Измените:
Port 2222  # Вместо 22

# Разрешите новый порт в firewall
sudo ufw allow 2222/tcp

# Перезапустите SSH
sudo systemctl restart ssh
```

### 3. Автоматические обновления безопасности

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

---

## 🎉 Готово!

Ваше приложение теперь доступно:
- 🌐 По IP: `http://ваш-ip`
- 🌐 По домену: `https://ваш-домен.ru`
- 🔐 Админка: `https://ваш-домен.ru/admin/`
- 📱 PWA можно установить на телефон!

---

**Разработано командой "Джунцы"** для IT-Sprint 2025 🚀

