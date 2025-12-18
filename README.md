# 🤖 AI Pamphlet Generator

An advanced agentic AI system that combines **Ollama** for intelligent text generation and **Stable Diffusion** for stunning image creation to generate professional product pamphlets automatically.

## ✨ Features

- **🧠 Agentic Pipeline**: Coordinated text, imagery, and layout generation in a single flow
- **📝 Ollama Integration**: Prompt variations keep every regeneration fresh and on-brand
- **🎨 Stable Diffusion**: High-quality backgrounds with whitespace carved out for typography
- **🎯 Smart Layout Engine**: Structured panels, balanced typography, and feature lists with auto wrapping
- **🛠️ Editing Suite**: Post-generation controls for layout, fonts, colors, filters, cropping, and effects
- **♻️ Regeneration Remix**: Each regenerate mixes layout, copy, and imagery for rapid exploration
- **🌐 Web Interface**: Beautiful, responsive web UI with instant preview and edit saving
- **📱 Mobile Friendly**: Works perfectly on all devices with touch-friendly controls
- **⚡ Real-time Generation**: Live preview and instant downloads

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running
3. **Stability AI API Key** (for image generation)

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd "/Users/archijain/Desktop/pbl5 2"
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and setup Ollama:**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull the recommended model
   ollama pull llama3.2
   
   # Start Ollama server
   ollama serve
   ```

4. **Get Stability AI API Key:**
   - Visit [Stability AI](https://platform.stability.ai/)
   - Sign up and get your API key
   - Update the API key in `app.py`:
     ```python
     STABILITY_API_KEY = "your_actual_api_key_here"
     ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Open your browser:**
   Navigate to `http://localhost:5002`

## 🎯 How to Use

1. **Fill in the form:**
   - Product Name: Enter your product name
   - Description: Describe your product in detail
   - Tone: Choose the communication style
   - Target Audience: Define your ideal customers
   - Key Features: Add important product features
   - Call to Action: Create compelling action text

2. **Customize design:**
   - Choose color scheme (Modern, Elegant, Minimal)
   - Select style (Professional, Creative, Minimalist, Vintage)

3. **Generate & iterate:**
   - Click "Generate Pamphlet" and watch the AI agents work their magic
   - Use the editing tabs (Layout, Text, Image, Effects) to fine-tune the design
   - Click "Regenerate" any time for an automatically remixed layout, copy, and background
   - Save edits and download the polished pamphlet

## 🏗️ Architecture

### AI Agent System
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Interface │───▶│  Flask Backend   │───▶│  AI Agent       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │  Ollama Text     │    │ Stable Diffusion│
                       │  Generator       │    │ Image Generator │
                       └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
                                                ┌─────────────────┐
                                                │ Pamphlet        │
                                                │ Designer        │
                                                └─────────────────┘
```

### Components

1. **PamphletAgent**: Main orchestrator that coordinates all components
2. **OllamaTextGenerator**: Handles intelligent text generation
3. **StableDiffusionGenerator**: Manages image creation
4. **PamphletDesigner**: Creates final visual layout
5. **Flask Web App**: Provides user interface and API

## 🔧 Configuration

### Ollama Models
You can use different Ollama models by modifying the model parameter:
```python
agent = PamphletAgent(STABILITY_API_KEY, ollama_model="llama3.2")
```

Available models:
- `llama3.2` (recommended)
- `llama3.1`
- `mistral`
- `codellama`

### API Configuration
Update API settings in `app.py`:
```python
# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"

# Stability AI configuration
STABILITY_API_KEY = "your_api_key_here"
```

## 📁 Project Structure

```
pbl5 2/
├── pamphlet_agent.py      # Main AI agent and components
├── app.py                 # Flask web application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   └── index.html        # Web interface template
└── static/
    ├── style.css         # Styling
    └── script.js         # Frontend JavaScript
```

## 🎨 Customization

### Adding New Color Schemes
Edit the `_get_color_scheme` method in `PamphletDesigner` class (and optionally tweak `_build_design_config` for custom font sizes, shadows, or panel opacity):

```python
def _get_color_scheme(self, scheme: str) -> Dict[str, Tuple[int, int, int]]:
    schemes = {
        'your_scheme': {
            'text': (255, 255, 255),
            'accent': (100, 200, 255),
            'cta': (255, 100, 100),
            'overlay': (0, 0, 0)
        }
    }
    return schemes.get(scheme, schemes['modern'])
```

### Modifying Text Generation
Update prompts in `OllamaTextGenerator` class methods:
- `generate_pamphlet_text()`
- `_call_ollama()`

## 🐛 Troubleshooting

### Common Issues

1. **Ollama not responding:**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   
   # Restart Ollama
   ollama serve
   ```

2. **Stability AI API errors:**
   - Verify your API key is correct
   - Check your API quota and billing
   - Ensure you have the right permissions

3. **Image generation fails:**
   - Check internet connection
   - Verify API key is valid
   - Try with a simpler prompt

4. **Text generation issues:**
   - Ensure Ollama is running
   - Check if the model is downloaded: `ollama list`
   - Try a different model

### Debug Mode
Run with debug logging:
```bash
export FLASK_DEBUG=1
python app.py
```

## 🚀 Advanced Usage

### API Endpoints

- `GET /` - Main interface
- `POST /generate` - Generate pamphlet
- `GET /download/<filename>` - Download generated pamphlet
- `GET /health` - Health check

### Programmatic Usage

```python
from pamphlet_agent import PamphletAgent, PamphletRequest

# Create agent
agent = PamphletAgent("your_api_key")

# Create request
request = PamphletRequest(
    product_name="My Product",
    description="Amazing product description",
    tone="professional",
    target_audience="professionals",
    key_features=["Feature 1", "Feature 2"],
    call_to_action="Buy now!"
)

# Generate pamphlet
result = agent.generate_pamphlet(request)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Ollama** for powerful local LLM capabilities
- **Stability AI** for high-quality image generation
- **Flask** for the web framework
- **PIL/Pillow** for image processing

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue with detailed information

---

**Happy Pamphlet Generating! 🎉**
=======
# AdGenie-AI-Driven-Advertisement-Generator
AdGenie is an AI-powered system that automatically creates complete advertisements — including text ad copy, poster images, using just basic product details like name, target audience, and tone. It is designed especially to help small and medium businesses create professional, creative, and personalized ads effortlessly using Generative AI
>>>>>>> a9f002c8bbaa8a281cd1d9b8673b3d1ad6983f2a
