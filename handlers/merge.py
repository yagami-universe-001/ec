# handlers/merge.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from utils.ffmpeg_helper import FFmpegHelper
from utils.config import Config
from utils.helpers import format_size, format_time
import os
import time

# Store user videos for merging
user_merge_videos = {}


@Client.on_message(filters.command("merge") & filters.private)
async def merge_videos_command(client: Client, message: Message):
    """Start video merging process"""
    user_id = message.from_user.id
    
    # Initialize merge session
    user_merge_videos[user_id] = {
        "videos": [],
        "file_paths": [],
        "started_at": time.time()
    }
    
    await message.reply_text(
        "**🔀 Merge Videos**\n\n"
        "**Steps:**\n"
        "1. Send me multiple video files one by one\n"
        "2. When you're done, type `done` or use /done\n"
        "3. I'll merge them in the order you sent them!\n\n"
        "**📝 Current Videos:** 0\n\n"
        "**Note:** All videos should have similar resolution and format for best results."
    )


@Client.on_message(filters.command("done") & filters.private)
async def done_merging(client: Client, message: Message):
    """Finish collecting videos and start merging"""
    user_id = message.from_user.id
    
    if user_id not in user_merge_videos:
        await message.reply_text(
            "**⚠️ No merge session active!**\n\n"
            "Use `/merge` to start a new merge session."
        )
        return
    
    session = user_merge_videos[user_id]
    
    if len(session['videos']) < 2:
        await message.reply_text(
            "**⚠️ Not enough videos!**\n\n"
            f"**Current Videos:** {len(session['videos'])}\n"
            f"**Required:** At least 2 videos\n\n"
            "Please send more videos or use /cancel to cancel."
        )
        return
    
    await process_merge(client, message, user_id, session)


@Client.on_message(filters.command("cancel") & filters.private)
async def cancel_merge(client: Client, message: Message):
    """Cancel merge session"""
    user_id = message.from_user.id
    
    if user_id in user_merge_videos:
        # Clean up downloaded files
        for file_path in user_merge_videos[user_id]['file_paths']:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        del user_merge_videos[user_id]
        await message.reply_text("**✅ Merge session cancelled!**")
    else:
        await message.reply_text("**⚠️ No active merge session!**")


@Client.on_message((filters.video | filters.document) & filters.private)
async def collect_merge_videos(client: Client, message: Message):
    """Collect videos for merging"""
    user_id = message.from_user.id
    
    if user_id not in user_merge_videos:
        return
    
    # Check if file is video
    if message.document and not message.document.mime_type.startswith("video/"):
        return
    
    file = message.video or message.document
    session = user_merge_videos[user_id]
    
    # Download video
    status_msg = await message.reply_text("**⬇️ Downloading video...**")
    
    try:
        file_path = os.path.join(
            Config.DOWNLOAD_DIR,
            f"{user_id}_merge_{len(session['videos'])}_{int(time.time())}.mp4"
        )
        
        await client.download_media(message, file_name=file_path)
        
        # Store video info
        session['videos'].append({
            'file_id': file.file_id,
            'file_name': file.file_name or f"video_{len(session['videos']) + 1}.mp4",
            'file_size': file.file_size,
            'duration': getattr(file, 'duration', 0)
        })
        session['file_paths'].append(file_path)
        
        # Show status
        total_duration = sum(v['duration'] for v in session['videos'])
        total_size = sum(v['file_size'] for v in session['videos'])
        
        video_list = "\n".join([
            f"{i+1}. `{v['file_name']}` - {format_time(v['duration'])}"
            for i, v in enumerate(session['videos'])
        ])
        
        await status_msg.edit_text(
            f"**✅ Video {len(session['videos'])} added!**\n\n"
            f"**📝 Videos in Queue:**\n{video_list}\n\n"
            f"**📊 Total Duration:** {format_time(total_duration)}\n"
            f"**📦 Total Size:** {format_size(total_size)}\n\n"
            f"**➡️ Send more videos or type `done` to merge them!**"
        )
        
    except Exception as e:
        await status_msg.edit_text(f"**❌ Error downloading video:** {str(e)}")


async def process_merge(client, message, user_id, session):
    """Process video merging"""
    processing_msg = await message.reply_text(
        f"**🔀 Merging {len(session['videos'])} videos...**\n\n"
        "**⏳ This may take a while...**"
    )
    
    try:
        # Prepare output file
        output_path = os.path.join(
            Config.UPLOAD_DIR,
            f"{user_id}_merged_{int(time.time())}.mp4"
        )
        
        # Merge videos
        success = await FFmpegHelper.merge_videos(session['file_paths'], output_path)
        
        if not success or not os.path.exists(output_path):
            await processing_msg.edit_text("**❌ Failed to merge videos!**")
            return
        
        await processing_msg.edit_text("**⬆️ Uploading merged video...**")
        
        # Get merged video info
        file_size = os.path.getsize(output_path)
        total_duration = sum(v['duration'] for v in session['videos'])
        
        # Upload merged video
        caption = f"""
**✅ Videos merged successfully!**

**📝 Total Videos:** {len(session['videos'])}
**⏱ Total Duration:** {format_time(total_duration)}
**📦 Size:** {format_size(file_size)}
**💪 Merged By:** ꜱᴋ•ᴘᴀᴛʜɪʀᴀᴊ.ᴘʏ™ 𝕏
        """
        
        await message.reply_video(
            video=output_path,
            caption=caption,
            duration=int(total_duration)
        )
        
        await processing_msg.delete()
        
        # Clean up
        for file_path in session['file_paths']:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if os.path.exists(output_path):
            os.remove(output_path)
        
        # Clear session
        del user_merge_videos[user_id]
        
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")
        
        # Clean up on error
        for file_path in session['file_paths']:
            if os.path.exists(file_path):
                os.remove(file_path)


@Client.on_callback_query(filters.regex("^merge_videos$"))
async def merge_callback(client: Client, callback_query: CallbackQuery):
    """Handle merge videos callback"""
    user_id = callback_query.from_user.id
    
    # Initialize merge session
    user_merge_videos[user_id] = {
        "videos": [],
        "file_paths": [],
        "started_at": time.time()
    }
    
    await callback_query.message.reply_text(
        "**🔀 Merge Videos**\n\n"
        "**Steps:**\n"
        "1. Send me multiple video files one by one\n"
        "2. When you're done, type `done` or use /done\n"
        "3. I'll merge them in the order you sent them!\n\n"
        "**📝 Current Videos:** 0\n\n"
        "**Note:** All videos should have similar resolution and format for best results."
    )
    
    await callback_query.answer("Send video files to merge")


# Handle text "done" as well
@Client.on_message(filters.text & filters.private)
async def handle_done_text(client: Client, message: Message):
    """Handle 'done' text message"""
    user_id = message.from_user.id
    
    if message.text.lower() == "done" and user_id in user_merge_videos:
        await done_merging(client, message)
