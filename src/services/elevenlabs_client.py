"""ElevenLabs Text-to-Speech client for voice synthesis."""

import logging
import asyncio
from pathlib import Path
from typing import Optional, BinaryIO
import tempfile
import io

try:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import Voice, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

from src.config import Config

logger = logging.getLogger(__name__)

class ElevenLabsClient:
    """Client for ElevenLabs Text-to-Speech API."""
    
    def __init__(self):
        """Initialize ElevenLabs client."""
        if not ELEVENLABS_AVAILABLE:
            raise ImportError("ElevenLabs package not installed. Run: pip install elevenlabs")
            
        self.api_key = Config.ELEVENLABS_API_KEY
        self.voice_name = "Vasiliy"  # Russian voice
        self.voice_id = "1REYVgkHGlaFX4Rz9cPZ"  # Voice ID for Vasiliy
        
        # Initialize ElevenLabs client
        self.client = ElevenLabs(api_key=self.api_key)
        
        # Voice settings as specified (corrected style parameter)
        self.voice_settings = VoiceSettings(
            stability=0.4,
            similarity_boost=0.75,
            style=1.0  # Changed from 1.2 to 1.0 (max allowed value)
        )
        
        logger.info("ElevenLabs client initialized")
    
    def test_connection(self) -> bool:
        """
        Test connection to ElevenLabs API.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Try to get voices to test API connection
            voices = self.client.voices.get_all()
            return True
        except Exception as e:
            logger.error(f"ElevenLabs API connection test failed: {e}")
            return False
    
    async def text_to_speech(self, text: str, voice_id: str = None) -> Optional[bytes]:
        """
        Convert text to speech using ElevenLabs API.
        
        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID (optional, uses default if not provided)
            
        Returns:
            bytes: Audio data or None if failed
        """
        try:
            # Use provided voice_id or default
            selected_voice_id = voice_id or self.voice_id
            
            logger.info(f"Converting text to speech: {text[:50]}... (voice: {selected_voice_id})")
            
            # Run the generation in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            audio = await loop.run_in_executor(
                None,
                self._generate_audio,
                text,
                selected_voice_id
            )
            
            if audio:
                logger.info("Successfully generated audio with ElevenLabs")
                return audio
            else:
                logger.error("Failed to generate audio")
                return None
                
        except Exception as e:
            logger.error(f"Error in text_to_speech: {e}")
            return None
    
    def _generate_audio(self, text: str, voice_id: str = None) -> Optional[bytes]:
        """
        Internal method to generate audio (runs in thread pool).
        
        Args:
            text: Text to convert
            voice_id: ElevenLabs voice ID (optional)
            
        Returns:
            bytes: Audio data or None if failed
        """
        try:
            # Use provided voice_id or default
            selected_voice_id = voice_id or self.voice_id
            
            # Generate speech using the new API
            audio = self.client.text_to_speech.convert(
                voice_id=selected_voice_id,
                text=text,
                voice_settings=self.voice_settings,
                model_id="eleven_multilingual_v2"
            )
            
            # Convert generator to bytes if needed
            if hasattr(audio, '__iter__') and not isinstance(audio, (str, bytes)):
                audio_bytes = b''.join(audio)
            else:
                audio_bytes = audio
                
            return audio_bytes
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            return None
    
    async def text_to_speech_file(self, text: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Convert text to speech and save to file.
        
        Args:
            text: Text to convert to speech
            output_path: Optional output file path. If None, creates temp file.
            
        Returns:
            Path: Path to saved audio file or None if failed
        """
        try:
            # Generate audio
            audio_bytes = await self.text_to_speech(text)
            if not audio_bytes:
                return None
            
            # Create output path if not provided
            if output_path is None:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                output_path = Path(temp_file.name)
                temp_file.close()
            
            # Save audio to file
            with open(output_path, 'wb') as f:
                f.write(audio_bytes)
            
            logger.info(f"Audio saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error saving audio to file: {e}")
            return None
    
    async def get_available_voices(self) -> list:
        """
        Get list of available voices.
        
        Returns:
            list: List of available voice names
        """
        try:
            # For now, return the configured voice
            # In production, you might want to query the API for all voices
            return [self.voice_name]
        except Exception as e:
            logger.error(f"Error getting available voices: {e}")
            return []
    
    def cleanup_temp_file(self, file_path: Path) -> None:
        """
        Clean up temporary audio file.
        
        Args:
            file_path: Path to file to clean up
        """
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temp file {file_path}: {e}")
