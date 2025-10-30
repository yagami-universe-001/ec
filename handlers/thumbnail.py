# handlers/thumbnail.py
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.database import Database
from utils.config import Config
import os

@Client.on_message(filters.command("setthumb") & filters.private)
async def set_thumbnail(client: Client, message: Message):
    """Set custom thumbnail for user"""
    user_id = message.from_user.id
    
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo
        file_id = photo.file_id
        
        await Database.set_thumbnail(user_id, file_id)
        
        await message.reply_photo(
            photo=file_id,
            caption="**✅ Thumbnail saved successfully!**\n\nThis thumbnail will be used for all your uploads."
        )
    else:
        await message.reply_text(
            "**📸 Set Thumbnail**\n\n"
            "**Usage:** Reply to an image with `/setthumb`\n\n"
            "**Example:**\n"
            "1. Send or forward an image\n"
            "2. Reply to that image with `/setthumb`\n"
            "3. Your thumbnail will be saved!"
        )


@Client.on_message(filters.command("getthumb") & filters.private)
async def get_thumbnail(client: Client, message: Message):
    """Get saved thumbnail"""
    user_id = message.from_user.id
    
    thumbnail = await Database.get_thumbnail(user_id)
    
    if thumbnail:
        await message.reply_photo(
            photo=thumbnail,
            caption="**📸 Your Saved Thumbnail**\n\nThis thumbnail is currently set for your uploads."
        )
    else:
        await message.reply_text(
            "**⚠️ No thumbnail saved!**\n\n"
            "Use `/setthumb` command to set a custom thumbnail."
        )


@Client.on_message(filters.command("delthumb") & filters.private)
async def delete_thumbnail(client: Client, message: Message):
    """Delete saved thumbnail"""
    user_id = message.from_user.id
    
    thumbnail = await Database.get_thumbnail(user_id)
    
    if thumbnail:
        await Database.delete_thumbnail(user_id)
        await message.reply_text(
            "**✅ Thumbnail deleted successfully!**\n\n"
            "Your uploads will now use auto-generated thumbnails from videos."
        )
    else:
        await message.reply_text(
            "**⚠️ No thumbnail found!**\n\n"
            "You don't have any saved thumbnail."
        )
