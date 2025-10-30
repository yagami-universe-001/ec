# utils/progress.py
import time
import math
import psutil
from utils.helpers import format_size, format_time

class ProgressTracker:
    """Professional progress tracking with animated loading bars"""
    
    # Different animated loading bar styles
    ANIMATIONS = {
        'dots': ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'],
        'line': ['|', '/', '-', '\\'],
        'arrow': ['←', '↖', '↑', '↗', '→', '↘', '↓', '↙'],
        'bounce': ['⠁', '⠂', '⠄', '⠂'],
        'blocks': ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█', '▇', '▆', '▅', '▄', '▃', '▂'],
        'circle': ['◐', '◓', '◑', '◒'],
        'square': ['◰', '◳', '◲', '◱'],
        'triangle': ['◢', '◣', '◤', '◥'],
    }
    
    animation_index = 0
    animation_style = 'dots'
    
    @staticmethod
    def get_animated_loader(style='dots'):
        """Get animated loading character"""
        frames = ProgressTracker.ANIMATIONS.get(style, ProgressTracker.ANIMATIONS['dots'])
        ProgressTracker.animation_index = (ProgressTracker.animation_index + 1) % len(frames)
        return frames[ProgressTracker.animation_index]
    
    @staticmethod
    def get_progress_bar(percentage, length=10, style='filled'):
        """Create professional progress bar with different styles"""
        filled = int(length * percentage / 100)
        empty = length - filled
        
        if style == 'filled':
            # ●●●●●○○○○○
            bar = "●" * filled + "○" * empty
        elif style == 'blocks':
            # ████████░░
            bar = "█" * filled + "░" * empty
        elif style == 'squares':
            # ■■■■■□□□□□
            bar = "■" * filled + "□" * empty
        elif style == 'arrows':
            # ►►►►►►▻▻▻▻
            bar = "►" * filled + "▻" * empty
        elif style == 'circles':
            # ◉◉◉◉◉○○○○○
            bar = "◉" * filled + "○" * empty
        elif style == 'dots':
            # ⬤⬤⬤⬤⬤○○○○○
            bar = "⬤" * filled + "○" * empty
        elif style == 'gradient':
            # ▰▰▰▰▰▱▱▱▱▱
            bar = "▰" * filled + "▱" * empty
        elif style == 'modern':
            # ━━━━━╾╌╌╌╌
            if filled > 0:
                bar = "━" * (filled - 1) + "╾" + "╌" * empty if filled < length else "━" * length
            else:
                bar = "╾" + "╌" * (empty - 1) if empty > 0 else ""
        else:
            bar = "●" * filled + "○" * empty
        
        return f"[ {bar} ]"
    
    @staticmethod
    def get_percentage_bar(percentage, width=20):
        """Create a visual percentage bar █████░░░░░ 50%"""
        filled = int(width * percentage / 100)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percentage:.1f}%"
    
    @staticmethod
    def get_bot_stats():
        """Get current bot statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            ram_percent = psutil.virtual_memory().percent
            uptime = time.time() - psutil.boot_time()
            disk = psutil.disk_usage('/')
            
            uptime_hours = int(uptime // 3600)
            uptime_mins = int((uptime % 3600) // 60)
            uptime_secs = int(uptime % 60)
            
            return {
                'cpu': cpu_percent,
                'ram': ram_percent,
                'uptime': f"{uptime_hours}h {uptime_mins}m {uptime_secs}s",
                'disk': f"{disk.free // (1024**3)} GB"
            }
        except:
            return {
                'cpu': 0,
                'ram': 0,
                'uptime': "0h 0m 0s",
                'disk': "0 GB"
            }
    
    @staticmethod
    async def download_progress(current, total, message, file_name, user_name, user_id, start_time):
        """Professional download progress display with animation"""
        try:
            percentage = (current / total) * 100
            speed = current / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            elapsed = time.time() - start_time
            
            # Get animated loader
            loader = ProgressTracker.get_animated_loader('dots')
            
            # Get progress bar with modern style
            progress_bar = ProgressTracker.get_progress_bar(percentage, 10, 'modern')
            
            # Get percentage bar
            percent_bar = ProgressTracker.get_percentage_bar(percentage, 15)
            
            bot_stats = ProgressTracker.get_bot_stats()
            
            # Only update every 3 seconds to avoid flood
            if hasattr(download_progress, 'last_update'):
                if time.time() - download_progress.last_update < 3:
                    return
            download_progress.last_update = time.time()
            
            text = f"""**{loader} 1. Downloading**

┃ `{file_name[:50]}{'...' if len(file_name) > 50 else ''}`

{progress_bar} >> {percentage:.1f}%
{percent_bar}
├ Speed: {format_size(int(speed))}/s
├ Downloaded: {format_size(current)} / {format_size(total)}
├ ETA: {format_time(int(eta))}
├ Elapsed: {format_time(int(elapsed))}
├ Task By: {user_name}
└ User ID: `{user_id}`

**📊 Bot Stats**
┣ CPU: {bot_stats['cpu']:.1f}%
┣ RAM: {bot_stats['ram']:.1f}%
┣ UPTIME: {bot_stats['uptime']}
┗ FREE: {bot_stats['disk']}

