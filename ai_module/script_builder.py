#!/usr/bin/env python3
"""
CIA Roblox Executor - Script Builder
Converts AI output into executable Lua scripts with proper formatting.
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from utils.config import Config
from executor.logger import ExecutionLogger


class ScriptBuilder:
    """
    Converts AI-generated text into properly formatted Lua scripts.
    Handles script extraction, formatting, and sanitization.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        
        # Script templates
        self.script_templates = {
            "basic": self._get_basic_template(),
            "game_script": self._get_game_script_template(),
            "utility": self._get_utility_template(),
            "test": self._get_test_template()
        }
        
        # Code block patterns
        self.code_patterns = [
            r'```lua\s*(.*?)\s*```',  # Markdown code blocks
            r'```\s*(.*?)\s*```',     # Generic code blocks
            r'`(.*?)`',               # Inline code
            r'--\s*Script\s*Start\s*--\s*(.*?)\s*--\s*Script\s*End\s*--',  # Custom markers
        ]
        
        # Script validation patterns
        self.validation_patterns = {
            'lua_keywords': [
                'local', 'function', 'if', 'then', 'else', 'elseif', 'end',
                'for', 'while', 'do', 'repeat', 'until', 'break', 'return',
                'and', 'or', 'not', 'true', 'false', 'nil'
            ],
            'roblox_apis': [
                'game', 'workspace', 'players', 'player', 'script',
                'Vector3', 'CFrame', 'Color3', 'Instance', 'TweenInfo',
                'wait', 'spawn', 'tick', 'time', 'warn', 'error', 'print'
            ]
        }
    
    def _get_basic_template(self) -> str:
        """Get basic script template"""
        return """-- CIA Roblox Executor - Generated Script
-- Generated: {timestamp}
-- Script Type: {script_type}
-- Security Level: {security_level}

{script_content}

-- End of generated script"""
    
    def _get_game_script_template(self) -> str:
        """Get game script template"""
        return """-- CIA Roblox Executor - Game Script
-- Generated: {timestamp}
-- Game Context: {game_context}
-- Script Type: Game Script

-- Initialize script
local function initialize()
    {script_content}
end

-- Run initialization
initialize()

-- End of game script"""
    
    def _get_utility_template(self) -> str:
        """Get utility script template"""
        return """-- CIA Roblox Executor - Utility Script
-- Generated: {timestamp}
-- Utility Type: {utility_type}
-- Description: {description}

-- Utility functions
{script_content}

-- End of utility script"""
    
    def _get_test_template(self) -> str:
        """Get test script template"""
        return """-- CIA Roblox Executor - Test Script
-- Generated: {timestamp}
-- Test Type: {test_type}
-- Purpose: {purpose}

-- Test script
{script_content}

-- End of test script"""
    
    def build_script(self, ai_response: str, script_type: str = "basic",
                    metadata: Dict[str, Any] = None) -> str:
        """
        Build a complete Lua script from AI response.
        
        Args:
            ai_response: Raw AI response
            script_type: Type of script to build
            metadata: Additional metadata for the script
            
        Returns:
            Formatted Lua script
        """
        try:
            # Extract Lua code from AI response
            lua_code = self._extract_lua_code(ai_response)
            
            if not lua_code:
                raise ValueError("No Lua code found in AI response")
            
            # Sanitize and format the code
            formatted_code = self._format_lua_code(lua_code)
            
            # Validate the code
            if not self._validate_lua_code(formatted_code):
                raise ValueError("Generated code failed validation")
            
            # Build the complete script
            complete_script = self._build_complete_script(
                formatted_code, script_type, metadata or {}
            )
            
            # Log the script building process
            self.logger.log_execution(
                f"Script built successfully from AI response",
                script_name=f"ai_generated_{script_type}",
                metadata={
                    "script_type": script_type,
                    "original_length": len(ai_response),
                    "final_length": len(complete_script),
                    "metadata": metadata
                }
            )
            
            return complete_script
            
        except Exception as e:
            self.logger.log_error(
                f"Script building failed: {str(e)}",
                error_type="script_building_error",
                metadata={"ai_response_length": len(ai_response), "script_type": script_type}
            )
            raise
    
    def _extract_lua_code(self, ai_response: str) -> str:
        """Extract Lua code from AI response"""
        # Try different patterns to extract code
        for pattern in self.code_patterns:
            matches = re.findall(pattern, ai_response, re.DOTALL | re.IGNORECASE)
            if matches:
                # Return the first match
                return matches[0].strip()
        
        # If no code blocks found, try to extract Lua-like content
        return self._extract_lua_like_content(ai_response)
    
    def _extract_lua_like_content(self, ai_response: str) -> str:
        """Extract Lua-like content when no code blocks are found"""
        lines = ai_response.split('\n')
        lua_lines = []
        in_code_section = False
        
        for line in lines:
            line = line.strip()
            
            # Check if line contains Lua-like content
            if self._is_lua_line(line):
                in_code_section = True
                lua_lines.append(line)
            elif in_code_section and line:
                # Continue if we're in a code section and line is not empty
                lua_lines.append(line)
            elif in_code_section and not line:
                # Empty line in code section - continue
                lua_lines.append(line)
            elif not line:
                # Empty line outside code section - skip
                continue
        
        return '\n'.join(lua_lines)
    
    def _is_lua_line(self, line: str) -> bool:
        """Check if a line looks like Lua code"""
        # Check for Lua keywords
        lua_keywords = self.validation_patterns['lua_keywords']
        roblox_apis = self.validation_patterns['roblox_apis']
        
        line_lower = line.lower()
        
        # Check for Lua keywords
        for keyword in lua_keywords:
            if keyword in line_lower:
                return True
        
        # Check for Roblox APIs
        for api in roblox_apis:
            if api.lower() in line_lower:
                return True
        
        # Check for Lua syntax patterns
        lua_patterns = [
            r'^\s*local\s+\w+',
            r'^\s*function\s+\w+',
            r'^\s*if\s+.*\s+then',
            r'^\s*for\s+.*\s+do',
            r'^\s*while\s+.*\s+do',
            r'^\s*print\s*\(',
            r'^\s*wait\s*\(',
            r'^\s*--.*',  # Comments
        ]
        
        for pattern in lua_patterns:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        
        return False
    
    def _format_lua_code(self, lua_code: str) -> str:
        """Format and clean Lua code"""
        # Remove extra whitespace
        lines = lua_code.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Basic indentation fix
                if line.startswith('end') or line.startswith('else') or line.startswith('elseif'):
                    # Reduce indentation for control flow keywords
                    line = line.lstrip()
                elif line.startswith('function') or line.startswith('if') or line.startswith('for') or line.startswith('while'):
                    # Ensure proper indentation for block starters
                    line = line.lstrip()
                
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def _validate_lua_code(self, lua_code: str) -> bool:
        """Validate that the code looks like valid Lua"""
        if not lua_code or len(lua_code.strip()) < 10:
            return False
        
        # Check for basic Lua structure
        has_function = 'function' in lua_code.lower()
        has_print = 'print' in lua_code.lower()
        has_roblox_api = any(api.lower() in lua_code.lower() for api in self.validation_patterns['roblox_apis'])
        
        # Must have at least one of these
        if not (has_function or has_print or has_roblox_api):
            return False
        
        # Check for balanced brackets and parentheses
        if not self._check_balanced_delimiters(lua_code):
            return False
        
        return True
    
    def _check_balanced_delimiters(self, code: str) -> bool:
        """Check if brackets and parentheses are balanced"""
        stack = []
        delimiters = {'(': ')', '[': ']', '{': '}'}
        
        for char in code:
            if char in delimiters:
                stack.append(char)
            elif char in delimiters.values():
                if not stack:
                    return False
                if delimiters[stack.pop()] != char:
                    return False
        
        return len(stack) == 0
    
    def _build_complete_script(self, lua_code: str, script_type: str,
                              metadata: Dict[str, Any]) -> str:
        """Build the complete script with template"""
        template = self.script_templates.get(script_type, self.script_templates["basic"])
        
        # Prepare template variables
        template_vars = {
            'timestamp': datetime.now().isoformat(),
            'script_type': script_type,
            'security_level': metadata.get('security_level', 'standard'),
            'script_content': lua_code,
            'game_context': metadata.get('game_context', 'General'),
            'utility_type': metadata.get('utility_type', 'General'),
            'description': metadata.get('description', 'AI-generated script'),
            'test_type': metadata.get('test_type', 'General'),
            'purpose': metadata.get('purpose', 'Testing and development')
        }
        
        return template.format(**template_vars)
    
    def sanitize_script(self, script: str) -> str:
        """
        Sanitize a script to remove potentially dangerous content.
        
        Args:
            script: The script to sanitize
            
        Returns:
            Sanitized script
        """
        # Remove dangerous patterns
        dangerous_patterns = [
            r'os\.execute\s*\(',
            r'io\.popen\s*\(',
            r'loadstring\s*\(',
            r'dofile\s*\(',
            r'loadfile\s*\(',
            r'require\s*\(',
            r'package\.',
            r'debug\.',
            r'collectgarbage\s*\(',
            r'coroutine\.',
            r'jit\.',
        ]
        
        sanitized_script = script
        
        for pattern in dangerous_patterns:
            sanitized_script = re.sub(pattern, '-- REMOVED: ' + pattern, sanitized_script, flags=re.IGNORECASE)
        
        # Add security warning if dangerous content was found
        if '-- REMOVED:' in sanitized_script:
            sanitized_script = f"""-- SECURITY WARNING: This script contained potentially dangerous code that has been removed
-- Please review the script before execution

{sanitized_script}"""
        
        return sanitized_script
    
    def add_error_handling(self, script: str) -> str:
        """
        Add error handling to a script.
        
        Args:
            script: The script to add error handling to
            
        Returns:
            Script with error handling
        """
        # Wrap main script content in error handling
        error_handled_script = f"""-- Error handling wrapper
local success, result = pcall(function()
{script}
end)

if not success then
    warn("Script execution failed: " .. tostring(result))
else
    print("Script executed successfully")
end"""
        
        return error_handled_script
    
    def add_performance_monitoring(self, script: str) -> str:
        """
        Add performance monitoring to a script.
        
        Args:
            script: The script to add monitoring to
            
        Returns:
            Script with performance monitoring
        """
        monitored_script = f"""-- Performance monitoring
local start_time = tick()

{script}

local end_time = tick()
local execution_time = end_time - start_time
print("Script execution time: " .. execution_time .. " seconds")"""
        
        return monitored_script
    
    def create_script_variant(self, script: str, variant_type: str) -> str:
        """
        Create a variant of a script.
        
        Args:
            script: The original script
            variant_type: Type of variant to create
            
        Returns:
            Script variant
        """
        if variant_type == "with_error_handling":
            return self.add_error_handling(script)
        elif variant_type == "with_performance_monitoring":
            return self.add_performance_monitoring(script)
        elif variant_type == "sanitized":
            return self.sanitize_script(script)
        else:
            return script
    
    def get_script_statistics(self, script: str) -> Dict[str, Any]:
        """
        Get statistics about a script.
        
        Args:
            script: The script to analyze
            
        Returns:
            Script statistics
        """
        lines = script.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith('--')]
        code_lines = [line for line in non_empty_lines if not line.strip().startswith('--')]
        
        # Count different elements
        function_count = len(re.findall(r'function\s+\w+', script, re.IGNORECASE))
        variable_count = len(re.findall(r'local\s+\w+', script, re.IGNORECASE))
        print_count = len(re.findall(r'print\s*\(', script, re.IGNORECASE))
        wait_count = len(re.findall(r'wait\s*\(', script, re.IGNORECASE))
        
        return {
            'total_lines': len(lines),
            'non_empty_lines': len(non_empty_lines),
            'comment_lines': len(comment_lines),
            'code_lines': len(code_lines),
            'function_count': function_count,
            'variable_count': variable_count,
            'print_count': print_count,
            'wait_count': wait_count,
            'script_size_bytes': len(script.encode('utf-8')),
            'comment_ratio': len(comment_lines) / len(non_empty_lines) if non_empty_lines else 0
        }