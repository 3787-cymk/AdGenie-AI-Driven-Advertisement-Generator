#!/usr/bin/env python3
"""
Demo script for AI Pamphlet Generator
Demonstrates the complete agentic AI system
"""

import os
import sys
from pamphlet_agent import PamphletAgent, PamphletRequest

def print_banner():
    """Print a nice banner"""
    print("=" * 60)
    print("🤖 AI PAMPHLET GENERATOR - DEMO")
    print("=" * 60)
    print("This demo showcases the complete agentic AI system")
    print("combining Ollama text generation with Stable Diffusion")
    print("image generation to create professional pamphlets.")
    print("=" * 60)

def get_user_input():
    """Get user input for pamphlet generation"""
    print("\n📝 Let's create your pamphlet!")
    print("-" * 40)
    
    product_name = input("Product Name: ").strip()
    if not product_name:
        product_name = "EcoClean Pro"
        print(f"Using default: {product_name}")
    
    description = input("Product Description: ").strip()
    if not description:
        description = "Revolutionary eco-friendly cleaning solution that removes 99.9% of bacteria"
        print(f"Using default: {description}")
    
    print("\nTone options: professional, casual, friendly, luxury, playful, serious")
    tone = input("Tone (professional): ").strip() or "professional"
    
    target_audience = input("Target Audience: ").strip()
    if not target_audience:
        target_audience = "health-conscious families"
        print(f"Using default: {target_audience}")
    
    print("\nKey Features (enter one per line, empty line to finish):")
    key_features = []
    while True:
        feature = input("Feature: ").strip()
        if not feature:
            break
        key_features.append(feature)
    
    if not key_features:
        key_features = ["100% biodegradable", "No harmful chemicals", "Long-lasting formula", "Safe for children and pets"]
        print("Using default features:", key_features)
    
    call_to_action = input("Call to Action: ").strip()
    if not call_to_action:
        call_to_action = "Order now and get 20% off your first purchase!"
        print(f"Using default: {call_to_action}")
    
    print("\nColor schemes: modern, elegant, minimal")
    color_scheme = input("Color Scheme (modern): ").strip() or "modern"
    
    print("\nStyles: professional, creative, minimalist, vintage")
    style = input("Style (professional): ").strip() or "professional"
    
    return PamphletRequest(
        product_name=product_name,
        description=description,
        tone=tone,
        target_audience=target_audience,
        key_features=key_features,
        call_to_action=call_to_action,
        color_scheme=color_scheme,
        style=style
    )

def main():
    """Main demo function"""
    print_banner()
    
    # Check if API key is set
    api_key = "your_stability_api_key_here"  # This should be updated
    
    if api_key == "your_stability_api_key_here":
        print("\n⚠️  WARNING: Stability AI API key not set!")
        print("Please update the API key in this script or in app.py")
        print("You can get a free API key from: https://platform.stability.ai/")
        
        use_demo = input("\nContinue with demo (text generation only)? (y/n): ").lower()
        if use_demo != 'y':
            print("Demo cancelled. Please set up your API key and try again.")
            return
    
    # Get user input
    request = get_user_input()
    
    print(f"\n🎯 Generating pamphlet for: {request.product_name}")
    print("⏳ This may take 1-2 minutes...")
    print("\n🤖 AI Agent Status:")
    print("   📝 Generating text with Ollama...")
    
    try:
        # Create agent
        agent = PamphletAgent(api_key)
        
        # Generate pamphlet
        result = agent.generate_pamphlet(request)
        
        if result.get('success'):
            print("\n✅ Pamphlet generated successfully!")
            print(f"📄 File saved as: {result['filename']}")
            
            # Display generated content
            print("\n📝 Generated Content:")
            print("-" * 30)
            for key, value in result['text_content'].items():
                print(f"{key.title()}: {value}")
            
            print(f"\n🎉 Your pamphlet is ready! Check the file: {result['filename']}")
            
        else:
            print(f"\n❌ Error generating pamphlet: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Ollama is running: ollama serve")
        print("2. Check if the model is downloaded: ollama list")
        print("3. Verify your Stability AI API key")
        print("4. Install dependencies: pip3 install -r requirements.txt")

if __name__ == "__main__":
    main()
