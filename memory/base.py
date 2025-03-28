"""
Base memory interface for the Syntient AI Assistant Platform.

This module defines the base Memory class that all memory implementations must inherit from,
providing a consistent interface for memory storage and retrieval.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


class Memory(ABC):
    """
    Abstract base class for all memory implementations in the Syntient AI Assistant Platform.
    
    All memory implementations must inherit from this class and implement the required methods.
    """
    
    def __init__(self, memory_id: str):
        """
        Initialize a memory instance with a unique identifier.
        
        Args:
            memory_id: Unique identifier for this memory instance
        """
        self.memory_id = memory_id
    
    @abstractmethod
    def add(self, data: Dict[str, Any], **kwargs) -> str:
        """
        Add data to memory and return a reference ID.
        
        Args:
            data: Data to store in memory
            **kwargs: Additional memory-specific parameters
            
        Returns:
            Reference ID for the stored data
        """
        pass
    
    @abstractmethod
    def get(self, reference_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from memory by reference ID.
        
        Args:
            reference_id: Reference ID of the data to retrieve
            
        Returns:
            Retrieved data, or None if not found
        """
        pass
    
    @abstractmethod
    def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Search memory for relevant data.
        
        Args:
            query: Search query
            **kwargs: Additional search parameters
            
        Returns:
            List of matching data items
        """
        pass
    
    @abstractmethod
    def update(self, reference_id: str, data: Dict[str, Any]) -> bool:
        """
        Update existing data in memory.
        
        Args:
            reference_id: Reference ID of the data to update
            data: New data to store
            
        Returns:
            True if update was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, reference_id: str) -> bool:
        """
        Delete data from memory.
        
        Args:
            reference_id: Reference ID of the data to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """
        Clear all data from this memory instance.
        
        Returns:
            True if clearing was successful, False otherwise
        """
        pass


class MemoryManager:
    """
    Manager for handling multiple memory instances.
    """
    
    def __init__(self):
        """Initialize an empty memory manager."""
        self.memories = {}
    
    def register_memory(self, memory: Memory) -> None:
        """
        Register a memory instance with the manager.
        
        Args:
            memory: Memory instance to register
            
        Raises:
            ValueError: If a memory with the same ID is already registered
        """
        if memory.memory_id in self.memories:
            raise ValueError(f"Memory with ID '{memory.memory_id}' is already registered")
        
        self.memories[memory.memory_id] = memory
    
    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """
        Get a memory instance by ID.
        
        Args:
            memory_id: ID of the memory instance to retrieve
            
        Returns:
            Memory instance if found, None otherwise
        """
        return self.memories.get(memory_id)
    
    def list_memories(self) -> List[str]:
        """
        List all registered memory instances.
        
        Returns:
            List of memory instance IDs
        """
        return list(self.memories.keys())
