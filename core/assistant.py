"""
Core assistant module for the Syntient AI Assistant Platform.

This module handles:
- Prompt construction and formatting
- OpenAI API integration
- Response processing
- Planning and execution logic
- Tool invocation support
"""

import os
import json
import time
import re
import requests
import logging
from typing import Dict, List, Any, Optional, Union

from tools import registry
from .llm_tool_selector import LLMToolSelector
from .simulated_flow import SimulatedFlowHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Assistant:
    """
    Core assistant class that handles interactions with the OpenAI API
    and manages the planning and execution of tasks.
    """
        
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", tool_registry=None):
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
        
        To use a tool, include a tool call in your response using this format:
        <<TOOL:tool_name {"param1": "value1", "param2": "value2"}>>
        
        Available tools:
        - browser_use: Browse websites and extract information
        - file_parser: Parse and extract information from files
        - code_executor: Execute code in various programming languages
        - web_search: Search the web for information
        """
        
        self.conversation_history = []
        self.tools = {}

        # Initialize tool registry
        self.tool_registry = tool_registry or registry
        
        # Initialize LLM tool selector (replacing TaskDetector)
        self.llm_tool_selector = LLMToolSelector(api_key=self.api_key, model=self.model)
        
        # Initialize simulated flow handler
        self.simulated_flow = SimulatedFlowHandler()
        
        # Configuration flags
        self.auto_detect_tools = True
        self.use_simulated_fallback = True
        self.use_llm_tool_selection = True  # New flag to control LLM-based tool selection
    
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
        # Update system prompt with available tools
        tools_info = self._get_tools_info()
        updated_system_prompt = self.system_prompt.strip() + "\n\nAvailable tools:\n" + tools_info
        
        messages = [{"role": "system", "content": updated_system_prompt}]
        
        if include_history and self.conversation_history:
            messages.extend(self.conversation_history)
        
        messages.append({"role": "user", "content": user_input})
        return messages
    
    def _get_tools_info(self) -> str:
        """
        Get information about available tools for the system prompt.
        
        Returns:
            String containing tool descriptions
        """
        tools_info = ""
        
        # Get tools from the registry
        tool_schemas = self.tool_registry.list_tools()
        
        for name, schema in tool_schemas.items():
            tools_info += f"- {name}: {schema['description']}\n"
        
        # Add legacy tools
        for name in self.tools:
            if name not in tool_schemas:
                tools_info += f"- {name}: Legacy tool\n"
        
        return tools_info
    
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
        # Check if the response contains a tool call using the new format
        tool_pattern = r"<<TOOL:(\w+)\s+({.*?})>>"
        tool_matches = re.findall(tool_pattern, response_content)
        
        if tool_matches:
            # Extract the first tool call
            tool_name, tool_args_str = tool_matches[0]
            
            try:
                # Parse tool arguments
                tool_args = json.loads(tool_args_str)
                
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
        # First, try to use the tool registry
        tool = self.tool_registry.get_tool(tool_name)
        if tool:
            try:
                logger.info(f"Executing tool from registry: {tool_name}")
                return tool.execute(**args)
            except Exception as e:
                error_msg = f"Tool execution failed: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg, "status": "error"}
        
        # Fall back to legacy tools
        if tool_name in self.tools:
            try:
                logger.info(f"Executing legacy tool: {tool_name}")
                return self.tools[tool_name](**args)
            except Exception as e:
                error_msg = f"Legacy tool execution failed: {str(e)}"
                logger.error(error_msg)
                return {"error": error_msg, "status": "error"}
        
        # Tool not found
        error_msg = f"Tool '{tool_name}' is not registered"
        logger.error(error_msg)
        return {"error": error_msg, "status": "error"}
    
    def ask(self, user_input: str, include_history: bool = True) -> Dict[str, Any]:
        """
        Process a user request and generate a response.
        
        Args:
            user_input: User's input message
            include_history: Whether to include conversation history
            
        Returns:
            Processed response with any actions or plans
        """
        # Check if automatic tool detection is enabled
        if self.auto_detect_tools:
            # Use LLM-based tool selection if enabled
            if self.use_llm_tool_selection:
                # Get available tools from the registry
                tool_schemas = []
                for name, schema in self.tool_registry.list_tools().items():
                    tool_info = {
                        "name": name,
                        "description": schema.get("description", ""),
                        "parameters": schema.get("parameters", {})
                    }
                    tool_schemas.append(tool_info)
                
                # Use LLM to select the appropriate tool
                llm_selection = self.llm_tool_selector.select_tool(user_input, tool_schemas)
                
                if llm_selection:
                    tool_name, tool_args = llm_selection
                    logger.info(f"🧠 LLM selected tool: {tool_name} with args {tool_args}")
                    
                    # Execute the tool
                    tool_result = self.execute_tool(tool_name, tool_args)
                    
                    # Format the tool call for inclusion in the response
                    tool_call_text = self.llm_tool_selector.format_tool_call(tool_name, tool_args)
                    
                    # Create a response that includes the tool call and result
                    if tool_result.get("status") == "success":
                        result_header = "\n\n**Tool Execution Successful**\n\n"
                    else:
                        result_header = "\n\n**Tool Execution Failed**\n\n"
                    
                    formatted_result = json.dumps(tool_result, indent=2)
                    tool_result_text = f"{result_header}```json\n{formatted_result}\n```\n\n"
                    
                    # Create a modified user input that includes the tool call
                    modified_user_input = f"{user_input}\n\n{tool_call_text}"
                    
                    # Create messages for the API request with the modified user input
                    messages = self.create_messages(modified_user_input, include_history)
                    
                    # Call the OpenAI API to get a response that incorporates the tool result
                    api_response = self.call_openai_api(messages)
                    response_content = self.extract_response_content(api_response)
                    
                    # Process the response
                    processed_response = self.process_response(response_content)
                    
                    # Add the tool result to the processed response
                    processed_response["tool_result"] = tool_result
                    processed_response["detected_tool"] = tool_name
                    processed_response["detected_args"] = tool_args
                    processed_response["llm_selected"] = True
                    
                    # Update the response to include the tool call and result
                    if "response" in processed_response:
                        processed_response["response"] = f"{tool_call_text}{tool_result_text}{processed_response['response']}"
                    else:
                        processed_response["response"] = f"{tool_call_text}{tool_result_text}"
                    
                    # Add the user input and assistant response to conversation history
                    self.add_message_to_history("user", user_input)
                    self.add_message_to_history("assistant", processed_response["response"])
                    
                    return processed_response
            
            # If LLM tool selection is disabled or didn't select a tool, check for simulated tasks
            if self.use_simulated_fallback:
                simulated_task = self.simulated_flow.detect_simulated_task(user_input)
                if simulated_task:
                    logger.info(f"Using simulated flow for task type: {simulated_task.get('type', 'unknown')}")
                    
                    # Generate a simulated response
                    simulated_response = self.simulated_flow.generate_simulated_response(simulated_task)
                    
                    # Create a processed response
                    processed_response = {
                        "type": "simulated",
                        "simulated_type": simulated_task.get("type", "unknown"),
                        "response": simulated_response,
                        "simulated_task": simulated_task
                    }
                    
                    # Add the user input and assistant response to conversation history
                    self.add_message_to_history("user", user_input)
                    self.add_message_to_history("assistant", simulated_response)
                    
                    return processed_response
        
        # If no automatic tool detection or no tool was detected, proceed with normal flow
        # Create messages for the API request
        messages = self.create_messages(user_input, include_history)
        
        # Call the OpenAI API
        api_response = self.call_openai_api(messages)
        
        # Extract the response content
        response_content = self.extract_response_content(api_response)
        
        # Process the response
        processed_response = self.process_response(response_content)
        
        # If the response contains a tool call, execute it
        if processed_response["type"] == "tool_call":
            tool_name = processed_response["tool"]
            tool_args = processed_response["args"]
            
            # Execute the tool
            tool_result = self.execute_tool(tool_name, tool_args)
            processed_response["tool_result"] = tool_result
            
            # Append the tool result to the response
            original_response = processed_response["original_response"]
            tool_call_text = f"<<TOOL:{tool_name} {json.dumps(tool_args)}>>"
            tool_result_text = f"\n\n**Tool Result:**\n\n```json\n{json.dumps(tool_result, indent=2)}\n```\n\n"
            
            # Replace the tool call with the tool call + result
            updated_response = original_response.replace(
                tool_call_text, 
                f"{tool_call_text}{tool_result_text}"
            )
            
            # Update the processed response
            processed_response["response"] = updated_response
            
            # Add follow-up context if needed for certain tools
            if tool_name == "browser_use" and tool_result.get("status") == "success":
                # Create a follow-up message to continue the conversation with the content
                follow_up_messages = messages.copy()
                follow_up_messages.append({"role": "assistant", "content": updated_response})
                follow_up_messages.append({
                    "role": "user", 
                    "content": f"I've fetched the content from {tool_args.get('url')}. Please continue with your analysis or summary based on this information."
                })
                
                # Get a follow-up response
                follow_up_api_response = self.call_openai_api(follow_up_messages)
                follow_up_content = self.extract_response_content(follow_up_api_response)
                
                # Append the follow-up to the response
                processed_response["response"] = updated_response + "\n\n" + follow_up_content
                processed_response["follow_up"] = follow_up_content
            
            elif tool_name == "code_executor" and tool_result.get("status") == "success":
                # Create a follow-up message to explain the code execution results
                follow_up_messages = messages.copy()
                follow_up_messages.append({"role": "assistant", "content": updated_response})
                follow_up_messages.append({
                    "role": "user", 
                    "content": "I've executed the code. Please explain the results and what they mean."
                })
                
                # Get a follow-up response
                follow_up_api_response = self.call_openai_api(follow_up_messages)
                follow_up_content = self.extract_response_content(follow_up_api_response)
                
                # Append the follow-up to the response
                processed_response["response"] = updated_response + "\n\n" + follow_up_content
                processed_response["follow_up"] = follow_up_content
        
        # Add the user input and assistant response to conversation history
        self.add_message_to_history("user", user_input)
        
        # For the assistant's message, use the updated response if available
        assistant_response = processed_response.get("response", response_content)
        self.add_message_to_history("assistant", assistant_response)
        
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
        for line in plan_content.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('- ')):
                steps.append(line)
        
        return steps
    
    def set_auto_detect_tools(self, enabled: bool):
        """
        Enable or disable automatic tool detection.
        
        Args:
            enabled: Whether automatic tool detection should be enabled
        """
        self.auto_detect_tools = enabled
        logger.info(f"Automatic tool detection {'enabled' if enabled else 'disabled'}")
    
    def set_simulated_fallback(self, enabled: bool):
        """
        Enable or disable fallback to simulated flow.
        
        Args:
            enabled: Whether fallback to simulated flow should be enabled
        """
        self.use_simulated_fallback = enabled
        logger.info(f"Simulated flow fallback {'enabled' if enabled else 'disabled'}")
    
    def set_llm_tool_selection(self, enabled: bool):
        """
        Enable or disable LLM-based tool selection.
        
        Args:
            enabled: Whether LLM-based tool selection should be enabled
        """
        self.use_llm_tool_selection = enabled
        logger.info(f"LLM-based tool selection {'enabled' if enabled else 'disabled'}")
