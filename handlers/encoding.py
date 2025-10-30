# handlers/encoding.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import Database
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size, format_time, format_progress_bar
from utils.progress import ProgressTracker
import os
import time
import asyncio

# Store user's last video for encoding
user_videos = {}


@Client.on_message(filters.video & filters.private | filters.document & filters.private)
async def handle_video(client: Client, message: Message):
    """Handle incoming video files"""
    user_id = message.from_user.id
    
    # Check if file is video
    if message.document and not message.document.mime_type.startswith("video/"):
        return
    
    file = message.video or message.document
    
    # Store video info
    user_videos[user_id] = {
        "file_id": file.file_id,
        "file_name": file.file_name or f"video_{int(time.time())}.mp4",
        "file_size": file.file_size,
        "duration": getattr(file, 'duration', 0),
        "message_id": message.id
    }
    
    # Show encoding options
    buttons = [
        [
            InlineKeyboardButton("🎬 144p", callback_data="encode_144p"),
            InlineKeyboardButton("🎬 240p", callback_data="encode_240p"),
            InlineKeyboardButton("🎬 360p", callback_data="encode_360p")
        ],
        [
            InlineKeyboardButton("🎬 480p", callback_data="encode_480p"),
            InlineKeyboardButton("🎬 720p", callback_data="encode_720p"),
            InlineKeyboardButton("🎬 1080p", callback_data="encode_1080p")
        ],
        [
            InlineKeyboardButton("🎬 2160p", callback_data="encode_2160p"),
            InlineKeyboardButton("🌟 ALL", callback_data="encode_all")
        ],
        [
            InlineKeyboardButton("📊 Media Info", callback_data="show_mediainfo"),
            InlineKeyboardButton("🗜 Compress", callback_data="compress_video")
        ],
        [
            InlineKeyboardButton("✂️ Cut", callback_data="cut_video"),
            InlineKeyboardButton("🔲 Crop", callback_data="crop_video"),
            InlineKeyboardButton("🔀 Merge", callback_data="merge_videos")
        ],
        [
            InlineKeyboardButton("📝 Subtitles", callback_data="subtitle_menu"),
            InlineKeyboardButton("🎵 Audio", callback_data="audio_menu")
        ],
        [
            InlineKeyboardButton("🖼️ Extract Thumb", callback_data="extract_thumb"),
            InlineKeyboardButton("💧 Watermark", callback_data="add_watermark")
        ],
        [
            InlineKeyboardButton("📋 Rename", callback_data="rename_file"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_operation")
        ]
    ]
    
    info_text = f"""
**📹 Video Received!**

**📁 File Name:** `{file.file_name or 'Unknown'}`
**📦 Size:** `{format_size(file.file_size)}`
**⏱ Duration:** `{format_time(getattr(file, 'duration', 0))}`

**🎯 Choose an action:**
    """
    
    await message.reply_text(
        text=info_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex(r"^encode_"))
async def encode_callback(client: Client, callback_query: CallbackQuery):
    """Handle encoding callbacks"""
    user_id = callback_query.from_user.id
    user_name = callback_query.from_user.first_name or callback_query.from_user.username or "User"
    quality = callback_query.data.replace("encode_", "")
    
    if user_id not in user_videos:
        await callback_query.answer("⚠️ Please send a video first!", show_alert=True)
        return
    
    video_info = user_videos[user_id]
    
    # Show processing message
    processing_msg = await callback_query.message.reply_text(
        f"**⏳ Initializing...**\n\n"
        f"Preparing to process your video..."
    )
    
    try:
        # Download video
        download_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}.mp4")
        start_time = time.time()
        
        await client.download_media(
            video_info['file_id'],
            file_name=download_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, video_info['file_name'], user_name, user_id, start_time)
        )
        
        if quality == "all":
            # Encode in all qualities
            await encode_all_qualities(client, callback_query, download_path, video_info, processing_msg, user_name, user_id)
        else:
            # Encode single quality
            await encode_single(client, callback_query, download_path, video_info, quality, processing_msg, user_name, user_id)
        
        # Clean up
        if os.path.exists(download_path):
            os.remove(download_path)
        
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")
        if os.path.exists(download_path):
            os.remove(download_path)


