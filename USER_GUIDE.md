# Syntient AI Assistant Platform - User Guide

## Overview

This guide provides instructions for using the enhanced Syntient AI Assistant Platform, which now includes:

1. **Continuous Execution Loop**: Enables the assistant to work on tasks persistently until completion
2. **Enhanced Reasoning and Planning**: Provides hierarchical task decomposition and advanced planning capabilities
3. **Simple Web UI**: Offers an intuitive interface for interacting with the assistant

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/iLikeSalat/Syntient.git
   cd Syntient
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   PORT=5000
   FLASK_DEBUG=True
   OPENAI_MODEL=gpt-3.5-turbo
   MAX_ITERATIONS=100
   ITERATION_DELAY=1.0
   ```

## Running the Web UI

1. Start the Flask application:
   ```
   python app.py
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

3. You'll see the Syntient AI Assistant web interface with three main sections:
   - **Task Configuration**: Define tasks and enable continuous execution
   - **Conversation**: Chat with the assistant
   - **Task Progress**: Monitor the progress of active tasks

## Using the Continuous Execution Loop

The continuous execution loop allows the assistant to work on complex tasks persistently until completion.

### Via Web UI

1. Enter your task description in the "Task Description" field
2. Check the "Enable continuous execution" checkbox
3. Click "Submit Task"
4. Monitor progress in the "Task Progress" section
5. Provide feedback in the chat if needed

### Via Python API

```python
from core.assistant import Assistant
from core.continuous_loop import ContinuousExecutionLoop

# Initialize the assistant
assistant = Assistant(api_key="your_api_key_here")

# Create a continuous execution loop
loop = ContinuousExecutionLoop(
    assistant=assistant,
    max_iterations=100,
    iteration_delay=1.0
)

# Define a task
task = "Create a Python function that calculates the Fibonacci sequence"

# Start the execution loop
result = loop.start(task)

# Check the result
print(f"Task completed with status: {result['status']}")
print(f"Total iterations: {result['iterations']}")
```

## Using Enhanced Planning

The enhanced planning system provides hierarchical task decomposition and detailed execution planning.

### Via Python API

```python
from core.assistant import Assistant
from core.enhanced_planning import EnhancedPlanner

# Initialize the assistant
assistant = Assistant(api_key="your_api_key_here")

# Create an enhanced planner
planner = EnhancedPlanner(assistant=assistant)

# Define a task
task = "Build a personal finance tracking application"

# Create a hierarchical plan
plan = planner.create_hierarchical_plan(task)

# Get the plan summary
summary = planner.get_plan_summary()
print(f"Task: {summary['task']}")
print(f"Overall Progress: {summary['overall_progress'] * 100:.1f}%")

# Execute steps
while True:
    # Get the next action
    action_type, action_details = planner.get_next_action()
    
    if action_type == "plan_completed":
        print("Plan completed!")
        break
    
    if action_type == "execute_step":
        component = action_details["component"]
        step_index = action_details["step_index"]
        step = action_details["step"]
        
        print(f"Executing step {step_index + 1} of component '{component}':")
        print(f"  {step}")
        
        # Execute the step (implementation depends on the specific step)
        # ...
        
        # Mark the step as completed
        planner.update_step_status(component, step_index, completed=True)
```

## API Endpoints

The Syntient AI Assistant provides the following API endpoints:

### Simple Question/Answer

```
POST /api/ask
Content-Type: application/json

{
  "message": "What is the capital of France?",
  "user_id": "user123"
}
```

### Start a Task

```
POST /api/task/start
Content-Type: application/json

{
  "task": "Create a Python function that calculates the Fibonacci sequence",
  "user_id": "user123",
  "continuous_mode": true
}
```

### Get Task Status

```
GET /api/task/{task_id}/status
```

### Provide Feedback

```
POST /api/task/{task_id}/feedback
Content-Type: application/json

{
  "feedback": "The function should handle negative numbers as well"
}
```

### Cancel Task

```
POST /api/task/{task_id}/cancel
```

## Example Use Cases

### Coding Projects

The continuous execution loop is particularly useful for coding projects:

1. Define a coding task: "Create a REST API for a todo list application using Flask"
2. Enable continuous execution
3. The assistant will:
   - Break down the task into components
   - Implement each component
   - Test the implementation
   - Debug any issues
   - Continue until the project is complete

### Research and Analysis

For research tasks, the enhanced planning system helps organize complex information:

1. Define a research task: "Research the impact of AI on healthcare"
2. The assistant will:
   - Create a hierarchical plan for the research
   - Gather information for each component
   - Analyze and synthesize the information
   - Present findings in a structured format

## Troubleshooting

### API Key Issues

If you encounter errors related to the OpenAI API key:

1. Ensure your API key is correctly set in the `.env` file
2. Check that your API key has sufficient quota
3. Verify that the API key has the necessary permissions

### Continuous Execution Loop Stalls

If the continuous execution loop appears to stall:

1. Check the logs for any error messages
2. Ensure the task is clearly defined
3. Try breaking the task into smaller, more manageable pieces

### Web UI Connection Issues

If you cannot connect to the web UI:

1. Ensure the Flask application is running
2. Check that you're using the correct port (default is 5000)
3. Verify that no firewall is blocking the connection

## Next Steps

To further enhance the Syntient AI Assistant Platform, consider:

1. Implementing more specialized tools for specific domains
2. Adding authentication to the web UI
3. Integrating with external services like GitHub or Jira
4. Implementing a more sophisticated memory system with vector storage
5. Adding support for multimodal inputs and outputs
