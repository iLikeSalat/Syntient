"""
Tools package for the Syntient AI Assistant Platform.

This package provides a modular system for tools that can be used by the assistant.
"""

from .base import Tool
from .tool_registry import registry, ToolRegistry

# Import placeholder tools to register them
from .browser_use import BrowserUseTool
from .file_parser import FileParserTool
from .code_executor import CodeExecutorTool

# Discover and register all tools
registry.discover_tools()

__all__ = ['Tool', 'registry', 'ToolRegistry']
