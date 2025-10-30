# handlers/extract.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size
from utils.progress import ProgressTracker
import os
import time

@Client.on_message(filters.command("extract_thumb") & filters.private)
async def extract_thumbnail(client: Client, message: Message):
    """Extract thumbnail from video"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**🖼️ Extract Thumbnail**\n\n"
            "**Usage:** Reply to a video with `/extract_thumb`\n\n"
            "This will extract a thumbnail image from the video."
        )
        return
    
    file = message.reply_to_message.video or message.reply_to_message.document
    file_name = file.file_name or f"video_{int(time.time())}.mp4"
    
    bot_stats = ProgressTracker.get_bot_stats()
    processing_msg = await message.reply_text(
        f"**1. Downloading**\n\n"
        f"┃ `{file_name}`\n\n"
        f"Downloading video file...\n"
        f"├ Task By: {user_name}\n"
        f"└ User ID: {user_id}\n\n"
        f"**📊 Bot Stats**\n"
        f"├ CPU: {bot_stats['cpu']:.1f}%\n"
        f"└ RAM: {bot_stats['ram']:.1f}%"
    )
    
    try:
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        start_time = time.time()
        
        await client.download_media(
            message.reply_to_message,
            file_name=input_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, start_time)
        )
        
        bot_stats = ProgressTracker.get_bot_stats()
        await processing_msg.edit_text(
            f"**2. Extracting Thumbnail**\n\n"
            f"┃ `{file_name}`\n\n"
            f"Processing video...\n"
            f"├ Extracting frame at 00:00:01\n"
            f"├ Task By: {user_name}\n"
            f"└ User ID: {user_id}\n\n"
            f"**📊 Bot Stats**\n"
            f"├ CPU: {bot_stats['cpu']:.1f}%\n"
            f"└ RAM: {bot_stats['ram']:.1f}%"
        )
        
        # Extract thumbnail
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_thumb.jpg")
        success = await FFmpegHelper.extract_thumbnail(input_path, output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to extract thumbnail!**")
            return
        
        # Upload thumbnail
        await message.reply_photo(
            photo=output_path,
            caption=f"**✅ Thumbnail extracted successfully!**\n\n**👤 Extracted For:** {user_name}"
        )
        
        await processing_msg.delete()
        
        # Clean up
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("cut") & filters.private)
async def cut_video(client: Client, message: Message):
    """Trim/cut video by time"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
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
    
    file = message.reply_to_message.video or message.reply_to_message.document
    file_name = file.file_name or f"video_{int(time.time())}.mp4"
    
    processing_msg = await message.reply_text("**⏳ Initializing...**")
    
    try:
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        dl_start = time.time()
        
        await client.download_media(
            message.reply_to_message,
            file_name=input_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, dl_start)
        )
        
        bot_stats = ProgressTracker.get_bot_stats()
        await processing_msg.edit_text(
            f"**2. Cutting Video**\n\n"
            f"┃ `{file_name}`\n\n"
            f"Trimming video...\n"
            f"├ Start: {start_time}\n"
            f"├ End: {end_time}\n"
            f"├ Task By: {user_name}\n"
            f"└ User ID: {user_id}\n\n"
            f"**📊 Bot Stats**\n"
            f"├ CPU: {bot_stats['cpu']:.1f}%\n"
            f"└ RAM: {bot_stats['ram']:.1f}%"
        )
        
        # Trim video
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_cut.mp4")
        success = await FFmpegHelper.trim_video(input_path, output_path, start_time, end_time)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to cut video!**")
            return
        
        # Upload result
        file_size = os.path.getsize(output_path)
        upload_start = time.time()
        
        await message.reply_video(
            video=output_path,
            caption=f"**✅ Video cut successfully!**\n\n"
                   f"**📦 Size:** `{format_size(file_size)}`\n"
                   f"**👤 Cut For:** {user_name}",
            progress=ProgressTracker.upload_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, upload_start)
        )
        
        await processing_msg.delete()
        
        # Clean up
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("crop") & filters.private)
async def crop_video(client: Client, message: Message):
    """Crop video to different aspect ratio"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if len(message.command) < 2:
        await message.reply_text(
            "**🔲 Crop Video**\n\n"
            "**Usage:** Reply to video with `/crop <aspect_ratio>`\n\n"
            "**Available Ratios:**\n"
            "• `16:9` - Widescreen (default)\n"
            "• `9:16` - Vertical/Stories\n"
            "• `1:1` - Square/Instagram\n"
            "• `4:3` - Classic TV\n\n"
            "**Example:** `/crop 9:16`"
        )
        return
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text("**⚠️ Please reply to a video file!**")
        return
    
    aspect_ratio = message.command[1]
    
    if aspect_ratio not in ["16:9", "9:16", "1:1", "4:3"]:
        await message.reply_text("**⚠️ Invalid aspect ratio!**\n\nUse: 16:9, 9:16, 1:1, or 4:3")
        return
    
    file = message.reply_to_message.video or message.reply_to_message.document
    file_name = file.file_name or f"video_{int(time.time())}.mp4"
    
    processing_msg = await message.reply_text("**⏳ Initializing...**")
    
    try:
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        dl_start = time.time()
        
        await client.download_media(
            message.reply_to_message,
            file_name=input_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, dl_start)
        )
        
        bot_stats = ProgressTracker.get_bot_stats()
        await processing_msg.edit_text(
            f"**2. Cropping Video**\n\n"
            f"┃ `{file_name}`\n\n"
            f"Applying {aspect_ratio} crop...\n"
            f"├ Aspect Ratio: {aspect_ratio}\n"
            f"├ Task By: {user_name}\n"
            f"└ User ID: {user_id}\n\n"
            f"**📊 Bot Stats**\n"
            f"├ CPU: {bot_stats['cpu']:.1f}%\n"
            f"└ RAM: {bot_stats['ram']:.1f}%"
        )
        
        # Crop video
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_crop.mp4")
        success = await FFmpegHelper.crop_video(input_path, output_path, aspect_ratio)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to crop video!**")
            return
        
        # Upload result
        file_size = os.path.getsize(output_path)
        upload_start = time.time()
        
        await message.reply_video(
            video=output_path,
            caption=f"**✅ Video cropped to {aspect_ratio}!**\n\n"
                   f"**📦 Size:** `{format_size(file_size)}`\n"
                   f"**👤 Cropped For:** {user_name}",
            progress=ProgressTracker.upload_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, upload_start)
        )
        
        await processing_msg.delete()
        
        # Clean up
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_callback_query(filters.regex("^(extract_thumb|cut_video|crop_video)$"))
async def extract_callbacks(client: Client, callback_query: CallbackQuery):
    """Handle extraction callbacks"""
    action = callback_query.data
    
    if action == "extract_thumb":
        await callback_query.message.reply_text(
            "**🖼️ Extract Thumbnail**\n\n"
            "Send me a video file and I'll extract a thumbnail from it!"
        )
    elif action == "cut_video":
        await callback_query.message.reply_text(
            "**✂️ Cut Video**\n\n"
            "Reply to a video with `/cut <start> <end>`\n\n"
            "Example: `/cut 00:00:10 00:01:30`"
        )
    elif action == "crop_video":
        await callback_query.message.reply_text(
            "**🔲 Crop Video**\n\n"
            "Reply to a video with `/crop <ratio>`\n\n"
            "Example: `/crop 9:16`"
        )
    
    await callback_query.answer()
