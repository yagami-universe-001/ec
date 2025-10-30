# handlers/mediainfo.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size, format_time
from utils.progress import ProgressTracker
import os
import time

@Client.on_message(filters.command("mediainfo") & filters.private)
async def media_info(client: Client, message: Message):
    """Get detailed media information"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**📊 Media Info**\n\n"
            "**Usage:** Reply to a video file with `/mediainfo`\n\n"
            "This will show detailed information about the media file."
        )
        return
    
    file = message.reply_to_message.video or message.reply_to_message.document
    file_name = file.file_name or f"video_{int(time.time())}.mp4"
    
    processing_msg = await message.reply_text(
        f"**📊 Analyzing Media**\n\n"
        f"┃ `{file_name}`\n\n"
        f"Downloading for analysis...\n"
        f"├ Task By: {user_name}\n"
        f"└ User ID: {user_id}"
    )
    
    try:
        # Download file
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_mediainfo.mp4")
        start_time = time.time()
        
        await client.download_media(
            message.reply_to_message,
            file_name=input_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, start_time)
        )
        
        await processing_msg.edit_text(
            f"**📊 Analyzing Media**\n\n"
            f"┃ `{file_name}`\n\n"
            f"Extracting metadata...\n"
            f"├ Task By: {user_name}\n"
            f"└ User ID: {user_id}"
        )
        
        # Get media info
        info = await FFmpegHelper.get_video_info(input_path)
        
        if not info:
            await processing_msg.edit_text("**❌ Failed to get media information!**")
            return
        
        # Format info
        duration = format_time(int(info.get('duration', 0)))
        size = format_size(info.get('size', 0))
        bitrate = f"{info.get('bitrate', 0) // 1000} kbps" if info.get('bitrate') else "Unknown"
        resolution = f"{info.get('width', 0)}x{info.get('height', 0)}"
        video_codec = info.get('video_codec', 'Unknown').upper()
        audio_codec = info.get('audio_codec', 'Unknown').upper()
        fps = f"{info.get('fps', 0):.2f}" if info.get('fps') else "Unknown"
        
        info_text = f"""
**📊 Media Information**

**📁 File Details:**
├ Name: `{file_name}`
├ Size: `{size}`
└ Duration: `{duration}`

**🎬 Video Details:**
├ Resolution: `{resolution}`
├ Codec: `{video_codec}`
├ Bitrate: `{bitrate}`
└ FPS: `{fps}`

**🎵 Audio Details:**
└ Codec: `{audio_codec}`

**👤 Requested By:** {user_name}
**🆔 User ID:** {user_id}
        """
        
        await processing_msg.edit_text(info_text)
        
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_callback_query(filters.regex("^show_mediainfo$"))
async def mediainfo_callback(client: Client, callback_query: CallbackQuery):
    """Handle media info callback"""
    await callback_query.message.reply_text(
        "**📊 Media Information**\n\n"
        "Send me a video file and I'll show you detailed information about it!"
    )
    await callback_query.answer("Send video file")
