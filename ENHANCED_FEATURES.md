# Syntient AI Assistant Platform - Enhanced Features Documentation

## Overview

This document provides detailed information about the new features implemented in the Syntient AI Assistant Platform:

1. **Modular Tool Registry System**: A flexible system for registering and using external tools
2. **Tool Invocation Support**: Enhanced Assistant class that can detect and execute tool calls
3. **Quantum-Inspired Logic**: Advanced decision-making and optimization capabilities
4. **Example Tasks**: Demonstration tasks showing how to use the new features
5. **LLM Manager**: Abstraction layer for different LLM providers

## 1. Modular Tool Registry System

The modular tool registry system allows for easy plug-and-play tool integration. Tools are implemented as Python classes that inherit from the base `Tool` class.

### Tool Structure

Each tool follows a standard interface:

```python
from tools.base import Tool

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_custom_tool",
            description="Description of what my tool does"
        )
    
    def run(self, param1: str, param2: int = 42) -> dict:
        # Tool implementation goes here
        return {
            "result": f"Processed {param1} with parameter {param2}"
        }
```

### Using the Tool Registry

```python
from tools import registry

# List all available tools
tools = registry.list_tools()

# Get a specific tool
my_tool = registry.get_tool("my_custom_tool")

# Execute a tool
result = registry.execute_tool("my_custom_tool", param1="hello", param2=123)
```

### Adding New Tools

To add a new tool:

1. Create a new Python file in the `tools/` directory (e.g., `my_custom_tool.py`)
2. Define a class that inherits from `Tool`
3. Implement the required methods
4. The tool will be automatically discovered and registered

## 2. Tool Invocation Support

The Assistant class now supports detecting and executing tool calls in the format:

```
<<TOOL:tool_name {"param1": "value1", "param2": "value2"}>>
```

### Using Tool Invocation

```python
from core.assistant import Assistant

# Create an assistant
assistant = Assistant()

# Ask a question that might trigger tool usage
response = assistant.ask("Summarize this website: https://example.com")

# If the response contains a tool call, it will be automatically executed
# and the result will be appended to the response
```

### Tool Invocation Flow

1. The Assistant receives a user query
2. If the LLM's response contains a tool call in the format `<<TOOL:tool_name {...}>>`, it's detected
3. The tool is looked up in the registry
4. The tool is executed with the provided parameters
5. The tool result is appended to the response
6. The updated response is returned to the user

## 3. Quantum-Inspired Logic

The quantum-inspired logic module provides advanced decision-making and optimization capabilities.

### Quantum Decision Making

```python
from core.quantum_logic import quantum_logic

# Create a decision maker
options = ["Option A", "Option B", "Option C"]
decision_maker = quantum_logic.create_decision_maker(options)

# Add uncertainty
decision_maker.add_uncertainty(0.7)

# Add preference for a specific option
decision_maker.add_preference(1, 0.3)  # Prefer Option B with strength 0.3

# Get probabilities for all options
probabilities = decision_maker.get_decision_probabilities()
print(probabilities)

# Make a decision
selected_option, option_index, probability = decision_maker.make_decision()
print(f"Selected: {selected_option} with probability {probability}")
```

### Quantum Optimization

```python
from core.quantum_logic import quantum_logic
import numpy as np

# Define a cost function to minimize
def cost_function(x):
    return np.sum(x**2)  # Simple quadratic function

# Perform quantum-inspired optimization
solution, cost = quantum_logic.optimize(
    cost_function=cost_function,
    dimensions=5,
    num_iterations=1000
)

print(f"Optimized solution: {solution}")
print(f"Cost: {cost}")
```

### Probabilistic Reasoning

```python
from core.quantum_logic import quantum_logic

# Define hypotheses
hypotheses = ["Hypothesis A", "Hypothesis B", "Hypothesis C"]

# Define prior probabilities
priors = [0.2, 0.5, 0.3]

# Define evidence impact
evidence = [(1, 0.4)]  # Evidence supports Hypothesis B with strength 0.4

# Perform probabilistic reasoning
posteriors = quantum_logic.probabilistic_reasoning(
    hypotheses=hypotheses,
    prior_probabilities=priors,
    evidence_impact=evidence
)

print(posteriors)
```

## 4. Example Tasks

