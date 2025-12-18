# 🔑 How to Add Your Stability AI API Key

## Step 1: Get Your API Key
1. Visit [Stability AI Platform](https://platform.stability.ai/)
2. Sign up for a free account
3. Go to your account settings
4. Generate a new API key
5. Copy the API key

## Step 2: Add API Key to the Project
1. Open `app.py` in your code editor
2. Find this line (around line 16):
   ```python
   STABILITY_API_KEY = "your_stability_api_key_here"
   ```
3. Replace `"your_stability_api_key_here"` with your actual API key:
   ```python
   STABILITY_API_KEY = "sk-your-actual-api-key-here"
   ```
4. Save the file

## Step 3: Restart the Application
1. Stop the current server (Ctrl+C)
2. Restart the application:
   ```bash
   source venv/bin/activate
   python3 app.py
   ```

## ✅ That's It!
Your AI Pamphlet Generator will now create beautiful pamphlets with both text and images!

## 🎯 What You'll Get
- **AI-Generated Text**: Compelling headlines, descriptions, and CTAs
- **AI-Generated Images**: Professional background images based on your product
- **Professional Layout**: Centered text, proper spacing, and visual hierarchy
- **Download Ready**: High-quality PNG files perfect for printing

## 💡 Pro Tips
- The system automatically detects product types (food, tech, beauty) and generates appropriate images
- Try different color schemes and styles for variety
- The AI creates content optimized for pamphlet layout (short, punchy text)
