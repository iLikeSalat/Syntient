"""
LLM Manager module for the Syntient AI Assistant Platform.

This module provides an abstraction layer for different LLM providers,
allowing easy switching between OpenAI, Claude, Mistral, Ollama, and others.
"""

import os
import json
import time
import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All LLM provider implementations must inherit from this class
    and implement the required methods.
    """
    
    @abstractmethod
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion from the LLM.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing the completion result
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from this provider.
        
        Returns:
            List of model identifiers
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        pass

class OpenAIProvider(LLMProvider):
    """
    OpenAI API provider implementation.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model: Model to use for completions (default: gpt-3.5-turbo)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set it in .env or pass to constructor.")
        
        self.model = model
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion from the OpenAI API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            **kwargs: Additional OpenAI-specific parameters
            
        Returns:
            Dictionary containing the completion result
        """
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["model"]:  # Skip parameters that are already set
                payload[key] = value
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Implement retry logic
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException:
                    retry_count += 1
            
            # If all retries fail, raise the exception
            raise Exception(f"Failed to call OpenAI API after {max_retries} retries: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from OpenAI.
        
        Returns:
            List of model identifiers
        """
        # This is a simplified implementation
        # In a real implementation, this would call the OpenAI API to get the list of models
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-32k"
        ]
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        return "OpenAI"

class AnthropicProvider(LLMProvider):
    """
    Anthropic Claude API provider implementation.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-opus-20240229"):
        """
        Initialize the Anthropic provider.
        
        Args:
            api_key: Anthropic API key (defaults to environment variable)
            model: Model to use for completions (default: claude-3-opus-20240229)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set it in .env or pass to constructor.")
        
        self.model = model
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion from the Anthropic Claude API.
        
        Args:
            messages: List of message dictionaries (OpenAI format)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            **kwargs: Additional Anthropic-specific parameters
            
        Returns:
            Dictionary containing the completion result (converted to OpenAI format)
        """
        # Convert OpenAI format messages to Anthropic format
        system_prompt = None
        anthropic_messages = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                anthropic_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                anthropic_messages.append({"role": "assistant", "content": content})
        
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": anthropic_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add system prompt if present
        if system_prompt:
            payload["system"] = system_prompt
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["model"]:  # Skip parameters that are already set
                payload[key] = value
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            # Convert Anthropic response to OpenAI format
            anthropic_response = response.json()
            openai_format_response = {
                "id": anthropic_response.get("id", ""),
                "object": "chat.completion",
                "created": int(time.time()),
                "model": anthropic_response.get("model", self.model),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": anthropic_response.get("content", [{"text": ""}])[0]["text"]
                        },
                        "finish_reason": anthropic_response.get("stop_reason", "stop")
                    }
                ],
                "usage": anthropic_response.get("usage", {})
            }
            
            return openai_format_response
        except requests.exceptions.RequestException as e:
            # Implement retry logic
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    
                    # Convert Anthropic response to OpenAI format
                    anthropic_response = response.json()
                    openai_format_response = {
                        "id": anthropic_response.get("id", ""),
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": anthropic_response.get("model", self.model),
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": anthropic_response.get("content", [{"text": ""}])[0]["text"]
                                },
                                "finish_reason": anthropic_response.get("stop_reason", "stop")
                            }
                        ],
                        "usage": anthropic_response.get("usage", {})
                    }
                    
                    return openai_format_response
                except requests.exceptions.RequestException:
                    retry_count += 1
            
            # If all retries fail, raise the exception
            raise Exception(f"Failed to call Anthropic API after {max_retries} retries: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from Anthropic.
        
        Returns:
            List of model identifiers
        """
        # This is a simplified implementation
        return [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0"
        ]
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        return "Anthropic Claude"

