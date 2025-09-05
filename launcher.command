#!/bin/bash

# Telegram Video Analyzer Bot Launcher
# Простой скрипт для запуска/остановки бота

TELEGRAM_BOT_DIR="/Users/caxa/Desktop/Контент Завод/telegram-video-analyzer"
LOG_FILE="$HOME/Desktop/video_analyzer_simple.log"

# Функция уведомлений
notify() {
    osascript -e "display notification \"$1\" with title \"Video Bot\""
}

# Проверяем текущий статус
existing=$(pgrep -f "python.*main.py")

if [ -n "$existing" ]; then
    # Бот запущен - предлагаем остановить
    choice=$(osascript -e 'display dialog "Бот уже запущен (PID: '"$existing"')\n\nЧто хотите сделать?" buttons {"Остановить", "Отмена"} default button "Остановить"')
    
    if [[ "$choice" == *"Остановить"* ]]; then
        pkill -f "python.*main.py"
        sleep 2
        if [ -z "$(pgrep -f 'python.*main.py')" ]; then
            notify "✅ Бот остановлен"
            osascript -e 'display dialog "✅ Бот успешно остановлен!" buttons {"OK"} default button "OK"'
        else
            notify "❌ Не удалось остановить бота"
            osascript -e 'display dialog "❌ Не удалось остановить бота" buttons {"OK"} default button "OK"'
        fi
    fi
    exit 0
fi

# Бот не запущен - запускаем
echo "$(date): Starting bot..." >> "$LOG_FILE"

# Проверяем директорию
if [ ! -d "$TELEGRAM_BOT_DIR" ]; then
    notify "❌ Директория бота не найдена"
    osascript -e 'display dialog "Ошибка: Директория не найдена\n'"$TELEGRAM_BOT_DIR"'" buttons {"OK"} default button "OK"'
    exit 1
fi

# Переходим в директорию бота
cd "$TELEGRAM_BOT_DIR" || exit 1
python_path="$TELEGRAM_BOT_DIR/venv/bin/python"

if [ ! -f "$python_path" ]; then
    notify "❌ Python не найден"
    osascript -e 'display dialog "Ошибка: Python не найден в\n'"$python_path"'" buttons {"OK"} default button "OK"'
    exit 1
fi

if [ ! -f "main.py" ]; then
    notify "❌ main.py не найден"
    osascript -e 'display dialog "Ошибка: main.py не найден в\n'"$TELEGRAM_BOT_DIR"'" buttons {"OK"} default button "OK"'
    exit 1
fi

# Запускаем бота
notify "🚀 Запускаю бота..."
nohup "$python_path" main.py >> "$LOG_FILE" 2>&1 &
sleep 3

# Проверяем результат
new_pid=$(pgrep -f "python.*main.py")
if [ -n "$new_pid" ]; then
    notify "✅ Бот запущен"
    osascript -e 'display dialog "✅ Бот успешно запущен!\n\nPID: '"$new_pid"'" buttons {"OK"} default button "OK"'
else
    notify "❌ Не удалось запустить бота"
    osascript -e 'display dialog "❌ Не удалось запустить бота\nПроверьте логи в '"$LOG_FILE"'" buttons {"OK"} default button "OK"'
fi
