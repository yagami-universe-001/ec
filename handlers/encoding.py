# handlers/encoding.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import Database
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size, format_time, format_progress_bar
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
    quality = callback_query.data.replace("encode_", "")
    
    if user_id not in user_videos:
        await callback_query.answer("⚠️ Please send a video first!", show_alert=True)
        return
    
    video_info = user_videos[user_id]
    
    # Show processing message
    processing_msg = await callback_query.message.reply_text(
        "**⏳ Processing...**\n\n"
        "**⬇️ Downloading video...**"
    )
    
    try:
        # Download video
        download_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}.mp4")
        await client.download_media(
            video_info['file_id'],
            file_name=download_path,
            progress=download_progress,
            progress_args=(processing_msg, "⬇️ Downloading")
        )
        
        if quality == "all":
            # Encode in all qualities
            await encode_all_qualities(client, callback_query, download_path, video_info, processing_msg)
        else:
            # Encode single quality
            await encode_single(client, callback_query, download_path, video_info, quality, processing_msg)
        
        # Clean up
        if os.path.exists(download_path):
            os.remove(download_path)
        
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")
        if os.path.exists(download_path):
            os.remove(download_path)


async def encode_single(client, callback_query, input_file, video_info, quality, status_msg):
    """Encode video in single quality"""
    user_id = callback_query.from_user.id
    
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
    await status_msg.edit_text(
        f"**🎬 Encoding to {quality.upper()}**\n\n"
        "**💪 Task By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏\n"
        "**📊 Progress:** 0%\n"
        "**⚡ Speed:** Calculating...\n"
        "**⏱ ETA:** Calculating..."
    )
    
    start_time = time.time()
    last_update = [0]
    
    async def progress_callback(percentage, speed, eta, current, total):
        """Progress callback for encoding"""
        current_time = time.time()
        if current_time - last_update[0] < Config.PROGRESS_UPDATE_INTERVAL:
            return
        last_update[0] = current_time
        
        progress_bar = format_progress_bar(percentage)
        elapsed = current_time - start_time
        
        text = f"""
**🎬 Encoding to {quality.upper()}**

{progress_bar} {percentage:.1f}%

**💪 Task By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏
**⚡ Speed:** {speed:.2f}x
**⏱ ETA:** {format_time(int(eta))}
**⏰ Elapsed:** {format_time(int(elapsed))}
**📊 Current:** {format_time(int(current))} / {format_time(int(total))}
        """
        
        try:
            await status_msg.edit_text(text)
        except:
            pass
    
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
    
    # Update status for upload
    await status_msg.edit_text(
        f"**⬆️ Uploading {quality.upper()}**\n\n"
        "**📊 Progress:** 0%"
    )
    
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
    caption = f"""
**✅ Encoding Complete!**

**📁 File:** `{os.path.basename(output_file)}`
**🎬 Quality:** `{quality.upper()}`
**📦 Size:** `{format_size(encoded_size)}`
**💪 Encoded By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏
    """
    
    try:
        if user_settings['upload_as_doc']:
            await callback_query.message.reply_document(
                document=output_file,
                caption=caption,
                thumb=thumb_path if os.path.exists(thumb_path) else None,
                progress=upload_progress,
                progress_args=(status_msg, f"⬆️ Uploading {quality.upper()}")
            )
        else:
            await callback_query.message.reply_video(
                video=output_file,
                caption=caption,
                thumb=thumb_path if os.path.exists(thumb_path) else None,
                duration=video_info.get('duration', 0),
                supports_streaming=True,
                has_spoiler=user_settings['spoiler_enabled'],
                progress=upload_progress,
                progress_args=(status_msg, f"⬆️ Uploading {quality.upper()}")
            )
        
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"**❌ Upload failed:** {str(e)}")
    
    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
    if thumb_path and os.path.exists(thumb_path):
        os.remove(thumb_path)


async def encode_all_qualities(client, callback_query, input_file, video_info, status_msg):
    """Encode video in all qualities"""
    qualities = ["144p", "240p", "360p", "480p", "720p", "1080p"]
    total = len(qualities)
    
    await status_msg.edit_text(
        f"**🌟 Encoding in ALL qualities**\n\n"
        f"**Total Tasks:** {total}\n"
        f"**Progress:** 0/{total}"
    )
    
    for i, quality in enumerate(qualities, 1):
        await status_msg.edit_text(
            f"**🌟 Encoding in ALL qualities**\n\n"
            f"**Current:** {quality.upper()}\n"
            f"**Progress:** {i-1}/{total}\n"
            f"**Status:** Encoding..."
        )
        
        await encode_single(client, callback_query, input_file, video_info, quality, status_msg)
        
        await asyncio.sleep(2)
    
    await status_msg.edit_text(
        f"**✅ All encodings complete!**\n\n"
        f"**Total:** {total} videos\n"
        f"**Encoded By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
    )


async def download_progress(current, total, status_msg, prefix):
    """Download progress callback"""
    percentage = (current / total) * 100
    progress_bar = format_progress_bar(percentage)
    
    text = f"""
**{prefix}**

{progress_bar} {percentage:.1f}%

**📦 Downloaded:** {format_size(current)} / {format_size(total)}
    """
    
    try:
        await status_msg.edit_text(text)
    except:
        pass


async def upload_progress(current, total, status_msg, prefix):
    """Upload progress callback"""
    percentage = (current / total) * 100
    progress_bar = format_progress_bar(percentage)
    
    text = f"""
**{prefix}**

{progress_bar} {percentage:.1f}%

**📤 Uploaded:** {format_size(current)} / {format_size(total)}
    """
    
    try:
        await status_msg.edit_text(text)
    except:
        pass


@Client.on_message(filters.command(["144p", "240p", "360p", "480p", "720p", "1080p", "2160p"]) & filters.private)
async def quality_command(client: Client, message: Message):
    """Handle quality commands"""
    user_id = message.from_user.id
    
    if user_id not in user_videos:
        await message.reply_text("**⚠️ Please send a video first!**")
        return
    
    quality = message.command[0][1:]  # Remove '/'
    
    # Create fake callback query for encode_single
    class FakeCallbackQuery:
        def __init__(self, message):
            self.message = message
            self.from_user = message.from_user
    
    fake_cb = FakeCallbackQuery(message)
    video_info = user_videos[user_id]
    
    processing_msg = await message.reply_text("**⏳ Processing...**")
    
    try:
        download_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}.mp4")
        await client.download_media(video_info['file_id'], file_name=download_path)
        
        await encode_single(client, fake_cb, download_path, video_info, quality, processing_msg)
        
        if os.path.exists(download_path):
            os.remove(download_path)
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("all") & filters.private)
async def all_command(client: Client, message: Message):
    """Handle /all command"""
    user_id = message.from_user.id
    
    if user_id not in user_videos:
        await message.reply_text("**⚠️ Please send a video first!**")
        return
    
    class FakeCallbackQuery:
        def __init__(self, message):
            self.message = message
            self.from_user = message.from_user
    
    fake_cb = FakeCallbackQuery(message)
    video_info = user_videos[user_id]
    
    processing_msg = await message.reply_text("**⏳ Processing...**")
    
    try:
        download_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}.mp4")
        await client.download_media(video_info['file_id'], file_name=download_path)
        
        await encode_all_qualities(client, fake_cb, download_path, video_info, processing_msg)
        
        if os.path.exists(download_path):
            os.remove(download_path)
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")
