"""OpenAI GPT client for creating YouTube scripts."""

import logging
import asyncio
from typing import Optional
import openai
import re

from src.config import Config

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Client for interacting with OpenAI GPT API."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        try:
            # Configure OpenAI API
            openai.api_key = Config.OPENAI_API_KEY
            self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
            
            logger.info("OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test connection to OpenAI API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Simple test request with standard model and parameters
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Тест"}],
                max_tokens=10
            )
            
            if response and response.choices:
                logger.info("OpenAI API connection test successful")
                return True
            else:
                logger.error("OpenAI API connection test failed: empty response")
                return False
                
        except Exception as e:
            logger.error(f"OpenAI API connection test failed: {e}")
            return False
    
    async def create_youtube_script(self, video_description: str, video_duration: float, language: str = 'ru') -> str:
        """
        Create YouTube Shorts script based on video analysis.
        
        Args:
            video_description: Analysis result from Gemini
            video_duration: Duration of video in seconds
            language: Language code for script generation
            
        Returns:
            Generated script with titles and keywords
        """
        try:
            # Calculate character count (1 minute = 1000 characters)
            duration_minutes = video_duration / 60
            character_count = int(duration_minutes * 1000)
            
            # Format duration for display
            minutes = int(video_duration // 60)
            seconds = int(video_duration % 60)
            duration_str = f"{minutes}:{seconds:02d}"
            
            # Get language-specific prompt
            prompt_template = Config.get_gpt_script_prompt(language)
            
            prompt = prompt_template.format(
                duration=duration_str,
                character_count=character_count,
                video_description=video_description
            )
            
            # Get language-specific system message
            system_messages = {
                'ru': "Ты профессиональный сценарист для YouTube Shorts. Создаешь душевные и трогательные сценарии для озвучки видео.",
                'en': "You are a professional scriptwriter for YouTube Shorts. You create heartfelt and touching scripts for video voice-overs.",
                'es': "Eres un guionista profesional de YouTube Shorts. Creas guiones emotivos y conmovedores para narraciones de video."
            }
            
            system_message = system_messages.get(language, system_messages['ru'])
            
            logger.info(f"Creating YouTube script for {duration_str} video ({character_count} characters) in {language}")
            
            # Generate script using standard GPT-4o model
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.8
            )
            
            if response and response.choices:
                script = response.choices[0].message.content
                logger.info("Successfully generated YouTube script")
                return script
            else:
                logger.error("Empty response from OpenAI")
                return "❌ Не удалось создать сценарий"
                
        except Exception as e:
            logger.error(f"Error creating YouTube script: {e}")
            return f"❌ Ошибка создания сценария: {str(e)}"
    
    def extract_video_duration(self, video_description: str) -> Optional[float]:
        """
        Extract video duration from Gemini analysis.
        
        Args:
            video_description: Analysis result from Gemini
            
        Returns:
            Duration in seconds or None if not found
        """
        try:
            # Look for duration patterns in the description
            patterns = [
                r'(\d+):(\d+)',  # MM:SS format
                r'(\d+)\s*мин\w*\s*(\d+)\s*сек',  # X минут Y секунд
                r'(\d+)\s*сек',  # X секунд
                r'(\d+)\s*мин',  # X минут
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, video_description)
                if matches:
                    match = matches[-1]  # Take the last match
                    if len(match) == 2:  # MM:SS or min sec format
                        minutes = int(match[0])
                        seconds = int(match[1])
                        return minutes * 60 + seconds
                    elif len(match) == 1:  # Only seconds or only minutes
                        value = int(match[0])
                        if 'мин' in pattern:
                            return value * 60
                        else:
                            return value
            
            # Default fallback if duration not found
            logger.warning("Could not extract duration from description")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting video duration: {e}")
            return None
    
    def extract_script_content(self, full_response: str) -> str:
        """
        Extract only the main script content from GPT response.
        
        Args:
            full_response: Full GPT response with headers and structure
            
        Returns:
            Clean script text without headers
        """
        try:
            # Look for script content between markers
            patterns = [
                r'🎙️\s*\*\*СЦЕНАРИЙ ДЛЯ ОЗВУЧКИ:\*\*\s*\n(.*?)(?=\n📺|\n🔑|$)',
                r'🎙️\s*\*\*VOICE-OVER SCRIPT:\*\*\s*\n(.*?)(?=\n📺|\n🔑|$)',
                r'🎙️\s*\*\*GUIÓN DE NARRACIÓN:\*\*\s*\n(.*?)(?=\n📺|\n🔑|$)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, full_response, re.DOTALL | re.IGNORECASE)
                if match:
                    script_content = match.group(1).strip()
                    # Remove any remaining formatting markers
                    script_content = re.sub(r'\[.*?\]', '', script_content)
                    return script_content
            
            # Fallback: return full response if no pattern matches
            return full_response.strip()
            
        except Exception as e:
            logger.error(f"Error extracting script content: {e}")
            return full_response.strip()
    
    def validate_script_length(self, script_content: str, min_length: int = 700, max_length: int = 900) -> bool:
        """
        Validate if script content is within acceptable length range.
        
        Args:
            script_content: Clean script text (without headers)
            min_length: Minimum acceptable length in characters
            max_length: Maximum acceptable length in characters
            
        Returns:
            True if length is acceptable, False otherwise
        """
        char_count = len(script_content)
        logger.info(f"Script length validation: {char_count} chars (target: {min_length}-{max_length})")
        return min_length <= char_count <= max_length
    
    async def correct_script_length(self, original_script: str, current_length: int, target_min: int = 700, target_max: int = 900, language: str = 'ru') -> str:
        """
        Ask GPT to correct script length while preserving quality.
        
        Args:
            original_script: Original script text
            current_length: Current character count
            target_min: Target minimum length
            target_max: Target maximum length
            language: Language for correction prompt
            
        Returns:
            Corrected script text
        """
        try:
            # Determine correction action
            if current_length < target_min:
                action = "расширь" if language == 'ru' else "expand" if language == 'en' else "amplía"
                direction = "добавив больше эмоциональных деталей" if language == 'ru' else "adding more emotional details" if language == 'en' else "añadiendo más detalles emocionales"
            else:
                action = "сократи" if language == 'ru' else "shorten" if language == 'en' else "acorta"
                direction = "убрав избыточные детали" if language == 'ru' else "removing excessive details" if language == 'en' else "eliminando detalles excesivos"
            
            # Create correction prompt based on language
            if language == 'ru':
                correction_prompt = f"""
                Твой текст содержит {current_length} символов, а нужно {target_min}-{target_max} символов.
                
                {action.capitalize()} этот текст до {target_min}-{target_max} символов, {direction}.
                
                ВАЖНО: 
                - НЕ меняй стиль и общий смысл
                - Сохрани все ключевые моменты и эмоциональность
                - Сохрани структуру повествования
                - Верни только исправленный текст БЕЗ заголовков и пояснений
                
                Исходный текст:
                {original_script}
                """
            elif language == 'en':
                correction_prompt = f"""
                Your text contains {current_length} characters, but needs {target_min}-{target_max} characters.
                
                {action.capitalize()} this text to {target_min}-{target_max} characters by {direction}.
                
                IMPORTANT: 
                - DON'T change style and overall meaning
                - Keep all key moments and emotionality
                - Preserve narrative structure
                - Return only the corrected text WITHOUT headers and explanations
                
                Original text:
                {original_script}
                """
            else:  # Spanish
                correction_prompt = f"""
                Tu texto contiene {current_length} caracteres, pero necesita {target_min}-{target_max} caracteres.
                
                {action.capitalize()} este texto a {target_min}-{target_max} caracteres {direction}.
                
                IMPORTANTE: 
                - NO cambies el estilo y significado general
                - Mantén todos los momentos clave y emocionalidad
                - Preserva la estructura narrativa
                - Devuelve solo el texto corregido SIN encabezados y explicaciones
                
                Texto original:
                {original_script}
                """
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": correction_prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            if response.choices and response.choices[0].message:
                corrected_script = response.choices[0].message.content.strip()
                logger.info(f"Script length corrected: {len(original_script)} → {len(corrected_script)} chars")
                return corrected_script
            else:
                logger.error("Empty response from OpenAI for script correction")
                return original_script
                
        except Exception as e:
            logger.error(f"Error correcting script length: {e}")
            return original_script