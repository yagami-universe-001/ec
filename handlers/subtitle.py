# handlers/subtitle.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size
import os
import time

# Store user subtitle files temporarily
user_subtitles = {}
user_videos_for_sub = {}


@Client.on_message(filters.command("sub") & filters.private)
async def add_soft_subtitle(client: Client, message: Message):
    """Add soft subtitle to video"""
    user_id = message.from_user.id
    
    await message.reply_text(
        "**📝 Add Soft Subtitle**\n\n"
        "**Steps:**\n"
        "1. Send me your video file\n"
        "2. Send me your subtitle file (.srt, .ass, .vtt)\n"
        "3. I'll merge them together!\n\n"
        "**Note:** Soft subtitles can be turned on/off by the viewer."
    )
    
    # Set user state to expect video and subtitle
    user_videos_for_sub[user_id] = {"type": "soft", "video": None, "subtitle": None}


@Client.on_message(filters.command("hsub") & filters.private)
async def add_hard_subtitle(client: Client, message: Message):
    """Add hard-coded subtitle to video"""
    user_id = message.from_user.id
    
    await message.reply_text(
        "**📝 Add Hard Subtitle**\n\n"
        "**Steps:**\n"
        "1. Send me your video file\n"
        "2. Send me your subtitle file (.srt, .ass, .vtt)\n"
        "3. I'll burn them into the video!\n\n"
        "**Note:** Hard subtitles are permanently embedded and cannot be turned off."
    )
    
    # Set user state to expect video and subtitle
    user_videos_for_sub[user_id] = {"type": "hard", "video": None, "subtitle": None}


