#!/bin/bash

# Quick fix for database and directory permissions

echo "🔧 Fixing permissions and directories..."

# Get current user
CURRENT_USER=$(whoami)

# Create directories with proper permissions
mkdir -p downloads uploads thumbs logs
chmod 755 downloads uploads thumbs logs

# Fix ownership
chown -R $CURRENT_USER:$CURRENT_USER downloads uploads thumbs logs

# If database file exists, fix its permissions
if [ -f "bot_database.db" ]; then
    chmod 644 bot_database.db
    chown $CURRENT_USER:$CURRENT_USER bot_database.db
    echo "✅ Fixed database file permissions"
fi

# Fix bot file permissions
chmod +x bot.py
chmod 644 requirements.txt

# Fix directory permissions
chmod 755 handlers utils

echo "✅ Permissions fixed!"
echo ""
echo "Now try running: python3 bot.py"
