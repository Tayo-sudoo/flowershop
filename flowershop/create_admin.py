# create_admin.py
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowershop.settings')
django.setup()

from django.contrib.auth.models import User

# Проверяем, есть ли уже admin
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Суперпользователь admin создан! Пароль: admin123')
else:
    print('Пользователь admin уже существует')