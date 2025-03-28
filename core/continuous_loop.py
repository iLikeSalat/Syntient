"""
Continuous execution loop for the Syntient AI Assistant Platform.

This module implements a persistent execution loop that allows the assistant
to continue working on tasks until completion, with self-monitoring and
recovery capabilities.
"""

import time
import logging
import traceback
from typing import Dict, Any, List, Optional, Callable

from .assistant import Assistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ContinuousExecutionLoop:
    """
    Implements a continuous execution loop for the Syntient AI Assistant.
    
    This class enables the assistant to:
    1. Maintain state across multiple execution cycles
    2. Monitor its own progress and detect stalls
    3. Recover from errors and continue execution
    4. Persist until tasks are completed
    """
    
    def __init__(
        self, 
        assistant: Assistant,
        max_iterations: int = 100,
        iteration_delay: float = 1.0,
        status_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        """
        Initialize the continuous execution loop.
        
        Args:
            assistant: The Assistant instance to use
            max_iterations: Maximum number of iterations before forced termination
            iteration_delay: Delay between iterations in seconds
            status_callback: Optional callback function for status updates
        """
        self.assistant = assistant
        self.max_iterations = max_iterations
        self.iteration_delay = iteration_delay
        self.status_callback = status_callback
        
        # State tracking
        self.current_task = None
        self.task_status = "idle"
        self.iteration_count = 0
        self.last_progress_time = time.time()
        self.execution_history = []
        self.error_count = 0
        
    def start(self, task: str) -> Dict[str, Any]:
        """
        Start the continuous execution loop for a given task.
        
        Args:
            task: The task description to execute
            
        Returns:
            Final result of the task execution
        """
        self.current_task = task
        self.task_status = "planning"
        self.iteration_count = 0
        self.last_progress_time = time.time()
        self.execution_history = []
        self.error_count = 0
        
        logger.info(f"Starting continuous execution loop for task: {task}")
        
        # Generate initial plan
        try:
            plan = self.assistant.plan_execution(task)
            self.execution_history.append({
                "type": "plan",
                "content": plan,
                "timestamp": time.time()
            })
            logger.info(f"Initial plan generated with {len(plan)} steps")
        except Exception as e:
            logger.error(f"Error generating initial plan: {str(e)}")
            self.error_count += 1
            plan = ["Analyze the task", "Execute the task step by step"]
        
        # Main execution loop
        result = None
        while self.should_continue():
            try:
                result = self.execute_iteration()
                
                # Check if task is complete
                if self.task_status == "completed":
                    logger.info(f"Task completed after {self.iteration_count} iterations")
                    break
                    
                # Prevent CPU overload
                time.sleep(self.iteration_delay)
                
            except Exception as e:
                self.handle_error(e)
                
        # Final status update
        final_status = {
            "task": self.current_task,
            "status": self.task_status,
            "iterations": self.iteration_count,
            "result": result,
            "error_count": self.error_count
        }
        
        if self.status_callback:
            self.status_callback(final_status)
            
        return final_status
    
    def execute_iteration(self) -> Dict[str, Any]:
        """
        Execute a single iteration of the continuous loop.
        
        Returns:
            Result of the current iteration
        """
        self.iteration_count += 1
        logger.info(f"Executing iteration {self.iteration_count}")
        
        # Update status
        if self.status_callback:
            self.status_callback({
                "task": self.current_task,
                "status": self.task_status,
                "iteration": self.iteration_count,
                "timestamp": time.time()
            })
        
        # Determine next action based on current status
        if self.task_status == "planning":
            return self.execute_planning_step()
        elif self.task_status == "executing":
            return self.execute_task_step()
        elif self.task_status == "reviewing":
            return self.execute_review_step()
        elif self.task_status == "error_recovery":
            return self.execute_recovery_step()
        else:
            logger.warning(f"Unknown task status: {self.task_status}")
            self.task_status = "planning"
            return {"status": "reset_to_planning"}
    
    def execute_planning_step(self) -> Dict[str, Any]:
        """
        Execute a planning step in the continuous loop.
        
        Returns:
            Result of the planning step
        """
        # Create a planning prompt
        planning_prompt = f"""
        I am working on this task: {self.current_task}
        
        Based on my current progress and the execution history, I need to:
        1. Assess the current state of the task
        2. Identify the next steps to take
        3. Create a detailed plan for the next phase of execution
        
        Current iteration: {self.iteration_count}
        """
        
        # Add execution history context if available
        if self.execution_history:
            recent_history = self.execution_history[-3:] if len(self.execution_history) > 3 else self.execution_history
            history_text = "\n".join([f"- {h['type']}: {h['content'][:200]}..." for h in recent_history])
            planning_prompt += f"\nRecent execution history:\n{history_text}\n"
        
        # Get planning response
        response = self.assistant.ask(planning_prompt)
        
        # Record the planning step
        self.execution_history.append({
            "type": "planning",
            "content": response.get("response", ""),
            "timestamp": time.time()
        })
        
        # Move to execution phase
        self.task_status = "executing"
        self.last_progress_time = time.time()
        
        return {
            "status": "planning_complete",
            "plan": response.get("response", "")
        }
    
    def execute_task_step(self) -> Dict[str, Any]:
        """
        Execute a task step in the continuous loop.
        
        Returns:
            Result of the task step
        """
        # Create an execution prompt
        execution_prompt = f"""
        I am working on this task: {self.current_task}
        
        I need to execute the next step in my plan. Based on my execution history,
        I should determine the most appropriate action to take now.
        
        Current iteration: {self.iteration_count}
        """
        
        # Add execution history context
        if self.execution_history:
            recent_history = self.execution_history[-5:] if len(self.execution_history) > 5 else self.execution_history
            history_text = "\n".join([f"- {h['type']}: {h['content'][:200]}..." for h in recent_history])
            execution_prompt += f"\nRecent execution history:\n{history_text}\n"
        
        # Get execution response
        response = self.assistant.ask(execution_prompt)
        
        # Check if the response contains a tool call
        if response.get("type") == "tool_call":
            # Record the tool call
            self.execution_history.append({
                "type": "tool_call",
                "content": f"Tool: {response.get('tool', '')}, Args: {response.get('args', {})}",
                "timestamp": time.time()
            })
            
            # Record the tool result if available
            if "tool_result" in response:
                self.execution_history.append({
                    "type": "tool_result",
                    "content": str(response.get("tool_result", "")),
                    "timestamp": time.time()
                })
        else:
            # Record the execution step
            self.execution_history.append({
                "type": "execution",
                "content": response.get("response", ""),
                "timestamp": time.time()
            })
        
        # Check for completion indicators in the response
        response_text = response.get("response", "") if response.get("type") == "response" else str(response)
        if "task completed" in response_text.lower() or "all steps completed" in response_text.lower():
            self.task_status = "reviewing"
        else:
            # Continue execution
            self.last_progress_time = time.time()
        
        return {
            "status": "execution_step_complete",
            "response": response
        }
    
    def execute_review_step(self) -> Dict[str, Any]:
        """
        Execute a review step to check if the task is truly complete.
        
        Returns:
            Result of the review step
        """
        # Create a review prompt
        review_prompt = f"""
        I have been working on this task: {self.current_task}
        
        I need to review my work to determine if the task is truly complete.
        I should check:
        1. Have all requirements been fulfilled?
        2. Is there any part of the task that remains incomplete?
        3. Are there any errors or issues that need to be addressed?
        4. Is there any way to improve the result?
        
        Current iteration: {self.iteration_count}
        """
        
        # Get review response
        response = self.assistant.ask(review_prompt)
        
        # Record the review step
        self.execution_history.append({
            "type": "review",
            "content": response.get("response", ""),
            "timestamp": time.time()
        })
        
        # Check for completion confirmation
        response_text = response.get("response", "")
        if "task is complete" in response_text.lower() or "requirements fulfilled" in response_text.lower():
            self.task_status = "completed"
            logger.info("Task marked as completed after review")
        else:
            # Return to execution phase
            self.task_status = "executing"
            logger.info("Task returned to execution phase after review")
        
        self.last_progress_time = time.time()
        
        return {
            "status": "review_complete",
            "is_complete": self.task_status == "completed",
            "review": response.get("response", "")
        }
    
    def execute_recovery_step(self) -> Dict[str, Any]:
        """
        Execute a recovery step after encountering an error.
        
        Returns:
            Result of the recovery step
        """
        # Create a recovery prompt
        recovery_prompt = f"""
        I encountered an error while working on this task: {self.current_task}
        
        I need to:
        1. Analyze what went wrong
        2. Determine how to recover
        3. Adjust my approach to avoid similar errors
        
        Current iteration: {self.iteration_count}
        Error count: {self.error_count}
        """
        
        # Add recent error information if available
        if self.execution_history and any(h["type"] == "error" for h in self.execution_history):
            error_entries = [h for h in self.execution_history if h["type"] == "error"]
            recent_error = error_entries[-1]["content"] if error_entries else "Unknown error"
            recovery_prompt += f"\nMost recent error:\n{recent_error}\n"
        
        # Get recovery response
        response = self.assistant.ask(recovery_prompt)
        
        # Record the recovery step
        self.execution_history.append({
            "type": "recovery",
            "content": response.get("response", ""),
            "timestamp": time.time()
        })
        
        # Return to planning phase
        self.task_status = "planning"
        self.last_progress_time = time.time()
        
        return {
            "status": "recovery_complete",
            "recovery_plan": response.get("response", "")
        }
    
    def handle_error(self, error: Exception) -> None:
        """
        Handle an error that occurred during execution.
        
        Args:
            error: The exception that was raised
        """
        self.error_count += 1
        error_message = f"{str(error)}\n{traceback.format_exc()}"
        logger.error(f"Error in iteration {self.iteration_count}: {error_message}")
        
        # Record the error
        self.execution_history.append({
            "type": "error",
            "content": error_message,
            "timestamp": time.time()
        })
        
        # Switch to error recovery mode
        self.task_status = "error_recovery"
        self.last_progress_time = time.time()
        
        # Notify via callback if available
        if self.status_callback:
            self.status_callback({
                "task": self.current_task,
                "status": "error",
                "error": str(error),
                "iteration": self.iteration_count,
                "timestamp": time.time()
            })
    
    def should_continue(self) -> bool:
        """
        Determine if the execution loop should continue.
        
        Returns:
            True if execution should continue, False otherwise
        """
        # Check if maximum iterations reached
        if self.iteration_count >= self.max_iterations:
            logger.warning(f"Maximum iterations ({self.max_iterations}) reached, stopping execution")
            return False
        
        # Check if task is already completed
        if self.task_status == "completed":
            return False
        
        # Check for progress stall (no progress for 5 minutes)
        if time.time() - self.last_progress_time > 300:  # 5 minutes
            logger.warning("No progress detected for 5 minutes, checking if recovery is possible")
            
            # If already in error recovery and still stalled, stop execution
            if self.task_status == "error_recovery" and self.error_count > 5:
                logger.error("Multiple recovery attempts failed, stopping execution")
                return False
            
            # Otherwise, trigger error recovery
            self.handle_error(Exception("Execution stalled - no progress detected for 5 minutes"))
        
        # Continue execution
        return True
