"""
Main entry point for running the Syntient AI Assistant Platform.

This script starts the Flask API server.
"""

import os
from app import app
from config import get_config

if __name__ == "__main__":
    # Load configuration
    config = get_config()
    
    # Get port from configuration
    port = config["flask"]["port"]
    debug = config["flask"]["debug"]
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=debug)