async def encode_single(client, callback_query, input_file, video_info, quality, status_msg, user_name, user_id):
    """Encode video in single quality"""
    
    # Get user settings
    watermark = await Database.get_watermark(user_id)
    thumbnail = await Database.get_thumbnail(user_id)
    user_settings = await Database.get_user_settings(user_id)
    
    # Prepare output file
    output_file = os.path.join(
        Config.UPLOAD_DIR,
        f"{os.path.splitext(video_info['file_name'])[0]}_{quality}.mp4"
    )
    
    # Get bot settings
    codec = await Database.get_bot_setting("codec") or Config.DEFAULT_CODEC
    preset = await Database.get_bot_setting("preset") or Config.DEFAULT_PRESET
    crf = int(await Database.get_bot_setting("crf") or Config.DEFAULT_CRF)
    audio_bitrate = await Database.get_bot_setting("audio_bitrate") or Config.DEFAULT_AUDIO_BITRATE
    
    # Update status
    bot_stats = ProgressTracker.get_bot_stats()
    await status_msg.edit_text(
        f"**2. Encoding to {quality.upper()}**\n\n"
        f"┃ `{video_info['file_name']}`\n\n"
        f"[ ○○○○○○○○○○ ] >> 0%\n"
        f"├ Speed: Calculating...\n"
        f"├ Progress: 00:00:00 / {format_time(video_info.get('duration', 0))}\n"
        f"├ ETA: Calculating...\n"
        f"├ Elapsed: 00:00:00\n"
        f"├ Task By: {user_name}\n"
        f"└ User ID: {user_id}\n\n"
        f"**📊 Bot Stats**\n"
        f"├ CPU: {bot_stats['cpu']:.1f}%\n"
        f"├ RAM: {bot_stats['ram']:.1f}%\n"
        f"├ UPTIME: {bot_stats['uptime']}\n"
        f"└ F: {bot_stats['disk']} GB\n\n"
        f"Page: 1/1 | Active Tasks: 1"
    )
    
    start_time = time.time()
    
    async def progress_callback(percentage, speed, eta, current, total):
        """Progress callback for encoding"""
        await ProgressTracker.encoding_progress(
            percentage, speed, eta, current, total,
            status_msg, video_info['file_name'], quality,
            user_name, user_id, start_time
        )
    
    # Encode video
    success = await FFmpegHelper.encode_video(
        input_file=input_file,
        output_file=output_file,
        resolution=quality,
        codec=codec,
        preset=preset,
        crf=crf,
        audio_bitrate=audio_bitrate,
        watermark_text=watermark.get('text'),
        watermark_image=watermark.get('image'),
        progress_callback=progress_callback
    )
    
    if not success or not os.path.exists(output_file):
        await status_msg.edit_text("**❌ Encoding failed!**")
        return
    
    # Get encoded file size
    encoded_size = os.path.getsize(output_file)
    
    # Download thumbnail if exists
    thumb_path = None
    if thumbnail:
        thumb_path = os.path.join(Config.THUMB_DIR, f"{user_id}_thumb.jpg")
        await client.download_media(thumbnail, file_name=thumb_path)
    else:
        # Extract thumbnail from video
        thumb_path = os.path.join(Config.THUMB_DIR, f"{user_id}_auto_thumb.jpg")
        await FFmpegHelper.extract_thumbnail(output_file, thumb_path)
    
    # Upload video
    upload_start = time.time()
    caption = f"""
**✅ Encoding Complete!**

**📁 File:** `{os.path.basename(output_file)}`
**🎬 Quality:** `{quality.upper()}`
**📦 Size:** `{format_size(encoded_size)}`
**👤 Encoded For:** {user_name}
    """
    
    try:
        if user_settings['upload_as_doc']:
            await callback_query.message.reply_document(
                document=output_file,
                caption=caption,
                thumb=thumb_path if os.path.exists(thumb_path) else None,
                progress=ProgressTracker.upload_progress,
                progress_args=(status_msg, os.path.basename(output_file), user_name, user_id, upload_start)
            )
        else:
            await callback_query.message.reply_video(
                video=output_file,
                caption=caption,
                thumb=thumb_path if os.path.exists(thumb_path) else None,
                duration=video_info.get('duration', 0),
                supports_streaming=True,
                has_spoiler=user_settings['spoiler_enabled'],
                progress=ProgressTracker.upload_progress,
                progress_args=(status_msg, os.path.basename(output_file), user_name, user_id, upload_start)
            )
        
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"**❌ Upload failed:** {str(e)}")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)


