#!/bin/bash
# Frontend Environment Setup Script
# This script sets up the Node.js environment for the frontend

set -e  # Exit on any error

echo "🚀 Setting up Mistral AI Chat Frontend Environment..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org"
    echo "  macOS: brew install node"
    echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi

# Check Node.js version
node_version=$(node --version | sed 's/v//')
major_version=$(echo $node_version | cut -d. -f1)

if [ "$major_version" -lt 18 ]; then
    echo "❌ Error: Node.js 18+ is required. Found Node.js $node_version"
    echo "Please upgrade Node.js to version 18 or later"
    exit 1
fi

echo "✅ Node.js $node_version found"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not available"
    exit 1
fi

echo "✅ npm $(npm --version) found"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Set up environment file
if [ ! -f ".env.local" ]; then
    echo "⚙️ Setting up environment file..."
    cp .env.example .env.local
    echo "✅ Created .env.local from .env.example"
    echo "Please edit .env.local with your configuration"
else
    echo "✅ Environment file already exists"
fi

echo "🎉 Frontend environment setup complete!"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "The app will be available at:"
echo "  http://localhost:3000"
echo ""
echo "Other available commands:"
echo "  npm run build    - Build for production"
echo "  npm run lint     - Run ESLint"
echo "  npm run format   - Format code with Prettier"
