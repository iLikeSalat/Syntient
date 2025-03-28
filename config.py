"""
Configuration utilities for the Syntient AI Assistant Platform.

This module provides functions for loading and validating configuration settings.
"""

import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_config() -> Dict[str, Any]:
    """
    Load configuration settings from environment variables.
    
    Returns:
        Dictionary containing configuration settings
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        logger.warning("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
    
    # Get Flask configuration
    flask_port = int(os.getenv("PORT", 5000))
    flask_debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    
    # Get model configuration
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Get continuous execution configuration
    max_iterations = int(os.getenv("MAX_ITERATIONS", 100))
    iteration_delay = float(os.getenv("ITERATION_DELAY", 1.0))
    
    # Create configuration dictionary
    config = {
        "openai": {
            "api_key": openai_api_key,
            "model": model
        },
        "flask": {
            "port": flask_port,
            "debug": flask_debug
        },
        "continuous_execution": {
            "max_iterations": max_iterations,
            "iteration_delay": iteration_delay
        }
    }
    
    return config
