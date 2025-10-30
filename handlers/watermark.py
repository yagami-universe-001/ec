# handlers/watermark.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from utils.database import Database
from utils.config import Config
import os

# Store temporary watermark images
user_watermark_images = {}


@Client.on_message(filters.command("setwatermark") & filters.private)
async def set_watermark(client: Client, message: Message):
    """Set default text watermark"""
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        current_wm = await Database.get_watermark(user_id)
        text_wm = current_wm.get('text', 'Not set')
        
        await message.reply_text(
            f"**💧 Watermark Settings**\n\n"
            f"**Current Text:** `{text_wm}`\n\n"
            f"**Usage:** `/setwatermark <your text>`\n"
            f"**Example:** `/setwatermark @MyChannel`\n\n"
            f"**Note:** This watermark will be automatically added to all encoded videos."
        )
        return
    
    watermark_text = message.text.split(None, 1)[1]
    
    await Database.set_watermark(user_id, watermark_text=watermark_text)
    
    await message.reply_text(
        f"**✅ Watermark set successfully!**\n\n"
        f"**Text:** `{watermark_text}`\n\n"
        f"This watermark will be added to all your encoded videos."
    )


@Client.on_message(filters.command("getwatermark") & filters.private)
async def get_watermark(client: Client, message: Message):
    """Get current watermark settings"""
    user_id = message.from_user.id
    
    watermark = await Database.get_watermark(user_id)
    
    text_wm = watermark.get('text')
    image_wm = watermark.get('image')
    
    if text_wm or image_wm:
        response = "**💧 Your Watermark Settings**\n\n"
        
        if text_wm:
            response += f"**Text Watermark:** `{text_wm}`\n\n"
        
        if image_wm:
            response += f"**Image Watermark:** `Set`\n\n"
            try:
                await message.reply_photo(
                    photo=image_wm,
                    caption=response
                )
                return
            except:
                pass
        
        await message.reply_text(response)
    else:
        await message.reply_text(
            "**⚠️ No watermark configured!**\n\n"
            "Use `/setwatermark <text>` to set a text watermark or\n"
            "Use `/addwatermark` to set an image watermark."
        )


@Client.on_message(filters.command("addwatermark") & filters.private)
async def add_watermark_image(client: Client, message: Message):
    """Add logo watermark to videos"""
    user_id = message.from_user.id
    
    if message.reply_to_message and message.reply_to_message.photo:
        photo = message.reply_to_message.photo
        file_id = photo.file_id
        
        # Download watermark image
        watermark_path = os.path.join(Config.THUMB_DIR, f"{user_id}_watermark.png")
        await client.download_media(file_id, file_name=watermark_path)
        
        # Save to database
        await Database.set_watermark(user_id, watermark_image=file_id)
        
        await message.reply_photo(
            photo=file_id,
            caption="**✅ Watermark logo saved!**\n\nThis logo will be added to all your encoded videos."
        )
    else:
        await message.reply_text(
            "**💧 Add Watermark Logo**\n\n"
            "**Usage:** Reply to an image with `/addwatermark`\n\n"
            "**Steps:**\n"
            "1. Send or forward an image (preferably PNG with transparent background)\n"
            "2. Reply to that image with `/addwatermark`\n"
            "3. The logo will be added to all your videos!\n\n"
            "**Tip:** Use PNG images with transparent backgrounds for best results."
        )


@Client.on_message(filters.command("delwatermark") & filters.private)
async def delete_watermark(client: Client, message: Message):
    """Delete all watermarks"""
    user_id = message.from_user.id
    
    watermark = await Database.get_watermark(user_id)
    
    if watermark.get('text') or watermark.get('image'):
        await Database.set_watermark(user_id, watermark_text=None, watermark_image=None)
        
        # Clean up local file
        watermark_path = os.path.join(Config.THUMB_DIR, f"{user_id}_watermark.png")
        if os.path.exists(watermark_path):
            os.remove(watermark_path)
        
        await message.reply_text(
            "**✅ All watermarks deleted!**\n\n"
            "Your videos will no longer have watermarks."
        )
    else:
        await message.reply_text(
            "**⚠️ No watermark found!**\n\n"
            "You don't have any watermarks configured."
        )


@Client.on_callback_query(filters.regex("^add_watermark$"))
async def watermark_callback(client: Client, callback_query: CallbackQuery):
    """Handle watermark callback from video options"""
    await callback_query.message.reply_text(
        "**💧 Watermark Options**\n\n"
        "**Available Commands:**\n"
        "• `/setwatermark <text>` - Set text watermark\n"
        "• `/addwatermark` - Set image/logo watermark (reply to image)\n"
        "• `/getwatermark` - View current watermarks\n"
        "• `/delwatermark` - Delete all watermarks\n\n"
        "**Note:** Watermarks are automatically applied during encoding."
    )
    await callback_query.answer()
