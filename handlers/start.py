# handlers/start.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from utils.database import Database
from utils.config import Config
import time

@Client.on_message(filters.command("start") & filters.private)
async def start_handler(client: Client, message: Message):
    """Handle /start command"""
    user = message.from_user
    
    # Add user to database
    await Database.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
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
        buttons = []
        for channel in not_joined:
            username = channel.get('username', f"Channel {channel['channel_id']}")
            buttons.append([InlineKeyboardButton(f"Join {username}", url=f"https://t.me/{username}")])
        buttons.append([InlineKeyboardButton("✅ Try Again", callback_data="check_fsub")])
        
        await message.reply_photo(
            photo=Config.START_PIC,
            caption="**🚫 Access Denied**\n\nYou must join our channels to use this bot.\n\nPlease join the channels below and click Try Again:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
    
    # Welcome message
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
    
    await message.reply_photo(
        photo=Config.START_PIC,
        caption=welcome_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@Client.on_message(filters.command("help") & filters.private)
async def help_handler(client: Client, message: Message):
    """Handle /help command"""
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
/144p - Cᴏɴᴠᴇʀᴛ ᴛᴏ 𝟷𝟺𝟺ᴘ
/240p - Cᴏɴᴠᴇʀᴛ ᴛᴏ 𝟸𝟺𝟶ᴘ
/360p - Cᴏɴᴠᴇʀᴛ ᴛᴏ 𝟹𝟾𝟶ᴘ
/480p - Cᴏɴᴠᴇʀᴛ ᴛᴏ 𝟺𝟾𝟶ᴘ
/720p - Cᴏɴᴠᴇʀᴛ ᴛᴏ 𝟽𝟸𝟶ᴘ
/1080p - Cᴏɴᴠᴇʀᴛ ᴛᴏ 𝟷𝟶𝟾𝟶ᴘ
/2160p - Cᴏɴᴠᴇʀᴛ ᴛᴏ 𝟸𝟷𝟼𝟶ᴘ
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
    
    # Check if user is admin
    if message.from_user.id in Config.ADMIN_IDS:
        help_text += """

**» ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅs:**

/restart - Rᴇsᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ (Aᴅᴍɪɴ ᴏɴʟʏ)
/queue - Cʜᴇᴄᴋ ᴛᴏᴛᴀʟ ǫᴜᴇᴜᴇ (Aᴅᴍɪɴ ᴏɴʟʏ)
/clear - Cʟᴇᴀʀ ᴀʟʟ ǫᴜᴇᴜᴇ ᴛᴀsᴋs (Aᴅᴍɪɴ ᴏɴʟʏ)
/audio - Sᴇᴛ ᴀᴜᴅɪᴏ ʙɪᴛʀᴀᴛᴇ (Aᴅᴍɪɴ ᴏɴʟʏ)
/codec - Sᴇᴛ ᴠɪᴅᴇᴏ ᴄᴏᴅᴇᴄ (Aᴅᴍɪɴ ᴏɴʟʏ)
/addchnl - Sᴇᴛ ғsᴜʙ ᴄʜᴀɴɴᴇʟ (Aᴅᴍɪɴ ᴏɴʟʏ)
/delchnl - Dᴇʟᴇᴛᴇ ғsᴜʙ (Aᴅᴍɪɴ ᴏɴʟʏ)
/listchnl - Lɪsᴛ ᴀʟʟ ғsᴜʙ ᴄʜᴀɴɴᴇʟs (Aᴅᴍɪɴ ᴏɴʟʏ)
/fsub_mode - ᴄʜᴇᴄᴋ ʀᴇǫᴜᴇsᴛ ᴍᴏᴅᴇ ғsᴜʙ (Aᴅᴍɪɴ ᴏɴʟʏ)
/shortner - sᴇᴇ sʜᴏʀᴛɴᴇʀ (Aᴅᴍɪɴ ᴏɴʟʏ)
/shortlink1 - sᴇᴛ sʜᴏʀᴛʟɪɴᴋ 𝟷 (Aᴅᴍɪɴ ᴏɴʟʏ)
/tutorial1 - sᴇᴛ ᴛᴜᴛᴏʀɪᴀʟ ғᴏʀ sʜᴏʀᴛɴᴇʀ𝟷 (Aᴅᴍɪɴ ᴏɴʟʏ)
/shortlink2 - sᴇᴛ sʜᴏʀᴛʟɪɴᴋ 𝟸 (Aᴅᴍɪɴ ᴏɴʟʏ)
/tutorial2 - sᴇᴛ ᴛᴜᴛᴏʀɪᴀʟ ғᴏʀ sʜᴏʀᴛɴᴇʀ𝟸 (Aᴅᴍɪɴ ᴏɴʟʏ)
/shortner1 - sᴇᴇ sʜᴏʀᴛᴇɴᴇʀ𝟷 ᴄᴏɴғɪɢ (Aᴅᴍɪɴ ᴏɴʟʏ)
/shortner2 - sᴇᴇ sʜᴏʀᴛᴇɴᴇʀ𝟸 ᴄᴏɴғɪɢ (Aᴅᴍɪɴ ᴏɴʟʏ)
/addpaid - ᴀᴅᴅ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀ (Aᴅᴍɪɴ ᴏɴʟʏ)
/listpaid - ʟɪsᴛ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs (Aᴅᴍɪɴ ᴏɴʟʏ)
/rempaid - ʀᴇᴍᴏᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴜsᴇʀs (Aᴅᴍɪɴ ᴏɴʟʏ)
/preset - Cʜᴀɴɢᴇ ᴇɴᴄᴏᴅɪɴɢ ᴘʀᴇsᴇᴛ (Aᴅᴍɪɴ ᴏɴʟʏ)
/crf - Sᴇᴛ CRF ᴠᴀʟᴜᴇ (Aᴅᴍɪɴ ᴏɴʟʏ)
/update - Gɪᴛ ᴘᴜʟʟ ʟᴀᴛᴇsᴛ ᴜᴘᴅᴀᴛᴇs (Aᴅᴍɪɴ ᴏɴʟʏ)
/Setstartpic - to setstartpic for bot (Admin only)
        """
    
    buttons = [
        [InlineKeyboardButton("🏠 Home", callback_data="start")],
        [InlineKeyboardButton("📢 Updates", url="https://t.me/YourChannel")]
    ]
    
    await message.reply_text(
        text=help_text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )
