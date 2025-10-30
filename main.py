# bot.py - Main bot file
import os
import logging
from pyrogram import Client, idle
from utils.config import Config
from utils.database import Database

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
        
        # Initialize database
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
    bot = Bot()
    bot.run()