async def encode_all_qualities(client, callback_query, input_file, video_info, status_msg, user_name, user_id):
    """Encode video in all qualities"""
    qualities = ["144p", "240p", "360p", "480p", "720p", "1080p"]
    total = len(qualities)
    
    bot_stats = ProgressTracker.get_bot_stats()
    await status_msg.edit_text(
        f"**🌟 Encoding in ALL qualities**\n\n"
        f"**Total Tasks:** {total}\n"
        f"**Progress:** 0/{total}\n"
        f"**Task By:** {user_name}\n\n"
        f"**📊 Bot Stats**\n"
        f"├ CPU: {bot_stats['cpu']:.1f}%\n"
        f"├ RAM: {bot_stats['ram']:.1f}%\n"
        f"└ UPTIME: {bot_stats['uptime']}"
    )
    
    for i, quality in enumerate(qualities, 1):
        await status_msg.edit_text(
            f"**🌟 Encoding in ALL qualities**\n\n"
            f"**Current:** {quality.upper()}\n"
            f"**Progress:** {i-1}/{total}\n"
            f"**Task By:** {user_name}\n"
            f"**Status:** Encoding..."
        )
        
        await encode_single(client, callback_query, input_file, video_info, quality, status_msg, user_name, user_id)
        
        await asyncio.sleep(2)
    
    await status_msg.edit_text(
        f"**✅ All encodings complete!**\n\n"
        f"**Total:** {total} videos\n"
        f"**Encoded For:** {user_name}"
    )


@Client.on_message(filters.command(["144p", "240p", "360p", "480p", "720p", "1080p", "2160p"]) & filters.private)
async def quality_command(client: Client, message: Message):
    """Handle quality commands"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if user_id not in user_videos:
        await message.reply_text("**⚠️ Please send a video first!**")
        return
    
    quality = message.command[0][1:]  # Remove '/'
    
    video_info = user_videos[user_id]
    
    processing_msg = await message.reply_text("**⏳ Initializing...**")
    
    try:
        download_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}.mp4")
        start_time = time.time()
        
        await client.download_media(
            video_info['file_id'],
            file_name=download_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, video_info['file_name'], user_name, user_id, start_time)
        )
        
        class FakeCallbackQuery:
            def __init__(self, message):
                self.message = message
                self.from_user = message.from_user
        
        fake_cb = FakeCallbackQuery(message)
        await encode_single(client, fake_cb, download_path, video_info, quality, processing_msg, user_name, user_id)
        
        if os.path.exists(download_path):
            os.remove(download_path)
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("all") & filters.private)
async def all_command(client: Client, message: Message):
    """Handle /all command"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if user_id not in user_videos:
        await message.reply_text("**⚠️ Please send a video first!**")
        return
    
    video_info = user_videos[user_id]
    processing_msg = await message.reply_text("**⏳ Initializing...**")
    
    try:
        download_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}.mp4")
        start_time = time.time()
        
        await client.download_media(
            video_info['file_id'],
            file_name=download_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, video_info['file_name'], user_name, user_id, start_time)
        )
        
        class FakeCallbackQuery:
            def __init__(self, message):
                self.message = message
                self.from_user = message.from_user
        
        fake_cb = FakeCallbackQuery(message)
        await encode_all_qualities(client, fake_cb, download_path, video_info, processing_msg, user_name, user_id)
        
        if os.path.exists(download_path):
            os.remove(download_path)
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("compress") & filters.private)
async def compress_command(client: Client, message: Message):
    """Compress video"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**🗜 Compress Video**\n\n"
            "**Usage:** Reply to a video with `/compress`\n\n"
            "This will compress the video to reduce file size."
        )
        return
    
    processing_msg = await message.reply_text("**⏳ Initializing...**")
    
    try:
        file = message.reply_to_message.video or message.reply_to_message.document
        file_name = file.file_name or f"video_{int(time.time())}.mp4"
        
        # Download
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        start_time = time.time()
        
        await client.download_media(
            message.reply_to_message,
            file_name=input_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, start_time)
        )
        
        # Compress
        bot_stats = ProgressTracker.get_bot_stats()
        await processing_msg.edit_text(
            f"**2. Compressing**\n\n"
            f"┃ `{file_name}`\n\n"
            f"Processing with CRF 35...\n"
            f"├ Task By: {user_name}\n"
            f"└ User ID: {user_id}\n\n"
            f"**📊 Bot Stats**\n"
            f"├ CPU: {bot_stats['cpu']:.1f}%\n"
            f"└ RAM: {bot_stats['ram']:.1f}%"
        )
        
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_compressed.mp4")
        success = await FFmpegHelper.compress_video(input_path, output_path, crf=35)
        
        if not success:
            await processing_msg.edit_text("**❌ Compression failed!**")
            return
        
        # Upload
        upload_start = time.time()
        file_size = os.path.getsize(output_path)
        
        await message.reply_video(
            video=output_path,
            caption=f"**✅ Video compressed!**\n\n**📦 Size:** `{format_size(file_size)}`\n**👤 Compressed For:** {user_name}",
            progress=ProgressTracker.upload_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, upload_start)
        )
        
        await processing_msg.delete()
        
        # Cleanup
        for path in [input_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
                
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")
