#!/usr/bin/env python
"""
Скрипт для автоматического создания суперпользователя
Используется при деплое на Render, когда Shell недоступен
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourclean.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser_if_not_exists():
    """Создает суперпользователя, если его еще нет"""
    username = os.getenv('ADMIN_USERNAME', 'admin')
    email = os.getenv('ADMIN_EMAIL', 'admin@yourclean.cz')
    password = os.getenv('ADMIN_PASSWORD', 'admin123')
    
    if User.objects.filter(username=username).exists():
        print(f'[INFO] Суперпользователь "{username}" уже существует')
        return False
    
    try:
        User.objects.create_superuser(
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
        return False

if __name__ == '__main__':
    create_superuser_if_not_exists()
