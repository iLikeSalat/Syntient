# Syntient Automatic Tool Detection Guide

## Overview

This guide explains the new automatic tool detection and execution functionality added to the Syntient AI Assistant Platform. The system now automatically detects when user inputs can be handled by tools, executes the appropriate tools, and falls back to simulated behavior when no tools apply.

## Key Features

1. **Automatic Tool Detection**: The system automatically detects when user inputs like "Summarize https://example.com" should trigger tools
2. **Real Tool Execution**: Tools are executed with real functionality instead of simulated responses
3. **Simulated Fallback**: For tasks that don't match any tool patterns, the system falls back to simulated behavior
4. **Seamless Integration**: All of this happens automatically without requiring explicit tool calls

## Components Added

### 1. TaskDetector

The `TaskDetector` class in `core/task_detector.py` is responsible for detecting tasks that can be handled by tools:

- Uses regex patterns to identify different types of tasks
- Currently detects URL summary tasks and code execution tasks
- Can be easily extended to detect other types of tasks

### 2. SimulatedFlowHandler

The `SimulatedFlowHandler` class in `core/simulated_flow.py` provides fallback behavior:

- Detects tasks that should be handled by simulated flow
- Generates realistic simulated responses for different types of tasks
- Maintains the existing simulated behavior for tasks that can't be handled by real tools

### 3. Updated Assistant

The `Assistant` class in `core/assistant.py` has been updated to:

- Integrate the TaskDetector and SimulatedFlowHandler
- Automatically detect and execute tools when appropriate
- Include real tool results in responses
- Generate follow-up responses that analyze or explain tool results

## How to Use

### URL Summary

To summarize a website, simply ask the assistant to summarize a URL:

```
Summarize https://example.com
```

The system will:
1. Automatically detect this as a URL summary task
2. Execute the browser_use tool to fetch the content
3. Include the real content in the response
4. Generate a summary based on the actual content

### Code Execution

To execute Python code, ask the assistant to execute the code:

```
Execute this Python code:
print('Hello, world!')
result = 2 + 2
```

The system will:
1. Automatically detect this as a code execution task
2. Execute the code_executor tool to run the code
3. Include the real execution results in the response
4. Explain what the code does and what the results mean

### Other Tasks

For tasks that don't match any tool patterns, the system will fall back to simulated behavior:

```
Search for information about climate change
```

The system will:
1. Detect that this is a simulated web search task
2. Generate a realistic simulated response
3. Indicate that this is a simulated response

## Configuration Options

The Assistant class includes two configuration options:

1. **auto_detect_tools**: Enable or disable automatic tool detection
   ```python
   assistant.set_auto_detect_tools(True)  # Enable (default)
   assistant.set_auto_detect_tools(False)  # Disable
   ```

2. **use_simulated_fallback**: Enable or disable fallback to simulated flow
   ```python
   assistant.set_simulated_fallback(True)  # Enable (default)
   assistant.set_simulated_fallback(False)  # Disable
   ```

## Testing

A test script is provided at `test_automatic_tools.py` to verify the functionality:

```bash
python test_automatic_tools.py
```

The test script includes test cases for:
- URL summary detection and execution
- Code execution detection and execution
- Simulated fallback for tasks that don't match tool patterns
- Regular questions

## Extending the System

### Adding New Tool Detection Patterns

To add new patterns for detecting tasks that can be handled by tools, modify the `patterns` dictionary in the `TaskDetector` class:

```python
self.patterns = {
    "url_summary": [
        r"(?i)summarize\s+(https?://\S+)",
        # Add more patterns here
    ],
    "code_execution": [
        r"(?i)execute\s+(?:this|the\s+following)\s+(?:python\s+)?code[:\n]+(.*?)(?:\n\s*$|\Z)",
        # Add more patterns here
    ],
    # Add new task types here
}
```

### Adding New Simulated Task Types

To add new types of simulated tasks, modify the `patterns` dictionary in the `SimulatedFlowHandler` class and add a corresponding response generation method:

```python
self.patterns = {
    "web_search": [
        r"(?i)search\s+(?:for|about)\s+(.*)",
        # Add more patterns here
    ],
    # Add new simulated task types here
}
```

## Example Workflow

1. User asks: "Summarize https://fcbsa.ch"
2. TaskDetector identifies this as a URL summary task
3. Assistant executes the browser_use tool with the URL
4. Tool fetches and processes the content from the website
5. Assistant includes the tool result in the response
6. Assistant generates a follow-up response analyzing the content
7. User receives a comprehensive response with real website content

## Troubleshooting

If automatic tool detection isn't working as expected:

1. Check that the input matches one of the patterns in the TaskDetector
2. Verify that the required tools (browser_use, code_executor) are properly registered
3. Ensure that the auto_detect_tools flag is enabled
4. Check the logs for any error messages during tool execution

If simulated fallback isn't working as expected:

1. Check that the input matches one of the patterns in the SimulatedFlowHandler
2. Verify that the use_simulated_fallback flag is enabled
3. Check that no tool patterns matched the input (tools take precedence over simulation)

## Conclusion

The automatic tool detection and execution functionality makes the Syntient AI Assistant Platform more powerful and user-friendly. Users can now simply ask for tasks to be performed in natural language, and the system will automatically use the appropriate tools to provide real, accurate responses.
