# handlers/rename.py
from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
from utils.config import Config
from utils.helpers import format_size, clean_filename, change_filename
from utils.progress import ProgressTracker
import os
import time

# Store rename sessions
rename_sessions = {}


@Client.on_message(filters.command("Rename") & filters.private)
async def rename_file(client: Client, message: Message):
    """Rename telegram files"""
    user_id = message.from_user.id
    
    if len(message.command) < 2:
        await message.reply_text(
            "**📋 Rename File**\n\n"
            "**Usage:** Reply to a file with `/Rename <new_name>`\n\n"
            "**Examples:**\n"
            "• `/Rename My Movie 2024` - Keeps original extension\n"
            "• `/Rename video.mp4` - Custom name with extension\n\n"
            "**Note:** File extension will be preserved if not provided."
        )
        return
    
    if not message.reply_to_message:
        await message.reply_text("**⚠️ Please reply to a file!**")
        return
    
    # Get file
    file = (message.reply_to_message.video or 
            message.reply_to_message.document or
            message.reply_to_message.audio or
            message.reply_to_message.animation)
    
    if not file:
        await message.reply_text("**⚠️ No valid file found in the replied message!**")
        return
    
    # Get new name
    new_name = message.text.split(None, 1)[1]
    old_name = file.file_name or "file"
    
    # Preserve extension if not provided
    if '.' not in new_name:
        new_name = change_filename(old_name, new_name)
    else:
        new_name = clean_filename(new_name)
    
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    processing_msg = await message.reply_text("**⏳ Renaming file...**")
    
    try:
        # Download file
        input_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_{old_name}")
        start_time = time.time()
        
        await client.download_media(
            message.reply_to_message,
            file_name=input_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, old_name, user_name, user_id, start_time)
        )
        
        # Rename (move) file
        output_path = os.path.join(Config.UPLOAD_DIR, new_name)
        os.rename(input_path, output_path)
        
        # Upload with new name
        file_size = os.path.getsize(output_path)
        upload_start = time.time()
        
        # Determine file type and upload accordingly
        if message.reply_to_message.video:
            await message.reply_video(
                video=output_path,
                caption=f"**✅ File renamed!**\n\n"
                       f"**Old:** `{old_name}`\n"
                       f"**New:** `{new_name}`\n"
                       f"**Size:** `{format_size(file_size)}`\n"
                       f"**👤 Renamed For:** {user_name}",
                progress=ProgressTracker.upload_progress,
                progress_args=(processing_msg, new_name, user_name, user_id, upload_start)
            )
        elif message.reply_to_message.audio:
            await message.reply_audio(
                audio=output_path,
                caption=f"**✅ File renamed!**\n\n**New Name:** `{new_name}`\n**👤 Renamed For:** {user_name}",
                progress=ProgressTracker.upload_progress,
                progress_args=(processing_msg, new_name, user_name, user_id, upload_start)
            )
        else:
            await message.reply_document(
                document=output_path,
                caption=f"**✅ File renamed!**\n\n**New Name:** `{new_name}`\n**👤 Renamed For:** {user_name}",
                progress=ProgressTracker.upload_progress,
                progress_args=(processing_msg, new_name, user_name, user_id, upload_start)
            )
        
        await processing_msg.delete()
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_callback_query(filters.regex("^rename_file$"))
async def rename_callback(client: Client, callback_query: CallbackQuery):
    """Handle rename callback"""
    await callback_query.message.reply_text(
        "**📋 Rename File**\n\n"
        "Reply to any file with `/Rename <new_name>` to rename it!"
    )
    await callback_query.answer("Use /Rename command")
