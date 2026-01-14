"""
Django management команда для автоматического создания суперпользователя.
Используется при деплое на Render Free (без shell доступа).
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает суперпользователя из переменных окружения (ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD)'

    def handle(self, *args, **options):
        # Проверка подключения к БД
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка подключения к БД: {e}')
            )
            return

        # Получение данных из env
        import os
        username = os.getenv('ADMIN_USERNAME', 'admin')
        email = os.getenv('ADMIN_EMAIL', 'admin@yourclean.cz')
        password = os.getenv('ADMIN_PASSWORD')

        if not password:
            self.stdout.write(
                self.style.WARNING('ADMIN_PASSWORD не установлен. Суперпользователь не создан.')
            )
            return

        # Проверка существования пользователя
        try:
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                user.is_superuser = True
                user.is_staff = True
                user.set_password(password)
                if email:
                    user.email = email
                user.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Суперпользователь "{username}" обновлен (пароль изменен)')
                )
            else:
                # Создание нового суперпользователя
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Суперпользователь "{username}" создан успешно')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка при создании/обновлении суперпользователя: {e}')
            )
