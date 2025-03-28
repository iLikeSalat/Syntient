"""
Test script for LLM-based tool selection.

This script tests the functionality of the LLM-based tool selection feature,
which replaces the regex-based TaskDetector with a more flexible and
semantically smarter approach.
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the Syntient directory to the Python path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.assistant import Assistant

# Load environment variables
load_dotenv()

def test_llm_tool_selection():
    """Test the LLM-based tool selection functionality."""
    print("Testing LLM-based tool selection...\n")
    
    # Initialize the assistant with the API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        api_key = input("Enter your OpenAI API key: ")
    
    assistant = Assistant(api_key=api_key)
    
    # Ensure LLM tool selection is enabled
    assistant.set_llm_tool_selection(True)
    
    # Test cases
    test_cases = [
        {
            "name": "URL Summary",
            "input": "Can you give me a summary of the content at https://fcbsa.ch?",
            "expected_tool": "browser_use"
        },
        {
            "name": "Code Execution",
            "input": "I need to calculate the factorial of 5. Can you run some Python code to do this?",
            "expected_tool": "code_executor"
        },
        {
            "name": "Web Search",
            "input": "What are the latest developments in quantum computing?",
            "expected_tool": "web_search"
        },
        {
            "name": "Regular Question",
            "input": "What is the capital of France?",
            "expected_type": "response"
        }
    ]
    
    # Run test cases
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['name']} ---")
        print(f"Input: {test_case['input']}")
        
        # Process the input
        response = assistant.ask(test_case['input'])
        
        # Print the response type
        print(f"Response type: {response.get('type', 'unknown')}")
        
        # Check if the response matches expectations
        if 'expected_tool' in test_case:
            if response.get('type') == 'tool_call' or 'detected_tool' in response:
                tool_name = response.get('detected_tool') or response.get('tool')
                if tool_name == test_case['expected_tool']:
                    print(f"✅ LLM successfully selected {tool_name} tool")
                    
                    # Print tool result status
                    if 'tool_result' in response:
                        print(f"Tool result status: {response['tool_result'].get('status', 'unknown')}")
                else:
                    print(f"❌ Expected {test_case['expected_tool']} tool, but got {tool_name}")
            else:
                print(f"❌ Expected tool call, but got {response.get('type', 'unknown')}")
        
        elif 'expected_type' in test_case:
            if response.get('type') == test_case['expected_type']:
                print(f"✅ Response type matches expected: {test_case['expected_type']}")
            else:
                print(f"❌ Expected {test_case['expected_type']} type, but got {response.get('type', 'unknown')}")
        
        # Print a snippet of the response
        if 'response' in response:
            response_text = response['response']
            snippet = response_text[:200] + "..." if len(response_text) > 200 else response_text
            print(f"\nResponse snippet: {snippet}")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_llm_tool_selection()
