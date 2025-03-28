"""
Memory module initialization for the Syntient AI Assistant Platform.

This module exposes the base Memory class and MemoryManager for managing memory instances.
"""

from .base import Memory, MemoryManager
from .simple import SimpleMemory

# Create a global memory manager instance
manager = MemoryManager()

__all__ = ['Memory', 'MemoryManager', 'SimpleMemory', 'manager']
