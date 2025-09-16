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
    MAX_VIDEO_SIZE_MB = 20
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
        Ты получаешь описание или раскадровку видео о спасении животного.
        Твоя задача — превратить это в цельный трогательный рассказ, написанный от третьего лица, максимально в стиле эталонного примера:

        "Парень пришёл выбросить мусор, а заметил на баке истощённого кота. Он был явно уличным и, видимо, давно не ел нормальной еды. Он был настолько худым, что сердце парня сжалось, и он просто не мог на это смотреть без слёз. Кот был явно когда-то домашним, но прошлые хозяева просто выбросили его на улицу. Кот перестал верить людям и не сразу дался в руки. Его приманили едой, и кот постепенно начал контактировать. Парень не сдавался и продолжал добиваться его доверия, и как только его удалось поймать, люди сразу же отнесли его в ветклинику. Коту провели полный обследование и оказали первую помощь. Впереди было долгое восстановление, и парень станет его опекуном. Благодаря усилиям и заботе людей, кот набрал вес и стал доверять людям. Он уже не боялся и не голодал. Кот жил в тёплом доме, где его любили и уважали. Доброта людей подарили ему настоящий шанс на вторую жизнь. Кота полюбили всем сердцем и обеспечат ему самую лучшую жизнь."

        📜 Правила написания:

        Только третье лицо.
        История должна быть написана строго от третьего лица.
        Никаких "я", "мы", "наш". Используй только конструкции:
        «женщина заметила…»
        «мужчина подошёл…»
        «сердце спасателя сжалось…»

        Начало — сразу с драмы.
        Первое предложение должно сразу содержать:
        кто заметил,
        кого заметил,
        что животное было брошено/оставлено.
        Пример: «Женщина заметила на холодном асфальте крошечного опоссума, которого мать бросила и ушла прочь.»

        Причина беды обязательна.
        В начале истории всегда указывай, почему животное оказалось в беде (бросила мать, выбросили, потерялось).

        Добавь детали внешнего вида.
        В первых абзацах обязательно упомяни признаки страдания животного (дрожь, худоба, грязь, шерсть выпадает, воспалённые глаза и т. д.). Это усиливает драму.

        Структура из 5 этапов:
        Начало: беда + причина + детали состояния.
        Конфликт: недоверие, страх, отказ идти на контакт.
        Поворот: первый контакт и забота (кормление, лечение, ласка).
        Развитие: восстановление здоровья, рост доверия, дружба с людьми.
        Финал: контраст с началом — напомни, каким несчастным оно было, и покажи, как оно теперь окружено любовью.

        Финал всегда тёплый и вдохновляющий.
        Он должен вызывать слёзы радости и подчёркивать: «Больше его никогда не бросят».

        Стиль: простая, живая и эмоциональная речь. Образы должны быть сильными:
        «тень самого себя»
        «искры жизни в глазах»
        «сердце сжалось»

        Длина текста: примерно {character_count} символов (700–900).

        ⚠️ ОБЯЗАТЕЛЬНАЯ САМОПРОВЕРКА

        Перед ответом сравни свой текст с эталоном:

        ✅ Первое предложение содержит «кто заметил», «кого заметил» и «почему он один»?
        ✅ Есть ли описания внешнего вида и страданий животного в начале?
        ✅ Есть ли все 5 этапов (бедствие → конфликт → поворот → восстановление → финал)?
        ✅ Есть ли драма доверия?
        ✅ Длина в диапазоне {character_count}?
        ✅ Финал тёплый, контрастный и вдохновляющий (с обязательным напоминанием о начале)?
        ✅ Рассказ написан строго от третьего лица?

        Если хотя бы один пункт не выполнен → переписать!

        Входные данные (описание видео):
        {video_description}

        📦 Структура ответа

        🎙️ **СЦЕНАРИЙ ДЛЯ ОЗВУЧКИ:**
        [Цельный рассказ на {character_count} символов]

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
        You receive a description or storyboard of a video about animal rescue.
        Your task is to turn this into a cohesive touching story, written in third person, in the style of this reference example:

        "A guy came to throw out trash and noticed an exhausted cat on the dumpster. It was clearly a street cat and apparently hadn't eaten proper food for a long time. It was so thin that the guy's heart sank, and he just couldn't look at it without tears. The cat was clearly once domestic, but previous owners simply threw it out on the street. The cat stopped trusting people and didn't immediately let itself be caught. They lured it with food, and the cat gradually began to make contact. The guy didn't give up and continued to earn its trust, and as soon as they managed to catch it, people immediately took it to the vet clinic. The cat underwent a full examination and received first aid. There was a long recovery ahead, and the guy would become its guardian. Thanks to people's efforts and care, the cat gained weight and began to trust people. It was no longer afraid and hungry. The cat lived in a warm home where it was loved and respected. People's kindness gave it a real chance for a second life. The cat was loved with all their hearts and they would provide it with the best life."

        📜 Writing Rules:

        Third person only.
        The story must be written strictly in third person.
        No "I", "we", "our". Use only constructions like:
        "the woman noticed..."
        "the man approached..."
        "the rescuer's heart sank..."

        Beginning — immediately with drama.
        The first sentence should immediately contain:
        who noticed,
        whom they noticed,
        that the animal was abandoned/left behind.
        Example: "A woman noticed a tiny opossum on the cold asphalt that its mother had abandoned and left behind."

        Reason for the trouble is mandatory.
        At the beginning of the story, always indicate why the animal ended up in trouble (mother abandoned it, was thrown out, got lost).

        Add details of appearance.
        In the first paragraphs, be sure to mention signs of the animal's suffering (trembling, thinness, dirt, fur falling out, inflamed eyes, etc.). This enhances the drama.

        5-stage structure:
        Beginning: trouble + reason + condition details.
        Conflict: distrust, fear, refusal to make contact.
        Turning point: first contact and care (feeding, treatment, affection).
        Development: health recovery, growing trust, friendship with people.
        Ending: contrast with the beginning — remind how miserable it was, and show how it's now surrounded by love.

        Ending is always warm and inspiring.
        It should bring tears of joy and emphasize: "It will never be abandoned again."

        Style: simple, lively and emotional speech. Images should be strong:
        "shadow of itself"
        "sparks of life in the eyes"
        "heart sank"

        Text length: approximately {character_count} characters (700–900).

        ⚠️ MANDATORY SELF-CHECK

        Before responding, compare your text with the reference:

        ✅ Does the first sentence contain "who noticed", "whom they noticed" and "why it's alone"?
        ✅ Are there descriptions of appearance and animal suffering at the beginning?
        ✅ Are all 5 stages present (disaster → conflict → turning point → recovery → ending)?
        ✅ Is there trust drama?
        ✅ Is the length within {character_count} range?
        ✅ Is the ending warm, contrasting and inspiring (with mandatory reminder of the beginning)?
        ✅ Is the story written strictly in third person?

        If at least one point is not fulfilled → rewrite!

        Input data (video description):
        {video_description}

        📦 Response Structure

        🎙️ **VOICE-OVER SCRIPT:**
        [Complete story of {character_count} characters]

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
        Recibes una descripción o guión gráfico de un video sobre rescate de animales. 
        Tu tarea es convertir esto en una historia conmovedora y cohesiva, escrita en tercera persona, 
        en el estilo de este ejemplo de referencia:

        "El chico notó en el concreto frío un gato que parecía la sombra de sí mismo. 
        Estaba delgado hasta los huesos, el pelaje se caía en mechones, la piel estaba inflamada, y los ojos llenos de dolor y fatiga. 
        El corazón del chico se encogió, y no pudo contener las lágrimas. Era evidente que una vez el gato fue doméstico, 
        pero la gente simplemente lo desechó, dejándolo solo con la enfermedad y la calle.
        ... (y así hasta un final cálido)"

        Reglas de escritura:
        1. Historia en tercera persona.
        2. Discurso simple, vivo y emocional.
        3. Longitud del texto: aproximadamente {character_count} caracteres.
        4. Estructura:
           - Inicio: descripción del estado severo del animal + primeras emociones del rescatista.
           - Conflicto: el animal no confía en las personas, requiere paciencia.
           - Punto de giro: primer contacto e inicio del tratamiento.
           - Desarrollo: recuperación gradual y crecimiento de la confianza.
           - Final: hogar feliz, amor, promesa de una vida mejor.
        5. Enfócate en los sentimientos del rescatista y el drama de la confianza.
        6. El final debe ser cálido, "que arranque lágrimas" e inspirador.
        7. No renarres el video cuadro por cuadro, sino escribe como una historia completa del destino.
        8. Usa imágenes emocionales ("corazón se encogió", "chispas de vida en los ojos", "sombra de sí mismo").
        
        ⚠️ **AUTOVERIFICACIÓN OBLIGATORIA ANTES DE RESPONDER:**
        
        ANTES de dar tu respuesta final, compara tu guión con el ejemplo de referencia:
        
        ✅ Verifica estilo: ¿tu texto usa imágenes emocionales como en la referencia?
        ✅ Verifica estructura: ¿están presentes las 5 etapas (condición → conflicto → punto de giro → desarrollo → final)?
        ✅ Verifica emociones: ¿el texto transmite los sentimientos del rescatista y el drama de confianza?
        ✅ Verifica longitud: ¿coincide aproximadamente con {character_count} caracteres?
        ✅ Verifica final: ¿es cálido, inspirador y "que arranque lágrimas"?
        ✅ Verifica narrativa: ¿es una historia completa del destino, no una renarración cuadro por cuadro?
        
        ¡SI al menos un punto NO coincide con la referencia - reescribe hasta cumplimiento completo!
        Responde SOLO cuando el guión esté lo más cerca posible del estilo del ejemplo de referencia.
        
        Datos de entrada (descripción del video):
        {video_description}
        
        También dame por separado:
        1. Tres opciones de título que deben ser provocativos, evocar curiosidad y el deseo de ver el video hasta el final.
        2. Elige 3 palabras clave basadas en lo que sucede en el video - deben coincidir exactamente con el tema del video y no ser vagas o generales en significado.
        
        Estructura de respuesta:
        
        🎙️ **GUIÓN DE NARRACIÓN:**
        [Guión de historia para narración, aproximadamente {character_count} caracteres]
        
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
