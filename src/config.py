"""Config# Дебаг для проверки Environment Variables
print("🔧 DEBUG: Checking environment variables...")
print(f"🔑 DEBUG: TELEGRAM_BOT_TOKEN = {os.environ.get('TELEGRAM_BOT_TOKEN', 'NOT_SET')[:20]}...")
print(f"🔑 DEBUG: GEMINI_API_KEY = {os.environ.get('GEMINI_API_KEY', 'NOT_SET')[:20]}...")
print(f"🔑 DEBUG: ELEVENLABS_API_KEY = {os.environ.get('ELEVENLABS_API_KEY', 'NOT_SET')[:20]}...")
print(f"🔑 DEBUG: OPENAI_API_KEY = {os.environ.get('OPENAI_API_KEY', 'NOT_SET')[:20]}...")settings for the Telegram Video Analyzer Bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Дебаг для проверки Environment Variables
print("🔧 DEBUG: Checking environment variables...")
print(f"🔑 DEBUG: TELEGRAM_BOT_TOKEN = {os.environ.get('TELEGRAM_BOT_TOKEN', 'NOT_SET')[:20]}...")
print(f"🔑 DEBUG: GEMINI_API_KEY = {os.environ.get('GEMINI_API_KEY', 'NOT_SET')[:20]}...")
print(f"🔑 DEBUG: ELEVENLABS_API_KEY = {os.environ.get('ELEVENLABS_API_KEY', 'NOT_SET')[:20]}...")
print(f"🔑 DEBUG: OPENAI_API_KEY = {os.environ.get('OPENAI_API_KEY', 'NOT_SET')[:20]}...")

class Config:
    """Application configuration class."""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # ElevenLabs Configuration
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')
    
    # Language Support Configuration
    SUPPORTED_LANGUAGES = {
        'ru': {
            'name': '🇷🇺 Русский',
            'gemini_prompt_lang': 'русском',
            'gpt_prompt_lang': 'русском',
            'elevenlabs_voice_id': '1REYVgkHGlaFX4Rz9cPZ',  # Vasiliy
            'elevenlabs_voice_name': 'Vasiliy'
        },
        'en': {
            'name': '🇺🇸 English',
            'gemini_prompt_lang': 'English',
            'gpt_prompt_lang': 'English',
            'elevenlabs_voice_id': 'EXAVITQu4vr4xnSDxMaL',  # Sarah
            'elevenlabs_voice_name': 'Sarah'
        },
        'es': {
            'name': '🇪🇸 Español',
            'gemini_prompt_lang': 'Spanish',
            'gpt_prompt_lang': 'Spanish',
            'elevenlabs_voice_id': 'XrExE9yKIg1WjnnlVkGX',  # Mateo
            'elevenlabs_voice_name': 'Mateo'
        }
    }
    
    DEFAULT_LANGUAGE = 'ru'
    
        # Video Processing Configuration
    MAX_VIDEO_SIZE_MB = 50
    FRAME_INTERVAL_SECONDS = float(os.getenv('FRAME_INTERVAL_SECONDS', 5.0))
    MAX_FRAMES_PER_VIDEO = int(os.getenv('MAX_FRAMES_PER_VIDEO', 100))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # File Storage Configuration
    BASE_DIR = Path(__file__).parent
    TEMP_DIR = Path(os.getenv('TEMP_DIR', BASE_DIR / 'temp'))
    LOGS_DIR = Path(os.getenv('LOGS_DIR', BASE_DIR / 'logs'))
    
    # Create directories if they don't exist
    TEMP_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)
    
    # Gemini Configuration
    GEMINI_MODEL = "gemini-2.5-flash"
    GEMINI_VISION_MODEL = "gemini-2.5-flash"
    
    # Language-specific prompts
    VIDEO_ANALYSIS_PROMPTS = {
        'ru': """
        Проанализируй что происходит на этом видео ПОЛНОСТЬЮ от начала до конца. Тебе предоставлены кадры из ВСЕГО видео с интервалом 5 секунд. 
        
        ВАЖНО: Анализируй ВСЁ ВИДЕО ЦЕЛИКОМ, включая финальные кадры и концовку.
        
        Структура ответа должна быть:
        🎬 **АНАЛИЗ ВИДЕО**
        
        📋 **ОБЩЕЕ ОПИСАНИЕ:**
        [Краткое описание ВСЕГО содержания видео от начала до конца]
        
        ⏰ **РАСКАДРОВКА ПО ВРЕМЕНИ:**
        
        🕐 **0:00-0:05** - [Описание происходящего]
        🕐 **0:05-0:10** - [Описание происходящего]
        [и так далее до КОНЦА видео...]
        
        🎯 **КЛЮЧЕВЫЕ МОМЕНТЫ:**
        • [Важный момент 1]
        • [Важный момент 2]
        • [Важный момент 3]
        
        📝 **ЗАКЛЮЧЕНИЕ:**
        [Общие выводы о ПОЛНОМ видео, включая развязку и финал]
        """,
        'en': """
        Analyze what is happening in this video, I want to see a storyboard with what is happening over time.
        
        The response structure should be:
        🎬 **VIDEO ANALYSIS**
        
        📋 **GENERAL DESCRIPTION:**
        [Brief description of video content]
        
        ⏰ **TIMELINE BREAKDOWN:**
        
        🕐 **0:00-0:05** - [Description of what's happening]
        🕐 **0:05-0:10** - [Description of what's happening]
        [and so on...]
        
        🎯 **KEY MOMENTS:**
        • [Important moment 1]
        • [Important moment 2]
        • [Important moment 3]
        
        📝 **CONCLUSION:**
        [General conclusions about the video]
        """,
        'es': """
        Analiza lo que está pasando en este video, quiero ver un guión gráfico con lo que está pasando a lo largo del tiempo.
        
        La estructura de respuesta debe ser:
        🎬 **ANÁLISIS DE VIDEO**
        
        📋 **DESCRIPCIÓN GENERAL:**
        [Breve descripción del contenido del video]
        
        ⏰ **DESGLOSE TEMPORAL:**
        
        🕐 **0:00-0:05** - [Descripción de lo que está pasando]
        🕐 **0:05-0:10** - [Descripción de lo que está pasando]
        [y así sucesivamente...]
        
        🎯 **MOMENTOS CLAVE:**
        • [Momento importante 1]
        • [Momento importante 2]
        • [Momento importante 3]
        
        📝 **CONCLUSIÓN:**
        [Conclusiones generales sobre el video]
        """
    }
    
    GPT_SCRIPT_PROMPTS = {
        'ru': """
        Сделай мне сценарий для озвучки от 3-го лица этого видео длиною {duration}, примерно на {character_count} символов. 
        Видео должно быть душевным и трогательным. Видео должно начинаться с крутого лука который должен удерживать интригу до самого конца видео. 
        
        Также дай мне отдельно:
        1. Три варианта заголовка, они должны быть провокационным, вызывать чувство любопытства и желание досмотреть видео до конца. 
        2. Подбери 3 ключевых слова на основе происходящего в видео они должны точно соответствовать теме видео и не быть расплывчатыми или общими по смыслу. 
        
        Описание видео для анализа:
        {video_description}
        
        Структура ответа:
        
        🎙️ **СЦЕНАРИЙ ДЛЯ ОЗВУЧКИ:**
        [Сценарий текста для озвучки видео, точно {character_count} символов]
        
        📺 **ВАРИАНТЫ ЗАГОЛОВКОВ:**
        1. [Заголовок 1]
        2. [Заголовок 2] 
        3. [Заголовок 3]
        
        🔑 **КЛЮЧЕВЫЕ СЛОВА:**
        1. [Ключевое слово 1]
        2. [Ключевое слово 2]
        3. [Ключевое слово 3]
        """,
        'en': """
        Create a third-person voice-over script for this video of {duration} duration, approximately {character_count} characters. 
        The video should be heartfelt and touching. The video must start with a compelling hook that maintains intrigue until the very end of the video.
        
        Also provide separately:
        1. Three title options that should be provocative, evoke curiosity and the desire to watch the video to the end.
        2. Pick 3 keywords based on what happens in the video - they should accurately match the video theme and not be vague or general in meaning.
        
        Video description for analysis:
        {video_description}
        
        Response structure:
        
        🎙️ **VOICE-OVER SCRIPT:**
        [Third-person text script for video voice-over, exactly {character_count} characters]
        
        📺 **TITLE OPTIONS:**
        1. [Title 1]
        2. [Title 2] 
        3. [Title 3]
        
        🔑 **KEYWORDS:**
        1. [Keyword 1]
        2. [Keyword 2]
        3. [Keyword 3]
        """,
        'es': """
        Crea un guión de narración en tercera persona para este video de {duration} de duración, aproximadamente {character_count} caracteres.
        El video debe ser emotivo y conmovedor. El video debe comenzar con un gancho compelling que mantenga la intriga hasta el final del video.
        
        También proporciona por separado:
        1. Tres opciones de título que deben ser provocativos, evocar curiosidad y el deseo de ver el video hasta el final.
        2. Elige 3 palabras clave basadas en lo que sucede en el video - deben coincidir exactamente con el tema del video y no ser vagas o generales en significado.
        
        Descripción de video para análisis:
        {video_description}
        
        Estructura de respuesta:
        
        🎙️ **GUIÓN DE NARRACIÓN:**
        [Guión de texto en tercera persona para narración de video, exactamente {character_count} caracteres]
        
        📺 **OPCIONES DE TÍTULO:**
        1. [Título 1]
        2. [Título 2] 
        3. [Título 3]
        
        🔑 **PALABRAS CLAVE:**
        1. [Palabra clave 1]
        2. [Palabra clave 2]
        3. [Palabra clave 3]
        """
    }
    
    @classmethod
    def get_video_analysis_prompt(cls, language='ru'):
        """Get video analysis prompt for specified language."""
        return cls.VIDEO_ANALYSIS_PROMPTS.get(language, cls.VIDEO_ANALYSIS_PROMPTS[cls.DEFAULT_LANGUAGE])
    
    @classmethod
    def get_gpt_script_prompt(cls, language='ru'):
        """Get GPT script prompt for specified language."""
        return cls.GPT_SCRIPT_PROMPTS.get(language, cls.GPT_SCRIPT_PROMPTS[cls.DEFAULT_LANGUAGE])
    
    @classmethod
    def get_language_config(cls, language='ru'):
        """Get language configuration."""
        return cls.SUPPORTED_LANGUAGES.get(language, cls.SUPPORTED_LANGUAGES[cls.DEFAULT_LANGUAGE])
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate required configuration parameters."""
        required_vars = [
            'TELEGRAM_BOT_TOKEN',
            'GEMINI_API_KEY',
            'ELEVENLABS_API_KEY'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"Missing required environment variables: {', '.join(missing_vars)}")
            print("Please check your .env file")
            return False
        
        return True
