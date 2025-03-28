"""
Integration of example tasks with the web UI for the Syntient AI Assistant Platform.

This module provides routes and handlers for the example tasks in the web UI.
"""

import logging
from typing import Dict, Any, List, Optional
from flask import Blueprint, request, jsonify

from core.assistant import Assistant
from core.example_tasks import ExampleTasks
from core.example_task_handler import ExampleTaskHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a blueprint for example tasks
example_tasks_bp = Blueprint('example_tasks', __name__)

def register_example_tasks_routes(app, assistant: Assistant):
    """
    Register routes for example tasks.
    
    Args:
        app: Flask application
        assistant: Assistant instance
    """
    # Create an example task handler
    task_handler = ExampleTaskHandler(assistant)
    
    @example_tasks_bp.route('/list', methods=['GET'])
    def list_tasks():
        """List all available example tasks."""
        tasks = ExampleTasks.get_task_list()
        return jsonify({"tasks": tasks})
    
    @example_tasks_bp.route('/execute', methods=['POST'])
    def execute_task():
        """Execute an example task."""
        data = request.json
        if not data or 'task_id' not in data:
            return jsonify({"error": "Task ID is required"}), 400
        
        task_id = data['task_id']
        params = data.get('params', {})
        
        # Execute the task
        try:
            if task_id == 'website_summary':
                url = params.get('url', 'https://example.com')
                result = task_handler.execute_website_summary_task(url)
            elif task_id == 'code_execution':
                code = params.get('code', 'print("Hello, world!")')
                result = task_handler.execute_code_execution_task(code)
            elif task_id == 'file_analysis':
                file_path = params.get('file_path', '/path/to/example.txt')
                result = task_handler.execute_file_analysis_task(file_path)
            elif task_id == 'web_search':
                query = params.get('query', 'quantum computing')
                result = task_handler.execute_web_search_task(query)
            elif task_id == 'quantum_decision':
                options = params.get('options', ['Option A', 'Option B', 'Option C'])
                result = task_handler.execute_quantum_decision_task(options)
            else:
                result = task_handler.execute_task(task_id, **params)
            
            return jsonify(result)
        except Exception as e:
            logger.error(f"Error executing task {task_id}: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
    # Register the blueprint
    app.register_blueprint(example_tasks_bp, url_prefix='/api/example_tasks')
