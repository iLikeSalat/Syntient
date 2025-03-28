"""
Enhanced planning and reasoning module for the Syntient AI Assistant Platform.

This module provides advanced planning and reasoning capabilities for the assistant,
enabling it to break down complex tasks, create detailed execution plans, and
make better decisions during task execution.
"""

import time
import logging
from typing import Dict, Any, List, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedPlanner:
    """
    Enhanced planning and reasoning system for the Syntient AI Assistant.
    
    This class provides advanced planning capabilities including:
    1. Hierarchical task decomposition
    2. Detailed execution planning
    3. Progress tracking and plan adaptation
    4. Reasoning about task dependencies and constraints
    """
    
    def __init__(self, assistant):
        """
        Initialize the enhanced planner.
        
        Args:
            assistant: The Assistant instance to use for generating plans
        """
        self.assistant = assistant
        self.current_plan = []
        self.plan_history = []
        self.task_hierarchy = {}
        self.execution_status = {}
        
    def create_hierarchical_plan(self, task: str) -> Dict[str, Any]:
        """
        Create a hierarchical plan for a complex task.
        
        Args:
            task: The task description
            
        Returns:
            Dictionary containing the hierarchical plan
        """
        logger.info(f"Creating hierarchical plan for task: {task}")
        
        # First, create a high-level plan
        high_level_prompt = f"""
        I need to create a hierarchical plan for this task:
        
        {task}
        
        First, I'll break this down into major components or phases.
        For each component:
        1. Provide a clear name and description
        2. Identify the key objectives
        3. List any dependencies on other components
        
        Format the response as a numbered list of components.
        """
        
        high_level_response = self.assistant.ask(high_level_prompt)
        high_level_plan = high_level_response.get("response", "")
        
        # Parse the high-level plan into components
        components = self._parse_numbered_list(high_level_plan)
        
        # Create detailed plans for each component
        detailed_plans = {}
        for i, component in enumerate(components):
            component_name = f"Component {i+1}: {component.split(':', 1)[0].strip() if ':' in component else component}"
            detailed_plan = self._create_detailed_plan(component, task)
            detailed_plans[component_name] = detailed_plan
        
        # Create the hierarchical plan structure
        hierarchical_plan = {
            "task": task,
            "high_level_plan": components,
            "detailed_plans": detailed_plans,
            "created_at": time.time()
        }
        
        # Store the plan
        self.current_plan = hierarchical_plan
        self.plan_history.append(hierarchical_plan)
        
        # Initialize execution status
        self._initialize_execution_status(hierarchical_plan)
        
        return hierarchical_plan
    
    def _create_detailed_plan(self, component: str, task: str) -> List[str]:
        """
        Create a detailed plan for a component.
        
        Args:
            component: The component description
            task: The overall task description
            
        Returns:
            List of detailed steps for the component
        """
        detailed_prompt = f"""
        I'm working on this overall task:
        
        {task}
        
        I need to create a detailed plan for this component:
        
        {component}
        
        Please provide a step-by-step plan that:
        1. Breaks down the component into specific, actionable steps
        2. Identifies any tools or resources needed for each step
        3. Specifies how to verify each step is completed correctly
        4. Anticipates potential challenges and how to address them
        
        Format the response as a numbered list of steps.
        """
        
        detailed_response = self.assistant.ask(detailed_prompt)
        detailed_plan = detailed_response.get("response", "")
        
        # Parse the detailed plan into steps
        steps = self._parse_numbered_list(detailed_plan)
        
        return steps
    
    def _parse_numbered_list(self, text: str) -> List[str]:
        """
        Parse a numbered list from text.
        
        Args:
            text: Text containing a numbered list
            
        Returns:
            List of items extracted from the numbered list
        """
        lines = text.strip().split('\n')
        items = []
        current_item = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line starts with a number followed by a period or parenthesis
            if (line[0].isdigit() and len(line) > 1 and 
                (line[1] == '.' or line[1] == ')' or 
                 (len(line) > 2 and line[1].isdigit() and line[2] in ['.', ')']))):
                
                # If we have a current item, add it to the list
                if current_item:
                    items.append(current_item)
                
                # Start a new item
                current_item = line
            else:
                # Continue the current item
                current_item += " " + line
        
        # Add the last item if there is one
        if current_item:
            items.append(current_item)
        
        return items
    
    def _initialize_execution_status(self, plan: Dict[str, Any]) -> None:
        """
        Initialize the execution status for a plan.
        
        Args:
            plan: The hierarchical plan
        """
        execution_status = {
            "task": plan["task"],
            "overall_progress": 0.0,
            "components": {}
        }
        
        for component_name in plan["detailed_plans"]:
            steps = plan["detailed_plans"][component_name]
            execution_status["components"][component_name] = {
                "progress": 0.0,
                "steps_completed": 0,
                "total_steps": len(steps),
                "current_step": 0,
                "status": "pending"  # pending, in_progress, completed, blocked
            }
        
        self.execution_status = execution_status
    
    def get_next_action(self) -> Tuple[str, Dict[str, Any]]:
        """
        Determine the next action to take based on the current plan and status.
        
        Returns:
            Tuple of (action_type, action_details)
        """
        # If no plan exists, return action to create a plan
        if not self.current_plan:
            return "create_plan", {"message": "No plan exists. Create a plan first."}
        
        # Find the next component to work on
        next_component = self._find_next_component()
        if not next_component:
            return "plan_completed", {"message": "All components in the plan are completed."}
        
        # Get the current step for the component
        component_status = self.execution_status["components"][next_component]
        current_step_index = component_status["current_step"]
        
        if current_step_index >= component_status["total_steps"]:
            # Mark component as completed
            component_status["status"] = "completed"
            component_status["progress"] = 1.0
            self._update_overall_progress()
            return "component_completed", {"component": next_component}
        
        # Get the step details
        step = self.current_plan["detailed_plans"][next_component][current_step_index]
        
        return "execute_step", {
            "component": next_component,
            "step_index": current_step_index,
            "step": step
        }
    
    def _find_next_component(self) -> Optional[str]:
        """
        Find the next component to work on.
        
        Returns:
            Name of the next component to work on, or None if all are completed
        """
        # First, check for in-progress components
        for component_name, status in self.execution_status["components"].items():
            if status["status"] == "in_progress":
                return component_name
        
        # Then, check for pending components
        for component_name, status in self.execution_status["components"].items():
            if status["status"] == "pending":
                # Mark as in-progress
                status["status"] = "in_progress"
                return component_name
        
        # No pending or in-progress components found
        return None
    
    def update_step_status(self, component: str, step_index: int, completed: bool) -> None:
        """
        Update the status of a step in the execution plan.
        
        Args:
            component: The component name
            step_index: The index of the step
            completed: Whether the step was completed successfully
        """
        if component not in self.execution_status["components"]:
            logger.warning(f"Component {component} not found in execution status")
            return
        
        component_status = self.execution_status["components"][component]
        
        if completed:
            # Mark step as completed
            component_status["steps_completed"] += 1
            component_status["current_step"] = step_index + 1
        else:
            # Keep the current step (will retry)
            pass
        
        # Update progress
        component_status["progress"] = component_status["steps_completed"] / component_status["total_steps"]
        
        # Update overall progress
        self._update_overall_progress()
    
    def _update_overall_progress(self) -> None:
        """
        Update the overall progress of the execution.
        """
        if not self.execution_status["components"]:
            self.execution_status["overall_progress"] = 0.0
            return
        
        # Calculate average progress across all components
        total_progress = sum(comp["progress"] for comp in self.execution_status["components"].values())
        self.execution_status["overall_progress"] = total_progress / len(self.execution_status["components"])
    
    def adapt_plan(self, feedback: str) -> Dict[str, Any]:
        """
        Adapt the current plan based on feedback or changing requirements.
        
        Args:
            feedback: Feedback or new information to incorporate
            
        Returns:
            Updated plan
        """
        if not self.current_plan:
            logger.warning("No current plan to adapt")
            return {}
        
        logger.info(f"Adapting plan based on feedback: {feedback}")
        
        # Create an adaptation prompt
        adaptation_prompt = f"""
        I'm working on this task:
        
        {self.current_plan["task"]}
        
        My current plan has these components:
        
        {', '.join(self.current_plan["detailed_plans"].keys())}
        
        I've received this feedback or new information:
        
        {feedback}
        
        Based on this, I need to adapt my plan. Please help me:
        1. Identify which components need to be modified
        2. Specify what changes are needed
        3. Determine if any new components should be added
        4. Assess if any components should be removed
        
        Provide specific recommendations for adapting the plan.
        """
        
        adaptation_response = self.assistant.ask(adaptation_prompt)
        adaptation_recommendations = adaptation_response.get("response", "")
        
        # Store the original plan
        original_plan = self.current_plan.copy()
        
        # Apply the adaptations (simplified implementation)
        # In a real implementation, this would parse the recommendations and modify the plan accordingly
        
        # For now, just add the adaptation as a new component
        component_name = f"Adaptation: {time.strftime('%Y-%m-%d %H:%M:%S')}"
        adaptation_plan = self._create_detailed_plan(feedback, self.current_plan["task"])
        
        self.current_plan["detailed_plans"][component_name] = adaptation_plan
        self.execution_status["components"][component_name] = {
            "progress": 0.0,
            "steps_completed": 0,
            "total_steps": len(adaptation_plan),
            "current_step": 0,
            "status": "pending"
        }
        
        # Add to plan history
        self.plan_history.append({
            "type": "adaptation",
            "original_plan": original_plan,
            "adapted_plan": self.current_plan,
            "feedback": feedback,
            "timestamp": time.time()
        })
        
        return self.current_plan
    
    def reason_about_approach(self, problem_description: str) -> Dict[str, Any]:
        """
        Perform advanced reasoning about how to approach a problem.
        
        Args:
            problem_description: Description of the problem to reason about
            
        Returns:
            Dictionary containing reasoning results
        """
        logger.info(f"Reasoning about approach for problem: {problem_description}")
        
        # Create a reasoning prompt
        reasoning_prompt = f"""
        I need to reason about how to approach this problem:
        
        {problem_description}
        
        Please help me think through:
        1. What are the key aspects or dimensions of this problem?
        2. What are different possible approaches to solving it?
        3. What are the trade-offs between these approaches?
        4. What information or resources would I need for each approach?
        5. Which approach seems most promising and why?
        
        Provide a structured analysis that demonstrates deep reasoning.
        """
        
        reasoning_response = self.assistant.ask(reasoning_prompt)
        reasoning_analysis = reasoning_response.get("response", "")
        
        # Extract the recommended approach (simplified implementation)
        # In a real implementation, this would parse the analysis more carefully
        
        # For now, just look for the "most promising" section
        recommended_approach = "Unknown"
        analysis_lines = reasoning_analysis.split('\n')
        for i, line in enumerate(analysis_lines):
            if "most promising" in line.lower() and i < len(analysis_lines) - 1:
                recommended_approach = analysis_lines[i+1].strip()
                break
        
        return {
            "problem": problem_description,
            "analysis": reasoning_analysis,
            "recommended_approach": recommended_approach,
            "timestamp": time.time()
        }
    
    def get_execution_status(self) -> Dict[str, Any]:
        """
        Get the current execution status.
        
        Returns:
            Dictionary containing execution status
        """
        return self.execution_status
    
    def get_plan_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current plan.
        
        Returns:
            Dictionary containing plan summary
        """
        if not self.current_plan:
            return {"status": "no_plan"}
        
        component_summaries = {}
        for component_name, steps in self.current_plan["detailed_plans"].items():
            component_status = self.execution_status["components"].get(component_name, {})
            component_summaries[component_name] = {
                "total_steps": len(steps),
                "completed_steps": component_status.get("steps_completed", 0),
                "progress": component_status.get("progress", 0.0),
                "status": component_status.get("status", "unknown")
            }
        
        return {
            "task": self.current_plan.get("task", ""),
            "overall_progress": self.execution_status.get("overall_progress", 0.0),
            "components": component_summaries,
            "created_at": self.current_plan.get("created_at", 0)
        }
