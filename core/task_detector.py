"""
Task detector module for the Syntient AI Assistant Platform.

This module provides functionality to automatically detect tasks that can use tools
and convert them into appropriate tool calls.
"""

import re
import logging
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskDetector:
    """
    Detects tasks that can be handled by tools and converts them to tool calls.
    
    This class analyzes user input to identify patterns that match tool capabilities
    and automatically generates appropriate tool calls.
    """
    
    def __init__(self):
        """Initialize the task detector with pattern recognition rules."""
        # Define patterns for different types of tasks
        self.patterns = {
            "url_summary": [
                r"(?i)summarize\s+(https?://\S+)",
                r"(?i)summarize\s+the\s+content\s+(?:at|on|of|from)\s+(https?://\S+)",
                r"(?i)give\s+(?:me\s+)?a\s+summary\s+of\s+(https?://\S+)",
                r"(?i)what(?:'s|\s+is)\s+(?:on|at)\s+(https?://\S+)",
                r"(?i)extract\s+(?:the\s+)?(?:content|information|text)\s+from\s+(https?://\S+)"
            ],
            "code_execution": [
                r"(?i)execute\s+(?:this|the\s+following)\s+(?:python\s+)?code[:\n]+(.*?)(?:\n\s*$|\Z)",
                r"(?i)run\s+(?:this|the\s+following)\s+(?:python\s+)?code[:\n]+(.*?)(?:\n\s*$|\Z)",
                r"(?i)evaluate\s+(?:this|the\s+following)\s+(?:python\s+)?code[:\n]+(.*?)(?:\n\s*$|\Z)"
            ]
        }
    
    def detect_task(self, user_input: str) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Detect if the user input contains a task that can be handled by a tool.
        
        Args:
            user_input: The user's input message
            
        Returns:
            Tuple of (tool_name, tool_args) if a task is detected, None otherwise
        """
        # Check for URL summary tasks
        for pattern in self.patterns["url_summary"]:
            match = re.search(pattern, user_input, re.DOTALL)
            if match:
                url = match.group(1).strip()
                # Validate URL
                if self._is_valid_url(url):
                    logger.info(f"Detected URL summary task for: {url}")
                    return "browser_use", {"url": url}
        
        # Check for code execution tasks
        for pattern in self.patterns["code_execution"]:
            match = re.search(pattern, user_input, re.DOTALL)
            if match:
                code = match.group(1).strip()
                if code:
                    logger.info("Detected code execution task")
                    return "code_executor", {"code": code}
        
        # No task detected
        return None
    
    def _is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL is valid, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def format_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """
        Format a tool call string.
        
        Args:
            tool_name: The name of the tool
            tool_args: The arguments for the tool
            
        Returns:
            Formatted tool call string
        """
        import json
        args_str = json.dumps(tool_args)
        return f"<<TOOL:{tool_name} {args_str}>>"
