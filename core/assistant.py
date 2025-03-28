"""
Core assistant module for the Syntient AI Assistant Platform.

This module handles:
- Prompt construction and formatting
- OpenAI API integration
- Response processing
- Planning and execution logic
"""

import os
import json
import time
import requests
from typing import Dict, List, Any, Optional, Union


class Assistant:
    """
    Core assistant class that handles interactions with the OpenAI API
    and manages the planning and execution of tasks.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the Assistant with API credentials and configuration.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: Model to use for completions (default: gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in .env or pass to constructor.")
        
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        # System prompt that defines assistant capabilities and behavior
        self.system_prompt = """
        You are an AI assistant that helps users accomplish tasks. You can:
        1. Plan and execute multi-step tasks
        2. Use tools when necessary
        3. Remember context from previous interactions
        4. Debug and retry when encountering issues
        
        When given a task:
        1. Break it down into steps
        2. Execute each step methodically
        3. Use available tools when needed
        4. Provide clear updates on progress
        5. Deliver final results in a clear format
        """
        
        # Store conversation history
        self.conversation_history = []
        
        # Available tools registry
        self.tools = {}
    
    def register_tool(self, tool_name: str, tool_function: callable):
        """
        Register a tool that the assistant can use.
        
        Args:
            tool_name: Name of the tool
            tool_function: Function to call when tool is used
        """
        self.tools[tool_name] = tool_function
    
    def add_message_to_history(self, role: str, content: str):
        """
        Add a message to the conversation history.
        
        Args:
            role: Role of the message sender (user, assistant, system)
            content: Content of the message
        """
        self.conversation_history.append({"role": role, "content": content})
    
    def clear_history(self):
        """Reset the conversation history."""
        self.conversation_history = []
    
    def create_messages(self, user_input: str, include_history: bool = True) -> List[Dict[str, str]]:
        """
        Create the messages array for the API request.
        
        Args:
            user_input: User's input message
            include_history: Whether to include conversation history
            
        Returns:
            List of message dictionaries for the API request
        """
        messages = [{"role": "system", "content": self.system_prompt.strip()}]
        
        if include_history and self.conversation_history:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        return messages
    
    def call_openai_api(self, messages: List[Dict[str, str]], 
                       temperature: float = 0.7, 
                       max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Make a direct call to the OpenAI API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            
        Returns:
            API response as a dictionary
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Implement retry logic here
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException:
                    retry_count += 1
            
            # If all retries fail, raise the exception
            raise Exception(f"Failed to call OpenAI API after {max_retries} retries: {str(e)}")
    
    def extract_response_content(self, api_response: Dict[str, Any]) -> str:
        """
        Extract the assistant's response content from the API response.
        
        Args:
            api_response: Response from the OpenAI API
            
        Returns:
            Assistant's response as a string
        """
        try:
            return api_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to extract response content: {str(e)}")
    
    def process_response(self, response_content: str) -> Dict[str, Any]:
        """
        Process the assistant's response to extract actions, plans, etc.
        
        Args:
            response_content: Assistant's response content
            
        Returns:
            Processed response with extracted components
        """
        # Check if the response contains a tool call
        if "<<TOOL:" in response_content and ">>" in response_content:
            # Extract tool call information
            tool_start = response_content.find("<<TOOL:")
            tool_end = response_content.find(">>", tool_start)
            tool_info = response_content[tool_start+7:tool_end].strip()
            
            try:
                # Parse tool name and arguments
                tool_parts = tool_info.split(" ", 1)
                tool_name = tool_parts[0]
                tool_args = json.loads(tool_parts[1]) if len(tool_parts) > 1 else {}
                
                return {
                    "type": "tool_call",
                    "tool": tool_name,
                    "args": tool_args,
                    "original_response": response_content
                }
            except Exception as e:
                return {
                    "type": "error",
                    "error": f"Failed to parse tool call: {str(e)}",
                    "original_response": response_content
                }
        
        # Check if the response contains a plan
        if "PLAN:" in response_content:
            plan_start = response_content.find("PLAN:")
            plan_section = response_content[plan_start:].split("\n\n", 1)[0]
            
            return {
                "type": "plan",
                "plan": plan_section,
                "response": response_content,
            }
        
        # Default case: just a regular response
        return {
            "type": "response",
            "response": response_content
        }
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a registered tool.
        
        Args:
            tool_name: Name of the tool to execute
            args: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' is not registered")
        
        try:
            return self.tools[tool_name](**args)
        except Exception as e:
            return {"error": f"Tool execution failed: {str(e)}"}
    
    def ask(self, user_input: str, include_history: bool = True) -> Dict[str, Any]:
        """
        Process a user request and generate a response.
        
        Args:
            user_input: User's input message
            include_history: Whether to include conversation history
            
        Returns:
            Processed response with any actions or plans
        """
        # Create messages for the API request
        messages = self.create_messages(user_input, include_history)
        
        # Call the OpenAI API
        api_response = self.call_openai_api(messages)
        
        # Extract the response content
        response_content = self.extract_response_content(api_response)
        
        # Add the response to conversation history
        self.add_message_to_history("user", user_input)
        self.add_message_to_history("assistant", response_content)
        
        # Process the response
        processed_response = self.process_response(response_content)
        
        # If the response contains a tool call, execute it
        if processed_response["type"] == "tool_call":
            tool_result = self.execute_tool(
                processed_response["tool"], 
                processed_response["args"]
            )
            processed_response["tool_result"] = tool_result
        
        return processed_response
    
    def plan_execution(self, task: str) -> List[str]:
        """
        Generate a plan for executing a complex task.
        
        Args:
            task: Task description
            
        Returns:
            List of steps in the plan
        """
        planning_prompt = f"""
        I need to create a step-by-step plan to accomplish this task:
        
        {task}
        
        Break this down into clear, executable steps. For each step, explain:
        1. What needs to be done
        2. What tools or information might be needed
        3. How to verify the step was completed successfully
        
        Format your response as a numbered list of steps.
        """
        
        # Create messages for the planning request
        messages = [
            {"role": "system", "content": self.system_prompt.strip()},
            {"role": "user", "content": planning_prompt}
        ]
        
        # Call the OpenAI API
        api_response = self.call_openai_api(messages)
        
        # Extract the response content
        plan_content = self.extract_response_content(api_response)
        
        # Parse the plan into steps
        steps = []
        for line in plan_content.split("\n"):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith("- ")):
                steps.append(line)
        
        return steps
    
    def execute_with_retry(self, function: callable, max_retries: int = 3, **kwargs) -> Any:
        """
        Execute a function with retry logic.
        
        Args:
            function: Function to execute
            max_retries: Maximum number of retry attempts
            **kwargs: Arguments to pass to the function
            
        Returns:
            Result of the function execution
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= max_retries:
            try:
                return function(**kwargs)
            except Exception as e:
                last_error = e
                retry_count += 1
                time.sleep(2 ** retry_count)  # Exponential backoff
        
        raise Exception(f"Failed after {max_retries} retries. Last error: {str(last_error)}")
