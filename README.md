# Telegram Video Analyzer Bot

Бот для анализа видео с помощью Gemini AI и создания YouTube Shorts скриптов с GPT-4o.

## 🚀 Возможности

- 📹 Анализ видео файлов с помощью Gemini AI
- 🎬 Автоматическое создание раскадровки по времени
- 🤖 Интеллектуальное описание происходящего на видео
- 🎙️ Создание сценария для озвучки YouTube Shorts с помощью GPT-4o
- 📝 Генерация заголовков и ключевых слов для YouTube
- ⚡ Быстрая обработка через Telegram бота

## 📋 Требования

- Python 3.8+
- Telegram Bot Token (от @BotFather)
- Gemini API Key (от Google AI Studio)
- OpenAI API Key (для создания сценариев)

## 🛠 Установка

1. **Клонируйте проект:**
   ```bash
   git clone https://github.com/caxa-od/telegram-video-analyzer.git
   cd telegram-video-analyzer
   ```

2. **Создайте виртуальное окружение:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # На Linux/Mac
   # или
   venv\Scripts\activate  # На Windows
   ```

3. **Установите зависимости:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Настройте переменные окружения:**
   ```bash
   cp .env.example .env
   ```
   
   Отредактируйте `.env` файл и добавьте ваши токены:
   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   GEMINI_API_KEY=your_gemini_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## 🔧 Настройка

### Получение Telegram Bot Token

1. Найдите [@BotFather](https://t.me/botfather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен

### Получение Gemini API Key

1. Перейдите на [ai.google.dev](https://ai.google.dev)
2. Войдите в Google аккаунт
3. Создайте новый API ключ
4. Скопируйте ключ (начинается с `AIza...`)

3. **Получите OpenAI API Key:**
   - Перейдите на [platform.openai.com](https://platform.openai.com)
   - Создайте аккаунт или войдите
   - Перейдите в API Keys
   - Создайте новый API ключ

## 🚀 Запуск

```bash
python main.py
```

Бот должен запуститься и начать обработку сообщений.

## 📱 Использование

1. **Запустите бота:**
   - Найдите вашего бота в Telegram
   - Отправьте команду `/start`

2. **Отправьте видео:**
   - Просто отправьте видео файл в чат
   - Дождитесь обработки (может занять несколько минут)

3. **Получите результаты:**
   - Подробную раскадровку видео
   - Готовый сценарий для озвучки
   - Варианты заголовков
   - Ключевые слова для продвижения

## 📊 Структура проекта

```
telegram-video-analyzer/
├── src/
│   ├── handlers/          # Обработчики сообщений
│   ├── services/          # Бизнес-логика
│   ├── utils/             # Утилиты
│   └── config.py          # Конфигурация
├── temp/                  # Временные файлы
├── logs/                  # Логи
├── main.py               # Точка входа
├── requirements.txt      # Зависимости
├── .env.example         # Пример конфигурации
└── README.md            # Документация
```

## ⚙️ Конфигурация

Основные настройки в `.env`:

```env
# Максимальный размер видео (MB)
MAX_VIDEO_SIZE_MB=50

# Интервал между кадрами (секунды)
FRAME_INTERVAL_SECONDS=5

# Максимальное количество кадров
MAX_FRAMES_PER_VIDEO=20

# Уровень логирования
LOG_LEVEL=INFO
```

## 🔧 Разработка

### Запуск в режиме разработки

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Установить dev зависимости
pip install black flake8

# Форматирование кода
black src/

# Линтинг
flake8 src/
```

### Тестирование

```bash
# Тест подключения к Gemini
python -c "from src.services.gemini_client import GeminiClient; print('OK' if GeminiClient().test_connection() else 'FAIL')"
```

## 📝 Команды бота

- `/start` - Начать работу с ботом
- `/help` - Справка по использованию

## 🚨 Ограничения

- Максимальный размер видео: 50MB (настраивается)
- Поддерживаемые форматы: MP4, AVI, MOV, WMV
- Максимальное время обработки: ~5 минут

## 🛡 Безопасность

- Никогда не публикуйте API ключи в коде
- Используйте `.env` файлы для конфиденциальных данных
- Регулярно обновляйте зависимости

## 📄 Лицензия

MIT License

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте логи в папке `logs/`
2. Убедитесь, что API ключи корректны
3. Проверьте размер и формат видео

## 🚀 Развертывание

### Docker (опционально)

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

### Системд сервис (Linux)

Создайте `/etc/systemd/system/video-analyzer-bot.service`:

```ini
[Unit]
Description=Telegram Video Analyzer Bot
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/telegram-video-analyzer
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```
