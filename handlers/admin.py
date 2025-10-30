# handlers/admin.py
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.database import Database
from utils.config import Config
import os
import sys
import subprocess

def admin_only(func):
    """Decorator for admin-only commands"""
    async def wrapper(client: Client, message: Message):
        if message.from_user.id not in Config.ADMIN_IDS:
            await message.reply_text("**⚠️ This command is only for admins!**")
            return
        return await func(client, message)
    return wrapper


@Client.on_message(filters.command("restart") & filters.private)
@admin_only
async def restart_bot(client: Client, message: Message):
    """Restart the bot"""
    await message.reply_text("**🔄 Restarting bot...**")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("queue") & filters.private)
@admin_only
async def check_queue(client: Client, message: Message):
    """Check total queue"""
    queue_size = await Database.get_queue_size()
    await message.reply_text(
        f"**📊 Queue Status**\n\n"
        f"**Total Pending Tasks:** `{queue_size}`"
    )


@Client.on_message(filters.command("clear") & filters.private)
@admin_only
async def clear_queue(client: Client, message: Message):
    """Clear all queue tasks"""
    await Database.clear_queue()
    await message.reply_text("**✅ Queue cleared successfully!**")


@Client.on_message(filters.command("audio") & filters.private)
@admin_only
async def set_audio_bitrate(client: Client, message: Message):
    """Set audio bitrate"""
    if len(message.command) < 2:
        current = await Database.get_bot_setting("audio_bitrate") or Config.DEFAULT_AUDIO_BITRATE
        await message.reply_text(
            f"**🎵 Audio Bitrate Settings**\n\n"
            f"**Current:** `{current}`\n\n"
            f"**Usage:** `/audio <bitrate>`\n"
            f"**Example:** `/audio 192k`"
        )
        return
    
    bitrate = message.command[1]
    await Database.set_bot_setting("audio_bitrate", bitrate)
    await message.reply_text(f"**✅ Audio bitrate set to:** `{bitrate}`")


@Client.on_message(filters.command("codec") & filters.private)
@admin_only
async def set_codec(client: Client, message: Message):
    """Set video codec"""
    if len(message.command) < 2:
        current = await Database.get_bot_setting("codec") or Config.DEFAULT_CODEC
        await message.reply_text(
            f"**🎬 Video Codec Settings**\n\n"
            f"**Current:** `{current}`\n\n"
            f"**Available Codecs:**\n"
            f"• `libx264` - H.264 (default, best compatibility)\n"
            f"• `libx265` - H.265 (better compression)\n"
            f"• `libvpx-vp9` - VP9 (web optimized)\n\n"
            f"**Usage:** `/codec <codec_name>`"
        )
        return
    
    codec = message.command[1]
    await Database.set_bot_setting("codec", codec)
    await message.reply_text(f"**✅ Video codec set to:** `{codec}`")


@Client.on_message(filters.command("preset") & filters.private)
@admin_only
async def set_preset(client: Client, message: Message):
    """Change encoding preset"""
    if len(message.command) < 2:
        current = await Database.get_bot_setting("preset") or Config.DEFAULT_PRESET
        await message.reply_text(
            f"**⚙️ Encoding Preset Settings**\n\n"
            f"**Current:** `{current}`\n\n"
            f"**Available Presets:**\n"
            f"• `ultrafast` - Fastest, larger files\n"
            f"• `superfast` - Very fast\n"
            f"• `veryfast` - Fast\n"
            f"• `faster` - Faster than medium\n"
            f"• `fast` - Fast\n"
            f"• `medium` - Balanced (default)\n"
            f"• `slow` - Slower, better quality\n"
            f"• `slower` - Very slow, great quality\n"
            f"• `veryslow` - Slowest, best quality\n\n"
            f"**Usage:** `/preset <preset_name>`"
        )
        return
    
    preset = message.command[1]
    await Database.set_bot_setting("preset", preset)
    await message.reply_text(f"**✅ Encoding preset set to:** `{preset}`")


