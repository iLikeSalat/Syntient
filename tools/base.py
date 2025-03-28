"""
Base tool interface for the Syntient AI Assistant Platform.

This module defines the base Tool class that all tools must inherit from,
providing a consistent interface for tool registration and execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import inspect
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Tool(ABC):
    """
    Abstract base class for all tools in the Syntient AI Assistant Platform.
    
    All tools must inherit from this class and implement the required methods.
    """
    
    def __init__(self, name: str, description: str):
        """
        Initialize a tool with a name and description.
        
        Args:
            name: Unique identifier for the tool
            description: Human-readable description of what the tool does
        """
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the provided arguments.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Dictionary containing the result of the tool execution
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool, including required parameters.
        
        Returns:
            Dictionary describing the tool's parameters and their types
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters_schema()
        }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool's parameters based on the run method signature.
        
        Returns:
            Dictionary describing the parameters and their types
        """
        # Inspect the run method to get parameter information
        signature = inspect.signature(self.run)
        parameters = {}
        
        for param_name, param in signature.parameters.items():
            if param_name == 'self':
                continue
                
            # Get parameter type annotation if available
            param_type = "string"  # Default type
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == List[str]:
                    param_type = "array"
                elif param.annotation == Dict[str, Any]:
                    param_type = "object"
            
            # Determine if parameter is required
            required = param.default == inspect.Parameter.empty
            
            # Add parameter to schema
            parameters[param_name] = {
                "type": param_type,
                "description": f"Parameter: {param_name}",
                "required": required
            }
        
        return parameters
    
    def validate_args(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the arguments against the parameter schema.
        
        Args:
            args: Dictionary of arguments to validate
            
        Returns:
            Validated and possibly transformed arguments
            
        Raises:
            ValueError: If required arguments are missing or of wrong type
        """
        schema = self._get_parameters_schema()
        validated_args = {}
        
        # Check for required parameters
        for param_name, param_schema in schema.items():
            if param_schema.get("required", False) and param_name not in args:
                raise ValueError(f"Required parameter '{param_name}' is missing")
        
        # Validate and transform parameters
        for arg_name, arg_value in args.items():
            if arg_name in schema:
                param_schema = schema[arg_name]
                
                # Type validation (simplified)
                if param_schema["type"] == "string" and not isinstance(arg_value, str):
                    try:
                        arg_value = str(arg_value)
                    except:
                        raise ValueError(f"Parameter '{arg_name}' must be a string")
                
                elif param_schema["type"] == "integer" and not isinstance(arg_value, int):
                    try:
                        arg_value = int(arg_value)
                    except:
                        raise ValueError(f"Parameter '{arg_name}' must be an integer")
                
                elif param_schema["type"] == "number" and not isinstance(arg_value, (int, float)):
                    try:
                        arg_value = float(arg_value)
                    except:
                        raise ValueError(f"Parameter '{arg_name}' must be a number")
                
                elif param_schema["type"] == "boolean" and not isinstance(arg_value, bool):
                    if isinstance(arg_value, str):
                        arg_value = arg_value.lower() in ("true", "yes", "1", "t", "y")
                    else:
                        try:
                            arg_value = bool(arg_value)
                        except:
                            raise ValueError(f"Parameter '{arg_name}' must be a boolean")
                
                validated_args[arg_name] = arg_value
            else:
                # Pass through unknown parameters
                validated_args[arg_name] = arg_value
        
        return validated_args
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Validate arguments and execute the tool.
        
        This method handles argument validation before passing them to the run method.
        
        Args:
            **kwargs: Tool-specific arguments
            
        Returns:
            Dictionary containing the result of the tool execution
        """
        try:
            # Validate arguments
            validated_args = self.validate_args(kwargs)
            
            # Execute the tool
            result = self.run(**validated_args)
            
            return result
        except Exception as e:
            logger.error(f"Error executing tool '{self.name}': {str(e)}")
            return {"error": str(e)}
