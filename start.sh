#!/bin/bash

# Telegram Video Analyzer Bot - Quick Start Script

echo "🚀 Запуск Telegram Video Analyzer Bot..."

# Проверка виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено. Создаю..."
    python3 -m venv venv
fi

# Активация виртуального окружения
source venv/bin/activate

# Проверка .env файла
if [ ! -f ".env" ]; then
    echo "⚠️  .env файл не найден. Скопируйте .env.example в .env и настройте токены."
    echo "cp .env.example .env"
    echo "Затем отредактируйте .env файл с вашими токенами."
    exit 1
fi

# Установка зависимостей если нужно
echo "📦 Проверка зависимостей..."
pip install -r requirements.txt > /dev/null 2>&1

# Запуск бота
echo "🤖 Запуск бота..."
python main.py
