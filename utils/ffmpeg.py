# utils/ffmpeg_helper.py
import os
import asyncio
import re
import time
from typing import Optional, Callable
from utils.config import Config

class FFmpegHelper:
    """Helper class for FFmpeg operations"""
    
    @staticmethod
    async def encode_video(
        input_file: str,
        output_file: str,
        resolution: str,
        codec: str = Config.DEFAULT_CODEC,
        preset: str = Config.DEFAULT_PRESET,
        crf: int = Config.DEFAULT_CRF,
        audio_bitrate: str = Config.DEFAULT_AUDIO_BITRATE,
        watermark_text: str = None,
        watermark_image: str = None,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """Encode video with specified parameters"""
        
        # Resolution mapping
        resolution_map = {
            "144p": "256x144",
            "240p": "426x240",
            "360p": "640x360",
            "480p": "854x480",
            "720p": "1280x720",
            "1080p": "1920x1080",
            "2160p": "3840x2160"
        }
        
        scale = resolution_map.get(resolution, "1280:720")
        
        # Build FFmpeg command
        cmd = [
            "ffmpeg", "-i", input_file,
            "-c:v", codec,
            "-preset", preset,
            "-crf", str(crf),
            "-vf", f"scale={scale}",
            "-c:a", "aac",
            "-b:a", audio_bitrate,
            "-threads", str(Config.FFMPEG_THREADS),
            "-y"
        ]
        
        # Add watermark if specified
        if watermark_text:
            cmd[cmd.index("-vf") + 1] += f",drawtext=text='{watermark_text}':fontsize=24:fontcolor=white:x=10:y=10"
        
        if watermark_image and os.path.exists(watermark_image):
            cmd[cmd.index("-vf") + 1] += f",movie={watermark_image}[watermark];[in][watermark]overlay=10:10[out]"
        
        cmd.append(output_file)
        
        # Get video duration for progress calculation
        duration = await FFmpegHelper.get_duration(input_file)
        
        # Execute FFmpeg
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Monitor progress
        start_time = time.time()
        while True:
            line = await process.stderr.readline()
            if not line:
                break
                
            line = line.decode('utf-8', errors='ignore')
            
            # Extract time progress
            time_match = re.search(r'time=(\d+):(\d+):(\d+\.\d+)', line)
            if time_match and duration and progress_callback:
                hours = int(time_match.group(1))
                minutes = int(time_match.group(2))
                seconds = float(time_match.group(3))
                current_time = hours * 3600 + minutes * 60 + seconds
                
                percentage = (current_time / duration) * 100
                elapsed = time.time() - start_time
                
                if elapsed > 0:
                    speed = current_time / elapsed
                    eta = (duration - current_time) / speed if speed > 0 else 0
                    
                    await progress_callback(
                        percentage=min(percentage, 100),
                        speed=speed,
                        eta=eta,
                        current=current_time,
                        total=duration
                    )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def get_duration(file_path: str) -> Optional[float]:
        """Get video duration in seconds"""
        cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        try:
            return float(stdout.decode().strip())
        except:
            return None
    
    @staticmethod
    async def get_video_info(file_path: str) -> dict:
        """Get video information"""
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            file_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        
        try:
            import json
            info = json.loads(stdout.decode())
            
            video_stream = next((s for s in info.get('streams', []) if s['codec_type'] == 'video'), None)
            audio_stream = next((s for s in info.get('streams', []) if s['codec_type'] == 'audio'), None)
            format_info = info.get('format', {})
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bitrate': int(format_info.get('bit_rate', 0)),
                'width': int(video_stream.get('width', 0)) if video_stream else 0,
                'height': int(video_stream.get('height', 0)) if video_stream else 0,
                'video_codec': video_stream.get('codec_name', 'unknown') if video_stream else 'none',
                'audio_codec': audio_stream.get('codec_name', 'unknown') if audio_stream else 'none',
                'fps': eval(video_stream.get('r_frame_rate', '0/1')) if video_stream else 0
            }
        except:
            return {}
    
    @staticmethod
    async def extract_thumbnail(video_path: str, output_path: str, time: str = "00:00:01") -> bool:
        """Extract thumbnail from video"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", time,
            "-vframes", "1",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def extract_audio(video_path: str, output_path: str) -> bool:
        """Extract audio from video"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vn", "-acodec", "copy",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def extract_subtitles(video_path: str, output_path: str) -> bool:
        """Extract subtitles from video"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-map", "0:s:0",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def add_subtitle(video_path: str, subtitle_path: str, output_path: str, hard: bool = False) -> bool:
        """Add subtitle to video (soft or hard)"""
        if hard:
            cmd = [
                "ffmpeg", "-i", video_path,
                "-vf", f"subtitles={subtitle_path}",
                "-c:a", "copy",
                "-y", output_path
            ]
        else:
            cmd = [
                "ffmpeg", "-i", video_path,
                "-i", subtitle_path,
                "-c", "copy",
                "-c:s", "mov_text",
                "-y", output_path
            ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def remove_subtitle(video_path: str, output_path: str) -> bool:
        """Remove all subtitles from video"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-c", "copy", "-sn",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def add_audio(video_path: str, audio_path: str, output_path: str) -> bool:
        """Add audio to video"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def remove_audio(video_path: str, output_path: str) -> bool:
        """Remove audio from video"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-c:v", "copy", "-an",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def trim_video(video_path: str, output_path: str, start_time: str, end_time: str) -> bool:
        """Trim video by time"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-ss", start_time,
            "-to", end_time,
            "-c", "copy",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def crop_video(video_path: str, output_path: str, aspect_ratio: str) -> bool:
        """Crop video to aspect ratio"""
        aspect_map = {
            "16:9": "crop=ih*16/9:ih",
            "9:16": "crop=iw:iw*16/9",
            "1:1": "crop=min(iw\\,ih):min(iw\\,ih)",
            "4:3": "crop=ih*4/3:ih"
        }
        
        crop_filter = aspect_map.get(aspect_ratio, "crop=ih*16/9:ih")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", crop_filter,
            "-c:a", "copy",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
    
    @staticmethod
    async def merge_videos(video_files: list, output_path: str) -> bool:
        """Merge multiple videos"""
        # Create concat file
        concat_file = "concat_list.txt"
        with open(concat_file, 'w') as f:
            for video in video_files:
                f.write(f"file '{video}'\n")
        
        cmd = [
            "ffmpeg", "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        
        # Clean up
        if os.path.exists(concat_file):
            os.remove(concat_file)
        
        return process.returncode == 0
    
    @staticmethod
    async def compress_video(video_path: str, output_path: str, crf: int = 35) -> bool:
        """Compress video with higher CRF"""
        cmd = [
            "ffmpeg", "-i", video_path,
            "-c:v", "libx264",
            "-crf", str(crf),
            "-c:a", "aac",
            "-b:a", "96k",
            "-y", output_path
        ]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL
        )
        
        await process.wait()
        return process.returncode == 0
