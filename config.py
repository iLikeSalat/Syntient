"""
Configuration utilities for the Syntient AI Assistant Platform.

This module provides functions for loading and validating configuration settings.
"""

import os
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv


def load_config() -> Dict[str, Any]:
    """
    Load configuration from environment variables.
    
    Returns:
        Dictionary containing configuration settings
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Create configuration dictionary
    config = {
        "openai": {
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        },
        "flask": {
            "app": os.getenv("FLASK_APP", "app.py"),
            "env": os.getenv("FLASK_ENV", "development"),
            "debug": os.getenv("FLASK_DEBUG", "False").lower() == "true",
            "port": int(os.getenv("PORT", 5000))
        },
        "memory": {
            "default_id": os.getenv("DEFAULT_MEMORY_ID", "default"),
            "use_chroma": os.getenv("USE_CHROMA", "False").lower() == "true"
        },
        "tools": {
            "telegram_bot_token": os.getenv("TELEGRAM_BOT_TOKEN", ""),
            "trading_api_key": os.getenv("TRADING_API_KEY", "")
        },
        "logging": {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "file": os.getenv("LOG_FILE", "syntient.log")
        }
    }
    
    return config


def validate_config(config: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate configuration settings.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dictionary of validation errors, empty if no errors
    """
    errors = {}
    
    # Validate OpenAI API key
    if not config["openai"]["api_key"]:
        errors["openai.api_key"] = "OpenAI API key is required"
    
    # Validate Flask port
    try:
        port = config["flask"]["port"]
        if not (1024 <= port <= 65535):
            errors["flask.port"] = f"Port must be between 1024 and 65535, got {port}"
    except (KeyError, ValueError):
        errors["flask.port"] = "Invalid port configuration"
    
    return errors


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Set up logging based on configuration.
    
    Args:
        config: Configuration dictionary
    """
    log_level_str = config["logging"]["level"]
    log_file = config["logging"]["file"]
    
    # Map string log level to logging constant
    log_level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    log_level = log_level_map.get(log_level_str, logging.INFO)
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def get_config() -> Dict[str, Any]:
    """
    Load, validate, and return configuration.
    
    Returns:
        Validated configuration dictionary
        
    Raises:
        ValueError: If configuration validation fails
    """
    config = load_config()
    errors = validate_config(config)
    
    if errors:
        error_msg = "Configuration validation failed:\n" + "\n".join([f"- {k}: {v}" for k, v in errors.items()])
        raise ValueError(error_msg)
    
    # Set up logging
    setup_logging(config)
    
    return config
