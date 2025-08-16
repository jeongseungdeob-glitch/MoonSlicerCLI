#!/usr/bin/env python3
"""
CIA Roblox Executor - AI Interface Module
Handles AI communication and prompt construction for Roblox script generation
"""

import asyncio
import httpx
import json
import re
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

from utils.config import Config


class AIInterface:
    """Interface for AI-powered script generation"""
    
    def __init__(self):
        self.config = Config()
        
        # Integration with existing AI backend
        self.ollama_api = "http://localhost:11434/api/generate"
        self.model_map = {
            "mistral": "mistral:7b-instruct-q4_0",
            "deepseek": "deepseek-coder:6.7b-instruct-q4_0",
            "starcoder2": "starcoder2:7b-q4_0"
        }
        
        # Prompt templates
        self.prompt_templates = {
            "basic": self._get_basic_prompt_template(),
            "advanced": self._get_advanced_prompt_template(),
            "game_specific": self._get_game_specific_prompt_template(),
            "utility": self._get_utility_prompt_template()
        }
        
        # Script categories
        self.script_categories = {
            "player_control": ["movement", "teleport", "speed", "jump"],
            "visual_effects": ["particle", "lighting", "color", "transparency"],
            "game_mechanics": ["damage", "health", "score", "inventory"],
            "ui_interface": ["gui", "button", "text", "screen"],
            "automation": ["auto", "bot", "macro", "script"],
            "utility": ["utility", "tool", "helper", "function"]
        }
    
    def generate_roblox_script(self, prompt: str, model: str = "mistral", 
                              category: Optional[str] = None) -> Optional[str]:
        """Generate a Roblox script using AI"""
        try:
            # Determine script category
            if not category:
                category = self._detect_script_category(prompt)
            
            # Build comprehensive prompt
            full_prompt = self._build_prompt(prompt, category, model)
            
            # Generate script using AI
            script_content = self._call_ai_api(full_prompt, model)
            
            if script_content:
                # Clean and validate generated script
                cleaned_script = self._clean_generated_script(script_content)
                return cleaned_script
            else:
                return None
                
        except Exception as e:
            print(f"AI generation failed: {str(e)}")
            return None
    
    def _detect_script_category(self, prompt: str) -> str:
        """Detect script category based on prompt content"""
        prompt_lower = prompt.lower()
        
        for category, keywords in self.script_categories.items():
            for keyword in keywords:
                if keyword in prompt_lower:
                    return category
        
        return "utility"  # Default category
    
    def _build_prompt(self, user_prompt: str, category: str, model: str) -> str:
        """Build comprehensive prompt for script generation"""
        # Select appropriate template
        if category in ["player_control", "game_mechanics"]:
            template = self.prompt_templates["game_specific"]
        elif category in ["visual_effects", "ui_interface"]:
            template = self.prompt_templates["advanced"]
        else:
            template = self.prompt_templates["basic"]
        
        # Build context-aware prompt
        context = self._get_category_context(category)
        
        full_prompt = f"""
{template}

CATEGORY: {category.upper()}
CONTEXT: {context}

USER REQUEST: {user_prompt}

Generate a complete, working Roblox Lua script that:
1. Is safe and ethical for educational/testing purposes
2. Follows Roblox API best practices
3. Includes proper error handling
4. Has clear comments explaining the code
5. Is ready to execute in a Roblox environment

Return ONLY the Lua code without any explanations or markdown formatting.
"""
        return full_prompt.strip()
    
    def _get_category_context(self, category: str) -> str:
        """Get context information for script category"""
        contexts = {
            "player_control": "Scripts that control player movement, abilities, or interactions",
            "visual_effects": "Scripts that create visual effects, particles, or lighting changes",
            "game_mechanics": "Scripts that implement game rules, scoring, or mechanics",
            "ui_interface": "Scripts that create or modify user interface elements",
            "automation": "Scripts that automate tasks or create bots (for testing only)",
            "utility": "General utility scripts and helper functions"
        }
        
        return contexts.get(category, "General utility script")
    
    def _get_basic_prompt_template(self) -> str:
        """Get basic prompt template"""
        return """
You are an expert Roblox Lua developer. Create a safe, educational Roblox script based on the user's request.

SAFETY REQUIREMENTS:
- No malicious code or exploits
- No external network connections
- No file system access
- No system commands
- Educational/testing purposes only

ROBLOX API GUIDELINES:
- Use proper Roblox services and objects
- Include error handling with pcall
- Add descriptive comments
- Follow Lua best practices
"""
    
    def _get_advanced_prompt_template(self) -> str:
        """Get advanced prompt template for complex scripts"""
        return """
You are an expert Roblox Lua developer specializing in advanced scripting techniques.

ADVANCED REQUIREMENTS:
- Use proper object-oriented patterns
- Implement efficient algorithms
- Include comprehensive error handling
- Add performance optimizations
- Use Roblox-specific APIs effectively

SAFETY REQUIREMENTS:
- No malicious code or exploits
- No external network connections
- No file system access
- No system commands
- Educational/testing purposes only
"""
    
    def _get_game_specific_prompt_template(self) -> str:
        """Get game-specific prompt template"""
        return """
You are an expert Roblox Lua developer specializing in game mechanics and player interactions.

GAME MECHANICS REQUIREMENTS:
- Use proper game services (Players, Workspace, etc.)
- Implement safe player interactions
- Include proper event handling
- Add game balance considerations
- Use appropriate data structures

SAFETY REQUIREMENTS:
- No malicious code or exploits
- No external network connections
- No file system access
- No system commands
- Educational/testing purposes only
"""
    
    def _get_utility_prompt_template(self) -> str:
        """Get utility prompt template"""
        return """
You are an expert Roblox Lua developer creating utility and helper scripts.

UTILITY REQUIREMENTS:
- Create reusable functions
- Implement proper error handling
- Add clear documentation
- Use efficient algorithms
- Follow Lua best practices

SAFETY REQUIREMENTS:
- No malicious code or exploits
- No external network connections
- No file system access
- No system commands
- Educational/testing purposes only
"""
    
    def _call_ai_api(self, prompt: str, model: str) -> Optional[str]:
        """Call AI API to generate script"""
        try:
            # Use existing AI backend integration
            async def generate():
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.ollama_api,
                        json={
                            "model": self.model_map.get(model, self.model_map["mistral"]),
                            "prompt": prompt,
                            "stream": False
                        },
                        timeout=120.0  # Longer timeout for complex generation
                    )
                    
                    if response.status_code == 200:
                        return response.json().get("response", "")
                    else:
                        print(f"AI API error: {response.status_code}")
                        return None
            
            # Run async function in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(generate())
            finally:
                loop.close()
                
        except Exception as e:
            print(f"AI API call failed: {str(e)}")
            return None
    
    def _clean_generated_script(self, script_content: str) -> str:
        """Clean and format generated script content"""
        if not script_content:
            return ""
        
        # Remove markdown code blocks
        script_content = re.sub(r'```lua\s*', '', script_content)
        script_content = re.sub(r'```\s*$', '', script_content)
        
        # Remove leading/trailing whitespace
        script_content = script_content.strip()
        
        # Ensure script starts with proper Lua code
        if not script_content.startswith('--') and not script_content.startswith('local') and not script_content.startswith('function'):
            # Add basic structure if missing
            script_content = f"-- Generated Roblox Script\n-- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n{script_content}"
        
        return script_content
    
    def get_available_models(self) -> List[str]:
        """Get list of available AI models"""
        return list(self.model_map.keys())
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        if model not in self.model_map:
            return {"error": "Model not found"}
        
        return {
            "name": model,
            "ollama_name": self.model_map[model],
            "description": self._get_model_description(model),
            "capabilities": self._get_model_capabilities(model)
        }
    
    def _get_model_description(self, model: str) -> str:
        """Get model description"""
        descriptions = {
            "mistral": "General-purpose model good for basic scripting tasks",
            "deepseek": "Code-focused model excellent for complex algorithms",
            "starcoder2": "Specialized code generation model for programming tasks"
        }
        return descriptions.get(model, "Unknown model")
    
    def _get_model_capabilities(self, model: str) -> List[str]:
        """Get model capabilities"""
        capabilities = {
            "mistral": ["Basic scripting", "Simple game mechanics", "Utility functions"],
            "deepseek": ["Complex algorithms", "Advanced game mechanics", "Performance optimization"],
            "starcoder2": ["Code generation", "API usage", "Best practices"]
        }
        return capabilities.get(model, [])
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate user prompt for safety and appropriateness"""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "category": None,
            "complexity": "low"
        }
        
        prompt_lower = prompt.lower()
        
        # Check for inappropriate content
        inappropriate_keywords = [
            "hack", "cheat", "exploit", "bypass", "crack", "steal",
            "ddos", "spam", "crash", "destroy", "malicious"
        ]
        
        for keyword in inappropriate_keywords:
            if keyword in prompt_lower:
                validation_result["warnings"].append(f"Potentially inappropriate keyword: {keyword}")
        
        # Check for complex requests
        complex_keywords = [
            "advanced", "complex", "multi", "system", "network",
            "database", "server", "api", "external"
        ]
        
        complexity_count = sum(1 for keyword in complex_keywords if keyword in prompt_lower)
        if complexity_count > 2:
            validation_result["complexity"] = "high"
        elif complexity_count > 0:
            validation_result["complexity"] = "medium"
        
        # Detect category
        validation_result["category"] = self._detect_script_category(prompt)
        
        # Check prompt length
        if len(prompt) < 10:
            validation_result["errors"].append("Prompt too short")
            validation_result["valid"] = False
        elif len(prompt) > 1000:
            validation_result["warnings"].append("Prompt very long, may affect generation quality")
        
        return validation_result
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get AI generation statistics"""
        # This would typically track generation metrics
        # For now, return basic structure
        return {
            "total_generations": 0,
            "successful_generations": 0,
            "failed_generations": 0,
            "average_generation_time": 0.0,
            "most_used_model": "mistral",
            "most_common_category": "utility"
        }