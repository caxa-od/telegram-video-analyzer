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