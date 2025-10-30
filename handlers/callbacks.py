# handlers/callbacks.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from utils.database import Database
from utils.config import Config
import time

@Client.on_callback_query(filters.regex("^(help|settings|start)$"))
async def main_callbacks(client: Client, callback_query: CallbackQuery):
    """Handle main menu callbacks"""
    action = callback_query.data
    user = callback_query.from_user
    
    if action == "help":
        help_text = """
**📚 Bot Commands Help**

**» ᴜsᴇʀ ᴄᴏᴍᴍᴀɴᴅs:**

/start - Sᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ ᴀɴᴅ ɢᴇᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ
/help - Sʜᴏᴡ ᴀʟʟ ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs
/setthumb - Sᴇᴛ ᴀ ᴄᴜsᴛᴏᴍ ᴛʜᴜᴍʙɴᴀɪʟ
/getthumb - Gᴇᴛ sᴀᴠᴇᴅ ᴛʜᴜᴍʙɴᴀɪʟ
/delthumb - Dᴇʟᴇᴛᴇ sᴀᴠᴇᴅ ᴛʜᴜᴍʙɴᴀɪʟ
/setwatermark - Sᴇᴛ ᴅᴇғᴀᴜʟᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ
/spoiler - ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ sᴘᴏɪʟᴇʀ
/getwatermark - Gᴇᴛ ᴄᴜʀʀᴇɴᴛ ᴡᴀᴛᴇʀᴍᴀʀᴋ
/addwatermark - Aᴅᴅ ʟᴏɢᴏ ᴡᴀᴛᴇʀᴍᴀʀᴋ ᴛᴏ ᴠɪᴅᴇᴏ
/setmedia - Sᴇᴛ ᴘʀᴇғᴇʀʀᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ
/compress - Cᴏᴍᴘʀᴇss ᴍᴇᴅɪᴀ
/cut - Tʀɪᴍ ᴠɪᴅᴇᴏ ʙʏ ᴛɪᴍᴇ
/crop - ᴄʜᴀɴɢᴇ ᴠɪᴅᴇᴏ ᴀsᴘᴇᴄᴛ ʀᴀᴛɪᴏ
/merge - Mᴇʀɢᴇ ᴍᴜʟᴛɪᴘʟᴇ ᴠɪᴅᴇᴏs
/all - Eɴᴄᴏᴅᴇ ɪɴ ᴀʟʟ ǫᴜᴀʟɪᴛɪᴇs ᴀᴛ ᴏɴᴄᴇ
/144p to /2160p - Cᴏɴᴠᴇʀᴛ ᴛᴏ sᴘᴇᴄɪғɪᴄ ǫᴜᴀʟɪᴛʏ
/sub - Aᴅᴅ sᴏғᴛ sᴜʙᴛɪᴛʟᴇs
/hsub - Aᴅᴅ ʜᴀʀᴅ sᴜʙᴛɪᴛʟᴇs
/rsub - Rᴇᴍᴏᴠᴇ ᴀʟʟ sᴜʙᴛɪᴛʟᴇs
/extract_sub - Exᴛʀᴀᴄᴛ sᴜʙᴛɪᴛʟᴇs ғʀᴏᴍ ᴠɪᴅᴇᴏ
/extract_audio - Exᴛʀᴀᴄᴛ ᴀᴜᴅɪᴏ ғʀᴏᴍ ᴠɪᴅᴇᴏ
/extract_thumb - Exᴛʀᴀᴄᴛ ᴛʜᴜᴍʙɴᴀɪʟ ғʀᴏᴍ ᴠɪᴅᴇᴏ
/addaudio - Aᴅᴅ ᴀᴜᴅɪᴏ ᴛᴏ ᴠɪᴅᴇᴏ
/remaudio - Rᴇᴍᴏᴠᴇ ᴀᴜᴅɪᴏ ғʀᴏᴍ ᴠɪᴅᴇᴏ
/upload - sᴇᴛ ᴜᴘʟᴏᴀᴅ ᴅᴇsᴛɪɴᴀᴛɪᴏɴ
/mediainfo - Gᴇᴛ ᴅᴇᴛᴀɪʟᴇᴅ ᴍᴇᴅɪᴀ ɪɴғᴏ
/Unzip - to unzip a zipfiles
/Rename - to rename the telegram files
        """
        
        buttons = [
            [InlineKeyboardButton("🏠 Home", callback_data="start")],
            [InlineKeyboardButton("📢 Updates", url="https://t.me/YourChannel")]
        ]
        
        await callback_query.message.edit_text(
            text=help_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif action == "settings":
        user_settings = await Database.get_user_settings(user.id)
        
        upload_mode = "📄 Document" if user_settings['upload_as_doc'] else "🎥 Video"
        spoiler_mode = "✅ Enabled" if user_settings['spoiler_enabled'] else "❌ Disabled"
        
        settings_text = f"""
**⚙️ Your Settings**

**Upload Mode:** {upload_mode}
**Spoiler:** {spoiler_mode}

**Use /upload to change upload mode**
**Use /spoiler to toggle spoiler**
        """
        
        buttons = [
            [
                InlineKeyboardButton("📄 Upload as Doc" if not user_settings['upload_as_doc'] else "🎥 Upload as Video", 
                                   callback_data="toggle_upload_mode")
            ],
            [
                InlineKeyboardButton("✅ Enable Spoiler" if not user_settings['spoiler_enabled'] else "❌ Disable Spoiler",
                                   callback_data="toggle_spoiler")
            ],
            [InlineKeyboardButton("« Back", callback_data="start")]
        ]
        
        await callback_query.message.edit_text(
            text=settings_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    elif action == "start":
        welcome_text = f"""
**👋 Welcome {user.mention}!**

I'm a powerful video encoder bot with advanced features!

**🎬 Main Features:**
• Multiple quality encoding (144p to 2160p)
• Custom watermark support
• Subtitle management
• Audio extraction & manipulation
• Video merging & trimming
• Compression & format conversion
• And much more!

**📝 Quick Start:**
Send me any video file and I'll show you available options!

Use /help to see all commands.

**👤 User:** {user.mention}
**🆔 User ID:** `{user.id}`
**⏰ Time:** `{time.strftime('%Y-%m-%d %H:%M:%S')}`
        """
        
        buttons = [
            [
                InlineKeyboardButton("📚 Help", callback_data="help"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📢 Updates", url="https://t.me/YourChannel"),
                InlineKeyboardButton("💬 Support", url="https://t.me/YourSupport")
            ]
        ]
        
        await callback_query.message.edit_text(
            text=welcome_text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
    
    await callback_query.answer()


@Client.on_callback_query(filters.regex("^toggle_"))
async def toggle_settings(client: Client, callback_query: CallbackQuery):
    """Handle settings toggles"""
    user_id = callback_query.from_user.id
    action = callback_query.data
    
    if action == "toggle_upload_mode":
        current_settings = await Database.get_user_settings(user_id)
        new_value = not current_settings['upload_as_doc']
        await Database.set_user_setting(user_id, "upload_as_doc", new_value)
        
        mode = "Document" if new_value else "Video"
        await callback_query.answer(f"✅ Upload mode changed to {mode}", show_alert=True)
    
    elif action == "toggle_spoiler":
        current_settings = await Database.get_user_settings(user_id)
        new_value = not current_settings['spoiler_enabled']
        await Database.set_user_setting(user_id, "spoiler_enabled", new_value)
        
        status = "Enabled" if new_value else "Disabled"
        await callback_query.answer(f"✅ Spoiler {status}", show_alert=True)
    
    # Refresh settings menu
    user_settings = await Database.get_user_settings(user_id)
    
    upload_mode = "📄 Document" if user_settings['upload_as_doc'] else "🎥 Video"
    spoiler_mode = "✅ Enabled" if user_settings['spoiler_enabled'] else "❌ Disabled"
    
    settings_text = f"""
**⚙️ Your Settings**

**Upload Mode:** {upload_mode}
**Spoiler:** {spoiler_mode}

**Use /upload to change upload mode**
**Use /spoiler to toggle spoiler**
    """
    
    buttons = [
        [
            InlineKeyboardButton("📄 Upload as Doc" if not user_settings['upload_as_doc'] else "🎥 Upload as Video", 
                               callback_data="toggle_upload_mode")
        ],
        [
            InlineKeyboardButton("✅ Enable Spoiler" if not user_settings['spoiler_enabled'] else "❌ Disable Spoiler",
                               callback_data="toggle_spoiler")
        ],
        [InlineKeyboardButton("« Back", callback_data="start")]
    ]
    
    await callback_query.message.edit_text(
        text=settings_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^cancel_operation$"))
async def cancel_operation(client: Client, callback_query: CallbackQuery):
    """Cancel current operation"""
    await callback_query.message.delete()
    await callback_query.answer("❌ Operation cancelled", show_alert=True)


@Client.on_callback_query(filters.regex("^back_to_main$"))
async def back_to_main(client: Client, callback_query: CallbackQuery):
    """Go back to main menu"""
    await callback_query.message.delete()
    await callback_query.answer("Returning to main menu...")


@Client.on_callback_query(filters.regex("^check_fsub$"))
async def check_fsub_callback(client: Client, callback_query: CallbackQuery):
    """Check force subscribe status"""
    user = callback_query.from_user
    
    # Check force subscribe
    fsub_channels = await Database.get_fsub_channels()
    not_joined = []
    
    for channel in fsub_channels:
        try:
            member = await client.get_chat_member(channel['channel_id'], user.id)
            if member.status in ["left", "kicked"]:
                not_joined.append(channel)
        except:
            not_joined.append(channel)
    
    if not_joined:
        await callback_query.answer("⚠️ Please join all channels first!", show_alert=True)
    else:
        await callback_query.answer("✅ Access granted!", show_alert=True)
        await callback_query.message.delete()
        
        # Show welcome message
        welcome_text = f"""
**👋 Welcome {user.mention}!**

You now have access to the bot!

Send me a video file to get started.

Use /help to see all commands.
        """
        
        await callback_query.message.reply_text(welcome_text)


@Client.on_message(filters.command(["upload", "setmedia"]) & filters.private)
async def set_upload_mode(client: Client, message: Message):
    """Set preferred upload mode"""
    user_id = message.from_user.id
    
    current_settings = await Database.get_user_settings(user_id)
    
    buttons = [
        [
            InlineKeyboardButton("🎥 Video", callback_data="set_upload_video"),
            InlineKeyboardButton("📄 Document", callback_data="set_upload_doc")
        ]
    ]
    
    current_mode = "Document" if current_settings['upload_as_doc'] else "Video"
    
    await message.reply_text(
        f"**⚙️ Upload Mode Settings**\n\n"
        f"**Current Mode:** {current_mode}\n\n"
        f"**Choose your preferred upload mode:**",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_callback_query(filters.regex("^set_upload_"))
async def set_upload_callback(client: Client, callback_query: CallbackQuery):
    """Handle upload mode selection"""
    user_id = callback_query.from_user.id
    mode = callback_query.data.replace("set_upload_", "")
    
    is_doc = mode == "doc"
    await Database.set_user_setting(user_id, "upload_as_doc", is_doc)
    
    mode_text = "Document" if is_doc else "Video"
    await callback_query.answer(f"✅ Upload mode set to {mode_text}", show_alert=True)
    await callback_query.message.delete()


@Client.on_message(filters.command("spoiler") & filters.private)
async def toggle_spoiler_command(client: Client, message: Message):
    """Toggle spoiler mode"""
    user_id = message.from_user.id
    
    current_settings = await Database.get_user_settings(user_id)
    new_value = not current_settings['spoiler_enabled']
    
    await Database.set_user_setting(user_id, "spoiler_enabled", new_value)
    
    status = "✅ Enabled" if new_value else "❌ Disabled"
    await message.reply_text(
        f"**🔒 Spoiler Mode {status}**\n\n"
        f"Videos will {'now' if new_value else 'no longer'} be sent with spoiler effect."
    )
