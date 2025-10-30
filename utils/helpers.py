# utils/helpers.py
import math
import time
from typing import Union

def format_size(bytes: int) -> str:
    """Format bytes to human readable size"""
    if bytes == 0:
        return "0 B"
    
    size_names = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    
    return f"{s} {size_names[i]}"


def format_time(seconds: Union[int, float]) -> str:
    """Format seconds to human readable time"""
    if seconds == 0:
        return "0s"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def format_progress_bar(percentage: float, length: int = 10) -> str:
    """Create a progress bar"""
    filled = int(length * percentage / 100)
    empty = length - filled
    
    bar = "●" * filled + "○" * empty
    return f"[{bar}]"


def time_formatter(milliseconds: int) -> str:
    """Format milliseconds to readable time"""
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    tmp = (
        (f"{days}d " if days else "")
        + (f"{hours}h " if hours else "")
        + (f"{minutes}m " if minutes else "")
        + (f"{seconds}s" if seconds else "")
    )
    
    return tmp or "0s"


def get_readable_time(seconds: int) -> str:
    """Get readable time from seconds"""
    result = ""
    (days, remainder) = divmod(seconds, 86400)
    days = int(days)
    
    if days != 0:
        result += f"{days}d"
    
    (hours, remainder) = divmod(remainder, 3600)
    hours = int(hours)
    
    if hours != 0:
        result += f"{hours}h"
    
    (minutes, seconds) = divmod(remainder, 60)
    minutes = int(minutes)
    seconds = int(seconds)
    
    if minutes != 0:
        result += f"{minutes}m"
    
    if seconds != 0:
        result += f"{seconds}s"
    
    return result or "0s"


def calculate_eta(current: int, total: int, start_time: float) -> str:
    """Calculate estimated time of arrival"""
    if current == 0:
        return "Calculating..."
    
    elapsed_time = time.time() - start_time
    rate = current / elapsed_time
    
    if rate == 0:
        return "Unknown"
    
    remaining = (total - current) / rate
    return get_readable_time(int(remaining))


def parse_time(time_str: str) -> int:
    """Parse time string to seconds"""
    try:
        parts = time_str.split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(s)
        elif len(parts) == 2:
            m, s = parts
            return int(m) * 60 + int(s)
        else:
            return int(parts[0])
    except:
        return 0


def format_seconds_to_hhmmss(seconds: int) -> str:
    """Format seconds to HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def clean_filename(filename: str) -> str:
    """Clean filename from invalid characters"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return filename.split('.')[-1] if '.' in filename else ''


def change_filename(filename: str, new_name: str) -> str:
    """Change filename keeping extension"""
    ext = get_file_extension(filename)
    return f"{new_name}.{ext}" if ext else new_name
