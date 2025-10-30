# utils/database.py
import aiosqlite
import json
import os
from typing import Optional, Dict, Any, List
from utils.config import Config

class Database:
    DB_PATH = Config.DATABASE_URL
    
    @staticmethod
    async def init_db():
        """Initialize database with all required tables"""
        # Ensure database directory exists
        db_dir = os.path.dirname(Database.DB_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # If DB_PATH is just a filename, use current directory
        if not db_dir:
            Database.DB_PATH = os.path.join(os.getcwd(), Database.DB_PATH)
        
        async with aiosqlite.connect(Database.DB_PATH) as db:
            # Users table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_premium INTEGER DEFAULT 0,
                    premium_expiry TIMESTAMP
                )
            """)
            
            # Thumbnails table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS thumbnails (
                    user_id INTEGER PRIMARY KEY,
                    file_id TEXT NOT NULL
                )
            """)
            
            # Watermarks table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS watermarks (
                    user_id INTEGER PRIMARY KEY,
                    watermark_text TEXT,
                    watermark_image TEXT
                )
            """)
            
            # User settings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS user_settings (
                    user_id INTEGER PRIMARY KEY,
                    upload_as_doc INTEGER DEFAULT 0,
                    spoiler_enabled INTEGER DEFAULT 0,
                    preferred_quality TEXT DEFAULT '720p'
                )
            """)
            
            # Force sub channels table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS fsub_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL UNIQUE,
                    channel_username TEXT
                )
            """)
            
            # Bot settings table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS bot_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            # Queue table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    file_id TEXT NOT NULL,
                    task_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await db.commit()
    
    # User operations
    @staticmethod
    async def add_user(user_id: int, username: str = None, first_name: str = None, last_name: str = None):
        """Add or update user in database"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, first_name, last_name))
            await db.commit()
    
    @staticmethod
    async def get_all_users() -> List[int]:
        """Get all user IDs"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("SELECT user_id FROM users") as cursor:
                return [row[0] async for row in cursor]
    
    @staticmethod
    async def is_premium_user(user_id: int) -> bool:
        """Check if user is premium"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("""
                SELECT is_premium FROM users WHERE user_id = ?
            """, (user_id,)) as cursor:
                result = await cursor.fetchone()
                return bool(result[0]) if result else False
    
    @staticmethod
    async def add_premium_user(user_id: int, days: int = 30):
        """Add premium user"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                UPDATE users 
                SET is_premium = 1, 
                    premium_expiry = datetime('now', '+' || ? || ' days')
                WHERE user_id = ?
            """, (days, user_id))
            await db.commit()
    
    @staticmethod
    async def remove_premium_user(user_id: int):
        """Remove premium status"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                UPDATE users SET is_premium = 0, premium_expiry = NULL WHERE user_id = ?
            """, (user_id,))
            await db.commit()
    
    @staticmethod
    async def get_premium_users() -> List[Dict]:
        """Get all premium users"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("""
                SELECT user_id, username, premium_expiry FROM users WHERE is_premium = 1
            """) as cursor:
                return [{"user_id": row[0], "username": row[1], "expiry": row[2]} async for row in cursor]
    
    # Thumbnail operations
    @staticmethod
    async def set_thumbnail(user_id: int, file_id: str):
        """Set user thumbnail"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                INSERT OR REPLACE INTO thumbnails (user_id, file_id) VALUES (?, ?)
            """, (user_id, file_id))
            await db.commit()
    
    @staticmethod
    async def get_thumbnail(user_id: int) -> Optional[str]:
        """Get user thumbnail"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("""
                SELECT file_id FROM thumbnails WHERE user_id = ?
            """, (user_id,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    
    @staticmethod
    async def delete_thumbnail(user_id: int):
        """Delete user thumbnail"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("DELETE FROM thumbnails WHERE user_id = ?", (user_id,))
            await db.commit()
    
    # Watermark operations
    @staticmethod
    async def set_watermark(user_id: int, watermark_text: str = None, watermark_image: str = None):
        """Set user watermark"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                INSERT OR REPLACE INTO watermarks (user_id, watermark_text, watermark_image)
                VALUES (?, ?, ?)
            """, (user_id, watermark_text, watermark_image))
            await db.commit()
    
    @staticmethod
    async def get_watermark(user_id: int) -> Dict[str, Optional[str]]:
        """Get user watermark"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("""
                SELECT watermark_text, watermark_image FROM watermarks WHERE user_id = ?
            """, (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    return {"text": result[0], "image": result[1]}
                return {"text": None, "image": None}
    
    # User settings
    @staticmethod
    async def set_user_setting(user_id: int, setting: str, value: Any):
        """Set user setting"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            if setting == "upload_as_doc":
                await db.execute("""
                    INSERT OR REPLACE INTO user_settings (user_id, upload_as_doc)
                    VALUES (?, ?)
                """, (user_id, 1 if value else 0))
            elif setting == "spoiler_enabled":
                await db.execute("""
                    INSERT OR REPLACE INTO user_settings (user_id, spoiler_enabled)
                    VALUES (?, ?)
                """, (user_id, 1 if value else 0))
            elif setting == "preferred_quality":
                await db.execute("""
                    INSERT OR REPLACE INTO user_settings (user_id, preferred_quality)
                    VALUES (?, ?)
                """, (user_id, value))
            await db.commit()
    
    @staticmethod
    async def get_user_settings(user_id: int) -> Dict:
        """Get user settings"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("""
                SELECT upload_as_doc, spoiler_enabled, preferred_quality
                FROM user_settings WHERE user_id = ?
            """, (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result:
                    return {
                        "upload_as_doc": bool(result[0]),
                        "spoiler_enabled": bool(result[1]),
                        "preferred_quality": result[2]
                    }
                return {
                    "upload_as_doc": False,
                    "spoiler_enabled": False,
                    "preferred_quality": "720p"
                }
    
    # Force sub operations
    @staticmethod
    async def add_fsub_channel(channel_id: int, channel_username: str = None):
        """Add force subscribe channel"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                INSERT OR IGNORE INTO fsub_channels (channel_id, channel_username)
                VALUES (?, ?)
            """, (channel_id, channel_username))
            await db.commit()
    
    @staticmethod
    async def remove_fsub_channel(channel_id: int):
        """Remove force subscribe channel"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("DELETE FROM fsub_channels WHERE channel_id = ?", (channel_id,))
            await db.commit()
    
    @staticmethod
    async def get_fsub_channels() -> List[Dict]:
        """Get all force subscribe channels"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("SELECT channel_id, channel_username FROM fsub_channels") as cursor:
                return [{"channel_id": row[0], "username": row[1]} async for row in cursor]
    
    # Bot settings
    @staticmethod
    async def set_bot_setting(key: str, value: str):
        """Set bot setting"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)
            """, (key, value))
            await db.commit()
    
    @staticmethod
    async def get_bot_setting(key: str) -> Optional[str]:
        """Get bot setting"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("""
                SELECT value FROM bot_settings WHERE key = ?
            """, (key,)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else None
    
    # Queue operations
    @staticmethod
    async def add_to_queue(user_id: int, file_id: str, task_type: str):
        """Add task to queue"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("""
                INSERT INTO queue (user_id, file_id, task_type) VALUES (?, ?, ?)
            """, (user_id, file_id, task_type))
            await db.commit()
    
    @staticmethod
    async def get_queue_size() -> int:
        """Get total queue size"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            async with db.execute("""
                SELECT COUNT(*) FROM queue WHERE status = 'pending'
            """) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else 0
    
    @staticmethod
    async def clear_queue():
        """Clear all queue tasks"""
        async with aiosqlite.connect(Database.DB_PATH) as db:
            await db.execute("DELETE FROM queue")
            await db.commit()
