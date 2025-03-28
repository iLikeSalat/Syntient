"""
LLM-based tool selector module for the Syntient AI Assistant Platform.

This module provides functionality to use the LLM itself to select the appropriate
tool based on user input, replacing the regex-based TaskDetector approach.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional, Tuple, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMToolSelector:
    """
    Uses the LLM to select the appropriate tool based on user input.
    
    This class replaces the regex-based TaskDetector with a more flexible and
    semantically smarter approach that uses the LLM itself to decide which tool
    to use for a given user input.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM tool selector.
        
        Args:
            api_key: OpenAI API key
            model: Model to use for completions (default: gpt-3.5-turbo)
        """
        self.api_key = api_key
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def select_tool(self, user_input: str, available_tools: List[Dict[str, Any]]) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Select the appropriate tool for the user input.
        
        Args:
            user_input: The user's input message
            available_tools: List of available tools with their schemas
            
        Returns:
            Tuple of (tool_name, tool_args) if a tool is selected, None otherwise
        """
        # Create a prompt for the LLM to select a tool
        tool_descriptions = "\n".join([
            f"- {tool['name']}: {tool['description']}" 
            for tool in available_tools
        ])
        
        tool_parameters = {}
        for tool in available_tools:
            tool_parameters[tool['name']] = tool.get('parameters', {})
        
        prompt = f"""
You are a tool selection assistant. Your job is to analyze a user message and determine if it should use a specific tool.

Available tools:
{tool_descriptions}

User message: "{user_input}"

First, decide if the user's message requires using one of the available tools. If not, respond with: {{"use_tool": false}}

If a tool should be used, identify which one and what parameters to use. Respond with a JSON object in this format:
{{
  "use_tool": true,
  "tool_name": "name_of_tool",
  "parameters": {{
    "param1": "value1",
    "param2": "value2"
  }}
}}

Only include parameters that are relevant and can be determined from the user message. Be precise and accurate.
Respond with valid JSON only, no additional text.
"""
        
        # Call the OpenAI API
        try:
            response = self._call_openai_api(prompt)
            
            # Parse the response
            try:
                tool_selection = json.loads(response)
                
                # Check if a tool should be used
                if tool_selection.get("use_tool", False):
                    tool_name = tool_selection.get("tool_name")
                    parameters = tool_selection.get("parameters", {})
                    
                    # Validate the tool name
                    if tool_name not in [tool["name"] for tool in available_tools]:
                        logger.warning(f"LLM selected invalid tool: {tool_name}")
                        return None
                    
                    logger.info(f"LLM selected tool: {tool_name} with parameters: {parameters}")
                    return tool_name, parameters
                else:
                    logger.info("LLM decided no tool is needed")
                    return None
            except json.JSONDecodeError:
                logger.error(f"Failed to parse LLM response as JSON: {response}")
                return None
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            return None
    
    def _call_openai_api(self, prompt: str) -> str:
        """
        Call the OpenAI API to get a response.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            The response from the API
        """
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a tool selection assistant that helps determine which tool to use for a given user input."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more deterministic responses
            "max_tokens": 500
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise Exception(f"Failed to call OpenAI API: {str(e)}")
    
    def format_tool_call(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """
        Format a tool call string.
        
        Args:
            tool_name: The name of the tool
            tool_args: The arguments for the tool
            
        Returns:
            Formatted tool call string
        """
        args_str = json.dumps(tool_args)
        return f"<<TOOL:{tool_name} {args_str}>>"
