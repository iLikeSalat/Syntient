"""
Example tasks module for the Syntient AI Assistant Platform.

This module provides example tasks that demonstrate the capabilities
of the assistant, including tool usage and quantum-inspired logic.
"""

import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ExampleTasks:
    """
    Collection of example tasks that demonstrate the capabilities of the assistant.
    """
    
    @staticmethod
    def get_task_list() -> List[Dict[str, str]]:
        """
        Get a list of available example tasks.
        
        Returns:
            List of dictionaries containing task ID and description
        """
        return [
            {
                "id": "website_summary",
                "name": "Website Summary",
                "description": "Summarize the content of a website",
                "prompt": "Summarize this website: https://example.com"
            },
            {
                "id": "code_execution",
                "name": "Code Execution",
                "description": "Execute a Python code snippet",
                "prompt": "Execute this Python code: print('Hello, world!')"
            },
            {
                "id": "file_analysis",
                "name": "File Analysis",
                "description": "Analyze the content of a file",
                "prompt": "Analyze this file: /path/to/example.txt"
            },
            {
                "id": "web_search",
                "name": "Web Search",
                "description": "Search the web for information",
                "prompt": "Search for information about quantum computing"
            },
            {
                "id": "quantum_decision",
                "name": "Quantum Decision Making",
                "description": "Make a decision using quantum-inspired logic",
                "prompt": "Help me decide between these options: Option A, Option B, Option C"
            }
        ]
    
    @staticmethod
    def get_task_by_id(task_id: str) -> Optional[Dict[str, str]]:
        """
        Get an example task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Dictionary containing task details, or None if not found
        """
        tasks = ExampleTasks.get_task_list()
        for task in tasks:
            if task["id"] == task_id:
                return task
        return None
    
    @staticmethod
    def get_task_prompt(task_id: str, **kwargs) -> str:
        """
        Get the prompt for an example task, with optional parameter substitution.
        
        Args:
            task_id: ID of the task
            **kwargs: Parameters to substitute in the prompt
            
        Returns:
            Task prompt with parameters substituted
        """
        task = ExampleTasks.get_task_by_id(task_id)
        if not task:
            raise ValueError(f"Task with ID '{task_id}' not found")
        
        prompt = task["prompt"]
        
        # Substitute parameters
        for key, value in kwargs.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))
        
        return prompt
    
    @staticmethod
    def get_website_summary_task(url: str) -> str:
        """
        Get a task prompt for summarizing a website.
        
        Args:
            url: URL of the website to summarize
            
        Returns:
            Task prompt for website summarization
        """
        return f"Please summarize the content of this website: {url}"
    
    @staticmethod
    def get_code_execution_task(code: str) -> str:
        """
        Get a task prompt for executing code.
        
        Args:
            code: Code to execute
            
        Returns:
            Task prompt for code execution
        """
        return f"Please execute this code and explain the results:\n\n```python\n{code}\n```"
    
    @staticmethod
    def get_file_analysis_task(file_path: str) -> str:
        """
        Get a task prompt for analyzing a file.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Task prompt for file analysis
        """
        return f"Please analyze the content of this file: {file_path}"
    
    @staticmethod
    def get_web_search_task(query: str) -> str:
        """
        Get a task prompt for searching the web.
        
        Args:
            query: Search query
            
        Returns:
            Task prompt for web search
        """
        return f"Please search the web for information about: {query}"
    
    @staticmethod
    def get_quantum_decision_task(options: List[str]) -> str:
        """
        Get a task prompt for quantum-inspired decision making.
        
        Args:
            options: List of decision options
            
        Returns:
            Task prompt for quantum-inspired decision making
        """
        options_text = ", ".join(options)
        return f"Please help me make a decision between these options using quantum-inspired logic: {options_text}"
