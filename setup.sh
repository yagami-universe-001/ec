#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Telegram Video Encoder Bot Setup        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo -e "${YELLOW}⚠️  Warning: Running as root is not recommended${NC}"
    echo -e "${YELLOW}   Consider running as a regular user${NC}"
    echo ""
fi

# Step 1: Check Python version
echo -e "${YELLOW}[1/8]${NC} Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ -z "$PYTHON_VERSION" ]; then
    echo -e "${RED}❌ Python 3 is not installed!${NC}"
    echo -e "${YELLOW}   Install Python 3.8 or higher:${NC}"
    echo -e "   sudo apt update && sudo apt install python3 python3-pip -y"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION found${NC}"
echo ""

# Step 2: Check FFmpeg
echo -e "${YELLOW}[2/8]${NC} Checking FFmpeg installation..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_VERSION=$(ffmpeg -version 2>&1 | head -n 1)
    echo -e "${GREEN}✅ FFmpeg installed: $FFMPEG_VERSION${NC}"
else
    echo -e "${RED}❌ FFmpeg is not installed!${NC}"
    echo -e "${YELLOW}   Install FFmpeg:${NC}"
    echo -e "   sudo apt update && sudo apt install ffmpeg -y"
    exit 1
fi
echo ""

# Step 3: Create directories
echo -e "${YELLOW}[3/8]${NC} Creating necessary directories..."
mkdir -p downloads uploads thumbs logs
chmod 755 downloads uploads thumbs logs
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Step 4: Check .env file
echo -e "${YELLOW}[4/8]${NC} Checking configuration..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}   Copying .env.example to .env...${NC}"
        cp .env.example .env
        echo -e "${GREEN}✅ .env file created${NC}"
        echo -e "${YELLOW}   Please edit .env and add your credentials:${NC}"
        echo -e "   nano .env"
    else
        echo -e "${RED}❌ .env.example not found!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ .env file exists${NC}"
fi
echo ""

# Step 5: Check virtual environment
echo -e "${YELLOW}[5/8]${NC} Checking Python virtual environment..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}   Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment exists${NC}"
fi
echo ""

# Step 6: Install dependencies
echo -e "${YELLOW}[6/8]${NC} Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Dependencies installed successfully${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    exit 1
fi
echo ""

# Step 7: Fix permissions
echo -e "${YELLOW}[7/8]${NC} Setting correct permissions..."
chmod +x bot.py
chmod 644 requirements.txt
chmod 644 .env 2>/dev/null
chmod 755 handlers utils
echo -e "${GREEN}✅ Permissions set${NC}"
echo ""

# Step 8: Test configuration
echo -e "${YELLOW}[8/8]${NC} Testing configuration..."

# Check if required env vars are set
source .env 2>/dev/null

if [ -z "$API_ID" ] || [ "$API_ID" == "your_api_id_here" ]; then
    echo -e "${RED}❌ API_ID not configured in .env${NC}"
    NEEDS_CONFIG=1
fi

if [ -z "$API_HASH" ] || [ "$API_HASH" == "your_api_hash_here" ]; then
    echo -e "${RED}❌ API_HASH not configured in .env${NC}"
    NEEDS_CONFIG=1
fi

if [ -z "$BOT_TOKEN" ] || [ "$BOT_TOKEN" == "your_bot_token_here" ]; then
    echo -e "${RED}❌ BOT_TOKEN not configured in .env${NC}"
    NEEDS_CONFIG=1
fi

if [ ! -z "$NEEDS_CONFIG" ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Please configure your .env file:${NC}"
    echo -e "   nano .env"
    echo ""
    echo -e "${YELLOW}   Required variables:${NC}"
    echo -e "   • API_ID - Get from https://my.telegram.org"
    echo -e "   • API_HASH - Get from https://my.telegram.org"
    echo -e "   • BOT_TOKEN - Get from @BotFather"
    echo -e "   • ADMIN_IDS - Your Telegram user ID"
    echo ""
    exit 1
fi

echo -e "${GREEN}✅ Configuration looks good${NC}"
echo ""

# Final summary
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Setup Complete! 🎉                ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Edit .env if you haven't already:"
echo -e "   ${GREEN}nano .env${NC}"
echo ""
echo -e "2. Start the bot:"
echo -e "   ${GREEN}python3 bot.py${NC}"
echo ""
echo -e "   Or use systemd service:"
echo -e "   ${GREEN}sudo systemctl start encoder-bot${NC}"
echo ""
echo -e "${YELLOW}Useful commands:${NC}"
echo -e "• View logs: ${GREEN}tail -f bot.log${NC}"
echo -e "• Stop bot: ${GREEN}Ctrl+C${NC} (if running in terminal)"
echo -e "• Check status: ${GREEN}ps aux | grep bot.py${NC}"
echo ""
