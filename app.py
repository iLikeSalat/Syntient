"""
Flask application for the Syntient AI Assistant Platform.

This module provides a web server that serves the UI and handles API requests
for the Syntient AI Assistant.
"""

import os
import json
import logging
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

from core.assistant import Assistant
from core.continuous_loop import ContinuousExecutionLoop
from core.enhanced_planning import EnhancedPlanner


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__, static_folder='static')

# Initialize the assistant
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    logger.info("✅ OpenAI API key loaded from .env")
else:
    logger.warning("⚠️ OpenAI API key not found. Set OPENAI_API_KEY in .env")




from tools.tool_registry import registry
assistant = Assistant(api_key=api_key, tool_registry=registry)
planner = EnhancedPlanner(assistant=assistant)
# Disable simulated fallback to clearly see if LLM tool selection is working
assistant.set_simulated_fallback(False)
assistant.set_llm_tool_selection(True)  # Optional but explicit

# Store active tasks
active_tasks = {}

@app.route('/')
def index():
    """Serve the main UI page."""
    return send_from_directory('static', 'index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
    """
    Handle a simple question/answer interaction.
    
    This endpoint is for simple interactions that don't require continuous execution.
    """
    data = request.json
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400
    
    user_id = data.get('user_id', 'default_user')
    message = data['message']
    
    logger.info("📥 Received request at /api/ask")
    logger.info(f"Request JSON: {json.dumps(request.json, indent=2)}")
    logger.info(f"LLM tool selection enabled: {assistant.use_llm_tool_selection}")
    logger.info(f"Simulated fallback enabled: {assistant.use_simulated_fallback}")
    


    try:
        # Get response from assistant
        response = assistant.ask(message)
        logger.info(f"🧠 Final assistant response: {response}")
        return jsonify({
            'response': response.get('response', ''),
            'type': response.get('type', 'response')
        })
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/start', methods=['POST'])
def start_task():
    """
    Start a new task with continuous execution.
    
    This endpoint creates a new task and starts the continuous execution loop.
    """
    data = request.json
    if not data or 'task' not in data:
        return jsonify({'error': 'Task description is required'}), 400
    
    user_id = data.get('user_id', 'default_user')
    task = data['task']
    continuous_mode = data.get('continuous_mode', True)
    
    try:
        # Create a task ID
        task_id = f"task_{len(active_tasks) + 1}"
        
        # Store task information
        active_tasks[task_id] = {
            'task': task,
            'user_id': user_id,
            'status': 'planning',
            'continuous_mode': continuous_mode,
            'progress': 0.0
        }
        
        # If continuous mode is enabled, create a plan
        if continuous_mode:
            # Create a hierarchical plan
            plan = planner.create_hierarchical_plan(task)
            active_tasks[task_id]['plan'] = plan
            active_tasks[task_id]['planner'] = planner
            
            # In a real implementation, we would start the continuous execution loop
            # in a separate thread or process
            
            return jsonify({
                'task_id': task_id,
                'status': 'planning',
                'message': 'Task started with continuous execution',
                'plan_summary': planner.get_plan_summary()
            })
        else:
            # For non-continuous mode, just get a simple response
            response = assistant.ask(f"I need help with this task: {task}")
            
            return jsonify({
                'task_id': task_id,
                'status': 'completed',
                'message': response.get('response', ''),
                'plan_summary': {
                    'task': task,
                    'overall_progress': 1.0,
                    'components': {
                        'Simple Response': {
                            'progress': 1.0,
                            'status': 'completed'
                        }
                    }
                }
            })
    except Exception as e:
        logger.error(f"Error starting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<task_id>/status', methods=['GET'])
def get_task_status(task_id):
    """
    Get the status of a task.
    
    This endpoint returns the current status and progress of a task.
    """
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    task_info = active_tasks[task_id]
    
    # If the task has a planner, get the plan summary
    if 'planner' in task_info:
        plan_summary = task_info['planner'].get_plan_summary()
    else:
        plan_summary = {
            'task': task_info['task'],
            'overall_progress': task_info['progress'],
            'components': {}
        }
    
    return jsonify({
        'task_id': task_id,
        'status': task_info['status'],
        'progress': task_info['progress'],
        'plan_summary': plan_summary
    })

@app.route('/api/task/<task_id>/feedback', methods=['POST'])
def provide_feedback(task_id):
    """
    Provide feedback for a task.
    
    This endpoint allows the user to provide feedback that will be incorporated
    into the execution plan.
    """
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    data = request.json
    if not data or 'feedback' not in data:
        return jsonify({'error': 'Feedback is required'}), 400
    
    feedback = data['feedback']
    task_info = active_tasks[task_id]
    
    try:
        # If the task has a planner, adapt the plan
        if 'planner' in task_info:
            adapted_plan = task_info['planner'].adapt_plan(feedback)
            return jsonify({
                'task_id': task_id,
                'status': 'adapting',
                'message': 'Feedback incorporated into execution plan',
                'plan_summary': task_info['planner'].get_plan_summary()
            })
        else:
            # For tasks without a planner, just store the feedback
            if 'feedback_history' not in task_info:
                task_info['feedback_history'] = []
            
            task_info['feedback_history'].append(feedback)
            
            return jsonify({
                'task_id': task_id,
                'status': task_info['status'],
                'message': 'Feedback received'
            })
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/task/<task_id>/cancel', methods=['POST'])
def cancel_task(task_id):
    """
    Cancel a task.
    
    This endpoint cancels a task and stops the continuous execution loop.
    """
    if task_id not in active_tasks:
        return jsonify({'error': 'Task not found'}), 404
    
    try:
        # In a real implementation, we would stop the continuous execution loop
        
        # Remove the task from active tasks
        task_info = active_tasks.pop(task_id)
        
        return jsonify({
            'task_id': task_id,
            'status': 'cancelled',
            'message': 'Task cancelled successfully'
        })
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Register some example tools
    assistant.register_tool("search_web", lambda query: {"results": f"Search results for: {query}"})
    assistant.register_tool("get_weather", lambda location: {"temperature": 72, "conditions": "sunny", "location": location})
    
    # Start the Flask app
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")
    
    logger.info(f"Starting Syntient AI Assistant on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
