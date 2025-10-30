# handlers/audio.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size
import os
import time

# Store user audio files temporarily
user_audio_operations = {}


@Client.on_message(filters.command("extract_audio") & filters.private)
async def extract_audio(client: Client, message: Message):
    """Extract audio from video"""
    user_id = message.from_user.id
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**🎵 Extract Audio**\n\n"
            "**Usage:** Reply to a video with `/extract_audio`\n\n"
            "This will extract the audio track from the video."
        )
        return
    
    processing_msg = await message.reply_text("**⏳ Processing...**\n\n**⬇️ Downloading video...**")
    
    try:
        file = message.reply_to_message.video or message.reply_to_message.document
        
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        await client.download_media(message.reply_to_message, file_name=input_path)
        
        await processing_msg.edit_text("**🔄 Extracting audio...**")
        
        # Extract audio
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_audio.mp3")
        success = await FFmpegHelper.extract_audio(input_path, output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to extract audio!**")
            return
        
        await processing_msg.edit_text("**⬆️ Uploading...**")
        
        # Upload audio file
        file_size = os.path.getsize(output_path)
        await message.reply_audio(
            audio=output_path,
            caption=f"**✅ Audio extracted successfully!**\n\n"
                   f"**📦 Size:** `{format_size(file_size)}`\n"
                   f"**💪 Extracted By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("addaudio") & filters.private)
async def add_audio_command(client: Client, message: Message):
    """Add audio to video"""
    user_id = message.from_user.id
    
    await message.reply_text(
        "**🎵 Add Audio to Video**\n\n"
        "**Steps:**\n"
        "1. Send me your video file\n"
        "2. Send me your audio file (.mp3, .aac, .m4a, etc.)\n"
        "3. I'll combine them together!\n\n"
        "**Note:** The original video audio will be replaced."
    )
    
    # Set user state
    user_audio_operations[user_id] = {"type": "add", "video": None, "audio": None}


@Client.on_message(filters.command("remaudio") & filters.private)
async def remove_audio(client: Client, message: Message):
    """Remove audio from video"""
    user_id = message.from_user.id
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**🔇 Remove Audio**\n\n"
            "**Usage:** Reply to a video with `/remaudio`\n\n"
            "This will remove the audio track from the video."
        )
        return
    
    processing_msg = await message.reply_text("**⏳ Processing...**\n\n**⬇️ Downloading video...**")
    
    try:
        file = message.reply_to_message.video or message.reply_to_message.document
        
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        await client.download_media(message.reply_to_message, file_name=input_path)
        
        await processing_msg.edit_text("**🔄 Removing audio...**")
        
        # Remove audio
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_no_audio.mp4")
        success = await FFmpegHelper.remove_audio(input_path, output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to remove audio!**")
            return
        
        await processing_msg.edit_text("**⬆️ Uploading...**")
        
        # Upload result
        file_size = os.path.getsize(output_path)
        await message.reply_video(
            video=output_path,
            caption=f"**✅ Audio removed successfully!**\n\n"
                   f"**📦 Size:** `{format_size(file_size)}`\n"
                   f"**💪 Processed By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


# Handle audio file uploads for audio operations
@Client.on_message(filters.audio & filters.private)
async def handle_audio_file(client: Client, message: Message):
    """Handle audio file uploads"""
    user_id = message.from_user.id
    
    if user_id not in user_audio_operations:
        return
    
    state = user_audio_operations[user_id]
    
    if state['type'] != 'add':
        return
    
    # Store audio file
    file = message.audio
    state['audio'] = {
        'file_id': file.file_id,
        'file_name': file.file_name or f"audio_{int(time.time())}.mp3"
    }
    
    await message.reply_text(
        f"**✅ Audio file received!**\n\n"
        f"**File:** `{state['audio']['file_name']}`\n\n"
    )
    
    # Check if we have both video and audio
    if state['video'] and state['audio']:
        await process_audio_addition(client, message, user_id, state)


async def process_audio_addition(client, message, user_id, state):
    """Process video + audio combination"""
    processing_msg = await message.reply_text("**⏳ Processing...**\n\n**⬇️ Downloading files...**")
    
    try:
        # Download video
        video_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_video.mp4")
        await client.download_media(state['video']['file_id'], file_name=video_path)
        
        # Download audio
        audio_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_audio.mp3")
        await client.download_media(state['audio']['file_id'], file_name=audio_path)
        
        await processing_msg.edit_text("**🔄 Adding audio to video...**")
        
        # Add audio
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_with_audio.mp4")
        success = await FFmpegHelper.add_audio(video_path, audio_path, output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to add audio!**")
            return
        
        await processing_msg.edit_text("**⬆️ Uploading...**")
        
        # Upload result
        file_size = os.path.getsize(output_path)
        await message.reply_video(
            video=output_path,
            caption=f"**✅ Audio added successfully!**\n\n"
                   f"**📦 Size:** `{format_size(file_size)}`\n"
                   f"**💪 Processed By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        for path in [video_path, audio_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
        
        # Clear state
        del user_audio_operations[user_id]
        
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_callback_query(filters.regex("^audio_menu$"))
async def audio_menu_callback(client: Client, callback_query: CallbackQuery):
    """Show audio operations menu"""
    buttons = [
        [
            InlineKeyboardButton("🎵 Extract Audio", callback_data="extract_audio_cb"),
            InlineKeyboardButton("➕ Add Audio", callback_data="add_audio_cb")
        ],
        [
            InlineKeyboardButton("🔇 Remove Audio", callback_data="remove_audio_cb")
        ],
        [InlineKeyboardButton("« Back", callback_data="back_to_main")]
    ]
    
    text = """
**🎵 Audio Operations**

**Available Operations:**
• **Extract Audio** - Get audio track from video
• **Add Audio** - Replace video audio with custom audio
• **Remove Audio** - Remove all audio tracks

**Choose an operation:**
    """
    
    await callback_query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer()


@Client.on_callback_query(filters.regex("^extract_audio_cb$"))
async def extract_audio_callback(client: Client, callback_query: CallbackQuery):
    """Handle extract audio callback"""
    await callback_query.message.reply_text(
        "**🎵 Extract Audio**\n\n"
        "**Usage:** Send me a video file and I'll extract the audio track.\n\n"
        "Send your video now!"
    )
    await callback_query.answer("Send video file")


@Client.on_callback_query(filters.regex("^add_audio_cb$"))
async def add_audio_callback(client: Client, callback_query: CallbackQuery):
    """Handle add audio callback"""
    user_id = callback_query.from_user.id
    user_audio_operations[user_id] = {"type": "add", "video": None, "audio": None}
    
    await callback_query.message.reply_text(
        "**🎵 Add Audio to Video**\n\n"
        "**Steps:**\n"
        "1. Send me your video file\n"
        "2. Send me your audio file\n"
        "3. I'll combine them together!"
    )
    await callback_query.answer("Send video and audio files")


@Client.on_callback_query(filters.regex("^remove_audio_cb$"))
async def remove_audio_callback(client: Client, callback_query: CallbackQuery):
    """Handle remove audio callback"""
    await callback_query.message.reply_text(
        "**🔇 Remove Audio**\n\n"
        "**Usage:** Send me a video file and I'll remove the audio track.\n\n"
        "Send your video now!"
    )
    await callback_query.answer("Send video file")


# Update video handler for audio operations
@Client.on_message((filters.video | filters.document) & filters.private)
async def handle_video_for_audio(client: Client, message: Message):
    """Handle video uploads for audio operations"""
    user_id = message.from_user.id
    
    if user_id not in user_audio_operations:
        return
    
    state = user_audio_operations[user_id]
    
    # Check if file is video
    if message.document and not message.document.mime_type.startswith("video/"):
        return
    
    file = message.video or message.document
    
    # Store video file
    state['video'] = {
        'file_id': file.file_id,
        'file_name': file.file_name or f"video_{int(time.time())}.mp4"
    }
    
    await message.reply_text(
        f"**✅ Video file received!**\n\n"
        f"**File:** `{state['video']['file_name']}`\n\n"
        f"Now send me the audio file."
    )
    
    # If audio is already received, process
    if state['audio']:
        await process_audio_addition(client, message, user_id, state)
