
# 🌸 Flora Luxe — Premium Flower Shop

Полнофункциональный интернет-магазин цветов на Django с поддержкой глобального деплоя.

---

## ⚡ Быстрый старт (локально)

```bash
# 1. Установить зависимости
pip install -r requirements.txt

# 2. Скопировать конфиг окружения
cp .env.example .env

# 3. Применить миграции
python manage.py migrate

# 4. Создать суперпользователя
python manage.py createsuperuser

# 5. Запустить сервер
python manage.py runserver
```

Откройте: http://127.0.0.1:8000  
Админка: http://127.0.0.1:8000/admin/

---

## 🌍 Деплой в интернет

### Вариант 1: Railway.app (рекомендуется, бесплатно)

1. Зарегистрируйтесь на https://railway.app
2. Создайте новый проект → "Deploy from GitHub"
3. Залейте код на GitHub, подключите репозиторий
4. Добавьте PostgreSQL плагин в Railway
5. Укажите переменные окружения:
   ```
   DJANGO_SECRET_KEY=<сгенерируйте длинный случайный ключ>
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=ваш-домен.railway.app
   DATABASE_URL=<автоматически из PostgreSQL плагина>
   ```
6. Railway сам запустит `railway.json` команды

### Вариант 2: Render.com (бесплатно)

1. Зарегистрируйтесь на https://render.com
2. Новый Web Service → подключите GitHub
3. Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
4. Start Command: `gunicorn flowershop.wsgi --workers 2 --bind 0.0.0.0:$PORT`
5. Добавьте те же переменные окружения

### Вариант 3: VPS/Ubuntu сервер

```bash
# На сервере
sudo apt update && sudo apt install python3-pip nginx certbot

# Клонировать проект
git clone <your-repo> /var/www/floraluxe
cd /var/www/floraluxe

# Установить зависимости
pip3 install -r requirements.txt

# Создать .env и заполнить
cp .env.example .env && nano .env

# Миграции и статика
python manage.py migrate
python manage.py collectstatic --noinput

# Запустить через gunicorn (systemd service)
gunicorn flowershop.wsgi --workers 3 --bind 127.0.0.1:8000 --daemon

# Настроить Nginx как reverse proxy (пример конфига ниже)
```

**Nginx конфиг** (`/etc/nginx/sites-available/floraluxe`):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location /static/ {
        alias /var/www/floraluxe/staticfiles/;
    }
    location /media/ {
        alias /var/www/floraluxe/media/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

**SSL сертификат (HTTPS)**:
```bash
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

---

## 🔧 Переменные окружения (.env)

| Переменная | Описание | Обязательно |
|-----------|----------|-------------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django (50+ символов) | ✅ |
| `DJANGO_DEBUG` | `True` для разработки, `False` для продакшна | ✅ |
| `DJANGO_ALLOWED_HOSTS` | Домены через запятую | ✅ |
| `DATABASE_URL` | PostgreSQL URL (для продакшна) | Рекомендуется |
| `GOOGLE_CLIENT_ID` | Google OAuth Client ID | Для входа через Google |
| `GOOGLE_CLIENT_SECRET` | Google OAuth Secret | Для входа через Google |
| `EMAIL_HOST_USER` | Email для отправки уведомлений | Опционально |
| `EMAIL_HOST_PASSWORD` | Пароль от email | Опционально |

---

## 🔐 Google OAuth (вход через Google)

1. Перейдите: https://console.cloud.google.com
2. Создайте проект → APIs & Services → Credentials
3. OAuth 2.0 Client IDs → Web application
4. Authorized redirect URIs: `https://yourdomain.com/auth/google/callback/`
5. Скопируйте Client ID и Secret в `.env`

---

## 📱 Структура проекта

```
flora_luxe_mobile/
├── flowershop/           # Django конфиг
│   ├── settings.py      # Настройки (prod-ready)
│   ├── urls.py
│   └── wsgi.py          # WSGI + WhiteNoise
├── main/                 # Основное приложение
│   ├── models.py        # Category, Flower, Order, Profile, Review
│   ├── views.py         # Все views
│   ├── urls.py          # URL маршруты
│   ├── ai_helper.py     # AI чат-помощник
│   ├── locales.py       # Переводы RU/UZ/EN
│   └── templates/       # HTML шаблоны
├── static/              # CSS, JS файлы
├── media/               # Загруженные изображения
├── requirements.txt     # Зависимости
├── Procfile             # Railway/Heroku
├── railway.json         # Railway деплой
├── runtime.txt          # Python версия
└── .env.example         # Пример конфига
```

---

## 🌐 Функции

- ✅ Каталог с фильтрами и поиском
- ✅ Корзина (сессия)
- ✅ Оформление заказов
- ✅ Регистрация / Вход / Google OAuth
- ✅ Профиль с аватаром и историей заказов
- ✅ Отзывы с модерацией
- ✅ AI чат-помощник
- ✅ Мультиязычность (RU / UZ / EN)
- ✅ Мобильная адаптация
- ✅ Панель администратора
- ✅ PWA (Progressive Web App)
- ✅ SSL / HTTPS готов
- ✅ PostgreSQL поддержка
- ✅ WhiteNoise для статики

---

Создано с ❤️ — Flora Luxe © 2025
