# 🚀 Quick Start Guide

## Get Started in 5 Minutes!

### 1. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### 2. Setup Ollama
```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama
ollama serve &

# Download model
ollama pull llama3.2
```

### 3. Get API Key
- Visit [Stability AI](https://platform.stability.ai/)
- Sign up and get your free API key
- Update `app.py` with your key:
```python
STABILITY_API_KEY = "your_actual_api_key_here"
```

### 4. Run the Application
```bash
# Activate virtual environment
source venv/bin/activate

# Start the app
python3 app.py
```

### 5. Open Your Browser
Go to: `http://localhost:5000`

## 🎯 What You Get

- **Beautiful Web Interface**: Modern, responsive design
- **AI-Powered Text**: Intelligent content generation with Ollama
- **Stunning Images**: High-quality visuals with Stable Diffusion
- **Professional Layout**: Automatic pamphlet design
- **Instant Download**: Get your pamphlet immediately

## 🧪 Test Everything Works

```bash
# Run the test script
python3 test_integration.py
```

## 🎮 Try the Demo

```bash
# Interactive demo
python3 demo.py
```

## 📁 Generated Files

Your pamphlets will be saved as:
- `pamphlet_[product_name].png`

## 🔧 Troubleshooting

**Ollama not working?**
```bash
ollama serve
ollama list  # Check if llama3.2 is there
```

**API errors?**
- Check your Stability AI API key
- Verify you have credits/quota

**Import errors?**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🎉 You're Ready!

Your AI Pamphlet Generator is now running! Create amazing pamphlets with just a few clicks.