━━━━━━━━━━━━━━━━━━━━
Page: 1/1 | Active Tasks: 1"""
            
            await message.edit_text(text)
        except Exception as e:
            pass
    
    @staticmethod
    async def upload_progress(current, total, message, file_name, user_name, user_id, start_time):
        """Professional upload progress display with animation"""
        try:
            percentage = (current / total) * 100
            speed = current / (time.time() - start_time) if (time.time() - start_time) > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            elapsed = time.time() - start_time
            
            # Get animated loader
            loader = ProgressTracker.get_animated_loader('arrow')
            
            # Get progress bar with blocks style
            progress_bar = ProgressTracker.get_progress_bar(percentage, 10, 'blocks')
            
            # Get percentage bar
            percent_bar = ProgressTracker.get_percentage_bar(percentage, 15)
            
            bot_stats = ProgressTracker.get_bot_stats()
            
            # Only update every 3 seconds
            if hasattr(upload_progress, 'last_update'):
                if time.time() - upload_progress.last_update < 3:
                    return
            upload_progress.last_update = time.time()
            
            text = f"""**{loader} 3. Uploading**

┃ `{file_name[:50]}{'...' if len(file_name) > 50 else ''}`

{progress_bar} >> {percentage:.1f}%
{percent_bar}
├ Speed: {format_size(int(speed))}/s
├ Uploaded: {format_size(current)} / {format_size(total)}
├ ETA: {format_time(int(eta))}
├ Elapsed: {format_time(int(elapsed))}
├ Task By: {user_name}
└ User ID: `{user_id}`

**📊 Bot Stats**
┣ CPU: {bot_stats['cpu']:.1f}%
┣ RAM: {bot_stats['ram']:.1f}%
┣ UPTIME: {bot_stats['uptime']}
┗ FREE: {bot_stats['disk']}

━━━━━━━━━━━━━━━━━━━━
Page: 1/1 | Active Tasks: 1"""
            
            await message.edit_text(text)
        except Exception as e:
            pass
    
    @staticmethod
    async def encoding_progress(percentage, speed, eta, current, total, message, file_name, quality, user_name, user_id, start_time):
        """Professional encoding progress display with animation"""
        try:
            elapsed = time.time() - start_time
            
            # Get animated loader
            loader = ProgressTracker.get_animated_loader('blocks')
            
            # Get progress bar with gradient style
            progress_bar = ProgressTracker.get_progress_bar(percentage, 10, 'gradient')
            
            # Get percentage bar
            percent_bar = ProgressTracker.get_percentage_bar(percentage, 15)
            
            bot_stats = ProgressTracker.get_bot_stats()
            
            text = f"""**{loader} 2. Encoding to {quality.upper()}**

┃ `{file_name[:50]}{'...' if len(file_name) > 50 else ''}`

{progress_bar} >> {percentage:.1f}%
{percent_bar}
├ Speed: {speed:.2f}x
├ Time: {format_time(int(current))} / {format_time(int(total))}
├ ETA: {format_time(int(eta))}
├ Elapsed: {format_time(int(elapsed))}
├ Task By: {user_name}
└ User ID: `{user_id}`

**📊 Bot Stats**
┣ CPU: {bot_stats['cpu']:.1f}%
┣ RAM: {bot_stats['ram']:.1f}%
┣ UPTIME: {bot_stats['uptime']}
┗ FREE: {bot_stats['disk']}

━━━━━━━━━━━━━━━━━━━━
Page: 1/1 | Active Tasks: 1"""
            
            await message.edit_text(text)
        except Exception as e:
            pass
    
    @staticmethod
    async def processing_progress(message, step, file_name, user_name, user_id, description="Processing..."):
        """Generic processing progress with animation"""
        try:
            loader = ProgressTracker.get_animated_loader('circle')
            bot_stats = ProgressTracker.get_bot_stats()
            
            text = f"""**{loader} {step}. Processing**

┃ `{file_name[:50]}{'...' if len(file_name) > 50 else ''}`

⏳ {description}

├ Task By: {user_name}
└ User ID: `{user_id}`

**📊 Bot Stats**
┣ CPU: {bot_stats['cpu']:.1f}%
┣ RAM: {bot_stats['ram']:.1f}%
┣ UPTIME: {bot_stats['uptime']}
┗ FREE: {bot_stats['disk']}

━━━━━━━━━━━━━━━━━━━━
Page: 1/1 | Active Tasks: 1"""
            
            await message.edit_text(text)
        except Exception as e:
            pass
    
    @staticmethod
    def get_speed_indicator(speed_mbps):
        """Get visual speed indicator"""
        if speed_mbps < 1:
            return "🐌 Slow"
        elif speed_mbps < 5:
            return "🚶 Normal"
        elif speed_mbps < 10:
            return "🏃 Fast"
        elif speed_mbps < 20:
            return "🚀 Very Fast"
        else:
            return "⚡ Ultra Fast"
    
    @staticmethod
    def get_eta_indicator(eta_seconds):
        """Get visual ETA indicator"""
        if eta_seconds < 60:
            return "⚡ Almost done"
        elif eta_seconds < 300:
            return "🕐 Few minutes"
        elif eta_seconds < 900:
            return "🕒 Quarter hour"
        elif eta_seconds < 1800:
            return "🕓 Half hour"
        else:
            return "🕔 Long wait"
    
    @staticmethod
    async def show_completion(message, file_name, user_name, file_size, duration=None):
        """Show completion message with stats"""
        try:
            bot_stats = ProgressTracker.get_bot_stats()
            
            text = f"""**✅ Processing Complete!**

┃ `{file_name[:50]}{'...' if len(file_name) > 50 else ''}`

━━━━━━━━━━━━━━━━━━━━
📦 Size: {format_size(file_size)}
"""
            
            if duration:
                text += f"⏱ Duration: {format_time(int(duration))}\n"
            
            text += f"""━━━━━━━━━━━━━━━━━━━━

👤 Processed For: {user_name}

**📊 Bot Stats**
┣ CPU: {bot_stats['cpu']:.1f}%
┣ RAM: {bot_stats['ram']:.1f}%
┣ UPTIME: {bot_stats['uptime']}
┗ FREE: {bot_stats['disk']}"""
            
            await message.edit_text(text)
        except Exception as e:
            pass
