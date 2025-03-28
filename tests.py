"""
Test script for the Syntient AI Assistant Platform.

This script tests the core functionality of the platform, including:
- Core assistant module
- Tool integration
- Memory system
- API endpoints
"""

import os
import sys
import json
import unittest
import requests
from unittest.mock import patch, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import components to test
from core import Assistant
from tools.base import Tool, ToolRegistry
from memory.simple import SimpleMemory
from config import get_config


class TestCoreAssistant(unittest.TestCase):
    """Test cases for the core assistant module."""
    
    def setUp(self):
        """Set up test environment."""
        # Use a mock API key for testing
        self.assistant = Assistant(api_key="test_api_key", model="gpt-3.5-turbo")
    
    @patch('requests.post')
    def test_call_openai_api(self, mock_post):
        """Test the OpenAI API call functionality."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "This is a test response."
                    }
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Call the API
        messages = [{"role": "user", "content": "Hello, world!"}]
        response = self.assistant.call_openai_api(messages)
        
        # Verify the response
        self.assertIn("choices", response)
        self.assertEqual(len(response["choices"]), 1)
        
        # Verify the API was called with the correct parameters
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "https://api.openai.com/v1/chat/completions")
        
        # Verify the payload
        payload = call_args[1]["json"]
        self.assertEqual(payload["model"], "gpt-3.5-turbo")
        self.assertEqual(payload["messages"], messages)
    
    def test_create_messages(self):
        """Test message creation for API requests."""
        # Test with a simple user input
        user_input = "Hello, world!"
        messages = self.assistant.create_messages(user_input, include_history=False)
        
        # Verify the messages structure
        self.assertEqual(len(messages), 2)  # System prompt + user input
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], user_input)
        
        # Test with conversation history
        self.assistant.add_message_to_history("user", "First message")
        self.assistant.add_message_to_history("assistant", "First response")
        
        messages = self.assistant.create_messages("Second message", include_history=True)
        
        # Verify the messages structure with history
        self.assertEqual(len(messages), 4)  # System prompt + 2 history messages + user input
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "First message")
        self.assertEqual(messages[2]["role"], "assistant")
        self.assertEqual(messages[2]["content"], "First response")
        self.assertEqual(messages[3]["role"], "user")
        self.assertEqual(messages[3]["content"], "Second message")


class TestToolIntegration(unittest.TestCase):
    """Test cases for tool integration."""
    
    def setUp(self):
        """Set up test environment."""
        self.registry = ToolRegistry()
        
        # Create a mock tool
        class MockTool(Tool):
            def __init__(self):
                super().__init__(name="mock_tool", description="A mock tool for testing")
            
            def execute(self, **kwargs):
                return {"result": "success", "args": kwargs}
            
            def _get_parameters_schema(self):
                return {
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"},
                        "param2": {"type": "integer"}
                    }
                }
        
        self.mock_tool = MockTool()
        self.registry.register_tool(self.mock_tool)
    
    def test_tool_registration(self):
        """Test tool registration and retrieval."""
        # Verify the tool was registered
        self.assertIn("mock_tool", self.registry.tools)
        
        # Retrieve the tool
        tool = self.registry.get_tool("mock_tool")
        self.assertEqual(tool.name, "mock_tool")
        self.assertEqual(tool.description, "A mock tool for testing")
    
    def test_tool_execution(self):
        """Test tool execution."""
        # Execute the tool
        result = self.registry.execute_tool("mock_tool", param1="test", param2=42)
        
        # Verify the result
        self.assertEqual(result["result"], "success")
        self.assertEqual(result["args"]["param1"], "test")
        self.assertEqual(result["args"]["param2"], 42)
    
    def test_tool_schema(self):
        """Test tool schema generation."""
        # Get the tool schema
        schema = self.mock_tool.get_schema()
        
        # Verify the schema
        self.assertEqual(schema["name"], "mock_tool")
        self.assertEqual(schema["description"], "A mock tool for testing")
        self.assertIn("parameters", schema)
        self.assertIn("properties", schema["parameters"])
        self.assertIn("param1", schema["parameters"]["properties"])
        self.assertIn("param2", schema["parameters"]["properties"])


class TestMemorySystem(unittest.TestCase):
    """Test cases for the memory system."""
    
    def setUp(self):
        """Set up test environment."""
        self.memory = SimpleMemory("test_memory")
    
    def test_add_and_get(self):
        """Test adding and retrieving data from memory."""
        # Add data to memory
        data = {"message": "Hello, world!", "timestamp": 1616161616}
        ref_id = self.memory.add(data)
        
        # Verify the reference ID
        self.assertIsNotNone(ref_id)
        self.assertTrue(isinstance(ref_id, str))
        
        # Retrieve the data
        retrieved_data = self.memory.get(ref_id)
        
        # Verify the retrieved data
        self.assertEqual(retrieved_data["message"], data["message"])
        self.assertEqual(retrieved_data["timestamp"], data["timestamp"])
    
    def test_search(self):
        """Test searching for data in memory."""
        # Add multiple data items
        self.memory.add({"message": "Hello, world!", "type": "greeting"})
        self.memory.add({"message": "Goodbye, world!", "type": "farewell"})
        self.memory.add({"message": "Hello again!", "type": "greeting"})
        
        # Search for greetings
        results = self.memory.search("Hello")
        
        # Verify the results
        self.assertEqual(len(results), 2)
        self.assertTrue(any("Hello, world!" in str(r) for r in results))
        self.assertTrue(any("Hello again!" in str(r) for r in results))
    
    def test_update_and_delete(self):
        """Test updating and deleting data in memory."""
        # Add data to memory
        data = {"message": "Original message", "type": "test"}
        ref_id = self.memory.add(data)
        
        # Update the data
        updated_data = {"message": "Updated message", "type": "test"}
        update_result = self.memory.update(ref_id, updated_data)
        
        # Verify the update
        self.assertTrue(update_result)
        retrieved_data = self.memory.get(ref_id)
        self.assertEqual(retrieved_data["message"], "Updated message")
        
        # Delete the data
        delete_result = self.memory.delete(ref_id)
        
        # Verify the deletion
        self.assertTrue(delete_result)
        self.assertIsNone(self.memory.get(ref_id))


class TestAPIEndpoints(unittest.TestCase):
    """Test cases for API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment for all tests in this class."""
        # Start the Flask app in a separate process
        # Note: In a real test, you would use Flask's test client or a running server
        # For this example, we'll mock the requests
        pass
    
    @patch('requests.post')
    def test_ask_endpoint(self, mock_post):
        """Test the /ask endpoint."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "This is a test response.",
            "type": "response",
            "reference_id": "test_ref_id",
            "user_id": "test_user"
        }
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        # Call the endpoint
        response = requests.post(
            "http://localhost:5000/ask",
            json={"message": "Hello, world!", "user_id": "test_user"}
        )
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["response"], "This is a test response.")
        self.assertEqual(data["type"], "response")
        self.assertEqual(data["user_id"], "test_user")
    
    @patch('requests.get')
    def test_health_endpoint(self, mock_get):
        """Test the /health endpoint."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {"status": "ok", "version": "1.0.0"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Call the endpoint
        response = requests.get("http://localhost:5000/health")
        
        # Verify the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "1.0.0")


class TestConfiguration(unittest.TestCase):
    """Test cases for configuration loading and validation."""
    
    @patch('os.getenv')
    def test_config_loading(self, mock_getenv):
        """Test configuration loading from environment variables."""
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            "OPENAI_API_KEY": "test_api_key",
            "OPENAI_MODEL": "gpt-3.5-turbo",
            "FLASK_APP": "app.py",
            "FLASK_ENV": "development",
            "FLASK_DEBUG": "False",
            "PORT": "5000",
            "DEFAULT_MEMORY_ID": "default",
            "USE_CHROMA": "False",
            "LOG_LEVEL": "INFO",
            "LOG_FILE": "test.log"
        }.get(key, default)
        
        # Load configuration
        with patch('dotenv.load_dotenv'):  # Mock dotenv.load_dotenv
            with patch('logging.basicConfig'):  # Mock logging.basicConfig
                config = get_config()
        
        # Verify the configuration
        self.assertEqual(config["openai"]["api_key"], "test_api_key")
        self.assertEqual(config["openai"]["model"], "gpt-3.5-turbo")
        self.assertEqual(config["flask"]["app"], "app.py")
        self.assertEqual(config["flask"]["env"], "development")
        self.assertEqual(config["flask"]["debug"], False)
        self.assertEqual(config["flask"]["port"], 5000)
        self.assertEqual(config["memory"]["default_id"], "default")
        self.assertEqual(config["memory"]["use_chroma"], False)
        self.assertEqual(config["logging"]["level"], "INFO")
        self.assertEqual(config["logging"]["file"], "test.log")


if __name__ == '__main__':
    unittest.main()
