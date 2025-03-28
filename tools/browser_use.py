"""
Browser use tool for the Syntient AI Assistant Platform.

This module provides a functional tool for browsing websites and extracting information
using requests and BeautifulSoup.
"""

import logging
import requests
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re

from .base import Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BrowserUseTool(Tool):
    """
    Tool for browsing websites and extracting information.
    
    This is a functional implementation using requests and BeautifulSoup.
    """
    
    def __init__(self):
        """Initialize the browser use tool."""
        super().__init__(
            name="browser_use",
            description="Browse websites and extract information"
        )
        # Common headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def run(self, url: str, selector: Optional[str] = None) -> Dict[str, Any]:
        """
        Browse a website and extract information.
        
        Args:
            url: URL of the website to browse
            selector: Optional CSS selector to target specific elements
            
        Returns:
            Dictionary containing the extracted information
        """
        logger.info(f"BrowserUseTool: Browsing URL: {url}")
                
        logger.info("🔧 browser_use tool triggered")
        logger.info(f"🧭 Target URL: {url}")



        try:
            # Make the request
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(["script", "style"]):
                script_or_style.decompose()
            
            # If a selector is provided, use it to find specific elements
            if selector:
                elements = soup.select(selector)
                text = "\n".join([elem.get_text(strip=True) for elem in elements])
            else:
                # Extract the main content
                # First try to find main content containers
                main_content = soup.find(['main', 'article', 'div', 'section'], 
                                        class_=re.compile(r'(content|main|article|post)'))
                
                if main_content:
                    text = main_content.get_text(separator="\n", strip=True)
                else:
                    # If no main content container is found, use the body
                    text = soup.body.get_text(separator="\n", strip=True)
            
            # Clean up the text
            text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with a single one
            text = re.sub(r'\s+', ' ', text)   # Replace multiple spaces with a single one
            
            # Create a summary if the text is too long
            if len(text) > 5000:
                summary = text[:5000] + "... [Content truncated due to length]"
            else:
                summary = text
            
            # Extract the title
            title = soup.title.string if soup.title else "No title found"
            
            # Extract meta description
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")
            
            return {
                "status": "success",
                "url": url,
                "title": title,
                "meta_description": meta_desc,
                "content": summary,
                "content_length": len(text),
                "truncated": len(text) > 5000
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return {
                "status": "error",
                "url": url,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return {
                "status": "error",
                "url": url,
                "error": str(e)
            }
    
    def execute(self, **kwargs):
        """
        Execute the tool with the provided parameters.
        
        This method is called by the tool registry.
        """
        return self.run(**kwargs)
