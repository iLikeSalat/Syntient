"""
Flask API for the Syntient AI Assistant Platform.

This module provides a Flask web API with an /ask endpoint for interacting with the assistant.
"""

import os
import json
import uuid
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Import core components
from core import Assistant
from tools import registry as tool_registry
from memory import manager as memory_manager
from memory.simple import SimpleMemory

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize assistant
assistant = Assistant(api_key=os.getenv("OPENAI_API_KEY"))

# Initialize default memory
default_memory = SimpleMemory("default")
memory_manager.register_memory(default_memory)


@app.route('/ask', methods=['POST'])
def ask():
    """
    Process a user request and generate a response.
    
    Request format:
    {
        "message": "User's message",
        "user_id": "unique_user_id",
        "include_history": true,
        "context": {}
    }
    
    Response format:
    {
        "response": "Assistant's response",
        "type": "response_type",
        "actions": [],
        "context": {}
    }
    """
    try:
        # Parse request data
        data = request.json
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Extract required fields
        message = data.get('message')
        user_id = data.get('user_id', str(uuid.uuid4()))
        include_history = data.get('include_history', True)
        context = data.get('context', {})
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Process the request
        response = assistant.ask(message, include_history)
        
        # Store the interaction in memory
        memory_data = {
            'user_id': user_id,
            'message': message,
            'response': response,
            'context': context,
            'timestamp': response.get('timestamp', None)
        }
        
        memory_ref = default_memory.add(memory_data, metadata={'user_id': user_id})
        
        # Prepare the response
        result = {
            'response': response.get('response', ''),
            'type': response.get('type', 'response'),
            'reference_id': memory_ref,
            'user_id': user_id
        }
        
        # Include any actions if present
        if 'tool_call' in response.get('type', '') and 'tool_result' in response:
            result['actions'] = [
                {
                    'tool': response.get('tool', ''),
                    'result': response.get('tool_result', {})
                }
            ]
        
        return jsonify(result)
    
    except Exception as e:
        # Log the error (in a production environment, use a proper logger)
        print(f"Error processing request: {str(e)}")
        
        # Return error response
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Simple health check endpoint.
    """
    return jsonify({"status": "ok", "version": "1.0.0"})


if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")
