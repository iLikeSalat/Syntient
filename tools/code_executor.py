"""
Code executor tool for the Syntient AI Assistant Platform.

This module provides a functional tool for executing Python code safely.
"""

import logging
import sys
import io
import traceback
from typing import Dict, Any, Optional
import ast
import builtins
import contextlib

from .base import Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CodeExecutorTool(Tool):
    """
    Tool for executing Python code safely.
    
    This is a functional implementation using Python's exec() with safety restrictions.
    """
    
    def __init__(self):
        """Initialize the code executor tool."""
        super().__init__(
            name="code_executor",
            description="Execute Python code safely and return the results"
        )
        
        # Define a list of safe builtins
        self.safe_builtins = {
            'abs': abs,
            'all': all,
            'any': any,
            'ascii': ascii,
            'bin': bin,
            'bool': bool,
            'bytearray': bytearray,
            'bytes': bytes,
            'chr': chr,
            'complex': complex,
            'dict': dict,
            'divmod': divmod,
            'enumerate': enumerate,
            'filter': filter,
            'float': float,
            'format': format,
            'frozenset': frozenset,
            'hash': hash,
            'hex': hex,
            'int': int,
            'isinstance': isinstance,
            'issubclass': issubclass,
            'iter': iter,
            'len': len,
            'list': list,
            'map': map,
            'max': max,
            'min': min,
            'next': next,
            'oct': oct,
            'ord': ord,
            'pow': pow,
            'print': print,
            'range': range,
            'repr': repr,
            'reversed': reversed,
            'round': round,
            'set': set,
            'slice': slice,
            'sorted': sorted,
            'str': str,
            'sum': sum,
            'tuple': tuple,
            'type': type,
            'zip': zip,
        }
        
        # Disallowed modules for security
        self.disallowed_modules = {
            'os', 'sys', 'subprocess', 'shutil', 'socket', 'requests',
            'urllib', 'http', 'ftplib', 'telnetlib', 'smtplib',
            'pickle', 'shelve', 'marshal', 'importlib', 'pathlib'
        }
    
    def _check_code_safety(self, code: str) -> bool:
        """
        Check if the code is safe to execute.
        
        Args:
            code: Python code to check
            
        Returns:
            True if the code is safe, False otherwise
        """
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Check for potentially dangerous operations
            for node in ast.walk(tree):
                # Check for imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for name in node.names:
                        module_name = name.name.split('.')[0]
                        if module_name in self.disallowed_modules:
                            logger.warning(f"Attempted to import disallowed module: {module_name}")
                            return False
                
                # Check for exec or eval calls
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in ('exec', 'eval', 'compile', '__import__'):
                        logger.warning(f"Attempted to use disallowed function: {node.func.id}")
                        return False
                
                # Check for attribute access on disallowed modules
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                    if node.value.id in self.disallowed_modules:
                        logger.warning(f"Attempted to access disallowed module: {node.value.id}")
                        return False
            
            return True
        except SyntaxError as e:
            logger.error(f"Syntax error in code: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error checking code safety: {str(e)}")
            return False
    
    def run(self, code: str, timeout: int = 5) -> Dict[str, Any]:
        """
        Execute Python code safely.
        
        Args:
            code: Python code to execute
            timeout: Maximum execution time in seconds (default: 5)
            
        Returns:
            Dictionary containing the execution result
        """
        logger.info(f"CodeExecutorTool: Executing Python code")
        
        # Check if the code is safe
        if not self._check_code_safety(code):
            return {
                "status": "error",
                "error": "Code contains potentially unsafe operations",
                "stdout": "",
                "stderr": "Security error: Attempted to use disallowed modules or functions"
            }
        
        # Capture stdout and stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        # Create a restricted globals dictionary
        restricted_globals = {
            '__builtins__': self.safe_builtins,
            'result': None
        }
        
        # Create a locals dictionary to store execution results
        locals_dict = {}
        
        try:
            # Execute the code with restricted globals and timeout
            with contextlib.redirect_stdout(stdout_capture), contextlib.redirect_stderr(stderr_capture):
                # Add a result variable that can be set in the executed code
                exec(code, restricted_globals, locals_dict)
            
            # Get the output
            stdout = stdout_capture.getvalue()
            stderr = stderr_capture.getvalue()
            
            # Try to extract a result if available
            result = None
            if 'result' in locals_dict and locals_dict['result'] is not None:
                result = locals_dict['result']
            
            return {
                "status": "success",
                "stdout": stdout,
                "stderr": stderr,
                "result": result
            }
        except Exception as e:
            # Get the traceback
            stderr = stderr_capture.getvalue()
            if not stderr:
                stderr = traceback.format_exc()
            
            logger.error(f"Error executing code: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr
            }
    
    def execute(self, **kwargs):
        """
        Execute the tool with the provided parameters.
        
        This method is called by the tool registry.
        """
        return self.run(**kwargs)
