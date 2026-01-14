# 🚀 Быстрая инструкция: Загрузить проект на GitHub

## Шаг 1: Создайте Personal Access Token

1. Откройте в браузере: **https://github.com/settings/tokens**
2. Нажмите **"Generate new token"** → **"Generate new token (classic)"**
3. Дайте имя: `yourclean-deploy`
4. Выберите срок: **90 days** или **No expiration**
5. Отметьте галочку: ✅ **repo** (полный доступ к репозиториям)
6. Прокрутите вниз и нажмите **"Generate token"**
7. **ВАЖНО:** Скопируйте токен сразу! (он начинается с `ghp_...`)

## Шаг 2: Выполните команды

Откройте PowerShell в папке проекта и выполните:

```powershell
cd c:\Users\Admin\Desktop\django\yourclean

# Используйте токен в URL (замените YOUR_TOKEN на ваш токен)
git remote set-url origin https://YOUR_TOKEN@github.com/citatydusi-sys/yourclean.git

# Загрузите проект
git push -u origin main
```

**Пример:**
```powershell
git remote set-url origin https://ghp_abc123xyz@github.com/citatydusi-sys/yourclean.git
git push -u origin main
```

## Шаг 3: После успешной загрузки

Удалите токен из URL (для безопасности):

```powershell
git remote set-url origin https://github.com/citatydusi-sys/yourclean.git
```

## ✅ Готово!

После этого ваш проект появится на GitHub по адресу:
**https://github.com/citatydusi-sys/yourclean**

---

## Альтернативный способ (через диалог ввода)

Если не хотите вставлять токен в URL, просто выполните:

```powershell
git push -u origin main
```

Когда Git попросит:
- **Username:** `citatydusi-sys`
- **Password:** вставьте ваш Personal Access Token (НЕ обычный пароль!)
