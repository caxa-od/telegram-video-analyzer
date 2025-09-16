"""Telegram bot handlers for voice synthesis functionality."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from pathlib import Path
import tempfile

from src.services.elevenlabs_client import ElevenLabsClient
from src.handlers.language_handler import LanguageHandler
from src.config import Config

logger = logging.getLogger(__name__)

class VoiceHandler:
    """Handler for voice synthesis functionality."""
    
    def __init__(self):
        """Initialize handler with ElevenLabs client."""
        self.elevenlabs_client = ElevenLabsClient()
        self.language_handler = LanguageHandler()
        logger.info("Initialized VoiceHandler")
    
    async def handle_voice_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /voice_text command to convert text to speech.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            message = update.message
            user = message.from_user
            
            # Get text from command arguments
            if not context.args:
                await message.reply_text(
                    "❌ Пожалуйста, укажите текст для озвучки.\n\n"
                    "Пример: `/voice_text Привет, это тестовое сообщение!`"
                )
                return
            
            text = " ".join(context.args)
            
            if len(text.strip()) == 0:
                await message.reply_text("❌ Текст не может быть пустым")
                return
            
            if len(text) > 5000:
                await message.reply_text("❌ Текст слишком длинный (максимум 5000 символов)")
                return
            
            # Get user language and voice configuration
            user_language = self.language_handler.get_user_language(context)
            lang_config = Config.get_language_config(user_language)
            
            logger.info(f"Voice synthesis request from user {user.id}: {text[:50]}... (language: {user_language})")
            
            # Send processing message
            processing_msg = await message.reply_text(
                "🎙️ Генерирую голосовое сообщение...\n"
                "⏳ Это может занять несколько секунд"
            )
            
            # Generate audio with language-specific voice
            audio_bytes = await self.elevenlabs_client.text_to_speech(
                text, 
                voice_id=lang_config['elevenlabs_voice_id']
            )
            
            if not audio_bytes:
                await processing_msg.edit_text("❌ Ошибка при генерации аудио. Попробуйте позже.")
                return
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = Path(temp_file.name)
            
            # Send audio file
            await processing_msg.edit_text("✅ Аудио готово! Отправляю...")
            
            with open(temp_path, 'rb') as audio_file:
                await message.reply_voice(
                    voice=audio_file,
                    caption=f"🎙️ Озвучка: \"{text[:100]}{'...' if len(text) > 100 else ''}\""
                )
            
            # Cleanup
            self.elevenlabs_client.cleanup_temp_file(temp_path)
            await processing_msg.delete()
            
            logger.info(f"Successfully generated voice for user {user.id}")
            
        except Exception as e:
            logger.error(f"Error in voice_text handler: {e}")
            try:
                await message.reply_text("❌ Произошла ошибка при генерации голоса")
            except:
                pass
    
    async def handle_voice_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /voice_settings command to show voice configuration.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            settings_message = """
🎙️ **Настройки голосового синтеза**

🔊 **Текущий голос:** Vasiliy (русский)
🎛️ **Настройки качества:**
• Стабильность: 0.4 (умеренная вариативность)
• Схожесть: 0.75 (высокая схожесть с оригиналом)
• Стиль: 1.0 (максимально выразительное чтение)

📝 **Команды:**
• `/voice_text [текст]` - Озвучить произвольный текст
• `/voice_settings` - Показать эти настройки

⚡ **Ограничения:**
• Максимум 5000 символов
• Поддержка русского и английского языков
• Время генерации: ~10-30 секунд

💡 **Пример:**
`/voice_text Привет! Это пример голосового сообщения от нашего бота.`
            """
            
            await update.message.reply_text(settings_message, parse_mode=None)
            
        except Exception as e:
            logger.error(f"Error in voice_settings handler: {e}")
            try:
                await update.message.reply_text("❌ Ошибка при получении настроек")
            except:
                pass
    
    async def synthesize_script(self, script_text: str) -> bytes:
        """
        Synthesize script text to speech (for integration with video handler).
        
        Args:
            script_text: Text to synthesize
            
        Returns:
            bytes: Audio data or None if failed
        """
        try:
            # Extract just the script content, removing formatting
            lines = script_text.split('\n')
            script_content = []
            
            for line in lines:
                line = line.strip()
                # Skip headers, titles, and metadata
                if (line.startswith('**') or 
                    line.startswith('#') or 
                    line.startswith('Заголовок:') or
                    line.startswith('Описание:') or
                    line.startswith('Ключевые слова:') or
                    len(line) == 0):
                    continue
                script_content.append(line)
            
            # Join script content
            clean_script = ' '.join(script_content)
            
            if len(clean_script.strip()) == 0:
                logger.warning("No script content found for synthesis")
                return None
            
            # Limit length for TTS with smarter truncation
            if len(clean_script) > 8000:  # Increased from 4000 to 8000 characters
                # Try to find a good break point near the limit
                truncated = clean_script[:8000]  # Increased from 4000 to 8000
                last_sentence = max(
                    truncated.rfind('.'),
                    truncated.rfind('!'),
                    truncated.rfind('?')
                )
                if last_sentence > 7000:  # Increased from 3500 to 7000 (Only truncate at sentence if it's not too short)
                    clean_script = truncated[:last_sentence + 1]
                else:
                    clean_script = truncated + "..."
                logger.info(f"Script truncated from original length to {len(clean_script)} characters")
            else:
                logger.info(f"Script length: {len(clean_script)} characters, proceeding with full synthesis")
            
            logger.info(f"Synthesizing script: {clean_script[:100]}...")
            
            # Generate audio
            audio_bytes = await self.elevenlabs_client.text_to_speech(clean_script)
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Error synthesizing script: {e}")
            return None
