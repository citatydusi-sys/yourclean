# Инструкция по деплою на Render

## Настройки в Render Dashboard

### 1. Тип сервиса
**Выберите: Web Service** (НЕ Static Site)

### 2. Основные настройки

**Build Command:**
```
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

**Start Command:**
```
python manage.py migrate && gunicorn yourclean.wsgi:application --bind 0.0.0.0:$PORT
```

**Environment:** Python 3

**Python Version:** 3.11.0

### 3. Переменные окружения (Environment Variables)

Добавьте следующие переменные:

- `SECRET_KEY` - сгенерируйте случайный ключ (можно использовать: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- `DEBUG` = `False`
- `ALLOWED_HOSTS` = `yourclean.onrender.com` (замените на ваш домен)
- `CORS_ALLOWED_ORIGINS` = `https://your-frontend.onrender.com` (если есть фронтенд, через запятую)

### 4. База данных

1. Создайте **PostgreSQL** базу данных в Render
2. Render автоматически создаст переменную `DATABASE_URL`
3. Проект автоматически использует эту переменную

### 5. Дополнительные настройки

- **Auto-Deploy:** Включите, если хотите автоматический деплой при push в репозиторий
- **Health Check Path:** `/` (опционально)

## После деплоя

1. Выполните миграции (если не выполнились автоматически):
   - Через Render Shell: `python manage.py migrate`

2. Создайте суперпользователя:
   - Через Render Shell: `python manage.py createsuperuser`

3. Проверьте работу сайта:
   - Откройте ваш домен на Render
   - Проверьте админку: `https://yourclean.onrender.com/admin/`

## Важные замечания

- Render автоматически устанавливает переменную `PORT` - не нужно её указывать вручную
- База данных SQLite не будет работать на Render - используйте PostgreSQL
- Статические файлы обрабатываются через WhiteNoise
- Все миграции выполняются автоматически при старте сервиса
