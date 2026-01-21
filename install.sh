#!/bin/bash

# Installation script for Chisom.ai
set -e

echo "🚀 Installing Chisom.ai..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.11"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ Python 3.11+ required. Found: $python_version${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $python_version${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python3 -m venv venv
echo -e "${GREEN}✅ Virtual environment created${NC}"

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip setuptools wheel

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "requirements-minimal.txt" ]; then
    pip install -r requirements-minimal.txt
else
    echo -e "${RED}❌ No requirements file found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python dependencies installed${NC}"

# Check Node.js
echo -e "${YELLOW}Checking Node.js...${NC}"
if command -v node &> /dev/null; then
    node_version=$(node --version)
    echo -e "${GREEN}✅ Node.js $node_version${NC}"
    
    # Install Node tools
    echo -e "${YELLOW}Installing Node.js tools...${NC}"
    npm install -g eslint prettier
    echo -e "${GREEN}✅ Node.js tools installed${NC}"
else
    echo -e "${YELLOW}⚠️  Node.js not found. Skipping ESLint/Prettier${NC}"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created. Please edit it with your credentials.${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p chroma_db logs tests

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Installation completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python cli.py init"
echo "4. Run: python cli.py create-user"
echo "5. Run: chainlit run app.py"
echo ""
