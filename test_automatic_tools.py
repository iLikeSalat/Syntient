"""
Test script for automatic tool detection and execution.

This script tests the functionality of the automatic tool detection and execution
features, including the fallback to simulated flow.
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

def test_automatic_tool_detection():
    """Test the automatic tool detection and execution functionality."""
    print("Testing automatic tool detection and execution...\n")
    
    # Use the provided API key
    api_key = "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"
    
    assistant = Assistant(api_key=api_key)
    
    # Test cases
    test_cases = [
        {
            "name": "URL Summary",
            "input": "Summarize https://fcbsa.ch",
            "expected_tool": "browser_use"
        },
        {
            "name": "Code Execution",
            "input": "Execute this python code:\nprint('Hello, world!')\nresult = 2 + 2",
            "expected_tool": "code_executor"
        },
        {
            "name": "Simulated Web Search",
            "input": "Search for information about climate change",
            "expected_type": "simulated"
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
                    print(f"✅ Successfully detected and used {tool_name} tool")
                    
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
    test_automatic_tool_detection()
