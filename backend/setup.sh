#!/bin/bash
# Backend Virtual Environment Setup Script
# This script creates and configures a Python virtual environment for the backend

set -e  # Exit on any error

echo "🚀 Setting up Mistral AI Chat Backend Environment..."

# Check if Python 3.11+ is available
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
major_version=$(echo $python_version | cut -d. -f1)
minor_version=$(echo $python_version | cut -d. -f2)

if [ "$major_version" -lt 3 ] || ([ "$major_version" -eq 3 ] && [ "$minor_version" -lt 11 ]); then
    echo "❌ Error: Python 3.11+ is required. Found Python $python_version"
    echo "Please install Python 3.11 or later:"
    echo "  macOS: brew install python@3.11"
    echo "  Ubuntu: sudo apt install python3.11 python3.11-venv"
    exit 1
fi

echo "✅ Python $python_version found"

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists. Removing old one..."
    rm -rf venv
fi

python3 -m venv venv
echo "✅ Virtual environment created"

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo "🎉 Backend environment setup complete!"
echo ""
echo "To activate the environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the development server:"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "To deactivate the environment:"
echo "  deactivate"
