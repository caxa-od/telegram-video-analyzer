"""Gemini AI client for video analysis."""

import logging
from typing import List, Optional
import google.generativeai as genai
from PIL import Image
import io

from src.config import Config

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Gemini AI API."""
    
    def __init__(self):
        """Initialize Gemini client with API key."""
        if not Config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=Config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(Config.GEMINI_VISION_MODEL)
        logger.info(f"Initialized Gemini client with model: {Config.GEMINI_VISION_MODEL}")
    
    async def analyze_video_frames(self, frames: List[Image.Image], language: str = 'ru', prompt: str = None) -> str:
        """
        Analyze video frames using Gemini Vision.
        
        Args:
            frames: List of PIL Image objects representing video frames
            language: Language code for analysis
            prompt: Custom prompt for analysis (optional)
            
        Returns:
            Analysis result as string
        """
        try:
            if not frames:
                return "❌ Ошибка: не удалось извлечь кадры из видео"
            
            # Use custom prompt or get language-specific prompt
            if prompt:
                analysis_prompt = prompt
            else:
                analysis_prompt = Config.get_video_analysis_prompt(language)
            
            logger.info(f"Analyzing {len(frames)} frames with Gemini using language: {language}")
            
            # Prepare content for Gemini
            content = [analysis_prompt]
            
            # Add frames to content
            for i, frame in enumerate(frames):
                content.append(frame)
                logger.debug(f"Added frame {i+1}/{len(frames)} to analysis")
            
            # Generate response
            response = await self._generate_content_async(content)
            
            if response and response.text:
                logger.info("Successfully received analysis from Gemini")
                return response.text
            else:
                logger.error("Empty response from Gemini")
                return "❌ Ошибка: пустой ответ от Gemini"
                
        except Exception as e:
            logger.error(f"Error analyzing frames with Gemini: {e}")
            return f"❌ Ошибка при анализе видео: {str(e)}"
    
    async def _generate_content_async(self, content):
        """Generate content asynchronously (wrapper for sync call)."""
        try:
            # Note: Current Gemini API is synchronous, but we wrap it for future async support
            response = self.model.generate_content(content)
            return response
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Test connection to Gemini API."""
        try:
            # Simple text test instead of image to save quota
            response = self.model.generate_content("Ответь одним словом: тест")
            
            if response and response.text:
                logger.info("Gemini API connection test successful")
                return True
            else:
                logger.error("Gemini API connection test failed: empty response")
                return False
                
        except Exception as e:
            logger.error(f"Gemini API connection test failed: {e}")
            return False
