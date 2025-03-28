"""
Telegram bot tool for the Syntient AI Assistant Platform.

This module provides integration with the Telegram API to send and receive messages.
"""

import requests
from typing import Dict, Any, Optional
from ..base import Tool


class TelegramBotTool(Tool):
    """
    Tool for interacting with Telegram bots.
    
    This tool allows the assistant to send messages, receive updates,
    and interact with users through Telegram.
    """
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Telegram bot tool.
        
        Args:
            token: Telegram bot token (optional, can be set later)
        """
        super().__init__(
            name="telegram_bot",
            description="Send and receive messages through Telegram"
        )
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/" if token else None
    
    def set_token(self, token: str) -> None:
        """
        Set the Telegram bot token.
        
        Args:
            token: Telegram bot token
        """
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a Telegram bot action.
        
        Args:
            action: Action to perform (send_message, get_updates, etc.)
            **kwargs: Action-specific parameters
            
        Returns:
            Result of the action
            
        Raises:
            ValueError: If the token is not set or the action is invalid
        """
        if not self.token:
            raise ValueError("Telegram bot token is not set")
        
        if action == "send_message":
            return self.send_message(**kwargs)
        elif action == "get_updates":
            return self.get_updates(**kwargs)
        else:
            raise ValueError(f"Invalid action: {action}")
    
    def send_message(self, chat_id: str, text: str, 
                    parse_mode: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a message to a Telegram chat.
        
        Args:
            chat_id: ID of the chat to send the message to
            text: Text of the message
            parse_mode: Parse mode for the message (Markdown, HTML, etc.)
            
        Returns:
            Response from the Telegram API
        """
        url = f"{self.base_url}sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_updates(self, offset: Optional[int] = None, 
                   limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Get updates from the Telegram API.
        
        Args:
            offset: Identifier of the first update to be returned
            limit: Limit the number of updates to be retrieved
            
        Returns:
            Updates from the Telegram API
        """
        url = f"{self.base_url}getUpdates"
        payload = {}
        
        if offset:
            payload["offset"] = offset
        
        if limit:
            payload["limit"] = limit
        
        try:
            response = requests.get(url, params=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool's parameters.
        
        Returns:
            Dictionary describing the parameters and their types
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["send_message", "get_updates"],
                    "description": "Action to perform"
                },
                "chat_id": {
                    "type": "string",
                    "description": "ID of the chat (for send_message)"
                },
                "text": {
                    "type": "string",
                    "description": "Text of the message (for send_message)"
                },
                "parse_mode": {
                    "type": "string",
                    "enum": ["Markdown", "HTML"],
                    "description": "Parse mode for the message (for send_message)"
                },
                "offset": {
                    "type": "integer",
                    "description": "Identifier of the first update to be returned (for get_updates)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Limit the number of updates to be retrieved (for get_updates)"
                }
            },
            "required": ["action"]
        }
