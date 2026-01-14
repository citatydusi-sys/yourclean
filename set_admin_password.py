#!/usr/bin/env python
"""
Скрипт для установки пароля администратора
Использование: python set_admin_password.py
"""
import os
import sys
import django

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourclean.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Пароль по умолчанию (измените на свой)
DEFAULT_PASSWORD = 'admin123'

def set_admin_password(username='admin', password=None):
    """Устанавливает пароль для администратора"""
    try:
        user = User.objects.get(username=username)
        if password is None:
            password = DEFAULT_PASSWORD
        
        user.set_password(password)
        user.save()
        print(f'[OK] Пароль успешно установлен для пользователя "{username}"')
        print(f'Логин: {username}')
        print(f'Пароль: {password}')
        print(f'\nВАЖНО: Измените пароль после первого входа!')
        return True
    except User.DoesNotExist:
        print(f'[ERROR] Пользователь "{username}" не найден')
        return False
    except Exception as e:
        print(f'[ERROR] Ошибка: {e}')
        return False

if __name__ == '__main__':
    # Можно передать пароль как аргумент: python set_admin_password.py mypassword
    password = sys.argv[1] if len(sys.argv) > 1 else None
    set_admin_password('admin', password)
