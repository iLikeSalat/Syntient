"""
Example task handler for the Syntient AI Assistant Platform.

This module provides handlers for example tasks that demonstrate
the capabilities of the assistant, including tool usage.
"""

import logging
import json
from typing import Dict, Any, List, Optional

from core.assistant import Assistant
from core.quantum_logic import quantum_logic
from core.example_tasks import ExampleTasks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExampleTaskHandler:
    """
    Handler for example tasks that demonstrate the capabilities of the assistant.
    """
    
    def __init__(self, assistant: Assistant):
        """
        Initialize the example task handler.
        
        Args:
            assistant: Assistant instance to use for task execution
        """
        self.assistant = assistant
    
    def execute_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """
        Execute an example task.
        
        Args:
            task_id: ID of the task to execute
            **kwargs: Parameters for the task
            
        Returns:
            Result of the task execution
        """
        task = ExampleTasks.get_task_by_id(task_id)
        if not task:
            return {"error": f"Task with ID '{task_id}' not found"}
        
        # Get the task prompt
        prompt = ExampleTasks.get_task_prompt(task_id, **kwargs)
        
        # Execute the task
        logger.info(f"Executing example task: {task_id}")
        result = self.assistant.ask(prompt)
        
        return {
            "task_id": task_id,
            "task_name": task.get("name", ""),
            "prompt": prompt,
            "result": result
        }
    
    def execute_website_summary_task(self, url: str) -> Dict[str, Any]:
        """
        Execute a website summary task.
        
        This task demonstrates the use of the browser_use tool.
        
        Args:
            url: URL of the website to summarize
            
        Returns:
            Result of the task execution
        """
        # Create a specialized prompt that encourages tool usage
        prompt = f"""
        Please summarize the content of this website: {url}
        
        To accomplish this task, you should:
        1. Use the browser_use tool to access the website
        2. Extract the main content
        3. Create a concise summary
        
        Make sure to use the browser_use tool with the URL parameter.
        """
        
        # Execute the task
        logger.info(f"Executing website summary task for URL: {url}")
        result = self.assistant.ask(prompt)
        
        return {
            "task_id": "website_summary",
            "task_name": "Website Summary",
            "url": url,
            "prompt": prompt,
            "result": result
        }
    
    def execute_code_execution_task(self, code: str) -> Dict[str, Any]:
        """
        Execute a code execution task.
        
        This task demonstrates the use of the code_executor tool.
        
        Args:
            code: Code to execute
            
        Returns:
            Result of the task execution
        """
        # Create a specialized prompt that encourages tool usage
        prompt = f"""
        Please execute this code and explain the results:
        
        ```python
        {code}
        ```
        
        To accomplish this task, you should:
        1. Use the code_executor tool to run the code
        2. Analyze the results
        3. Provide an explanation
        
        Make sure to use the code_executor tool with the code parameter.
        """
        
        # Execute the task
        logger.info(f"Executing code execution task")
        result = self.assistant.ask(prompt)
        
        return {
            "task_id": "code_execution",
            "task_name": "Code Execution",
            "code": code,
            "prompt": prompt,
            "result": result
        }
    
    def execute_file_analysis_task(self, file_path: str) -> Dict[str, Any]:
        """
        Execute a file analysis task.
        
        This task demonstrates the use of the file_parser tool.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Result of the task execution
        """
        # Create a specialized prompt that encourages tool usage
        prompt = f"""
        Please analyze the content of this file: {file_path}
        
        To accomplish this task, you should:
        1. Use the file_parser tool to read the file
        2. Analyze the content
        3. Provide insights and summary
        
        Make sure to use the file_parser tool with the file_path parameter.
        """
        
        # Execute the task
        logger.info(f"Executing file analysis task for file: {file_path}")
        result = self.assistant.ask(prompt)
        
        return {
            "task_id": "file_analysis",
            "task_name": "File Analysis",
            "file_path": file_path,
            "prompt": prompt,
            "result": result
        }
    
    def execute_web_search_task(self, query: str) -> Dict[str, Any]:
        """
        Execute a web search task.
        
        This task demonstrates the use of the web_search tool.
        
        Args:
            query: Search query
            
        Returns:
            Result of the task execution
        """
        # Create a specialized prompt that encourages tool usage
        prompt = f"""
        Please search the web for information about: {query}
        
        To accomplish this task, you should:
        1. Use the web_search tool to find relevant information
        2. Analyze the search results
        3. Provide a comprehensive answer
        
        Make sure to use the web_search tool with the query parameter.
        """
        
        # Execute the task
        logger.info(f"Executing web search task for query: {query}")
        result = self.assistant.ask(prompt)
        
        return {
            "task_id": "web_search",
            "task_name": "Web Search",
            "query": query,
            "prompt": prompt,
            "result": result
        }
    
    def execute_quantum_decision_task(self, options: List[str]) -> Dict[str, Any]:
        """
        Execute a quantum decision making task.
        
        This task demonstrates the use of quantum-inspired logic.
        
        Args:
            options: List of decision options
            
        Returns:
            Result of the task execution
        """
        # Create a specialized prompt that encourages quantum logic usage
        options_text = ", ".join(options)
        prompt = f"""
        Please help me make a decision between these options using quantum-inspired logic: {options_text}
        
        To accomplish this task, you should:
        1. Consider the options: {options_text}
        2. Apply quantum-inspired decision making
        3. Provide a recommendation with probabilities
        
        Use quantum-inspired logic to handle uncertainty and provide a nuanced decision.
        """
        
        # Execute the task with the assistant
        logger.info(f"Executing quantum decision task for options: {options_text}")
        assistant_result = self.assistant.ask(prompt)
        
        # Also use the quantum logic directly for comparison
        decision_maker = quantum_logic.create_decision_maker(options)
        
        # Add some uncertainty
        decision_maker.add_uncertainty(0.7)
        
        # Get the probabilities
        quantum_probabilities = decision_maker.get_decision_probabilities()
        
        # Make a decision
        selected_option, option_index, probability = decision_maker.make_decision()
        
        return {
            "task_id": "quantum_decision",
            "task_name": "Quantum Decision Making",
            "options": options,
            "prompt": prompt,
            "assistant_result": assistant_result,
            "quantum_result": {
                "selected_option": selected_option,
                "probability": probability,
                "all_probabilities": quantum_probabilities
            }
        }
