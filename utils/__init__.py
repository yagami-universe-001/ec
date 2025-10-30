# utils/__init__.py
from .config import Config
from .database import Database
from .ffmpeg_helper import FFmpegHelper
from .helpers import *
from .progress import ProgressTracker

# Create necessary directories on import
Config.create_dirs()
