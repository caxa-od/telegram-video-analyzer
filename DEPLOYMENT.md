# 🚀 Deployment Guide

## Шаги для деплоя на GitHub:

### 1. Создание репозитория на GitHub

1. Перейдите на [GitHub](https://github.com)
2. Нажмите "New repository"
3. Введите название: `telegram-video-analyzer`
4. Описание: `Multi-language Telegram bot for AI-powered video analysis and voice synthesis`
5. Выберите "Public" или "Private"
6. **НЕ инициализируйте** с README, .gitignore или LICENSE (они уже есть)
7. Нажмите "Create repository"

### 2. Связывание с удаленным репозиторием

Выполните команды в терминале:

```bash
cd "/Users/caxa/Desktop/Контент Завод/telegram-video-analyzer"

# Добавить удаленный репозиторий (замените YOUR_USERNAME на ваш GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/telegram-video-analyzer.git

# Отправить код на GitHub
git branch -M main
git push -u origin main
```

### 3. После создания репозитория

Обновите README.md, заменив `<your-repo-url>` на актуальную ссылку:
```
git clone https://github.com/YOUR_USERNAME/telegram-video-analyzer.git
```

### 4. Проверка безопасности

✅ Убедитесь, что в репозитории НЕТ:
- Файла `.env` (должен быть только `.env.example`)
- API ключей в коде
- Личных данных

✅ В репозитории ЕСТЬ:
- `.gitignore` файл
- Документация в README.md
- Пример конфигурации в `.env.example`

## 🔒 Безопасность

**ВАЖНО:** Никогда не добавляйте настоящие API ключи в репозиторий!

Файл `.env` с настоящими ключами должен оставаться только на вашем компьютере.

## 📝 Дальнейшие коммиты

Для обновления репозитория:

```bash
git add .
git commit -m "Описание изменений"
git push
```

## 🌟 Готово!

После выполнения этих шагов ваш проект будет доступен на GitHub и готов к использованию другими разработчиками.
