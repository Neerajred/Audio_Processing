import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
FLASK_API_KEY = os.getenv("FLASK_API_KEY")
UPLOAD_FOLDER = "Uploads"
FFMPEG_PATH = os.getenv("FFMPEG_PATH")
TASK_URL = os.getenv("TASK_URL")
SUPPORTED_FORMATS = {".wav", ".flac", ".ogg", ".mpeg", ".mp3", ".amr"}
COMMON_LANGUAGES = [
    "en-US", "te-IN", "hi-IN", "ta-IN", "kn-IN", "ml-IN", "mr-IN", "fr-FR",
    "es-ES", "bn-IN", "gu-IN", "pa-IN", "ur-IN", "de-DE", "it-IT", "ja-JP",
    "zh-CN", "or-IN", "as-IN", "si-LK", "ar-SA", "ru-RU", "pt-BR", "ko-KR"
]

def validate_credentials():
    if not GOOGLE_CREDENTIALS_PATH or not os.path.exists(GOOGLE_CREDENTIALS_PATH):
        logger.error("Google Cloud credentials not found or invalid")
        raise ValueError("Set GOOGLE_APPLICATION_CREDENTIALS to a valid JSON key file")
    if not GEMINI_API_KEY:
        logger.error("Gemini API key not found")
        raise ValueError("Set GEMINI_API_KEY in .env file")