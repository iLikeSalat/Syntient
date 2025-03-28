"""
Example script demonstrating the enhanced planning capabilities.

This script shows how to use the EnhancedPlanner class to create
hierarchical plans, track execution progress, and adapt plans based on feedback.
"""

import os
import sys
import time
import logging
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.assistant import Assistant
from core.enhanced_planning import EnhancedPlanner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_plan_summary(plan_summary):
    """
    Print a summary of the current plan.
    
    Args:
        plan_summary: Dictionary containing plan summary
    """
    logger.info("=" * 50)
    logger.info(f"PLAN SUMMARY FOR: {plan_summary.get('task', 'Unknown task')}")
    logger.info(f"Overall Progress: {plan_summary.get('overall_progress', 0.0) * 100:.1f}%")
    logger.info("-" * 50)
    
    for component_name, summary in plan_summary.get('components', {}).items():
        logger.info(f"Component: {component_name}")
        logger.info(f"  Status: {summary.get('status', 'unknown')}")
        logger.info(f"  Progress: {summary.get('progress', 0.0) * 100:.1f}%")
        logger.info(f"  Steps: {summary.get('completed_steps', 0)}/{summary.get('total_steps', 0)}")
        logger.info("-" * 30)
    
    logger.info("=" * 50)

def main():
    """
    Main function to demonstrate the enhanced planning capabilities.
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
    
    # Create an EnhancedPlanner instance
    planner = EnhancedPlanner(assistant=assistant)
    
    # Define a complex task
    task = "Build a personal finance tracking application with expense categorization, budget planning, and visualization features."
    
    # Create a hierarchical plan
    logger.info(f"Creating hierarchical plan for task: {task}")
    hierarchical_plan = planner.create_hierarchical_plan(task)
    
    # Print the initial plan summary
    plan_summary = planner.get_plan_summary()
    print_plan_summary(plan_summary)
    
    # Simulate execution of the first few steps
    for _ in range(5):
        # Get the next action
        action_type, action_details = planner.get_next_action()
        
        if action_type == "execute_step":
            component = action_details["component"]
            step_index = action_details["step_index"]
            step = action_details["step"]
            
            logger.info(f"Executing step {step_index + 1} of component '{component}':")
            logger.info(f"  {step}")
            
            # Simulate successful execution (in a real scenario, this would actually execute the step)
            time.sleep(1)  # Simulate work being done
            
            # Update the step status (mark as completed)
            planner.update_step_status(component, step_index, completed=True)
            
            # Print updated status
            logger.info(f"Step {step_index + 1} of '{component}' completed.")
        
        elif action_type == "component_completed":
            logger.info(f"Component '{action_details['component']}' completed!")
        
        elif action_type == "plan_completed":
            logger.info("All components in the plan are completed!")
            break
    
    # Print the updated plan summary
    plan_summary = planner.get_plan_summary()
    print_plan_summary(plan_summary)
    
    # Simulate adapting the plan based on new requirements
    new_requirement = "The application should also support multiple currencies and exchange rate conversion."
    logger.info(f"Adapting plan based on new requirement: {new_requirement}")
    
    adapted_plan = planner.adapt_plan(new_requirement)
    
    # Print the adapted plan summary
    plan_summary = planner.get_plan_summary()
    print_plan_summary(plan_summary)
    
    # Demonstrate reasoning about an approach
    problem = "How to implement secure user authentication for the finance application?"
    logger.info(f"Reasoning about approach for problem: {problem}")
    
    reasoning_result = planner.reason_about_approach(problem)
    
    logger.info("Reasoning Analysis:")
    logger.info(f"Recommended Approach: {reasoning_result.get('recommended_approach', 'Unknown')}")
    
    logger.info("Enhanced planning demonstration completed.")

if __name__ == "__main__":
    main()
