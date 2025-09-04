"""Language settings handler for multi-language support."""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from src.config import Config

logger = logging.getLogger(__name__)

class LanguageHandler:
    """Handler for language selection and settings."""
    
    def __init__(self):
        """Initialize language handler."""
        logger.info("Initialized LanguageHandler")
    
    async def handle_language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /language command to show language selection.
        
        Args:
            update: Telegram update object
            context: Telegram context object
        """
        try:
            # Get current language from user data or use default
            current_lang = context.user_data.get('language', Config.DEFAULT_LANGUAGE)
            current_lang_config = Config.get_language_config(current_lang)
            
            # Создаем текстовый интерфейс вместо inline кнопок (временно)
            message_text = f"""
🌍 **Выбор языка / Language Selection**

**Текущий язык:** {current_lang_config['name']}

**Доступные команды для переключения языка:**

🇷🇺 `/set_ru` - Русский (голос: Vasiliy)
🇺🇸 `/set_en` - English (voice: Sarah)  
🇪🇸 `/set_es` - Español (voz: Mateo)

Просто отправьте нужную команду для переключения языка!
"""
            
            await update.message.reply_text(
                message_text,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Error in language command: {e}")
            await update.message.reply_text(
                "❌ Ошибка при обработке команды языка"
            )
    
    async def handle_language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle language selection callback.
        
        Args:
            update: Telegram update object  
            context: Telegram context object
        """
        try:
            query = update.callback_query
            logger.info(f"Received language callback: {query.data}")
            
            # Answer the callback query first
            await query.answer()
            
            # Extract language code from callback data
            if not query.data.startswith('lang_'):
                logger.warning(f"Invalid callback data: {query.data}")
                return
            
            selected_lang = query.data.replace('lang_', '')
            logger.info(f"Selected language: {selected_lang}")
            
            # Validate language
            if selected_lang not in Config.SUPPORTED_LANGUAGES:
                logger.error(f"Unsupported language: {selected_lang}")
                await query.edit_message_text(
                    "❌ Неподдерживаемый язык"
                )
                return
            
            # Save language to user data
            context.user_data['language'] = selected_lang
            lang_config = Config.get_language_config(selected_lang)
            logger.info(f"Language config for {selected_lang}: {lang_config}")
            
            await query.edit_message_text(
                f"✅ **Язык изменен / Language Changed**\n\n"
                f"🔤 **Новый язык:** {lang_config['name']}\n"
                f"🎙️ **Голос для озвучки:** {lang_config['elevenlabs_voice_name']}\n\n"
                f"Теперь все анализы видео, сценарии и озвучка будут на выбранном языке.\n"
                f"Now all video analysis, scripts and voice synthesis will be in the selected language.",
                parse_mode='Markdown'
            )
            
            logger.info(f"User {query.from_user.id} changed language to {selected_lang}")
            
        except Exception as e:
            logger.error(f"Error in language callback: {e}")
            await query.edit_message_text(
                "❌ Ошибка при изменении языка"
            )
    
    async def handle_set_russian(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /set_ru command."""
        await self._set_language(update, context, 'ru')
    
    async def handle_set_english(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /set_en command."""
        await self._set_language(update, context, 'en')
    
    async def handle_set_spanish(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /set_es command."""
        await self._set_language(update, context, 'es')
    
    async def _set_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE, language: str) -> None:
        """
        Set user language.
        
        Args:
            update: Telegram update object
            context: Telegram context object
            language: Language code
        """
        try:
            if language not in Config.SUPPORTED_LANGUAGES:
                await update.message.reply_text("❌ Неподдерживаемый язык")
                return
            
            # Save language to user data
            context.user_data['language'] = language
            lang_config = Config.get_language_config(language)
            
            await update.message.reply_text(
                f"✅ **Язык изменен / Language Changed**\n\n"
                f"🔤 **Новый язык:** {lang_config['name']}\n"
                f"🎙️ **Голос для озвучки:** {lang_config['elevenlabs_voice_name']}\n\n"
                f"Теперь все анализы видео, сценарии и озвучка будут на выбранном языке.\n"
                f"Now all video analysis, scripts and voice synthesis will be in the selected language.",
                parse_mode='Markdown'
            )
            
            logger.info(f"User {update.message.from_user.id} changed language to {language}")
            
        except Exception as e:
            logger.error(f"Error setting language: {e}")
            await update.message.reply_text("❌ Ошибка при изменении языка")
    
    def get_user_language(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        """
        Get user's selected language or default.
        
        Args:
            context: Telegram context object
            
        Returns:
            Language code
        """
        return context.user_data.get('language', Config.DEFAULT_LANGUAGE)
