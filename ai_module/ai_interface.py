#!/usr/bin/env python3
"""
CIA Roblox Executor - AI Interface
Handles AI communication for generating Roblox Lua scripts.
"""

import os
import json
import time
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

from utils.config import Config
from executor.logger import ExecutionLogger


class AIInterface:
    """
    Interface for AI model communication and script generation.
    Supports multiple AI models and provides structured script generation.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        
        # AI model configuration
        self.models = {
            "mistral": {
                "name": "mistral:7b-instruct-q4_0",
                "api_url": "http://localhost:11434/api/generate",
                "max_tokens": 2048,
                "temperature": 0.7
            },
            "deepseek": {
                "name": "deepseek-coder:6.7b-instruct-q4_0",
                "api_url": "http://localhost:11434/api/generate",
                "max_tokens": 2048,
                "temperature": 0.5
            },
            "starcoder2": {
                "name": "starcoder2:7b-q4_0",
                "api_url": "http://localhost:11434/api/generate",
                "max_tokens": 2048,
                "temperature": 0.6
            }
        }
        
        # Default model
        self.default_model = "mistral"
        
        # Prompt templates
        self.prompt_templates = {
            "basic": self._get_basic_prompt_template(),
            "advanced": self._get_advanced_prompt_template(),
            "security": self._get_security_prompt_template(),
            "game_specific": self._get_game_specific_prompt_template()
        }
        
        # Generation history
        self.generation_history = []
    
    def _get_basic_prompt_template(self) -> str:
        """Get basic prompt template for script generation"""
        return """You are an expert Roblox Lua script developer. Generate a safe, functional Lua script based on the user's request.

Requirements:
- Use only safe Roblox APIs
- Include proper error handling
- Add comments for clarity
- Ensure the script is ethical and for educational purposes only
- Do not include any malicious code or exploits

User Request: {user_request}

Generate a complete, working Lua script:"""

    def _get_advanced_prompt_template(self) -> str:
        """Get advanced prompt template with more detailed instructions"""
        return """You are an expert Roblox Lua script developer with deep knowledge of Roblox APIs and best practices.

Generate a professional-grade Lua script with the following requirements:

1. **Safety First**: Only use safe, documented Roblox APIs
2. **Error Handling**: Include proper try-catch blocks and error checking
3. **Performance**: Optimize for performance and avoid infinite loops
4. **Documentation**: Add comprehensive comments explaining the code
5. **Modularity**: Structure the code in a modular, maintainable way
6. **Ethics**: Ensure the script is for educational/internal testing only

User Request: {user_request}

Additional Context: {additional_context}

Generate a complete, production-ready Lua script:"""

    def _get_security_prompt_template(self) -> str:
        """Get security-focused prompt template"""
        return """You are a security-conscious Roblox Lua script developer. Generate a script that prioritizes safety and security.

Security Requirements:
- NO file system access
- NO network requests (unless explicitly requested)
- NO debug functions
- NO coroutines or threading
- NO infinite loops
- NO memory-intensive operations
- Use only whitelisted Roblox APIs

Safety Checklist:
✓ Input validation
✓ Error handling
✓ Resource limits
✓ Safe API usage
✓ No malicious code

User Request: {user_request}

Generate a secure Lua script:"""

    def _get_game_specific_prompt_template(self) -> str:
        """Get game-specific prompt template"""
        return """You are a Roblox game developer. Generate a Lua script for a specific game scenario.

Game Development Guidelines:
- Use appropriate Roblox game APIs
- Consider game performance and optimization
- Include proper game state management
- Handle player interactions safely
- Follow Roblox game development best practices

Game Context: {game_context}
User Request: {user_request}

