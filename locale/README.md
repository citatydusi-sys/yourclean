# Переводы

Для создания файлов переводов выполните:

```bash
python manage.py makemessages -l ru
python manage.py makemessages -l cz
python manage.py makemessages -l en
```

Затем отредактируйте файлы `.po` в соответствующих папках и выполните:

```bash
python manage.py compilemessages
```

