#!/bin/bash

# AI Pamphlet Generator Setup Script
# This script sets up the complete environment for the AI Pamphlet Generator

echo "🤖 AI Pamphlet Generator Setup"
echo "================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip first."
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Python dependencies installed successfully"
else
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
    
    if [ $? -eq 0 ]; then
        echo "✅ Ollama installed successfully"
    else
        echo "❌ Failed to install Ollama"
        exit 1
    fi
else
    echo "✅ Ollama is already installed"
fi

# Start Ollama service
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama failed to start"
    exit 1
fi

# Pull the recommended model
echo "📥 Downloading Llama 3.2 model (this may take a while)..."
ollama pull llama3.2

if [ $? -eq 0 ]; then
    echo "✅ Llama 3.2 model downloaded successfully"
else
    echo "❌ Failed to download Llama 3.2 model"
    exit 1
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p templates static

# Set up environment file
echo "🔧 Setting up environment configuration..."
cat > .env << EOF
# AI Pamphlet Generator Configuration
STABILITY_API_KEY=your_stability_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
FLASK_ENV=development
FLASK_DEBUG=1
EOF

echo "✅ Environment file created (.env)"

# Make app.py executable
chmod +x app.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Get your Stability AI API key from: https://platform.stability.ai/"
echo "2. Update the API key in app.py or .env file"
echo "3. Run the application: python3 app.py"
echo "4. Open your browser to: http://localhost:5000"
echo ""
echo "🔧 Configuration files:"
echo "- app.py: Main application and API key"
echo "- .env: Environment variables"
echo "- pamphlet_agent.py: AI agent configuration"
echo ""
echo "📚 For more information, see README.md"
echo ""
echo "🚀 To start the application now, run: python3 app.py"