Generate a game-specific Lua script:"""

    def generate_roblox_script(self, user_request: str, 
                              model: str = None, 
                              prompt_type: str = "basic",
                              additional_context: str = "",
                              game_context: str = "") -> str:
        """
        Generate a Roblox Lua script using AI.
        
        Args:
            user_request: The user's script request
            model: AI model to use (default: auto-select)
            prompt_type: Type of prompt template to use
            additional_context: Additional context for the request
            game_context: Game-specific context
            
        Returns:
            Generated Lua script
        """
        try:
            start_time = time.time()
            
            # Auto-select model if not specified
            if not model:
                model = self._select_best_model(user_request)
            
            # Validate model
            if model not in self.models:
                raise ValueError(f"Unknown model: {model}")
            
            # Get prompt template
            template = self.prompt_templates.get(prompt_type, self.prompt_templates["basic"])
            
            # Format prompt
            prompt = self._format_prompt(template, user_request, additional_context, game_context)
            
            # Generate script
            self.logger.log_ai_interaction(
                prompt=prompt,
                response="",  # Will be filled after generation
                model=model,
                generation_time=0.0,
                metadata={"prompt_type": prompt_type}
            )
            
            # Call AI model
            response = self._call_ai_model(model, prompt)
            
            # Calculate generation time
            generation_time = time.time() - start_time
            
            # Log the complete interaction
            self.logger.log_ai_interaction(
                prompt=prompt,
                response=response,
                model=model,
                generation_time=generation_time,
                metadata={"prompt_type": prompt_type}
            )
            
            # Store in history
            self._store_generation_history(user_request, response, model, generation_time)
            
            return response
            
        except Exception as e:
            self.logger.log_error(
                f"AI script generation failed: {str(e)}",
                error_type="ai_generation_error",
                metadata={"user_request": user_request, "model": model}
            )
            raise
    
    def _select_best_model(self, user_request: str) -> str:
        """Select the best AI model based on the request"""
        request_lower = user_request.lower()
        
        # Route based on content
        if any(keyword in request_lower for keyword in ["python", "automation", "scripting"]):
            return "deepseek"
        elif any(keyword in request_lower for keyword in ["repo", "multi-file", "github", "complex"]):
            return "starcoder2"
        else:
            return "mistral"
    
    def _format_prompt(self, template: str, user_request: str, 
                      additional_context: str = "", game_context: str = "") -> str:
        """Format the prompt template with user input"""
        return template.format(
            user_request=user_request,
            additional_context=additional_context,
            game_context=game_context
        )
    
    def _call_ai_model(self, model: str, prompt: str) -> str:
        """Call the AI model API"""
        model_config = self.models[model]
        
        # Prepare request payload
        payload = {
            "model": model_config["name"],
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": model_config["temperature"],
                "num_predict": model_config["max_tokens"]
            }
        }
        
        try:
            # Make API request
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    model_config["api_url"],
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code != 200:
                    raise Exception(f"API request failed with status {response.status_code}")
                
                result = response.json()
                return result.get("response", "")
                
        except httpx.RequestError as e:
            raise Exception(f"Network error: {str(e)}")
        except Exception as e:
            raise Exception(f"AI model call failed: {str(e)}")
    
    def _store_generation_history(self, user_request: str, response: str, 
                                 model: str, generation_time: float):
        """Store generation in history"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_request": user_request,
            "response": response,
            "model": model,
            "generation_time": generation_time,
            "response_length": len(response)
        }
        
        self.generation_history.append(history_entry)
        
        # Keep only last 100 entries
        if len(self.generation_history) > 100:
            self.generation_history = self.generation_history[-100:]
    
    def generate_script_with_context(self, user_request: str, 
                                   context_type: str = "general",
                                   **kwargs) -> str:
        """
        Generate script with specific context.
        
        Args:
            user_request: The user's request
            context_type: Type of context (general, game, security, etc.)
            **kwargs: Additional context parameters
            
        Returns:
            Generated script
        """
        context_mapping = {
            "general": "basic",
            "game": "game_specific",
            "security": "security",
            "advanced": "advanced"
        }
        
        prompt_type = context_mapping.get(context_type, "basic")
        
        # Extract context parameters
        additional_context = kwargs.get("additional_context", "")
        game_context = kwargs.get("game_context", "")
        model = kwargs.get("model", None)
        
        return self.generate_roblox_script(
            user_request=user_request,
            model=model,
            prompt_type=prompt_type,
            additional_context=additional_context,
            game_context=game_context
        )
    
    def get_generation_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get generation history"""
        return self.generation_history[-limit:]
    
    def clear_generation_history(self):
        """Clear generation history"""
        self.generation_history.clear()
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}")
        
        return self.models[model].copy()
    
    def list_available_models(self) -> List[str]:
        """List available AI models"""
        return list(self.models.keys())
    
    def test_model_connection(self, model: str) -> bool:
        """Test connection to a specific model"""
        try:
            if model not in self.models:
                return False
            
            # Simple test prompt
            test_prompt = "Generate a simple Lua script that prints 'Hello, World!'"
            response = self._call_ai_model(model, test_prompt)
            
            return len(response.strip()) > 0
            
        except Exception:
            return False
    
    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get statistics about script generation"""
        if not self.generation_history:
            return {
                "total_generations": 0,
                "average_generation_time": 0,
                "model_usage": {},
                "total_response_length": 0
            }
        
        total_generations = len(self.generation_history)
        total_time = sum(entry["generation_time"] for entry in self.generation_history)
        average_time = total_time / total_generations
        
        # Model usage statistics
        model_usage = {}
        for entry in self.generation_history:
            model = entry["model"]
            model_usage[model] = model_usage.get(model, 0) + 1
        
        total_response_length = sum(entry["response_length"] for entry in self.generation_history)
        
        return {
            "total_generations": total_generations,
            "average_generation_time": average_time,
            "model_usage": model_usage,
            "total_response_length": total_response_length,
            "last_generation": self.generation_history[-1]["timestamp"] if self.generation_history else None
        }