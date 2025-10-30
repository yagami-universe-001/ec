# handlers/extract.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size
import os
import time

@Client.on_message(filters.command("extract_thumb") & filters.private)
async def extract_thumbnail(client: Client, message: Message):
    """Extract thumbnail from video"""
    user_id = message.from_user.id
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**🖼️ Extract Thumbnail**\n\n"
            "**Usage:** Reply to a video with `/extract_thumb`\n\n"
            "This will extract a thumbnail image from the video."
        )
        return
    
    processing_msg = await message.reply_text(
        "**1. Downloading**\n\n"
        f"┌ Video file downloading...\n"
        f"├ Speed: Calculating...\n"
        f"├ Progress: 0%\n"
        f"├ ETA: Calculating...\n"
        f"├ Task By: ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏\n"
        f"└ User ID: {user_id}"
    )
    
    try:
        file = message.reply_to_message.video or message.reply_to_message.document
        
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        await client.download_media(message.reply_to_message, file_name=input_path)
        
        await processing_msg.edit_text(
            "**2. Extracting Thumbnail**\n\n"
            f"┌ Processing video...\n"
            f"├ Extracting frame at 00:00:01\n"
            f"├ Task By: ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏\n"
            f"└ User ID: {user_id}"
        )
        
        # Extract thumbnail
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_thumb.jpg")
        success = await FFmpegHelper.extract_thumbnail(input_path, output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to extract thumbnail!**")
            return
        
        await processing_msg.edit_text(
            "**3. Uploading**\n\n"
            f"┌ Thumbnail extracted successfully\n"
            f"├ Uploading image...\n"
            f"├ Task By: ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏\n"
            f"└ User ID: {user_id}"
        )
        
        # Upload thumbnail
        await message.reply_photo(
            photo=output_path,
            caption=f"**✅ Thumbnail extracted successfully!**\n\n**💪 Extracted By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_callback_query(filters.regex("^extract_thumb$"))
async def extract_thumb_callback(client: Client, callback_query: CallbackQuery):
    """Handle extract thumbnail callback"""
    await callback_query.message.reply_text(
        "**🖼️ Extract Thumbnail**\n\n"
        "**Usage:** Send me a video file and I'll extract a thumbnail from it.\n\n"
        "Send your video now!"
    )
    await callback_query.answer("Send video file")


@Client.on_message(filters.command("cut") & filters.private)
async def cut_video(client: Client, message: Message):
    """Trim/cut video by time"""
    user_id = message.from_user.id
    
    if len(message.command) < 3:
        await message.reply_text(
            "**✂️ Cut/Trim Video**\n\n"
            "**Usage:** Reply to video with `/cut <start_time> <end_time>`\n\n"
            "**Time Format:** HH:MM:SS or MM:SS or SS\n\n"
            "**Examples:**\n"
            "• `/cut 00:00:10 00:01:30` - Cut from 10s to 1m 30s\n"
            "• `/cut 10 90` - Cut from 10s to 90s\n"
            "• `/cut 00:05:00 00:10:00` - Cut from 5min to 10min"
        )
        return
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text("**⚠️ Please reply to a video file!**")
        return
    
    start_time = message.command[1]
    end_time = message.command[2]
    
    processing_msg = await message.reply_text(
        "**1. Downloading**\n\n"
        f"┌ Video file downloading...\n"
        f"├ Speed: Calculating...\n"
        f"├ Progress: 0%\n"
        f"├ Task By: ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏\n"
        f"└ User ID: {user_id}"
    )
    
    try:
        file = message.reply_to_message.video or message.reply_to_message.document
        
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        await client.download_media(message.reply_to_message, file_name=input_path)
        
        await processing_msg.edit_text(
            "**2. Cutting Video**\n\n"
            f"┌ Trimming video...\n"
            f"├ Start: {start_time}\n"
            f"├ End: {end_time}\n"
            f"├ Task By: ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏\n"
            f"└ User ID: {user_id}"
        )
        
        # Trim video
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_cut.mp4")
        success = await FFmpegHelper.trim_video(input_path, output_path, start_time, end_time)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to cut video!**")
            return
        
        await processing_msg.edit_text(
            "**3. Uploading**\n\n"
            f"┌ Video cut successfully\n"
            f"├ Uploading...\n"
            f"├ Task By: ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏\n"
            f"└ User ID: {user_id}"
        )
        
        # Upload result
        file_size = os.path.getsize(output_path)
        await message.reply_video(
            video=output_path,
            caption=f"**✅ Video cut successfully!**\n\n"
                   f"**📦 Size:** `{format_size(file_size)}`\n"
                   f"**💪 Cut By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("crop") & filters.private)
async def crop_video(client: Client, message: Message):
    """Crop video to different aspect ratio"""
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        await message.reply_text(
            "**🔲 Crop Video**\n\n"
            "**Usage:** Reply to video with `/crop <aspect_ratio>`\n\n"
            "**Available Ratios:**\n"
            "• `16:9` - Widescreen (default)\n"
            "• `