class MistralProvider(LLMProvider):
    """
    Mistral AI provider implementation.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "mistral-large-latest"):
        """
        Initialize the Mistral provider.
        
        Args:
            api_key: Mistral API key (defaults to environment variable)
            model: Model to use for completions (default: mistral-large-latest)
        """
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set it in .env or pass to constructor.")
        
        self.model = model
        self.api_url = "https://api.mistral.ai/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion from the Mistral API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            **kwargs: Additional Mistral-specific parameters
            
        Returns:
            Dictionary containing the completion result
        """
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ["model"]:  # Skip parameters that are already set
                payload[key] = value
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # Implement retry logic
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    return response.json()
                except requests.exceptions.RequestException:
                    retry_count += 1
            
            # If all retries fail, raise the exception
            raise Exception(f"Failed to call Mistral API after {max_retries} retries: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from Mistral.
        
        Returns:
            List of model identifiers
        """
        # This is a simplified implementation
        return [
            "mistral-tiny",
            "mistral-small",
            "mistral-medium",
            "mistral-large-latest"
        ]
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        return "Mistral AI"

class OllamaProvider(LLMProvider):
    """
    Ollama local LLM provider implementation.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        """
        Initialize the Ollama provider.
        
        Args:
            base_url: Base URL for the Ollama API (default: http://localhost:11434)
            model: Model to use for completions (default: llama3)
        """
        self.base_url = base_url
        self.model = model
        self.api_url = f"{base_url}/api/chat"
        self.headers = {
            "Content-Type": "application/json"
        }
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion from the Ollama API.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            **kwargs: Additional Ollama-specific parameters
            
        Returns:
            Dictionary containing the completion result (converted to OpenAI format)
        """
        payload = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        # Add any additional options
        for key, value in kwargs.items():
            if key not in ["model"] and key not in payload["options"]:
                payload["options"][key] = value
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            # Convert Ollama response to OpenAI format
            ollama_response = response.json()
            openai_format_response = {
                "id": f"ollama-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": ollama_response.get("model", self.model),
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": ollama_response.get("message", {}).get("content", "")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": ollama_response.get("prompt_eval_count", 0),
                    "completion_tokens": ollama_response.get("eval_count", 0),
                    "total_tokens": ollama_response.get("prompt_eval_count", 0) + ollama_response.get("eval_count", 0)
                }
            }
            
            return openai_format_response
        except requests.exceptions.RequestException as e:
            # Implement retry logic
            retry_count = 0
            max_retries = 3
            while retry_count < max_retries:
                try:
                    time.sleep(2 ** retry_count)  # Exponential backoff
                    response = requests.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload
                    )
                    response.raise_for_status()
                    
                    # Convert Ollama response to OpenAI format
                    ollama_response = response.json()
                    openai_format_response = {
                        "id": f"ollama-{int(time.time())}",
                        "object": "chat.completion",
                        "created": int(time.time()),
                        "model": ollama_response.get("model", self.model),
                        "choices": [
                            {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": ollama_response.get("message", {}).get("content", "")
                                },
                                "finish_reason": "stop"
                            }
                        ],
                        "usage": {
                            "prompt_tokens": ollama_response.get("prompt_eval_count", 0),
                            "completion_tokens": ollama_response.get("eval_count", 0),
                            "total_tokens": ollama_response.get("prompt_eval_count", 0) + ollama_response.get("eval_count", 0)
                        }
                    }
                    
                    return openai_format_response
                except requests.exceptions.RequestException:
                    retry_count += 1
            
            # If all retries fail, raise the exception
            raise Exception(f"Failed to call Ollama API after {max_retries} retries: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """
        Get a list of available models from Ollama.
        
        Returns:
            List of model identifiers
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models_data = response.json()
            
            # Extract model names
            models = [model["name"] for model in models_data.get("models", [])]
            return models
        except:
            # Return default models if API call fails
            return [
                "llama3",
                "llama3:8b",
                "llama3:70b",
                "mistral",
                "mixtral",
                "phi3"
            ]
    
    def get_provider_name(self) -> str:
        """
        Get the name of this provider.
        
        Returns:
            Provider name
        """
        return "Ollama"

class LLMManager:
    """
    Manager for LLM providers.
    
    This class provides a unified interface for different LLM providers
    and allows easy switching between them.
    """
    
    def __init__(self, default_provider: str = "openai"):
        """
        Initialize the LLM manager.
        
        Args:
            default_provider: Default provider to use (default: openai)
        """
        self.providers = {}
        self.default_provider = default_provider
        
        # Register built-in providers
        self._register_built_in_providers()
    
    def _register_built_in_providers(self):
        """Register the built-in providers."""
        try:
            self.register_provider("openai", OpenAIProvider())
        except Exception as e:
            logger.warning(f"Failed to register OpenAI provider: {str(e)}")
        
        try:
            self.register_provider("anthropic", AnthropicProvider())
        except Exception as e:
            logger.warning(f"Failed to register Anthropic provider: {str(e)}")
        
        try:
            self.register_provider("mistral", MistralProvider())
        except Exception as e:
            logger.warning(f"Failed to register Mistral provider: {str(e)}")
        
        try:
            self.register_provider("ollama", OllamaProvider())
        except Exception as e:
            logger.warning(f"Failed to register Ollama provider: {str(e)}")
    
    def register_provider(self, name: str, provider: LLMProvider):
        """
        Register an LLM provider.
        
        Args:
            name: Name of the provider
            provider: Provider instance
        """
        self.providers[name] = provider
        logger.info(f"Registered LLM provider: {name}")
    
    def get_provider(self, name: Optional[str] = None) -> LLMProvider:
        """
        Get an LLM provider by name.
        
        Args:
            name: Name of the provider (defaults to default_provider)
            
        Returns:
            Provider instance
            
        Raises:
            ValueError: If the provider is not found
        """
        provider_name = name or self.default_provider
        
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not found")
        
        return self.providers[provider_name]
    
    def set_default_provider(self, name: str):
        """
        Set the default provider.
        
        Args:
            name: Name of the provider
            
        Raises:
            ValueError: If the provider is not found
        """
        if name not in self.providers:
            raise ValueError(f"Provider '{name}' not found")
        
        self.default_provider = name
        logger.info(f"Set default LLM provider to: {name}")
    
    def get_available_providers(self) -> Dict[str, str]:
        """
        Get a dictionary of available providers.
        
        Returns:
            Dictionary mapping provider names to their display names
        """
        return {name: provider.get_provider_name() for name, provider in self.providers.items()}
    
    def get_available_models(self, provider_name: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Get available models from providers.
        
        Args:
            provider_name: Optional name of a specific provider
            
        Returns:
            Dictionary mapping provider names to lists of available models
        """
        if provider_name:
            provider = self.get_provider(provider_name)
            return {provider_name: provider.get_available_models()}
        
        return {name: provider.get_available_models() for name, provider in self.providers.items()}
    
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        provider_name: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a completion using the specified provider.
        
        Args:
            messages: List of message dictionaries
            provider_name: Name of the provider to use (defaults to default_provider)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in the response
            **kwargs: Additional provider-specific parameters
            
        Returns:
            Dictionary containing the completion result
        """
        provider = self.get_provider(provider_name)
        
        logger.info(f"Generating completion using provider: {provider.get_provider_name()}")
        return provider.generate_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def extract_response_content(self, api_response: Dict[str, Any]) -> str:
        """
        Extract the assistant's response content from the API response.
        
        This method works with the OpenAI-compatible format that all providers
        are converted to.
        
        Args:
            api_response: Response from the LLM API
            
        Returns:
            Assistant's response as a string
        """
        try:
            return api_response["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            raise Exception(f"Failed to extract response content: {str(e)}")

# Create a singleton instance
llm_manager = LLMManager()