The platform includes example tasks that demonstrate the capabilities of the assistant, including tool usage.

### Available Example Tasks

- **Website Summary**: Summarizes the content of a website using the browser_use tool
- **Code Execution**: Executes a Python code snippet using the code_executor tool
- **File Analysis**: Analyzes the content of a file using the file_parser tool
- **Web Search**: Searches the web for information using the web_search tool
- **Quantum Decision**: Makes a decision using quantum-inspired logic

### Using Example Tasks

```python
from core.assistant import Assistant
from core.example_task_handler import ExampleTaskHandler

# Create an assistant
assistant = Assistant()

# Create an example task handler
task_handler = ExampleTaskHandler(assistant)

# Execute a website summary task
result = task_handler.execute_website_summary_task("https://example.com")

# Execute a quantum decision task
options = ["Option A", "Option B", "Option C"]
result = task_handler.execute_quantum_decision_task(options)
```

### Web API for Example Tasks

The platform includes a web API for executing example tasks:

- `GET /api/example_tasks/list`: List all available example tasks
- `POST /api/example_tasks/execute`: Execute an example task

Example request:
```json
{
  "task_id": "website_summary",
  "params": {
    "url": "https://example.com"
  }
}
```

## 5. LLM Manager

The LLM Manager provides an abstraction layer for different LLM providers, allowing easy switching between OpenAI, Claude, Mistral, Ollama, and others.

### Supported Providers

- **OpenAI**: GPT-3.5, GPT-4, etc.
- **Anthropic Claude**: Claude 3 Opus, Sonnet, Haiku, etc.
- **Mistral AI**: Mistral Large, Medium, Small, etc.
- **Ollama**: Local models like Llama 3, Mistral, Mixtral, etc.

### Using the LLM Manager

```python
from core.llm_manager import llm_manager

# Get available providers
providers = llm_manager.get_available_providers()
print(providers)

# Get available models for a provider
models = llm_manager.get_available_models("openai")
print(models)

# Set the default provider
llm_manager.set_default_provider("anthropic")

# Generate a completion
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello, who are you?"}
]

response = llm_manager.generate_completion(
    messages=messages,
    temperature=0.7,
    max_tokens=100
)

# Extract the content
content = llm_manager.extract_response_content(response)
print(content)

# Generate a completion with a specific provider
response = llm_manager.generate_completion(
    messages=messages,
    provider_name="mistral",
    model="mistral-large-latest"
)
```

### Configuration

The LLM Manager uses environment variables for API keys:

- `OPENAI_API_KEY`: API key for OpenAI
- `ANTHROPIC_API_KEY`: API key for Anthropic Claude
- `MISTRAL_API_KEY`: API key for Mistral AI

For Ollama, it connects to the local Ollama server (default: http://localhost:11434).

## Integration Example

Here's an example that combines all the new features:

```python
from core.assistant import Assistant
from core.quantum_logic import quantum_logic
from core.example_task_handler import ExampleTaskHandler
from core.llm_manager import llm_manager
from tools import registry

# Set up the LLM manager
llm_manager.set_default_provider("openai")

# Create an assistant
assistant = Assistant()

# Register a custom tool
from tools.base import Tool

class CustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="custom_tool",
            description="A custom tool for demonstration"
        )
    
    def run(self, input: str) -> dict:
        return {
            "result": f"Processed: {input}"
        }

registry.register_tool(CustomTool())

# Create an example task handler
task_handler = ExampleTaskHandler(assistant)

# Execute a task that uses tools
result = task_handler.execute_website_summary_task("https://example.com")

# Use quantum-inspired logic
options = ["Option A", "Option B", "Option C"]
decision_maker = quantum_logic.create_decision_maker(options)
decision_maker.add_uncertainty(0.5)
selected_option, _, _ = decision_maker.make_decision()

# Ask the assistant a question that might use the custom tool
response = assistant.ask(f"Process this input with the custom tool: {selected_option}")

print(response)
```

## Next Steps

To further enhance the Syntient AI Assistant Platform, consider:

1. Implementing more specialized tools for specific domains
2. Adding authentication to the web UI
3. Integrating with external services like GitHub or Jira
4. Implementing a more sophisticated memory system with vector storage
5. Adding support for multimodal inputs and outputs
