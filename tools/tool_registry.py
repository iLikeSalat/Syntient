"""
Tool registry for the Syntient AI Assistant Platform.

This module provides a registry for managing and loading tools dynamically.
It handles tool discovery, registration, and execution.
"""

import os
import sys
import importlib
import inspect
import logging
from typing import Dict, Any, List, Optional, Type

from .base import Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ToolRegistry:
    """
    Registry for managing and accessing tools.
    
    This class handles tool discovery, registration, and execution.
    It supports dynamic loading of tools from the tools directory.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools = {}
        self.tool_modules = {}
    
    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool in the registry.
        
        Args:
            tool: Tool instance to register
        
        Raises:
            ValueError: If a tool with the same name is already registered
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool with name '{tool.name}' is already registered")
        
        logger.info(f"Registering tool: {tool.name}")
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.
        
        Args:
            name: Name of the tool to retrieve
            
        Returns:
            Tool instance if found, None otherwise
        """
        return self.tools.get(name)
    
    def execute_tool(self, name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool by name with the provided arguments.
        
        Args:
            name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result of the tool execution
            
        Raises:
            ValueError: If the tool is not found
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found in registry")
        
        logger.info(f"Executing tool: {name}")
        return tool.execute(**kwargs)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered tools and their schemas.
        
        Returns:
            Dictionary mapping tool names to their schemas
        """
        return {name: tool.get_schema() for name, tool in self.tools.items()}
    
    def discover_tools(self, tools_dir: Optional[str] = None) -> None:
        """
        Discover and register tools from the tools directory.
        
        This method scans the tools directory for Python files that define Tool classes
        and automatically registers them.
        
        Args:
            tools_dir: Directory to scan for tools (defaults to the directory containing this file)
        """
        if tools_dir is None:
            # Default to the directory containing this file
            tools_dir = os.path.dirname(os.path.abspath(__file__))
        
        logger.info(f"Discovering tools in directory: {tools_dir}")
        
        # Get all Python files in the directory
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base.py', 'tool_registry.py']:
                module_name = filename[:-3]  # Remove .py extension
                module_path = f"tools.{module_name}"
                
                try:
                    # Import the module
                    if module_path in self.tool_modules:
                        # Reload the module if it's already loaded
                        module = importlib.reload(self.tool_modules[module_path])
                    else:
                        module = importlib.import_module(module_path)
                        self.tool_modules[module_path] = module
                    
                    # Find Tool classes in the module
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, Tool) and 
                            obj != Tool and
                            not inspect.isabstract(obj)):
                            
                            # Create an instance of the tool
                            try:
                                tool_instance = obj()
                                self.register_tool(tool_instance)
                                logger.info(f"Registered tool from {module_path}: {tool_instance.name}")
                            except Exception as e:
                                logger.error(f"Error instantiating tool {name} from {module_path}: {str(e)}")
                
                except Exception as e:
                    logger.error(f"Error loading module {module_path}: {str(e)}")
    
    def load_tool_from_file(self, file_path: str) -> None:
        """
        Load and register tools from a specific file.
        
        Args:
            file_path: Path to the Python file containing tool definitions
        """
        try:
            # Get the module name from the file path
            module_name = os.path.basename(file_path)[:-3]  # Remove .py extension
            
            # Add the directory to sys.path if it's not already there
            dir_path = os.path.dirname(os.path.abspath(file_path))
            if dir_path not in sys.path:
                sys.path.append(dir_path)
            
            # Import the module
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find Tool classes in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, Tool) and 
                    obj != Tool and
                    not inspect.isabstract(obj)):
                    
                    # Create an instance of the tool
                    try:
                        tool_instance = obj()
                        self.register_tool(tool_instance)
                        logger.info(f"Registered tool from {file_path}: {tool_instance.name}")
                    except Exception as e:
                        logger.error(f"Error instantiating tool {name} from {file_path}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error loading tools from {file_path}: {str(e)}")
    
    def reload_tools(self) -> None:
        """
        Reload all registered tools.
        
        This method clears the registry and rediscovers all tools.
        """
        logger.info("Reloading all tools")
        self.tools = {}
        self.discover_tools()

# Create a singleton instance of the tool registry
registry = ToolRegistry()
