#!/usr/bin/env python3
"""
Test script for AI Pamphlet Generator
Tests the integration between Ollama and Stable Diffusion
"""

import requests
import json
import time
from pamphlet_agent import PamphletAgent, PamphletRequest

def test_ollama_connection():
    """Test if Ollama is running and accessible"""
    print("🔍 Testing Ollama connection...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"✅ Ollama is running with {len(models)} models")
            
            # Check if llama3.2 is available
            model_names = [model['name'] for model in models]
            if any('llama3.2' in name for name in model_names):
                print("✅ Llama 3.2 model is available")
                return True
            else:
                print("⚠️  Llama 3.2 model not found, but Ollama is running")
                return True
        else:
            print(f"❌ Ollama returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("💡 Make sure Ollama is running: ollama serve")
        return False

def test_ollama_text_generation():
    """Test text generation with Ollama"""
    print("\n📝 Testing Ollama text generation...")
    try:
        from pamphlet_agent import OllamaTextGenerator
        
        generator = OllamaTextGenerator()
        
        # Test simple generation
        test_prompt = "Write a short, catchy headline for a new eco-friendly cleaning product."
        response = generator._call_ollama(test_prompt)
        
        if response and "Error" not in response:
            print("✅ Ollama text generation working")
            print(f"📄 Sample output: {response[:100]}...")
            return True
        else:
            print("❌ Ollama text generation failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def test_stability_api_connection(api_key):
    """Test Stability AI API connection"""
    print("\n🎨 Testing Stability AI API connection...")
    
    if not api_key or api_key == "your_stability_api_key_here":
        print("⚠️  Stability AI API key not set")
        print("💡 Please update the API key in app.py or .env file")
        return False
    
    try:
        url = "https://api.stability.ai/v2beta/stable-image/generate/core"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "image/*"
        }
        
        # Test with a simple prompt
        files = {
            "prompt": (None, "A simple test image"),
            "output_format": (None, "png"),
            "aspect_ratio": (None, "1:1"),
            "mode": (None, "text-to-image")
        }
        
        response = requests.post(url, headers=headers, files=files, timeout=30)
        
        if response.status_code == 200:
            print("✅ Stability AI API connection successful")
            return True
        else:
            print(f"❌ Stability AI API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Stability AI API: {e}")
        return False

def test_complete_integration(api_key):
    """Test the complete pamphlet generation pipeline"""
    print("\n🤖 Testing complete AI agent integration...")
    
    try:
        # Create a test request
        test_request = PamphletRequest(
            product_name="Test Product",
            description="A revolutionary test product for demonstration",
            tone="professional",
            target_audience="test users",
            key_features=["Feature 1", "Feature 2", "Feature 3"],
            call_to_action="Try it now!",
            color_scheme="modern",
            style="professional"
        )
        
        # Create agent (only if API key is available)
        if api_key and api_key != "your_stability_api_key_here":
            agent = PamphletAgent(api_key)
            
            print("⏳ Generating test pamphlet (this may take 1-2 minutes)...")
            result = agent.generate_pamphlet(test_request)
            
            if result.get('success'):
                print("✅ Complete integration test successful!")
                print(f"📄 Generated file: {result['filename']}")
                print(f"📝 Generated content preview:")
                for key, value in result['text_content'].items():
                    print(f"   {key}: {value[:50]}...")
                return True
            else:
                print(f"❌ Pamphlet generation failed: {result.get('error')}")
                return False
        else:
            print("⚠️  Skipping complete test due to missing API key")
            return True
            
    except Exception as e:
        print(f"❌ Error in complete integration test: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AI Pamphlet Generator Integration Test")
    print("=" * 50)
    
    # Test results
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Ollama connection
    total_tests += 1
    if test_ollama_connection():
        tests_passed += 1
    
    # Test 2: Ollama text generation
    total_tests += 1
    if test_ollama_text_generation():
        tests_passed += 1
    
    # Test 3: Stability AI API (if key is available)
    api_key = "your_stability_api_key_here"  # This should be updated
    total_tests += 1
    if test_stability_api_connection(api_key):
        tests_passed += 1
    
    # Test 4: Complete integration
    total_tests += 1
    if test_complete_integration(api_key):
        tests_passed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your AI Pamphlet Generator is ready to use.")
        print("\n🚀 To start the application:")
        print("   python3 app.py")
        print("\n🌐 Then open: http://localhost:5000")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("\n🔧 Common fixes:")
        print("   1. Start Ollama: ollama serve")
        print("   2. Download model: ollama pull llama3.2")
        print("   3. Update API key in app.py")
        print("   4. Install dependencies: pip3 install -r requirements.txt")

if __name__ == "__main__":
    main()
