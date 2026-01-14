# Инструкция по загрузке проекта на GitHub

## Проблема: требуется аутентификация

GitHub требует аутентификацию для загрузки кода. Есть два способа:

## Способ 1: Personal Access Token (Рекомендуется)

### Шаг 1: Создайте Personal Access Token

1. Зайдите на GitHub: https://github.com
2. Перейдите в **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
3. Нажмите **Generate new token (classic)**
4. Дайте имя токену (например: "yourclean-deploy")
5. Выберите срок действия (рекомендуется: 90 дней или No expiration)
6. Отметьте права доступа:
   - ✅ **repo** (полный доступ к репозиториям)
7. Нажмите **Generate token**
8. **ВАЖНО:** Скопируйте токен сразу! Он больше не будет показан.

### Шаг 2: Используйте токен для push

Выполните команду (замените `YOUR_TOKEN` на ваш токен):

```bash
cd c:\Users\Admin\Desktop\django\yourclean
git push -u origin main
```

Когда Git попросит пароль:
- **Username:** ваш GitHub username (citatydusi-sys)
- **Password:** вставьте ваш Personal Access Token (НЕ ваш обычный пароль!)

### Или используйте токен в URL (временно):

```bash
git remote set-url origin https://YOUR_TOKEN@github.com/citatydusi-sys/yourclean.git
git push -u origin main
```

**⚠️ ВАЖНО:** После успешного push удалите токен из URL:
```bash
git remote set-url origin https://github.com/citatydusi-sys/yourclean.git
```

## Способ 2: GitHub CLI (gh)

Если у вас установлен GitHub CLI:

```bash
gh auth login
gh repo set-default citatydusi-sys/yourclean
git push -u origin main
```

## Способ 3: Настройка SSH (для постоянного использования)

### Шаг 1: Проверьте наличие SSH ключа

```bash
ls ~/.ssh/id_rsa.pub
```

Если файла нет, создайте ключ:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### Шаг 2: Добавьте ключ на GitHub

1. Скопируйте содержимое `~/.ssh/id_rsa.pub`
2. GitHub → Settings → SSH and GPG keys → New SSH key
3. Вставьте ключ и сохраните

### Шаг 3: Используйте SSH URL

```bash
git remote set-url origin git@github.com:citatydusi-sys/yourclean.git
git push -u origin main
```

## Текущий статус

✅ Git репозиторий инициализирован
✅ Все файлы добавлены и закоммичены
✅ Remote настроен: https://github.com/citatydusi-sys/yourclean.git
✅ Ветка переименована в `main`

**Осталось:** Выполнить `git push -u origin main` с аутентификацией
