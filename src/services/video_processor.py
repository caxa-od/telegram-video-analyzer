"""Video processing utilities for extracting frames from videos."""

import logging
import tempfile
import cv2
import numpy as np
from typing import List, Optional, Tuple
from pathlib import Path
from PIL import Image
import os

from src.config import Config

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Class for processing video files and extracting frames."""
    
    def __init__(self):
        """Initialize video processor."""
        self.temp_dir = Config.TEMP_DIR
        logger.info("Initialized VideoProcessor")
    
    async def extract_frames_from_video(self, video_path: Path, interval_seconds: float = None) -> List[Image.Image]:
        """
        Extract frames from video at specified intervals.
        
        Args:
            video_path: Path to video file
            interval_seconds: Interval between frames in seconds
            
        Returns:
            List of PIL Image objects
        """
        try:
            interval = interval_seconds or Config.FRAME_INTERVAL_SECONDS
            frames = []
            
            logger.info(f"Extracting frames from video: {video_path}")
            
            # Open video file
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                logger.error(f"Could not open video file: {video_path}")
                return []
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Video info: FPS={fps}, Total frames={total_frames}, Duration={duration:.2f}s")
            
            # Calculate frame interval
            frame_interval = int(fps * interval) if fps > 0 else 30
            
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Extract frame at intervals
                if frame_count % frame_interval == 0:
                    if extracted_count >= Config.MAX_FRAMES_PER_VIDEO:
                        logger.info(f"Reached maximum frame limit: {Config.MAX_FRAMES_PER_VIDEO}")
                        break
                    
                    # Convert BGR to RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Convert to PIL Image
                    pil_image = Image.fromarray(frame_rgb)
                    
                    # Resize if needed (optional optimization)
                    pil_image = self._resize_image(pil_image)
                    
                    frames.append(pil_image)
                    extracted_count += 1
                    
                    time_stamp = frame_count / fps
                    logger.info(f"Extracted frame {extracted_count} at {time_stamp:.2f}s")
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Successfully extracted {len(frames)} frames from video")
            
            return frames
            
        except Exception as e:
            logger.error(f"Error extracting frames from video: {e}")
            return []
    
    def _resize_image(self, image: Image.Image, max_size: Tuple[int, int] = (1024, 1024)) -> Image.Image:
        """
        Resize image while maintaining aspect ratio.
        
        Args:
            image: PIL Image to resize
            max_size: Maximum size (width, height)
            
        Returns:
            Resized PIL Image
        """
        try:
            # Get current size
            width, height = image.size
            
            # Calculate new size maintaining aspect ratio
            if width > max_size[0] or height > max_size[1]:
                ratio = min(max_size[0] / width, max_size[1] / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                logger.debug(f"Resized image from {width}x{height} to {new_width}x{new_height}")
            
            return image
            
        except Exception as e:
            logger.error(f"Error resizing image: {e}")
            return image
    
    async def download_video_from_telegram(self, file_path: str, file_id: str) -> Optional[Path]:
        """
        Download video file from Telegram and save to temp directory.
        
        Args:
            file_path: Telegram file path
            file_id: Telegram file ID
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Create unique filename
            temp_filename = f"video_{file_id}.mp4"
            temp_path = self.temp_dir / temp_filename
            
            logger.info(f"Saving video to: {temp_path}")
            
            # Note: This method should be called with actual file download logic
            # The file_path parameter would contain the downloaded file data
            
            return temp_path
            
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def cleanup_temp_file(self, file_path: Path) -> None:
        """
        Clean up temporary file.
        
        Args:
            file_path: Path to file to delete
        """
        try:
            if file_path.exists():
                os.remove(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.error(f"Error cleaning up temp file {file_path}: {e}")
    
    def get_video_info(self, video_path: Path) -> dict:
        """
        Get video information.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            cap = cv2.VideoCapture(str(video_path))
            
            if not cap.isOpened():
                return {}
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            cap.release()
            
            info = {
                'fps': fps,
                'total_frames': total_frames,
                'duration': duration,
                'width': width,
                'height': height,
                'size_mb': video_path.stat().st_size / (1024 * 1024) if video_path.exists() else 0
            }
            
            logger.info(f"Video info: {info}")
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
