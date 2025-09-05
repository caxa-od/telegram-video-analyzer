"""Telegram bot handlers for video processing."""

import logging
import asyncio
from telegram import Update, Message, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from pathlib import Path
import tempfile
import os

from src.services.video_processor import VideoProcessor
from src.services.gemini_client import GeminiClient
from src.services.openai_client import OpenAIClient
from src.services.elevenlabs_client import ElevenLabsClient
from src.handlers.language_handler import LanguageHandler
from src.config import Config

logger = logging.getLogger(__name__)

class VideoAnalysisHandler:
    """Handler for video analysis functionality."""
    
    def __init__(self):
        """Initialize handler with required services."""
        self.video_processor = VideoProcessor()
        self.gemini_client = GeminiClient()
        self.openai_client = OpenAIClient()
        self.elevenlabs_client = ElevenLabsClient()
        self.language_handler = LanguageHandler()
        logger.info("Initialized VideoAnalysisHandler")
    
    async def handle_video(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle incoming video messages.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            message = update.message
            video = message.video
            
            if not video:
                await message.reply_text("❌ Ошибка: видео не найдено в сообщении")
                return
            
            # Check video size
            if video.file_size > Config.MAX_VIDEO_SIZE_MB * 1024 * 1024:
                file_size_mb = round(video.file_size / (1024 * 1024), 1)
                await message.reply_text(
                    f"❌ Видео слишком большое!\n\n"
                    f"📏 Размер вашего видео: {file_size_mb} МБ\n"
                    f"📐 Максимальный размер: {Config.MAX_VIDEO_SIZE_MB} МБ\n\n"
                    f"💡 Что можно сделать:\n"
                    f"• Сжать видео с помощью любого видеоредактора\n"
                    f"• Уменьшить разрешение видео\n"
                    f"• Сократить длительность видео\n"
                    f"• Использовать более сжатый кодек (H.264)"
                )
                return
            
            # Send processing message
            processing_msg = await message.reply_text(
                "🎬 Обрабатываю видео...\n"
                "⏳ Это может занять несколько минут"
            )
            
            # Download video file
            video_file = await context.bot.get_file(video.file_id)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_path = Path(temp_file.name)
                await video_file.download_to_drive(temp_path)
            
            logger.info(f"Downloaded video to: {temp_path}")
            
            # Update progress
            await processing_msg.edit_text(
                "🎬 Видео загружено\n"
                "🔍 Извлекаю кадры..."
            )
            
            # Extract frames
            frames = await self.video_processor.extract_frames_from_video(temp_path)
            
            if not frames:
                await processing_msg.edit_text("❌ Ошибка: не удалось извлечь кадры из видео")
                self.video_processor.cleanup_temp_file(temp_path)
                return
            
            # Get user language
            user_language = self.language_handler.get_user_language(context)
            
            # Update progress
            await processing_msg.edit_text(
                f"🎬 Извлечено {len(frames)} кадров\n"
                "🤖 Анализирую с помощью Gemini..."
            )
            
            # Analyze with Gemini using user's language
            analysis_result = await self.gemini_client.analyze_video_frames(frames, user_language)
            
            # Update progress
            await processing_msg.edit_text("✅ Анализ завершен! Создаю сценарий...")
            
            # Get video info for duration
            video_info = self.video_processor.get_video_info(temp_path)
            video_duration = video_info.get('duration', 60)  # Default to 60 seconds
            
            # Extract duration from analysis if not available
            if not video_duration or video_duration == 0:
                extracted_duration = self.openai_client.extract_video_duration(analysis_result)
                if extracted_duration:
                    video_duration = extracted_duration
                else:
                    video_duration = 60  # Default fallback
            
            # Create YouTube script with OpenAI using user's language
            youtube_script = await self.openai_client.create_youtube_script(
                analysis_result, video_duration, user_language
            )
            
            # Update progress
            await processing_msg.edit_text("✅ Готово! Отправляю результаты...")
            
            # Send analysis result in separate blocks
            await self._send_analysis_blocks(message, analysis_result)
            
            # Send YouTube script
            script_message = f"🎙️ **СЦЕНАРИЙ ДЛЯ YOUTUBE SHORTS**\n\n{youtube_script}"
            await message.reply_text(script_message, parse_mode=None)
            
            # Generate voice synthesis for the script
            await processing_msg.edit_text("🎙️ Создаю озвучку сценария...")
            
            try:
                # Extract and synthesize script content
                audio_bytes = await self._synthesize_script(youtube_script, user_language)
                
                if audio_bytes:
                    # Create temporary file for audio
                    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_audio:
                        temp_audio.write(audio_bytes)
                        temp_audio_path = Path(temp_audio.name)
                    
                    # Send voice message
                    with open(temp_audio_path, 'rb') as audio_file:
                        await message.reply_voice(
                            voice=audio_file,
                            caption="🎙️ Озвучка сценария готова!"
                        )
                    
                    # Cleanup audio file
                    self.elevenlabs_client.cleanup_temp_file(temp_audio_path)
                    logger.info("Successfully generated voice synthesis for script")
                else:
                    await message.reply_text("⚠️ Не удалось создать озвучку сценария")
                    
            except Exception as voice_error:
                logger.error(f"Error generating voice synthesis: {voice_error}")
                error_message = "⚠️ Ошибка при создании озвучки сценария"
                
                # Check if it's a quota error
                if "quota_exceeded" in str(voice_error) or "credits remaining" in str(voice_error):
                    error_message = "⚠️ Превышена квота ElevenLabs. Попробуйте позже или обновите план."
                
                await message.reply_text(error_message)
            
            # Cleanup
            self.video_processor.cleanup_temp_file(temp_path)
            
            logger.info(f"Successfully processed video for user {message.from_user.id}")
            
        except Exception as e:
            logger.error(f"Error handling video: {e}")
            try:
                await message.reply_text(
                    f"❌ Произошла ошибка при обработке видео:\n{str(e)}"
                )
            except:
                pass
            
            # Cleanup on error
            if 'temp_path' in locals():
                self.video_processor.cleanup_temp_file(temp_path)
    
    async def handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        welcome_message = """
🎬 **Добро пожаловать в Video Analyzer Bot!**

Этот бот анализирует видео с помощью Gemini AI и создает:
• Подробную раскадровку содержания
• Сценарий для озвучки YouTube Shorts
• Варианты заголовков и ключевые слова

📹 **Как использовать:**
1. Отправьте мне видео файл
2. Дождитесь обработки
3. Получите анализ видео
4. Получите готовый сценарий для озвучки

⚡ **Ограничения:**
• Максимальный размер видео: {max_size}MB
• Максимальная длительность обработки: 5 минут

🤖 Powered by **Gemini AI** + **OpenAI GPT**
        """.format(max_size=Config.MAX_VIDEO_SIZE_MB)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='Markdown'
        )
        
        logger.info(f"Sent welcome message to user {update.message.from_user.id}")
    
    async def handle_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        help_message = """
🆘 **Справка по Video Analyzer Bot**

📋 **Основные команды:**
• `/start` - Начать работу с ботом
• `/help` - Показать эту справку

🌍 **Переключение языка:**
• `/language` - Показать кнопки выбора языка
• `/set_ru` - Переключить на русский язык 🇷🇺
• `/set_en` - Переключить на английский язык 🇺🇸  
• `/set_es` - Переключить на испанский язык 🇪🇸

📹 **Анализ видео:**
1. Просто отправьте видео файл в чат
2. Бот автоматически начнет обработку
3. Результат будет отправлен в виде анализа, скрипта и озвучки

🎙️ **Голосовой синтез:**
• `/voice_text [текст]` - Озвучить произвольный текст
• `/voice_settings` - Показать настройки голоса
• Автоматическая озвучка сценариев после анализа видео

⚙️ **Настройки анализа:**
• Интервал между кадрами: {interval}с
• Максимум кадров: {max_frames}
• Максимальный размер: {max_size}MB

🔧 **Поддерживаемые форматы:**
• MP4, AVI, MOV, WMV
• Максимальное разрешение: 1920x1080

💡 **Пример команд:**
• `/voice_text Привет, это тестовое сообщение!`
• Просто отправьте видео для полного анализа

❓ **Проблемы?**
Убедитесь, что:
• Видео не превышает {max_size}MB
• Файл не поврежден
• Формат поддерживается
        """.format(
            interval=Config.FRAME_INTERVAL_SECONDS,
            max_frames=Config.MAX_FRAMES_PER_VIDEO,
            max_size=Config.MAX_VIDEO_SIZE_MB
        )
        
        await update.message.reply_text(
            help_message,
            parse_mode='Markdown'
        )
        
        # Добавим тестовую кнопку для диагностики callback
        test_keyboard = [[
            InlineKeyboardButton("🧪 Тест кнопки", callback_data="test_button")
        ]]
        await update.message.reply_text(
            "🧪 Тест inline кнопки:",
            reply_markup=InlineKeyboardMarkup(test_keyboard)
        )
        
        logger.info(f"Sent help message to user {update.message.from_user.id}")
    
    async def handle_unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle unknown messages (non-video).
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        await update.message.reply_text(
            "📹 Пожалуйста, отправьте видео файл для анализа.\n\n"
            "Используйте /help для получения справки."
        )
        
        logger.info(f"Received unknown message from user {update.message.from_user.id}")
    
    async def _synthesize_script(self, script_text: str, language: str = 'ru') -> bytes:
        """
        Synthesize script text to speech for automatic voice generation.
        
        Args:
            script_text: YouTube script text to synthesize
            language: Language code for voice selection
            
        Returns:
            bytes: Audio data or None if failed
        """
        try:
            # Get language configuration
            lang_config = Config.get_language_config(language)
            
            # Find the script section specifically
            lines = script_text.split('\n')
            script_content = []
            in_script_section = False
            
            # Look for different script section headers based on language
            script_headers = {
                'ru': "🎙️ **СЦЕНАРИЙ ДЛЯ ОЗВУЧКИ:**",
                'en': "🎙️ **VOICE-OVER SCRIPT:**", 
                'es': "🎙️ **GUIÓN DE NARRACIÓN:**"
            }
            
            target_header = script_headers.get(language, script_headers['ru'])
            
            for line in lines:
                line = line.strip()
                
                # Start collecting after finding the script header
                if "🎙️" in line and any(keyword in line for keyword in ["СЦЕНАРИЙ", "SCRIPT", "GUIÓN"]):
                    in_script_section = True
                    continue
                    
                # Stop collecting when we hit other sections
                if in_script_section and (
                    line.startswith("📺") or 
                    line.startswith("🔑") or
                    line.startswith("**ВАРИАНТЫ ЗАГОЛОВКОВ") or
                    line.startswith("**КЛЮЧЕВЫЕ СЛОВА") or
                    line.startswith("**TITLE OPTIONS") or
                    line.startswith("**KEYWORDS") or
                    ("ЗАГОЛОВКОВ" in line and "ВАРИАНТЫ" in line) or
                    ("КЛЮЧЕВЫЕ" in line and "СЛОВА" in line) or
                    ("TITLE" in line and "OPTIONS" in line) or
                    ("KEYWORDS" in line)
                ):
                    break
                    
                # Collect script content (skip empty lines and format markers)
                if in_script_section:
                    if (len(line) > 0 and 
                        not line.startswith('[') and 
                        not line.startswith('**') and
                        not line.startswith('#') and
                        not line == "---"):
                        script_content.append(line)
            
            # Join script content
            clean_script = ' '.join(script_content).strip()
            
            # Remove any remaining formatting markers
            clean_script = clean_script.replace('[', '').replace(']', '')
            
            if len(clean_script.strip()) == 0:
                logger.warning("No script content found for synthesis")
                return None
            
            # Limit length for TTS (moderate limit for better quality)
            if len(clean_script) > 1000:
                # Try to find a good break point near the limit
                truncated = clean_script[:1000]
                last_sentence = max(
                    truncated.rfind('.'),
                    truncated.rfind('!'),
                    truncated.rfind('?')
                )
                if last_sentence > 800:  # Only truncate at sentence if it's not too short
                    clean_script = truncated[:last_sentence + 1]
                else:
                    clean_script = truncated + "..."
            
            logger.info(f"Extracted script for synthesis ({len(clean_script)} chars): {clean_script[:100]}...")
            logger.debug(f"Full extracted script: {clean_script}")
            
            # Generate audio using ElevenLabs with language-specific voice
            audio_bytes = await self.elevenlabs_client.text_to_speech(
                clean_script, 
                voice_id=lang_config['elevenlabs_voice_id']
            )
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Error synthesizing script: {e}")
            return None
    
    async def _send_analysis_blocks(self, message: Message, analysis_result: str) -> None:
        """
        Send analysis result as separate blocks.
        
        Args:
            message: Telegram message object to reply to
            analysis_result: Full analysis text to split into blocks
        """
        try:
            # Split the analysis into blocks based on headers
            blocks = []
            
            # Find each section by its header
            sections = [
                ("📋 **ОБЩЕЕ ОПИСАНИЕ:**", "⏰ **РАСКАДРОВКА ПО ВРЕМЕНИ:**"),
                ("⏰ **РАСКАДРОВКА ПО ВРЕМЕНИ:**", "🎯 **КЛЮЧЕВЫЕ МОМЕНТЫ:**"),
                ("🎯 **КЛЮЧЕВЫЕ МОМЕНТЫ:**", "📝 **ЗАКЛЮЧЕНИЕ:**"),
                ("📝 **ЗАКЛЮЧЕНИЕ:**", None)
            ]
            
            for start_marker, end_marker in sections:
                start_pos = analysis_result.find(start_marker)
                if start_pos != -1:
                    if end_marker:
                        end_pos = analysis_result.find(end_marker)
                        if end_pos != -1:
                            block_text = analysis_result[start_pos:end_pos].strip()
                        else:
                            block_text = analysis_result[start_pos:].strip()
                    else:
                        block_text = analysis_result[start_pos:].strip()
                    
                    if block_text:
                        blocks.append(block_text)
            
            # If no blocks found, send as single message
            if not blocks:
                await message.reply_text(f"🎬 **АНАЛИЗ ВИДЕО**\n\n{analysis_result}", parse_mode=None)
                return
            
            # Send each block as separate message
            for block in blocks:
                await message.reply_text(block, parse_mode=None)
                # Small delay to avoid spam protection
                await asyncio.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error sending analysis blocks: {e}")
            # Fallback to single message
            await message.reply_text(f"🎬 **АНАЛИЗ ВИДЕО**\n\n{analysis_result}", parse_mode=None)

class MessageHandler:
    """Handler for different types of messages."""
    
    def __init__(self):
        """Initialize message handler."""
        self.video_handler = VideoAnalysisHandler()
        logger.info("Initialized MessageHandler")
    
    async def route_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Route different types of messages to appropriate handlers.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            message = update.message
            
            if message.video:
                await self.video_handler.handle_video(update, context)
            else:
                await self.video_handler.handle_unknown(update, context)
                
        except Exception as e:
            logger.error(f"Error routing message: {e}")
            try:
                await message.reply_text("❌ Произошла внутренняя ошибка")
            except:
                pass
