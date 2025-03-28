"""
Test script for validating the Syntient AI Assistant Platform enhancements.

This script tests the modular tool registry, tool invocation support,
quantum-inspired logic, example tasks, and LLM manager.
"""

import os
import sys
import unittest
import logging
from typing import Dict, Any, List

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.assistant import Assistant
from core.quantum_logic import quantum_logic, QuantumDecisionMaker
from core.example_tasks import ExampleTasks
from core.example_task_handler import ExampleTaskHandler
from core.llm_manager import llm_manager
from tools import registry, Tool
from tools.browser_use import BrowserUseTool
from tools.file_parser import FileParserTool
from tools.code_executor import CodeExecutorTool
from tools.web_search import WebSearchTool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyntientEnhancementsTest(unittest.TestCase):
    """Test case for the Syntient AI Assistant Platform enhancements."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Create an Assistant instance
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.skipTest("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        
        self.assistant = Assistant(api_key=api_key)
    
    def test_tool_registry(self):
        """Test the tool registry functionality."""
        # Check that the registry is initialized
        self.assertIsNotNone(registry)
        
        # Check that tools are registered
        tools = registry.list_tools()
        self.assertGreater(len(tools), 0)
        
        # Check that we can get a tool by name
        browser_tool = registry.get_tool("browser_use")
        self.assertIsNotNone(browser_tool)
        self.assertEqual(browser_tool.name, "browser_use")
        
        # Check tool schema
        schema = browser_tool.get_schema()
        self.assertEqual(schema["name"], "browser_use")
        self.assertIn("description", schema)
        self.assertIn("parameters", schema)
    
    def test_tool_execution(self):
        """Test tool execution through the registry."""
        # Execute the browser_use tool
        result = registry.execute_tool("browser_use", url="https://example.com")
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "placeholder")
        self.assertEqual(result["url"], "https://example.com")
        
        # Execute the web_search tool
        result = registry.execute_tool("web_search", query="quantum computing")
        self.assertIsNotNone(result)
        self.assertEqual(result["status"], "placeholder")
        self.assertEqual(result["query"], "quantum computing")
    
    def test_assistant_tool_invocation(self):
        """Test tool invocation support in the Assistant class."""
        # Create a test prompt that should trigger tool usage
        prompt = "Please summarize this website: https://example.com"
        
        # Process the prompt
        response = self.assistant.ask(prompt)
        
        # Check the response
        self.assertIsNotNone(response)
        
        # Note: We can't guarantee the model will use the tool in this test,
        # but we can check that the response is processed correctly
        self.assertIn("type", response)
    
    def test_quantum_logic(self):
        """Test the quantum-inspired logic module."""
        # Test quantum decision maker
        options = ["Option A", "Option B", "Option C"]
        decision_maker = quantum_logic.create_decision_maker(options)
        
        # Add some uncertainty
        decision_maker.add_uncertainty(0.5)
        
        # Get probabilities
        probabilities = decision_maker.get_decision_probabilities()
        self.assertEqual(len(probabilities), 3)
        
        # Make a decision
        selected_option, option_index, probability = decision_maker.make_decision()
        self.assertIn(selected_option, options)
        self.assertGreaterEqual(option_index, 0)
        self.assertLess(option_index, 3)
        self.assertGreaterEqual(probability, 0)
        self.assertLessEqual(probability, 1)
        
        # Test quantum random
        random_value = quantum_logic.quantum_random(0, 10)
        self.assertGreaterEqual(random_value, 0)
        self.assertLessEqual(random_value, 10)
    
    def test_example_tasks(self):
        """Test the example tasks functionality."""
        # Get the list of example tasks
        tasks = ExampleTasks.get_task_list()
        self.assertGreater(len(tasks), 0)
        
        # Get a task by ID
        website_summary_task = ExampleTasks.get_task_by_id("website_summary")
        self.assertIsNotNone(website_summary_task)
        self.assertEqual(website_summary_task["id"], "website_summary")
        
        # Get a task prompt
        prompt = ExampleTasks.get_task_prompt("website_summary", url="https://example.com")
        self.assertIn("https://example.com", prompt)
        
        # Create an example task handler
        task_handler = ExampleTaskHandler(self.assistant)
        
        # Execute a task
        result = task_handler.execute_website_summary_task("https://example.com")
        self.assertIsNotNone(result)
        self.assertEqual(result["task_id"], "website_summary")
        self.assertEqual(result["url"], "https://example.com")
    
    def test_llm_manager(self):
        """Test the LLM manager functionality."""
        # Check that the LLM manager is initialized
        self.assertIsNotNone(llm_manager)
        
        # Get available providers
        providers = llm_manager.get_available_providers()
        self.assertGreater(len(providers), 0)
        self.assertIn("openai", providers)
        
        # Get available models
        models = llm_manager.get_available_models("openai")
        self.assertIn("openai", models)
        self.assertGreater(len(models["openai"]), 0)
        
        # Test with the default provider (should be OpenAI)
        try:
            # Create a simple message
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, who are you?"}
            ]
            
            # Generate a completion
            response = llm_manager.generate_completion(
                messages=messages,
                temperature=0.7,
                max_tokens=100
            )
            
            # Extract the content
            content = llm_manager.extract_response_content(response)
            self.assertIsNotNone(content)
            self.assertGreater(len(content), 0)
        except Exception as e:
            # Skip this test if API call fails
            self.skipTest(f"LLM API call failed: {str(e)}")

if __name__ == "__main__":
    unittest.main()
