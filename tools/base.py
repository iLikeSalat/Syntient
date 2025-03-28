"""
Base tool interface for the Syntient AI Assistant Platform.

This module defines the base Tool class that all tools must inherit from,
providing a consistent interface for tool registration and execution.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


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
    def execute(self, **kwargs) -> Dict[str, Any]:
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
    
    @abstractmethod
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool's parameters.
        
        Returns:
            Dictionary describing the parameters and their types
        """
        pass


class ToolRegistry:
    """
    Registry for managing and accessing tools.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools = {}
    
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
        
        return tool.execute(**kwargs)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        List all registered tools and their schemas.
        
        Returns:
            Dictionary mapping tool names to their schemas
        """
        return {name: tool.get_schema() for name, tool in self.tools.items()}
