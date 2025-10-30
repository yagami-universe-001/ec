# bot.py - Main bot file
import os
import logging
from pyrogram import Client, idle
from utils.config import Config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="VideoEncoderBot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            workers=Config.WORKERS,
            plugins=dict(root="handlers"),
            sleep_threshold=60
        )
        
    async def start(self):
        await super().start()
        me = await self.get_me()
        self.username = me.username
        self.id = me.id
        
        # Initialize database after bot starts
        try:
            from utils.database import Database
            await Database.init_db()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            logger.info("Attempting to create database directory...")
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(Config.DATABASE_URL)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            # Try again
            await Database.init_db()
        
        logger.info(f"╔══════════════════════════════════════════╗")
        logger.info(f"║  Bot Started Successfully!               ║")
        logger.info(f"║  Username: @{me.username:<25} ║")
        logger.info(f"║  Bot ID: {me.id:<29} ║")
        logger.info(f"╚══════════════════════════════════════════╝")
        
    async def stop(self):
        await super().stop()
        logger.info("Bot stopped!")

if __name__ == "__main__":
    # Ensure all directories exist before starting
    try:
        Config.create_dirs()
        logger.info("Directories created successfully")
    except Exception as e:
        logger.error(f"Error creating directories: {e}")
    
    # Start bot
    bot = Bot()
    bot.run()
