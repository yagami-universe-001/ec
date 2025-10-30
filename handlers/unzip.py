# handlers/unzip.py
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.config import Config
from utils.helpers import format_size
from utils.progress import ProgressTracker
import os
import time
import zipfile
import py7zr
import rarfile

@Client.on_message(filters.command("Unzip") & filters.private)
async def unzip_file(client: Client, message: Message):
    """Unzip compressed files"""for 
    user_id = message.from_user.id
    user_name = message.from_user.first_name or message.from_user.username or "User"
    
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply_text(
            "**📦 Unzip Files**\n\n"
            "**Usage:** Reply to a compressed file with `/Unzip`\n\n"
            "**Supported Formats:**\n"
            "• ZIP (.zip)\n"
            "• RAR (.rar)\n"
            "• 7Z (.7z)\n\n"
            "**Note:** All extracted files will be uploaded separately."
        )
        return
    
    file = message.reply_to_message.document
    file_name = file.file_name
    
    # Check if it's a compressed file
    if not file_name.endswith(('.zip', '.rar', '.7z')):
        await message.reply_text(
            "**⚠️ Invalid file type!**\n\n"
            "Please send a ZIP, RAR, or 7Z file."
        )
        return
    
    processing_msg = await message.reply_text("**⏳ Starting extraction...**")
    
    try:
        # Download archive
        archive_path = os.path.join(Config.DOWNLOAD_DIR, f"{user_id}_{int(time.time())}_{file_name}")
        start_time = time.time()
        
        await client.download_media(
            message.reply_to_message,
            file_name=archive_path,
            progress=ProgressTracker.download_progress,
            progress_args=(processing_msg, file_name, user_name, user_id, start_time)
        )
        
        bot_stats = ProgressTracker.get_bot_stats()
        await processing_msg.edit_text(
            f"**📦 Extracting Archive**\n\n"
            f"┃ `{file_name}`\n\n"
            f"Extracting files...\n"
            f"├ Task By: {user_name}\n"
            f"└ User ID: {user_id}\n\n"
            f"**📊 Bot Stats**\n"
            f"├ CPU: {bot_stats['cpu']:.1f}%\n"
            f"└ RAM: {bot_stats['ram']:.1f}%"
        )
        
        # Extract files
        extract_dir = os.path.join(Config.UPLOAD_DIR, f"{user_id}_{int(time.time())}_extracted")
        os.makedirs(extract_dir, exist_ok=True)
        
        extracted_files = []
        
        if file_name.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                extracted_files = zip_ref.namelist()
        
        elif file_name.endswith('.rar'):
            with rarfile.RarFile(archive_path, 'r') as rar_ref:
                rar_ref.extractall(extract_dir)
                extracted_files = rar_ref.namelist()
        
        elif file_name.endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, 'r') as seven_ref:
                seven_ref.extractall(extract_dir)
                extracted_files = seven_ref.getnames()
        
        if not extracted_files:
            await processing_msg.edit_text("**⚠️ No files found in archive!**")
            return
        
        await processing_msg.edit_text(
            f"**✅ Extraction complete!**\n\n"
            f"**Total Files:** {len(extracted_files)}\n"
            f"**Uploading files...**"
        )
        
        # Upload all extracted files
        uploaded = 0
        for extracted_file in extracted_files:
            file_path = os.path.join(extract_dir, extracted_file)
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            file_size = os.path.getsize(file_path)
            
            # Skip if file too large (2GB limit)
            if file_size > 2 * 1024 * 1024 * 1024:
                await message.reply_text(
                    f"**⚠️ Skipped:** `{extracted_file}`\n"
                    f"**Reason:** File too large ({format_size(file_size)})"
                )
                continue
            
            upload_start = time.time()
            
            try:
                # Determine file type and upload
                if extracted_file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')):
                    await message.reply_video(
                        video=file_path,
                        caption=f"**📹 Extracted File**\n\n`{extracted_file}`\n\n**👤 For:** {user_name}",
                        progress=ProgressTracker.upload_progress,
                        progress_args=(processing_msg, extracted_file, user_name, user_id, upload_start)
                    )
                elif extracted_file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                    await message.reply_photo(
                        photo=file_path,
                        caption=f"**🖼️ Extracted File**\n\n`{extracted_file}`\n\n**👤 For:** {user_name}"
                    )
                elif extracted_file.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac')):
                    await message.reply_audio(
                        audio=file_path,
                        caption=f"**🎵 Extracted File**\n\n`{extracted_file}`\n\n**👤 For:** {user_name}",
                        progress=ProgressTracker.upload_progress,
                        progress_args=(processing_msg, extracted_file, user_name, user_id, upload_start)
                    )
                else:
                    await message.reply_document(
                        document=file_path,
                        caption=f"**📄 Extracted File**\n\n`{extracted_file}`\n\n**👤 For:** {user_name}",
                        progress=ProgressTracker.upload_progress,
                        progress_args=(processing_msg, extracted_file, user_name, user_id, upload_start)
                    )
                
                uploaded += 1
                
            except Exception as e:
                await message.reply_text(
                    f"**❌ Failed to upload:** `{extracted_file}`\n"
                    f"**Error:** {str(e)}"
                )
        
        await processing_msg.edit_text(
            f"**✅ Extraction & Upload Complete!**\n\n"
            f"**Total Files:** {len(extracted_files)}\n"
            f"**Uploaded:** {uploaded}\n"
            f"**👤 Extracted For:** {user_name}"
        )
        
        # Clean up
        if os.path.exists(archive_path):
            os.remove(archive_path)
        
        # Remove extracted directory
        import shutil
        if os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
            
    except Exception as e:
        await processing_msg.edit_text(f"**❌ Error:** {str(e)}")
        
        # Clean up on error
        if 'archive_path' in locals() and os.path.exists(archive_path):
            os.remove(archive_path)
        if 'extract_dir' in locals() and os.path.exists(extract_dir):
            import shutil
            shutil.rmtree(extract_dir)
