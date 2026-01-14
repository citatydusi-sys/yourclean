#!/usr/bin/env python
"""
Скрипт для автоматического создания суперпользователя
Используется при деплое на Render, когда Shell недоступен
"""
import os
import sys
import django
import traceback

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourclean.settings')

try:
    django.setup()
except Exception as e:
    print(f'[ERROR] Ошибка при настройке Django: {e}')
    sys.exit(1)

from django.contrib.auth import get_user_model
from django.db import connection

User = get_user_model()

def check_database():
    """Проверяет подключение к базе данных"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print('[OK] Подключение к базе данных успешно')
        return True
    except Exception as e:
        print(f'[ERROR] Ошибка подключения к базе данных: {e}')
        return False

def create_superuser_if_not_exists():
    """Создает суперпользователя, если его еще нет"""
    print('[INFO] Начало создания суперпользователя...')
    
    # Проверка базы данных
    if not check_database():
        return False
    
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@yourclean.cz')
    password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    print(f'[INFO] Параметры: username={username}, email={email}')
    
    # Проверка существования пользователя
    try:
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            if user.is_superuser:
                print(f'[INFO] Суперпользователь "{username}" уже существует')
                # Обновляем пароль на случай, если он изменился в env
                user.set_password(password)
                user.save()
                print(f'[INFO] Пароль обновлен для пользователя "{username}"')
                print(f'[INFO] Логин: {username}')
                print(f'[INFO] Пароль: {password}')
                return True
            else:
                print(f'[WARNING] Пользователь "{username}" существует, но не является суперпользователем')
                user.is_superuser = True
                user.is_staff = True
                user.set_password(password)
                user.save()
                print(f'[OK] Пользователь "{username}" повышен до суперпользователя')
                print(f'[INFO] Логин: {username}')
                print(f'[INFO] Пароль: {password}')
                return True
    except Exception as e:
        print(f'[ERROR] Ошибка при проверке пользователя: {e}')
        traceback.print_exc()
    
    # Создание нового суперпользователя
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f'[OK] Суперпользователь "{username}" успешно создан')
        print(f'[INFO] Логин: {username}')
        print(f'[INFO] Пароль: {password}')
        print(f'[WARNING] ВАЖНО: Измените пароль после первого входа!')
        return True
    except Exception as e:
        print(f'[ERROR] Ошибка при создании суперпользователя: {e}')
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_superuser_if_not_exists()
    if not success:
        print('[ERROR] Не удалось создать суперпользователя')
        sys.exit(1)
    else:
        print('[OK] Скрипт выполнен успешно')