@Client.on_message(filters.command("crf") & filters.private)
@admin_only
async def set_crf(client: Client, message: Message):
    """Set CRF value"""
    if len(message.command) < 2:
        current = await Database.get_bot_setting("crf") or Config.DEFAULT_CRF
        await message.reply_text(
            f"**📊 CRF Settings**\n\n"
            f"**Current:** `{current}`\n\n"
            f"**CRF Range:** 0-51\n"
            f"• 0-17: Visually lossless\n"
            f"• 18-23: High quality (recommended)\n"
            f"• 24-28: Medium quality (default: 28)\n"
            f"• 29-51: Low quality, smaller files\n\n"
            f"**Usage:** `/crf <value>`\n"
            f"**Example:** `/crf 23`"
        )
        return
    
    try:
        crf = int(message.command[1])
        if crf < 0 or crf > 51:
            await message.reply_text("**⚠️ CRF must be between 0 and 51!**")
            return
        
        await Database.set_bot_setting("crf", str(crf))
        await message.reply_text(f"**✅ CRF value set to:** `{crf}`")
    except ValueError:
        await message.reply_text("**⚠️ Invalid CRF value! Must be a number.**")


@Client.on_message(filters.command("addchnl") & filters.private)
@admin_only
async def add_fsub_channel(client: Client, message: Message):
    """Add force subscribe channel"""
    if len(message.command) < 2:
        await message.reply_text(
            "**📢 Add Force Subscribe Channel**\n\n"
            "**Usage:** `/addchnl <channel_id or @username>`\n"
            "**Example:** `/addchnl -1001234567890`"
        )
        return
    
    channel = message.command[1]
    
    try:
        if channel.startswith("@"):
            chat = await client.get_chat(channel)
            channel_id = chat.id
            username = chat.username
        else:
            channel_id = int(channel)
            try:
                chat = await client.get_chat(channel_id)
                username = chat.username
            except:
                username = None
        
        await Database.add_fsub_channel(channel_id, username)
        await message.reply_text(
            f"**✅ Force subscribe channel added!**\n\n"
            f"**Channel ID:** `{channel_id}`\n"
            f"**Username:** `{username if username else 'N/A'}`"
        )
    except Exception as e:
        await message.reply_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("delchnl") & filters.private)
@admin_only
async def delete_fsub_channel(client: Client, message: Message):
    """Delete force subscribe channel"""
    if len(message.command) < 2:
        await message.reply_text(
            "**🗑 Delete Force Subscribe Channel**\n\n"
            "**Usage:** `/delchnl <channel_id>`"
        )
        return
    
    try:
        channel_id = int(message.command[1])
        await Database.remove_fsub_channel(channel_id)
        await message.reply_text(f"**✅ Channel {channel_id} removed from force subscribe!**")
    except Exception as e:
        await message.reply_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("listchnl") & filters.private)
@admin_only
async def list_fsub_channels(client: Client, message: Message):
    """List all force subscribe channels"""
    channels = await Database.get_fsub_channels()
    
    if not channels:
        await message.reply_text("**📢 No force subscribe channels configured!**")
        return
    
    text = "**📢 Force Subscribe Channels**\n\n"
    for i, channel in enumerate(channels, 1):
        text += f"**{i}.** ID: `{channel['channel_id']}`\n"
        if channel['username']:
            text += f"   Username: @{channel['username']}\n"
        text += "\n"
    
    await message.reply_text(text)


@Client.on_message(filters.command("addpaid") & filters.private)
@admin_only
async def add_premium_user(client: Client, message: Message):
    """Add premium user"""
    if len(message.command) < 2:
        await message.reply_text(
            "**💎 Add Premium User**\n\n"
            "**Usage:** `/addpaid <user_id> [days]`\n"
            "**Example:** `/addpaid 123456789 30`\n\n"
            "**Default:** 30 days"
        )
        return
    
    try:
        user_id = int(message.command[1])
        days = int(message.command[2]) if len(message.command) > 2 else 30
        
        await Database.add_premium_user(user_id, days)
        await message.reply_text(
            f"**✅ Premium access granted!**\n\n"
            f"**User ID:** `{user_id}`\n"
            f"**Duration:** `{days} days`"
        )
    except Exception as e:
        await message.reply_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("listpaid") & filters.private)
