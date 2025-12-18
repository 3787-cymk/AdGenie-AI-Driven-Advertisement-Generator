#!/usr/bin/env python3
"""
Test script for pamphlet editing features
"""

import requests
import base64
import json
from pathlib import Path
from PIL import Image
from pamphlet_agent import PamphletAgent, PamphletRequest, PamphletDesigner

def test_editing_features():
    """Test the new editing features"""
    
    print("🧪 Testing Pamphlet Editing Features...")
    
    # Initialize the agent
    STABILITY_API_KEY = "sk-a3ebXgGIjvAnJEr70JyP1iIMiGZlsoEz23C2tkrDu2MuefKY"
    agent = PamphletAgent(STABILITY_API_KEY)
    
    # Create a test pamphlet request
    request = PamphletRequest(
        product_name="Test Product",
        description="A test product for demonstrating editing features",
        tone="professional",
        target_audience="test users",
        key_features=[
            "Easy to use",
            "High quality",
            "Affordable price",
            "Great support"
        ],
        call_to_action="Try it now!",
        color_scheme="modern",
        style="professional"
    )
    
    print("📝 Generating test pamphlet...")
    result = agent.generate_pamphlet(request)
    
    if result.get('success'):
        print(f"✅ Pamphlet generated: {result['filename']}")
        
        # Test editing features
        print("🎨 Testing editing features...")
        
        # Read the generated image
        with open(result['filename'], 'rb') as f:
            original_image_data = f.read()
        
        # Test different edit scenarios
        test_edits = [
            {
                "name": "Size Change",
                "edits": {
                    "size": {"width": 800, "height": 1000},
                    "overallBrightness": 120
                }
            },
            {
                "name": "Filter Application",
                "edits": {
                    "imageFilter": "sepia",
                    "filterIntensity": 80,
                    "borderRadius": 25
                }
            },
            {
                "name": "Cropping Test",
                "edits": {
                    "imageCrop": "square",
                    "backgroundOpacity": 60
                }
            }
        ]
        
        for test in test_edits:
            print(f"🔧 Testing: {test['name']}")
            
            edited_result = agent.edit_pamphlet(original_image_data, test['edits'])
            
            if edited_result:
                edited_data, layout_base = edited_result
                filename = f"test_{test['name'].lower().replace(' ', '_')}.png"
                with open(filename, 'wb') as f:
                    f.write(edited_data)
                base_filename = f"test_{test['name'].lower().replace(' ', '_')}_layout.png"
                with open(base_filename, 'wb') as f:
                    f.write(layout_base)
                print(f"✅ {test['name']} test passed: {filename}")
            else:
                print(f"❌ {test['name']} test failed")
        
        print("\n🎉 All editing tests completed!")
        print("📁 Check the generated files to see the results")
        
    else:
        print(f"❌ Failed to generate test pamphlet: {result.get('error')}")

def test_offline_layout_engine():
    """Validate the layout engine without hitting external APIs."""
    print("\n🧪 Testing offline layout engine rendering...")
    designer = PamphletDesigner()
    canvas = Image.new("RGBA", (1200, 1600), (42, 98, 156, 255))
    
    mock_edits = {
        "size": {"width": 1200, "height": 1600},
        "layout": "split",
        "headlineFont": "Helvetica-Bold",
        "headlineSize": 82,
        "headlineColor": "#f9fafb",
        "bodyFont": "Georgia",
        "bodySize": 30,
        "bodyColor": "#f0f4f8",
        "ctaBgColor": "#ef4444",
        "ctaTextColor": "#ffffff",
        "backgroundOpacity": 65,
        "borderRadius": 26,
        "shadowIntensity": 35,
        "textShadow": 40,
        "imageFilter": "contrast",
        "filterIntensity": 60,
        "overallBrightness": 110,
        "imageCrop": "portrait",
        "imagePosition": "top"
    }
    
    text_content = {
        "headline": "ELEVATE YOUR FLOW",
        "tagline": "Precision Meets Comfort",
        "description": "Discover a thoughtfully engineered toolset that adapts to the way you build, create, and scale ideas. Crafted for makers who refuse to compromise on performance or aesthetics.",
        "call_to_action": "Start your upgrade"
    }
    
    features = [
        "Adaptive ergonomic geometry",
        "Premium alloy construction",
        "Interview-ready presentation kit",
        "Lifetime concierge support"
    ]
    
    final_canvas, layout_base = designer.apply_edits(canvas, mock_edits, text_content, features=features)
    output_dir = Path("test_outputs")
    output_dir.mkdir(exist_ok=True)
    offline_path = output_dir / "offline_layout_preview.png"
    final_canvas.save(offline_path, format="PNG")
    layout_path = output_dir / "offline_layout_base.png"
    layout_base.save(layout_path, format="PNG")
    print(f"✅ Offline layout rendering saved to {offline_path.resolve()}")

if __name__ == "__main__":
    test_editing_features()
    test_offline_layout_engine()
