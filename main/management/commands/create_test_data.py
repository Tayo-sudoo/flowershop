from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import Category, Flower


class Command(BaseCommand):
    help = 'Создает тестовые данные для магазина цветов'

    def handle(self, *args, **kwargs):
        # Создаем категории
        categories = [
            {'name': 'Розы', 'slug': 'roses'},
            {'name': 'Тюльпаны', 'slug': 'tulips'},
            {'name': 'Букеты', 'slug': 'bouquets'},
            {'name': 'Комнатные растения', 'slug': 'indoor'},
        ]

        for cat_data in categories:
            Category.objects.get_or_create(**cat_data)
            self.stdout.write(f'Создана категория: {cat_data["name"]}')

        # Создаем цветы
        flowers = [
            {
                'category': Category.objects.get(slug='roses'),
                'name': 'Красные розы',
                'price': 1500,
                'description': 'Классические красные розы - символ страсти и любви. 25 см, 5 цветков в букете.',
                'available': True
            },
            {
                'category': Category.objects.get(slug='roses'),
                'name': 'Белые розы',
                'price': 1600,
                'description': 'Нежные белые розы - символ чистоты и невинности. 30 см, 7 цветков.',
                'available': True
            },
            {
                'category': Category.objects.get(slug='tulips'),
                'name': 'Жёлтые тюльпаны',
                'price': 800,
                'description': 'Яркие весенние тюльпаны поднимут настроение. 35 см, 11 цветков.',
                'available': True
            },
            {
                'category': Category.objects.get(slug='bouquets'),
                'name': 'Свадебный букет',
                'price': 3000,
                'description': 'Изысканный букет из белых роз, пионов и зелени. Идеален для невесты.',
                'available': True
            },
            {
                'category': Category.objects.get(slug='indoor'),
                'name': 'Орхидея',
                'price': 2500,
                'description': 'Красивое комнатное растение с длительным цветением. В горшке.',
                'available': True
            },
        ]

        for flower_data in flowers:
            Flower.objects.get_or_create(
                name=flower_data['name'],
                defaults=flower_data
            )
            self.stdout.write(f'Создан цветок: {flower_data["name"]}')

        self.stdout.write(self.style.SUCCESS('Все тестовые данные созданы!'))