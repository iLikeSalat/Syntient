"""
File parser tool for the Syntient AI Assistant Platform.

This module provides file parsing capabilities for various file formats.
"""

import json
import csv
import os
from typing import Dict, Any, Optional, List, Union, TextIO
from ..base import Tool


class FileParserTool(Tool):
    """
    Tool for parsing and extracting information from various file formats.
    
    This tool allows the assistant to read and parse different file types,
    including CSV, JSON, TXT, and more.
    """
    
    def __init__(self):
        """Initialize the File Parser tool."""
        super().__init__(
            name="file_parser",
            description="Parse and extract information from various file formats"
        )
        self.supported_formats = ["csv", "json", "txt", "md"]
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a file parsing action.
        
        Args:
            action: Action to perform (parse_file, extract_data, etc.)
            **kwargs: Action-specific parameters
            
        Returns:
            Result of the action
            
        Raises:
            ValueError: If the action is invalid or file format is unsupported
        """
        if action == "parse_file":
            return self.parse_file(**kwargs)
        elif action == "extract_data":
            return self.extract_data(**kwargs)
        elif action == "get_file_info":
            return self.get_file_info(**kwargs)
        else:
            raise ValueError(f"Invalid action: {action}")
    
    def parse_file(self, file_path: str, format_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Parse a file and return its contents in a structured format.
        
        Args:
            file_path: Path to the file to parse
            format_hint: Optional hint about the file format
            
        Returns:
            Parsed file contents
            
        Raises:
            ValueError: If the file format is unsupported or the file doesn't exist
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        file_format = format_hint or self._detect_format(file_path)
        
        if file_format not in self.supported_formats:
            return {"error": f"Unsupported file format: {file_format}"}
        
        try:
            if file_format == "csv":
                return self._parse_csv(file_path)
            elif file_format == "json":
                return self._parse_json(file_path)
            elif file_format in ["txt", "md"]:
                return self._parse_text(file_path)
            else:
                return {"error": f"Unsupported file format: {file_format}"}
        except Exception as e:
            return {"error": f"Failed to parse file: {str(e)}"}
    
    def extract_data(self, file_path: str, query: str) -> Dict[str, Any]:
        """
        Extract specific data from a file based on a query.
        
        Args:
            file_path: Path to the file to extract data from
            query: Query to extract data (e.g., JSON path, CSV column)
            
        Returns:
            Extracted data
            
        Raises:
            ValueError: If the file format is unsupported or the query is invalid
        """
        parsed_data = self.parse_file(file_path)
        
        if "error" in parsed_data:
            return parsed_data
        
        file_format = self._detect_format(file_path)
        
        try:
            if file_format == "csv":
                # For CSV, query can be a column name or index
                if isinstance(query, str) and query.isdigit():
                    query = int(query)
                
                if isinstance(query, int):
                    # Extract by column index
                    return {
                        "data": [row[query] if query < len(row) else None for row in parsed_data["data"]],
                        "format": "csv"
                    }
                else:
                    # Extract by column name
                    if query not in parsed_data["headers"]:
                        return {"error": f"Column not found: {query}"}
                    
                    col_idx = parsed_data["headers"].index(query)
                    return {
                        "data": [row[col_idx] if col_idx < len(row) else None for row in parsed_data["data"]],
                        "format": "csv"
                    }
            
            elif file_format == "json":
                # For JSON, query can be a simple path (e.g., "data.items[0].name")
                parts = query.split(".")
                result = parsed_data["data"]
                
                for part in parts:
                    if "[" in part and part.endswith("]"):
                        # Handle array indexing
                        key, idx_str = part.split("[", 1)
                        idx = int(idx_str[:-1])  # Remove the closing bracket
                        
                        if key:
                            result = result.get(key, [])
                        
                        if isinstance(result, list) and 0 <= idx < len(result):
                            result = result[idx]
                        else:
                            return {"error": f"Invalid array index: {idx}"}
                    else:
                        # Handle object property
                        if isinstance(result, dict):
                            result = result.get(part)
                        else:
                            return {"error": f"Cannot access property '{part}' on non-object"}
                
                return {
                    "data": result,
                    "format": "json"
                }
            
            elif file_format in ["txt", "md"]:
                # For text files, query can be a line number or a search string
                if query.isdigit():
                    # Extract by line number
                    line_num = int(query)
                    lines = parsed_data["data"].split("\n")
                    
                    if 0 <= line_num < len(lines):
                        return {
                            "data": lines[line_num],
                            "format": "text"
                        }
                    else:
                        return {"error": f"Line number out of range: {line_num}"}
                else:
                    # Extract by search string
                    lines = parsed_data["data"].split("\n")
                    matching_lines = [line for line in lines if query in line]
                    
                    return {
                        "data": matching_lines,
                        "format": "text"
                    }
            
            else:
                return {"error": f"Unsupported file format for extraction: {file_format}"}
        
        except Exception as e:
            return {"error": f"Failed to extract data: {str(e)}"}
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File information
        """
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
        
        try:
            file_stats = os.stat(file_path)
            file_format = self._detect_format(file_path)
            
            return {
                "path": file_path,
                "size": file_stats.st_size,
                "format": file_format,
                "last_modified": file_stats.st_mtime,
                "supported": file_format in self.supported_formats
            }
        except Exception as e:
            return {"error": f"Failed to get file info: {str(e)}"}
    
    def _detect_format(self, file_path: str) -> str:
        """
        Detect the format of a file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Detected file format
        """
        _, ext = os.path.splitext(file_path)
        return ext.lower()[1:] if ext else ""
    
    def _parse_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a CSV file.
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Parsed CSV data
        """
        with open(file_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            data = list(reader)
            
            return {
                "headers": headers,
                "data": data,
                "rows": len(data),
                "columns": len(headers),
                "format": "csv"
            }
    
    def _parse_json(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            return {
                "data": data,
                "format": "json"
            }
    
    def _parse_text(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            Parsed text data
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            return {
                "data": content,
                "lines": len(lines),
                "format": "text"
            }
    
    def _get_parameters_schema(self) -> Dict[str, Any]:
        """
        Get the schema for this tool's parameters.
        
        Returns:
            Dictionary describing the parameters and their types
        """
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["parse_file", "extract_data", "get_file_info"],
                    "description": "Action to perform"
                },
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to parse or extract data from"
                },
                "format_hint": {
                    "type": "string",
                    "enum": ["csv", "json", "txt", "md"],
                    "description": "Optional hint about the file format"
                },
                "query": {
                    "type": "string",
                    "description": "Query to extract data (e.g., JSON path, CSV column)"
                }
            },
            "required": ["action", "file_path"]
        }
