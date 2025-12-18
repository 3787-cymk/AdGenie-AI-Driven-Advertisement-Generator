#!/usr/bin/env python3
"""
Flask Web Application for AI Pamphlet Generator
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import base64
from pamphlet_agent import PamphletAgent, PamphletRequest
import json

app = Flask(__name__)


STABILITY_API_KEY = "sk-yOveJUr42rXpmcP9577FZtprJk5guzQW8CN7Ofq4FQQZdFzR"

if STABILITY_API_KEY == "your_stability_api_key_here":
    print("⚠️  WARNING: Please set your Stability AI API key in app.py")
    print("   Get your free API key from: https://platform.stability.ai/")
    print("   Then update STABILITY_API_KEY in app.py")
else:
    print("✅ Stability AI API key is set!")

# Use the full pamphlet agent with image generation
from pamphlet_agent import PamphletAgent
agent = PamphletAgent(STABILITY_API_KEY)

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_pamphlet():
    """Generate pamphlet endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_name', 'description', 'tone', 'target_audience', 'key_features', 'call_to_action']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create pamphlet request
        pamphlet_request = PamphletRequest(
            product_name=data['product_name'],
            description=data['description'],
            tone=data['tone'],
            target_audience=data['target_audience'],
            key_features=data['key_features'],
            call_to_action=data['call_to_action'],
            color_scheme=data.get('color_scheme', 'modern'),
            style=data.get('style', 'professional'),
            image_prompt=data.get('image_prompt', ''),
            custom_image=data.get('custom_image', ''),
            image_source=data.get('image_source', 'ai_generated'),
            regeneration_index=int(data.get('regeneration_count', 0) or 0)
        )
        
        # Generate pamphlet
        result = agent.generate_pamphlet(pamphlet_request)
        
        if result.get('success'):
            # Read the generated image file and encode as base64
            with open(result['filename'], 'rb') as f:
                image_data = f.read()
            
            # Convert to base64 for web display
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            return jsonify({
                'success': True,
                'image': image_base64,
                'layout_base_image': result.get('layout_base_image'),
                'text_content': result['text_content'],
                'filename': result['filename'],
                'message': result['message']
            })
        else:
            return jsonify({'error': result.get('error', 'Unknown error')}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_pamphlet(filename):
    """Download generated pamphlet"""
    try:
        return send_file(filename, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

@app.route('/edit-pamphlet', methods=['POST'])
def edit_pamphlet():
    """Edit pamphlet with custom settings"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'originalImage' not in data or 'edits' not in data:
            return jsonify({'error': 'Missing required fields: originalImage and edits'}), 400
        
        # Decode the original image
        original_image_data = base64.b64decode(data['originalImage'])
        
        # Get edit settings
        edits = data['edits']
        
        # Create edited pamphlet
        edited_result = agent.edit_pamphlet(original_image_data, edits, data.get('textContent'))
        
        if edited_result:
            edited_image_data, layout_base_data = edited_result
            # Save edited pamphlet
            filename = f"edited_{data.get('filename', 'pamphlet')}"
            with open(filename, 'wb') as f:
                f.write(edited_image_data)
            
            # Convert to base64 for response
            edited_image_base64 = base64.b64encode(edited_image_data).decode('utf-8')
            layout_base_base64 = base64.b64encode(layout_base_data).decode('utf-8')
            
            return jsonify({
                'success': True,
                'editedImage': edited_image_base64,
                'layoutBaseImage': layout_base_base64,
                'filename': filename,
                'message': 'Pamphlet edited successfully!'
            })
        else:
            return jsonify({'error': 'Failed to edit pamphlet'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'AI Pamphlet Generator is running'})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🚀 Starting AI Pamphlet Generator...")
    print("📱 Open your browser and go to: http://localhost:5002")
    print("🤖 Make sure Ollama is running on http://localhost:11434")
    print("🎨 Make sure you have set your Stability AI API key in app.py")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
