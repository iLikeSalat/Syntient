"""
Example script demonstrating the continuous execution loop functionality.

This script shows how to use the ContinuousExecutionLoop class to run
a task until completion, with progress monitoring and status updates.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.assistant import Assistant
from core.continuous_loop import ContinuousExecutionLoop

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def status_callback(status):
    """
    Callback function to handle status updates from the execution loop.
    
    Args:
        status: Dictionary containing status information
    """
    logger.info(f"Status update: {status.get('status', 'unknown')} - Iteration: {status.get('iteration', 0)}")
    
    # Print additional details for certain status types
    if status.get('status') == 'error':
        logger.error(f"Error encountered: {status.get('error', 'unknown error')}")
    elif status.get('status') == 'completed':
        logger.info(f"Task completed with result: {status.get('result', {})}")

def main():
    """
    Main function to demonstrate the continuous execution loop.
    """
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Create an Assistant instance
    assistant = Assistant(api_key=api_key)
    
    # Register some example tools
    assistant.register_tool("search_web", lambda query: {"results": f"Search results for: {query}"})
    assistant.register_tool("get_weather", lambda location: {"temperature": 72, "conditions": "sunny", "location": location})
    
    # Create a ContinuousExecutionLoop instance
    loop = ContinuousExecutionLoop(
        assistant=assistant,
        max_iterations=20,  # Limit to 20 iterations for this example
        iteration_delay=2.0,  # 2 second delay between iterations
        status_callback=status_callback
    )
    
    # Define a task
    task = "Create a simple Python function that calculates the Fibonacci sequence up to n terms."
    
    # Start the execution loop
    logger.info(f"Starting continuous execution for task: {task}")
    result = loop.start(task)
    
    # Print the final result
    logger.info(f"Execution completed with status: {result.get('status', 'unknown')}")
    logger.info(f"Total iterations: {result.get('iterations', 0)}")
    logger.info(f"Error count: {result.get('error_count', 0)}")
    
    if result.get('status') == 'completed':
        logger.info("Task completed successfully!")
    else:
        logger.warning("Task did not complete successfully.")

if __name__ == "__main__":
    main()
