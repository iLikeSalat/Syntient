"""
Tools module initialization for the Syntient AI Assistant Platform.

This module exposes the base Tool class and ToolRegistry for managing tools.
"""

from .base import Tool, ToolRegistry

# Create a global tool registry instance
registry = ToolRegistry()

__all__ = ['Tool', 'ToolRegistry', 'registry']
