# utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot credentials
    API_ID = int(os.environ.get("API_ID", "0"))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    
    # Database
    DATABASE_URL = os.environ.get("DATABASE_URL", "/app/data/bot_database.db")
    
    # Admin settings
    ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "0").split()]
    
    # Download/Upload settings
    DOWNLOAD_DIR = os.environ.get("DOWNLOAD_DIR", "./downloads")
    UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "./uploads")
    THUMB_DIR = os.environ.get("THUMB_DIR", "./thumbs")
    
    # Worker settings
    WORKERS = int(os.environ.get("WORKERS", "4"))
    
    # Encoding defaults
    DEFAULT_PRESET = os.environ.get("DEFAULT_PRESET", "medium")
    DEFAULT_CRF = int(os.environ.get("DEFAULT_CRF", "28"))
    DEFAULT_CODEC = os.environ.get("DEFAULT_CODEC", "libx264")
    DEFAULT_AUDIO_BITRATE = os.environ.get("DEFAULT_AUDIO_BITRATE", "128k")
    
    # Start pic
    START_PIC = os.environ.get("START_PIC", "https://i.imgur.com/example.jpg")
    
    # Force subscribe channels
    FSUB_CHANNELS = []
    
    # Shortener settings
    SHORTENER_1_API = os.environ.get("SHORTENER_1_API", "")
    SHORTENER_1_URL = os.environ.get("SHORTENER_1_URL", "")
    TUTORIAL_1 = os.environ.get("TUTORIAL_1", "")
    
    SHORTENER_2_API = os.environ.get("SHORTENER_2_API", "")
    SHORTENER_2_URL = os.environ.get("SHORTENER_2_URL", "")
    TUTORIAL_2 = os.environ.get("TUTORIAL_2", "")
    
    # Upload destination
    UPLOAD_AS_DOC = os.environ.get("UPLOAD_AS_DOC", "False").lower() == "true"
    
    # Premium users
    PREMIUM_USERS = []
    
    # Queue settings
    MAX_QUEUE_SIZE = int(os.environ.get("MAX_QUEUE_SIZE", "10"))
    
    # Progress update interval (seconds)
    PROGRESS_UPDATE_INTERVAL = int(os.environ.get("PROGRESS_UPDATE_INTERVAL", "5"))
    
    # FFmpeg settings
    FFMPEG_THREADS = int(os.environ.get("FFMPEG_THREADS", "2"))
    
    @staticmethod
    def create_dirs():
        """Create necessary directories"""
        for directory in [Config.DOWNLOAD_DIR, Config.UPLOAD_DIR, Config.THUMB_DIR]:
            os.makedirs(directory, exist_ok=True)