@admin_only
async def list_premium_users(client: Client, message: Message):
    """List premium users"""
    users = await Database.get_premium_users()
    
    if not users:
        await message.reply_text("**💎 No premium users found!**")
        return
    
    text = "**💎 Premium Users**\n\n"
    for i, user in enumerate(users, 1):
        text += f"**{i}.** ID: `{user['user_id']}`\n"
        if user['username']:
            text += f"   Username: @{user['username']}\n"
        text += f"   Expires: `{user['expiry']}`\n\n"
    
    await message.reply_text(text)


@Client.on_message(filters.command("rempaid") & filters.private)
@admin_only
async def remove_premium_user(client: Client, message: Message):
    """Remove premium user"""
    if len(message.command) < 2:
        await message.reply_text(
            "**🗑 Remove Premium User**\n\n"
            "**Usage:** `/rempaid <user_id>`"
        )
        return
    
    try:
        user_id = int(message.command[1])
        await Database.remove_premium_user(user_id)
        await message.reply_text(f"**✅ Premium access removed for user:** `{user_id}`")
    except Exception as e:
        await message.reply_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("update") & filters.private)
@admin_only
async def git_update(client: Client, message: Message):
    """Git pull latest updates"""
    msg = await message.reply_text("**🔄 Checking for updates...**")
    
    try:
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True
        )
        
        output = result.stdout + result.stderr
        
        if "Already up to date" in output:
            await msg.edit_text("**✅ Bot is already up to date!**")
        elif "Updating" in output:
            await msg.edit_text(
                f"**✅ Updated successfully!**\n\n"
                f"```\n{output}\n```\n\n"
                f"**Use /restart to apply changes.**"
            )
        else:
            await msg.edit_text(f"**Output:**\n```\n{output}\n```")
    except Exception as e:
        await msg.edit_text(f"**❌ Error:** {str(e)}")


@Client.on_message(filters.command("Setstartpic") & filters.private)
@admin_only
async def set_start_pic(client: Client, message: Message):
    """Set start picture for bot"""
    if len(message.command) < 2:
        current = Config.START_PIC
        await message.reply_text(
            f"**🖼 Start Picture Settings**\n\n"
            f"**Current:** `{current}`\n\n"
            f"**Usage:** `/Setstartpic <image_url>`"
        )
        return
    
    pic_url = message.command[1]
    await Database.set_bot_setting("start_pic", pic_url)
    Config.START_PIC = pic_url
    
    await message.reply_text(
        f"**✅ Start picture updated!**\n\n"
        f"**New URL:** `{pic_url}`"
    )


@Client.on_message(filters.command("shortner") & filters.private)
@admin_only
async def view_shortener(client: Client, message: Message):
    """View shortener configuration"""
    shortener1_api = await Database.get_bot_setting("shortener_1_api") or "Not Set"
    shortener1_url = await Database.get_bot_setting("shortener_1_url") or "Not Set"
    tutorial1 = await Database.get_bot_setting("tutorial_1") or "Not Set"
    
    shortener2_api = await Database.get_bot_setting("shortener_2_api") or "Not Set"
    shortener2_url = await Database.get_bot_setting("shortener_2_url") or "Not Set"
    tutorial2 = await Database.get_bot_setting("tutorial_2") or "Not Set"
    
    text = f"""
**🔗 Shortener Configuration**

**📱 Shortener 1:**
• API: `{shortener1_api}`
• URL: `{shortener1_url}`
• Tutorial: `{tutorial1}`

**📱 Shortener 2:**
• API: `{shortener2_api}`
• URL: `{shortener2_url}`
• Tutorial: `{tutorial2}`
    """
    
    await message.reply_text(text)


