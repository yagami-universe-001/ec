# Use lightweight Python base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (FFmpeg, SQLite, etc.)
RUN apt update && apt install -y ffmpeg sqlite3 && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Ensure downloads/uploads/thumbs exist
RUN mkdir -p downloads uploads thumbs

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    DOWNLOAD_DIR=/app/downloads \
    UPLOAD_DIR=/app/uploads \
    THUMB_DIR=/app/thumbs \
    WORKERS=4

# Expose no external port (Telegram bots don't need inbound ports)
# EXPOSE 8000  <-- uncomment only if using webhook mode

# Default command: start bot
CMD ["python", "bot.py"]
