#!/bin/bash

# Telegram Video Analyzer Bot Launcher
# Автоматический запуск бота на macOS

# Получаем путь к директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🤖 Запуск Telegram Video Analyzer Bot..."
echo "📁 Рабочая директория: $SCRIPT_DIR"

# Переходим в директорию проекта
cd "$SCRIPT_DIR"

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo "❌ Виртуальное окружение не найдено!"
    echo "📝 Создайте виртуальное окружение командой: python3 -m venv venv"
    exit 1
fi

# Активируем виртуальное окружение и запускаем бота
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

echo "🚀 Запуск бота..."
python main.py
