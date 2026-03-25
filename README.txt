=== Flora Luxe - Dragon Flower Shop ===

УСТАНОВКА И ЗАПУСК:

1. Установите зависимости:
   pip install -r requirements.txt

2. Перейдите в папку с manage.py:
   cd flowershop

3. Примените миграции:
   python manage.py migrate

4. Создайте администратора:
   python manage.py createsuperuser

5. Запустите сервер:
   python manage.py runserver

6. Откройте браузер: http://127.0.0.1:8000/
   Админка:         http://127.0.0.1:8000/admin/

СТРУКТУРА:
   flowershop/         <- главная папка проекта
   ├── manage.py       <- ЗАПУСКАТЬ ОТСЮДА
   ├── requirements.txt
   ├── db.sqlite3
   ├── flowershop/     <- настройки Django
   │   ├── settings.py
   │   └── urls.py
   ├── main/           <- приложение магазина
   │   ├── views.py
   │   ├── models.py
   │   ├── urls.py
   │   └── templates/
   └── static/         <- CSS, JS файлы
