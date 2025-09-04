"""Main bot application."""

import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram import BotCommand, Update
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent))

from src.config import Config
from src.handlers.video_handler import VideoAnalysisHandler, MessageHandler as CustomMessageHandler
from src.handlers.voice_handler import VoiceHandler
from src.handlers.language_handler import LanguageHandler
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)

class TelegramVideoAnalyzerBot:
    """Main bot application class."""
    
    def __init__(self):
        """Initialize the bot application."""
        # Setup logging
        setup_logging()
        
        # Validate configuration
        if not Config.validate_config():
            raise ValueError("Invalid configuration. Please check your .env file.")
        
        # Initialize handlers
        self.video_handler = VideoAnalysisHandler()
        self.message_handler = CustomMessageHandler()
        self.voice_handler = VoiceHandler()
        self.language_handler = LanguageHandler()
        
        # Initialize bot application
        self.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Setup handlers
        self._setup_handlers()
        
        logger.info("Bot initialized successfully")
    
    async def debug_callback_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Debug callback handler to test if callbacks work at all."""
        query = update.callback_query
        logger.info(f"DEBUG: Received callback: {query.data}")
        
        # Обработаем все callback здесь
        if query.data.startswith('lang_'):
            await self.language_handler.handle_language_callback(update, context)
        elif query.data == 'test_button':
            await query.answer(f"✅ Тест успешен! Данные: {query.data}")
        else:
            await query.answer(f"Получен callback: {query.data}")
    
    def _setup_handlers(self):
        """Setup message and command handlers."""
        try:
            # Command handlers
            self.application.add_handler(
                CommandHandler("start", self.video_handler.handle_start)
            )
            self.application.add_handler(
                CommandHandler("help", self.video_handler.handle_help)
            )
            self.application.add_handler(
                CommandHandler("voice_text", self.voice_handler.handle_voice_text)
            )
            self.application.add_handler(
                CommandHandler("voice_settings", self.voice_handler.handle_voice_settings)
            )
            self.application.add_handler(
                CommandHandler("language", self.language_handler.handle_language_command)
            )
            self.application.add_handler(
                CommandHandler("set_ru", self.language_handler.handle_set_russian)
            )
            self.application.add_handler(
                CommandHandler("set_en", self.language_handler.handle_set_english)
            )
            self.application.add_handler(
                CommandHandler("set_es", self.language_handler.handle_set_spanish)
            )
            
            # Единый callback handler для всех кнопок
            self.application.add_handler(
                CallbackQueryHandler(self.debug_callback_handler)
            )
            
            # Message handlers
            self.application.add_handler(
                MessageHandler(
                    filters.VIDEO,
                    self.video_handler.handle_video
                )
            )
            
            # Handle all other messages (but not commands) - должен быть последним
            self.application.add_handler(
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    self.message_handler.route_message
                )
            )
            
            logger.info("Handlers setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up handlers: {e}")
            raise
    
    async def setup_bot_commands(self):
        """Setup bot commands menu."""
        try:
            commands = [
                BotCommand("start", "Начать работу с ботом"),
                BotCommand("help", "Показать справку"),
                BotCommand("language", "Выбор языка / Language selection"),
                BotCommand("voice_text", "Озвучить текст голосом"),
                BotCommand("voice_settings", "Настройки голосового синтеза")
            ]
            
            await self.application.bot.set_my_commands(commands)
            logger.info("Bot commands menu set successfully")
            
        except Exception as e:
            logger.error(f"Error setting up bot commands: {e}")
    
    async def start_polling(self):
        """Start the bot with polling."""
        try:
            logger.info("Starting bot with polling...")
            
            # Test Gemini connection
            if self.video_handler.gemini_client.test_connection():
                logger.info("✅ Gemini API connection successful")
            else:
                logger.warning("⚠️ Gemini API connection failed - check your API key")
            
            # Test OpenAI connection
            if self.video_handler.openai_client.test_connection():
                logger.info("✅ OpenAI API connection successful")
            else:
                logger.warning("⚠️ OpenAI API connection failed - check your API key")
            
            # Test ElevenLabs connection
            if self.voice_handler.elevenlabs_client.test_connection():
                logger.info("✅ ElevenLabs API connection successful")
            else:
                logger.warning("⚠️ ElevenLabs API connection failed - check your API key")
            
            # Initialize and start polling
            await self.application.initialize()
            await self.application.start()
            
            # Setup bot commands menu
            await self.setup_bot_commands()
            
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=["message", "edited_message"]
            )
            
            # Keep running
            logger.info("🤖 Bot is running successfully! Press Ctrl+C to stop.")
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                logger.info("Received stop signal")
            finally:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
            
        except Exception as e:
            logger.error(f"Error starting bot: {e}")
            raise
    
    def run(self):
        """Run the bot."""
        try:
            logger.info("Starting bot...")
            # Use asyncio.run properly
            asyncio.run(self.start_polling())
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot crashed: {e}")
            raise

if __name__ == "__main__":
    try:
        # Create and run bot
        bot = TelegramVideoAnalyzerBot()
        bot.run()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)