@Client.on_message(filters.command("shortlink1") & filters.private)
@admin_only
async def set_shortlink1(client: Client, message: Message):
    """Set shortlink 1"""
    if len(message.command) < 3:
        await message.reply_text(
            "**🔗 Set Shortlink 1**\n\n"
            "**Usage:** `/shortlink1 <api_key> <url>`\n"
            "**Example:** `/shortlink1 abc123 https://example.com`"
        )
        return
    
    api_key = message.command[1]
    url = message.command[2]
    
    await Database.set_bot_setting("shortener_1_api", api_key)
    await Database.set_bot_setting("shortener_1_url", url)
    
    await message.reply_text(
        f"**✅ Shortlink 1 configured!**\n\n"
        f"**API:** `{api_key}`\n"
        f"**URL:** `{url}`"
    )


@Client.on_message(filters.command("tutorial1") & filters.private)
@admin_only
async def set_tutorial1(client: Client, message: Message):
    """Set tutorial for shortener 1"""
    if len(message.command) < 2:
        await message.reply_text(
            "**📚 Set Tutorial 1**\n\n"
            "**Usage:** `/tutorial1 <tutorial_url>`"
        )
        return
    
    tutorial_url = message.command[1]
    await Database.set_bot_setting("tutorial_1", tutorial_url)
    
    await message.reply_text(f"**✅ Tutorial 1 set to:** `{tutorial_url}`")


@Client.on_message(filters.command("shortlink2") & filters.private)
@admin_only
async def set_shortlink2(client: Client, message: Message):
    """Set shortlink 2"""
    if len(message.command) < 3:
        await message.reply_text(
            "**🔗 Set Shortlink 2**\n\n"
            "**Usage:** `/shortlink2 <api_key> <url>`"
        )
        return
    
    api_key = message.command[1]
    url = message.command[2]
    
    await Database.set_bot_setting("shortener_2_api", api_key)
    await Database.set_bot_setting("shortener_2_url", url)
    
    await message.reply_text(
        f"**✅ Shortlink 2 configured!**\n\n"
        f"**API:** `{api_key}`\n"
        f"**URL:** `{url}`"
    )


@Client.on_message(filters.command("tutorial2") & filters.private)
@admin_only
async def set_tutorial2(client: Client, message: Message):
    """Set tutorial for shortener 2"""
    if len(message.command) < 2:
        await message.reply_text(
            "**📚 Set Tutorial 2**\n\n"
            "**Usage:** `/tutorial2 <tutorial_url>`"
        )
        return
    
    tutorial_url = message.command[1]
    await Database.set_bot_setting("tutorial_2", tutorial_url)
    
    await message.reply_text(f"**✅ Tutorial 2 set to:** `{tutorial_url}`")


@Client.on_message(filters.command("shortner1") & filters.private)
@admin_only
async def view_shortner1(client: Client, message: Message):
    """View shortener 1 config"""
    api = await Database.get_bot_setting("shortener_1_api") or "Not Set"
    url = await Database.get_bot_setting("shortener_1_url") or "Not Set"
    tutorial = await Database.get_bot_setting("tutorial_1") or "Not Set"
    
    text = f"""
**🔗 Shortener 1 Configuration**

**API Key:** `{api}`
**URL:** `{url}`
**Tutorial:** `{tutorial}`
    """
    
    await message.reply_text(text)


@Client.on_message(filters.command("shortner2") & filters.private)
@admin_only
async def view_shortner2(client: Client, message: Message):
    """View shortener 2 config"""
    api = await Database.get_bot_setting("shortener_2_api") or "Not Set"
    url = await Database.get_bot_setting("shortener_2_url") or "Not Set"
    tutorial = await Database.get_bot_setting("tutorial_2") or "Not Set"
    
    text = f"""
**🔗 Shortener 2 Configuration**

**API Key:** `{api}`
**URL:** `{url}`
**Tutorial:** `{tutorial}`
    """
    
    await message.reply_text(text)


@Client.on_message(filters.command("fsub_mode") & filters.private)
@admin_only
async def fsub_mode(client: Client, message: Message):
    """Check force subscribe mode"""
    channels = await Database.get_fsub_channels()
    
    if not channels:
        mode = "Disabled"
    else:
        mode = "Enabled"
    
    text = f"""
**📢 Force Subscribe Mode**

**Status:** `{mode}`
**Total Channels:** `{len(channels)}`

**Mode:** Request mode (users must join to use bot)
    """
    
    await message.reply_text(text)