@Client.on_message(filters.command("rsub") & filters.private)
async def remove_subtitle(client: Client, message: Message):
    """Remove all subtitles from video"""
    user_id = message.from_user.id
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**🗑️ Remove Subtitles**\n\n"
            "**Usage:** Reply to a video with `/rsub`\n\n"
            "This will remove all subtitle tracks from the video."
        )
        return
    
    processing_msg = await message.reply_text("**⏳ Processing...**\n\n**⬇️ Downloading video...**")
    
    try:
        file = message.reply_to_message.video or message.reply_to_message.document
        
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        await client.download_media(message.reply_to_message, file_name=input_path)
        
        await processing_msg.edit_text("**🔄 Removing subtitles...**")
        
        # Remove subtitles
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_no_sub.mp4")
        success = await FFmpegHelper.remove_subtitle(input_path, output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to remove subtitles!**")
            return
        
        await processing_msg.edit_text("**⬆️ Uploading...**")
        
        # Upload result
        await message.reply_video(
            video=output_path,
            caption="**✅ Subtitles removed successfully!**\n\n**💪 Processed By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("extract_sub") & filters.private)
async def extract_subtitle(client: Client, message: Message):
    """Extract subtitles from video"""
    user_id = message.from_user.id
    
    if not message.reply_to_message or (not message.reply_to_message.video and not message.reply_to_message.document):
        await message.reply_text(
            "**📤 Extract Subtitles**\n\n"
            "**Usage:** Reply to a video with `/extract_sub`\n\n"
            "This will extract all subtitle tracks from the video."
        )
        return
    
    processing_msg = await message.reply_text("**⏳ Processing...**\n\n**⬇️ Downloading video...**")
    
    try:
        file = message.reply_to_message.video or message.reply_to_message.document
        
        # Download video
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_input.mp4")
        await client.download_media(message.reply_to_message, file_name=input_path)
        
        await processing_msg.edit_text("**🔄 Extracting subtitles...**")
        
        # Extract subtitles
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_subtitle.srt")
        success = await FFmpegHelper.extract_subtitles(input_path, output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text(
                "**⚠️ No subtitles found in the video!**\n\n"
                "The video doesn't contain any subtitle tracks."
            )
            if os.path.exists(input_path):
                os.remove(input_path)
            return
        
        await processing_msg.edit_text("**⬆️ Uploading...**")
        
        # Upload subtitle file
        await message.reply_document(
            document=output_path,
            caption="**✅ Subtitle extracted successfully!**\n\n**💪 Extracted By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


# Handle subtitle file uploads
@Client.on_message(filters.document & filters.private)
async def handle_subtitle_file(client: Client, message: Message):
    """Handle subtitle file uploads"""
    user_id = message.from_user.id
    
    if user_id not in user_videos_for_sub:
        return
    
    # Check if it's a subtitle file
    file = message.document
    if not file.file_name.endswith(('.srt', '.ass', '.vtt', '.sub')):
        return
    
    state = user_videos_for_sub[user_id]
    
    # Store subtitle file
    state['subtitle'] = {
        'file_id': file.file_id,
        'file_name': file.file_name
    }
    
    await message.reply_text(
        f"**✅ Subtitle file received!**\n\n"
        f"**File:** `{file.file_name}`\n\n"
    )
    
    # Check if we have both video and subtitle
    if state['video'] and state['subtitle']:
        await process_subtitle_addition(client, message, user_id, state)


async def process_subtitle_addition(client, message, user_id, state):
    """Process video + subtitle combination"""
    processing_msg = await message.reply_text("**⏳ Processing...**\n\n**⬇️ Downloading files...**")
    
    try:
        # Download video
        video_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_video.mp4")
        await client.download_media(state['video']['file_id'], file_name=video_path)
        
        # Download subtitle
        subtitle_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_{state['subtitle']['file_name']}")
        await client.download_media(state['subtitle']['file_id'], file_name=subtitle_path)
        
        await processing_msg.edit_text(f"**🔄 Adding {state['type']} subtitles...**")
        
        # Add subtitle
        output_path = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_with_sub.mp4")
        hard = state['type'] == 'hard'
        success = await FFmpegHelper.add_subtitle(video_path, subtitle_path, output_path, hard=hard)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to add subtitles!**")
            return
        
        await processing_msg.edit_text("**⬆️ Uploading...**")
        
        # Upload result
        file_size = os.path.getsize(output_path)
        subtitle_type = "Hard-coded" if hard else "Soft"
        
        await message.reply_video(
            video=output_path,
            caption=f"**✅ {subtitle_type} subtitle added successfully!**\n\n"
                   f"**📦 Size:** `{format_size(file_size)}`\n"
                   f"**💪 Processed By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏"
        )
        
        await processing_msg.delete()
        
        # Clean up
        for path in [video_path, subtitle_path, output_path]:
            if os.path.exists(path):
                os.remove(path)
        
        # Clear state
        del user_videos_for_sub[user_id]
        
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_callback_query(filters.regex("^subtitle_menu$"))
async def subtitle_menu_callback(client: Client, callback_query: CallbackQuery):
    """Show subtitle menu"""
    buttons = [
        [
            InlineKeyboardButton("📝 Add Soft Sub", callback_data="add_soft_sub"),
            InlineKeyboardButton("🔥 Add Hard Sub", callback_data="add_hard_sub")
        ],
        [
            InlineKeyboardButton("📤 Extract Sub", callback_data="extract_subtitle"),
            InlineKeyboardButton("🗑️ Remove Sub", callback_data="remove_subtitle")
        ],
        [InlineKeyboardButton("« Back", callback_data="back_to_main")]
    ]
    
    text = """
**📝 Subtitle Operations**

**Available Operations:**
• **Add Soft Subtitle** - Can be toggled on/off
• **Add Hard Subtitle** - Permanently embedded
• **Extract Subtitle** - Get subtitle file from video
• **Remove Subtitle** - Remove all subtitle tracks

**Choose an operation:**
    """
    
    await callback_query.message.edit_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
    await callback_query.answer()


@Client.on_callback_query(filters.regex("^add_soft_sub$"))
async def add_soft_sub_callback(client: Client, callback_query: CallbackQuery):
    """Handle add soft subtitle callback"""
    user_id = callback_query.from_user.id
    user_videos_for_sub[user_id] = {"type": "soft", "video": None, "subtitle": None}
    
    await callback_query.message.reply_text(
        "**📝 Add Soft Subtitle**\n\n"
        "**Steps:**\n"
        "1. Send me your video file\n"
        "2. Send me your subtitle file (.srt, .ass, .vtt)\n"
        "3. I'll merge them together!\n\n"
        "**Note:** Soft subtitles can be turned on/off by the viewer."
    )
    await callback_query.answer("Send video and subtitle files")


@Client.on_callback_query(filters.regex("^add_hard_sub$"))
async def add_hard_sub_callback(client: Client, callback_query: CallbackQuery):
    """Handle add hard subtitle callback"""
    user_id = callback_query.from_user.id
    user_videos_for_sub[user_id] = {"type": "hard", "video": None, "subtitle": None}
    
    await callback_query.message.reply_text(
        "**📝 Add Hard Subtitle**\n\n"
        "**Steps:**\n"
        "1. Send me your video file\n"
        "2. Send me your subtitle file (.srt, .ass, .vtt)\n"
        "3. I'll burn them into the video!\n\n"
        "**Note:** Hard subtitles are permanently embedded and cannot be turned off."
    )
    await callback_query.answer("Send video and subtitle files")


@Client.on_callback_query(filters.regex("^extract_subtitle$"))
async def extract_subtitle_callback(client: Client, callback_query: CallbackQuery):
    """Handle extract subtitle callback"""
    await callback_query.message.reply_text(
        "**📤 Extract Subtitles**\n\n"
        "**Usage:** Send me a video file and I'll extract all subtitle tracks.\n\n"
        "Send your video now!"
    )
    await callback_query.answer("Send video file")


@Client.on_callback_query(filters.regex("^remove_subtitle$"))
async def remove_subtitle_callback(client: Client, callback_query: CallbackQuery):
    """Handle remove subtitle callback"""
    await callback_query.message.reply_text(
        "**🗑️ Remove Subtitles**\n\n"
        "**Usage:** Send me a video file and I'll remove all subtitle tracks.\n\n"
        "Send your video now!"
    )
    await callback_query.answer("Send video file")
