#!/bin/bash

echo "🚀 Setting up Letter Counter Agent UI..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 14+ and try again."
    exit 1
fi

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv and try again."
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   Or via pip: pip install uv"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment with uv..."
    uv venv
else
    echo "✅ Virtual environment already exists"
fi

# Install Python dependencies with uv
echo "📦 Installing Python dependencies with uv..."
uv pip install -r requirements.txt

# Navigate to frontend and install Node dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install

# Build the React app
echo "🔨 Building React app..."
npm run build

# Go back to root directory
cd ..

# Check if LANGSMITH_API_KEY is set
if [ -z "$LANGSMITH_API_KEY" ]; then
    echo "⚠️  LANGSMITH_API_KEY environment variable is not set."
    echo "   You can set it with: export LANGSMITH_API_KEY=your_api_key_here"
    echo "   Or continue without authentication (may cause issues)."
fi

# Start the FastAPI server using uv
echo ""
echo "🌟 Starting the application..."
echo "📍 The app will be available at: http://localhost:8000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

uv run python backend/main.py 