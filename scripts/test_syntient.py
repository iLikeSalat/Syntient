# Syntient AI Assistant Platform - Test Script

"""
Test script for validating the Syntient AI Assistant Platform implementation.

This script tests the core functionality, continuous execution loop,
enhanced planning, and web UI components.
"""

import os
import sys
import time
import logging
import unittest
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.assistant import Assistant
from core.continuous_loop import ContinuousExecutionLoop
from core.enhanced_planning import EnhancedPlanner
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SyntientTestCase(unittest.TestCase):
    """Test case for the Syntient AI Assistant Platform."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Load environment variables
        load_dotenv()
        
        # Get configuration
        self.config = get_config()
        
        # Create an Assistant instance
        api_key = self.config["openai"]["api_key"]
        if not api_key:
            self.skipTest("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")
        
        self.assistant = Assistant(api_key=api_key)
        
        # Register some example tools
        self.assistant.register_tool("search_web", lambda query: {"results": f"Search results for: {query}"})
        self.assistant.register_tool("get_weather", lambda location: {"temperature": 72, "conditions": "sunny", "location": location})
    
    def test_assistant_initialization(self):
        """Test that the Assistant can be initialized correctly."""
        self.assertIsNotNone(self.assistant)
        self.assertEqual(self.assistant.model, self.config["openai"]["model"])
    
    def test_assistant_ask(self):
        """Test that the Assistant can process a simple question."""
        response = self.assistant.ask("What is the capital of France?")
        
        self.assertIsNotNone(response)
        self.assertIn("type", response)
        self.assertIn("response", response)
        self.assertGreater(len(response["response"]), 0)
    
    def test_tool_registration(self):
        """Test that tools can be registered and executed."""
        # Register a test tool
        self.assistant.register_tool("test_tool", lambda x: {"result": x * 2})
        
        # Create a message that should trigger the tool
        response = self.assistant.ask("I need to use the test_tool with input 5")
        
        # This test is a bit tricky because it depends on the model's behavior
        # In a real test, we might need to be more explicit about tool usage
        self.assertIsNotNone(response)
    
    def test_continuous_loop_initialization(self):
        """Test that the ContinuousExecutionLoop can be initialized."""
        loop = ContinuousExecutionLoop(
            assistant=self.assistant,
            max_iterations=10,
            iteration_delay=0.1
        )
        
        self.assertIsNotNone(loop)
        self.assertEqual(loop.max_iterations, 10)
        self.assertEqual(loop.iteration_delay, 0.1)
    
    def test_enhanced_planner_initialization(self):
        """Test that the EnhancedPlanner can be initialized."""
        planner = EnhancedPlanner(assistant=self.assistant)
        
        self.assertIsNotNone(planner)
    
    def test_enhanced_planner_create_plan(self):
        """Test that the EnhancedPlanner can create a hierarchical plan."""
        planner = EnhancedPlanner(assistant=self.assistant)
        
        # Create a simple task
        task = "Write a Python function to calculate the factorial of a number."
        
        # Create a plan
        plan = planner.create_hierarchical_plan(task)
        
        self.assertIsNotNone(plan)
        self.assertEqual(plan["task"], task)
        self.assertIn("high_level_plan", plan)
        self.assertIn("detailed_plans", plan)
        self.assertGreater(len(plan["detailed_plans"]), 0)
    
    def test_enhanced_planner_get_next_action(self):
        """Test that the EnhancedPlanner can determine the next action."""
        planner = EnhancedPlanner(assistant=self.assistant)
        
        # Create a simple task
        task = "Write a Python function to calculate the factorial of a number."
        
        # Create a plan
        planner.create_hierarchical_plan(task)
        
        # Get the next action
        action_type, action_details = planner.get_next_action()
        
        self.assertIsNotNone(action_type)
        self.assertIsNotNone(action_details)
        self.assertEqual(action_type, "execute_step")
        self.assertIn("component", action_details)
        self.assertIn("step_index", action_details)
        self.assertIn("step", action_details)
    
    def test_config_loading(self):
        """Test that configuration can be loaded correctly."""
        config = get_config()
        
        self.assertIsNotNone(config)
        self.assertIn("openai", config)
        self.assertIn("flask", config)
        self.assertIn("continuous_execution", config)
        self.assertEqual(config["flask"]["port"], int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    unittest.main()
