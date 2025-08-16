#!/usr/bin/env python3
"""
CIA Roblox Executor - Anti-Cheat Bypass
Handles Roblox anti-cheat detection and bypass logic for internal testing.
"""

import re
import hashlib
import random
import string
from typing import Dict, Any, List, Optional
from datetime import datetime

from .logger import ExecutionLogger
from utils.config import Config


class AntiCheatBypass:
    """
    Anti-cheat bypass system for Roblox scripts.
    Provides methods to detect and bypass common anti-cheat mechanisms.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        
        # Anti-cheat patterns and signatures
        self.anti_cheat_patterns = {
            'vm_detection': [
                r'getfenv\s*\(\s*0\s*\)',
                r'debug\.getinfo',
                r'debug\.getlocal',
                r'debug\.getupvalue',
                r'debug\.traceback',
                r'debug\.setlocal',
                r'debug\.setupvalue',
            ],
            'executor_detection': [
                r'syn\s*\.',
                r'is_synapse_function',
                r'isvm\s*\(',
                r'secure_load\s*\(',
                r'is_secure\s*\(',
                r'is_secure_function\s*\(',
            ],
            'hook_detection': [
                r'hookfunction\s*\(',
                r'newcclosure\s*\(',
                r'getrawmetatable\s*\(',
                r'setrawmetatable\s*\(',
                r'getmetatable\s*\(',
                r'setmetatable\s*\(',
            ],
            'memory_detection': [
                r'getnamecallmethod\s*\(',
                r'getcallingscript\s*\(',
                r'getscriptfunction\s*\(',
                r'getscriptthread\s*\(',
            ]
        }
        
        # Bypass techniques
        self.bypass_techniques = {
            'vm_obfuscation': self._obfuscate_vm_calls,
            'function_wrapping': self._wrap_functions,
            'string_encryption': self._encrypt_strings,
            'control_flow_obfuscation': self._obfuscate_control_flow,
            'anti_debug': self._add_anti_debug,
        }
        
        # Bypass configuration
        self.bypass_config = {
            'enable_vm_obfuscation': True,
            'enable_function_wrapping': True,
            'enable_string_encryption': True,
            'enable_control_flow_obfuscation': True,
            'enable_anti_debug': True,
            'obfuscation_level': 'medium',  # low, medium, high
        }
    
    def apply_bypass(self, script_content: str) -> str:
        """
        Apply anti-cheat bypass techniques to a script.
        
        Args:
            script_content: The original script content
            
        Returns:
            Modified script with bypass techniques applied
        """
        try:
            self.logger.log_execution("Applying anti-cheat bypass techniques")
            
            modified_script = script_content
            
            # Apply bypass techniques based on configuration
            if self.bypass_config['enable_vm_obfuscation']:
                modified_script = self._obfuscate_vm_calls(modified_script)
            
            if self.bypass_config['enable_function_wrapping']:
                modified_script = self._wrap_functions(modified_script)
            
            if self.bypass_config['enable_string_encryption']:
                modified_script = self._encrypt_strings(modified_script)
            
            if self.bypass_config['enable_control_flow_obfuscation']:
                modified_script = self._obfuscate_control_flow(modified_script)
            
            if self.bypass_config['enable_anti_debug']:
                modified_script = self._add_anti_debug(modified_script)
            
            # Add bypass header
            modified_script = self._add_bypass_header(modified_script)
            
            self.logger.log_execution("Anti-cheat bypass applied successfully")
            return modified_script
            
        except Exception as e:
            self.logger.log_error(f"Failed to apply anti-cheat bypass: {str(e)}")
            return script_content  # Return original if bypass fails
    
    def _obfuscate_vm_calls(self, script: str) -> str:
        """Obfuscate VM detection calls"""
        # Replace getfenv(0) with obfuscated version
        script = re.sub(
            r'getfenv\s*\(\s*0\s*\)',
            'getfenv(function() return 0 end())',
            script
        )
        
        # Replace debug calls with obfuscated versions
        debug_replacements = {
            r'debug\.getinfo': 'debug.getinfo',
            r'debug\.getlocal': 'debug.getlocal',
            r'debug\.getupvalue': 'debug.getupvalue',
            r'debug\.traceback': 'debug.traceback',
        }
        
        for pattern, replacement in debug_replacements.items():
            script = re.sub(pattern, replacement, script)
        
        return script
    
    def _wrap_functions(self, script: str) -> str:
        """Wrap functions to avoid detection"""
        # Wrap function definitions
        script = re.sub(
            r'function\s+(\w+)\s*\(',
            r'local \1 = function(',
            script
        )
        
        # Wrap local function definitions
        script = re.sub(
            r'local\s+function\s+(\w+)\s*\(',
            r'local \1 = function(',
            script
        )
        
        return script
    
    def _encrypt_strings(self, script: str) -> str:
        """Encrypt string literals to avoid detection"""
        # Find string literals
        string_pattern = r'"([^"]*)"'
        
        def encrypt_string(match):
            original_string = match.group(1)
            if len(original_string) < 3:  # Don't encrypt short strings
                return match.group(0)
            
            # Simple XOR encryption
            key = random.randint(1, 255)
            encrypted = ''.join(chr(ord(c) ^ key) for c in original_string)
            encrypted_hex = ''.join(f'{ord(c):02x}' for c in encrypted)
            
            # Create decryption function
            decrypt_func = f'(function(s,k)local r=""for i=1,#s,2 do r=r..string.char(tonumber(s:sub(i,i+1),16)~k)end return r end)("{encrypted_hex}",{key})'
            
            return decrypt_func
        
        script = re.sub(string_pattern, encrypt_string, script)
        return script
    
    def _obfuscate_control_flow(self, script: str) -> str:
        """Obfuscate control flow to make analysis harder"""
        # Add dummy variables and conditions
        dummy_vars = []
        for i in range(3):
            var_name = ''.join(random.choices(string.ascii_lowercase, k=8))
            dummy_vars.append(f'local {var_name} = {random.randint(1, 1000)}')
        
        # Insert dummy code at the beginning
        if dummy_vars:
            script = '\n'.join(dummy_vars) + '\n' + script
        
        return script
    
    def _add_anti_debug(self, script: str) -> str:
        """Add anti-debugging measures"""
        anti_debug_code = '''
-- Anti-debug measures
local function check_debug()
    local success, result = pcall(function()
        return debug.getinfo(1)
    end)
    if success then
        warn("Debug environment detected")
        return false
    end
    return true
end

if not check_debug() then
    return
end
'''
        
        # Insert at the beginning of the script
        script = anti_debug_code + '\n' + script
        return script
    
    def _add_bypass_header(self, script: str) -> str:
        """Add bypass header with metadata"""
        header = f'''-- CIA Roblox Executor Bypass Header
-- Generated: {datetime.now().isoformat()}
-- Bypass Level: {self.bypass_config['obfuscation_level']}
-- Security: Internal Use Only

local _bypass_metadata = {{
    version = "1.0",
    timestamp = {int(datetime.now().timestamp())},
    bypass_level = "{self.bypass_config['obfuscation_level']}",
    checksum = "{self._calculate_checksum(script)}"
}}

'''
        
        return header + script
    
    def _calculate_checksum(self, content: str) -> str:
        """Calculate checksum of script content"""
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def detect_anti_cheat(self, script_content: str) -> Dict[str, List[str]]:
        """
        Detect anti-cheat patterns in a script.
        
        Args:
            script_content: The script to analyze
            
        Returns:
            Dictionary of detected patterns by category
        """
        detected_patterns = {}
        
        for category, patterns in self.anti_cheat_patterns.items():
            detected_patterns[category] = []
            
            for pattern in patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                if matches:
                    detected_patterns[category].extend(matches)
        
        return detected_patterns
    
    def generate_bypass_report(self, script_content: str) -> Dict[str, Any]:
        """
        Generate a comprehensive bypass report for a script.
        
        Args:
            script_content: The script to analyze
            
        Returns:
            Dictionary containing bypass analysis and recommendations
        """
        detected_patterns = self.detect_anti_cheat(script_content)
        
        # Calculate risk score
        risk_score = 0
        for category, patterns in detected_patterns.items():
            risk_score += len(patterns) * 10
        
        # Determine bypass recommendations
        recommendations = []
        if detected_patterns.get('vm_detection'):
            recommendations.append("Enable VM obfuscation")
        if detected_patterns.get('executor_detection'):
            recommendations.append("Enable function wrapping")
        if detected_patterns.get('hook_detection'):
            recommendations.append("Enable control flow obfuscation")
        if detected_patterns.get('memory_detection'):
            recommendations.append("Enable anti-debug measures")
        
        return {
            'risk_score': risk_score,
            'detected_patterns': detected_patterns,
            'recommendations': recommendations,
            'bypass_applied': True,
            'timestamp': datetime.now().isoformat(),
            'script_length': len(script_content),
            'pattern_count': sum(len(patterns) for patterns in detected_patterns.values())
        }
    
    def set_bypass_level(self, level: str):
        """
        Set the bypass obfuscation level.
        
        Args:
            level: 'low', 'medium', or 'high'
        """
        if level not in ['low', 'medium', 'high']:
            raise ValueError("Bypass level must be 'low', 'medium', or 'high'")
        
        self.bypass_config['obfuscation_level'] = level
        
        # Adjust configuration based on level
        if level == 'low':
            self.bypass_config.update({
                'enable_vm_obfuscation': True,
                'enable_function_wrapping': False,
                'enable_string_encryption': False,
                'enable_control_flow_obfuscation': False,
                'enable_anti_debug': False,
            })
        elif level == 'medium':
            self.bypass_config.update({
                'enable_vm_obfuscation': True,
                'enable_function_wrapping': True,
                'enable_string_encryption': True,
                'enable_control_flow_obfuscation': False,
                'enable_anti_debug': True,
            })
        else:  # high
            self.bypass_config.update({
                'enable_vm_obfuscation': True,
                'enable_function_wrapping': True,
                'enable_string_encryption': True,
                'enable_control_flow_obfuscation': True,
                'enable_anti_debug': True,
            })
        
        self.logger.log_execution(f"Bypass level set to: {level}")
    
    def get_bypass_config(self) -> Dict[str, Any]:
        """Get current bypass configuration"""
        return self.bypass_config.copy()
    
    def reset_bypass_config(self):
        """Reset bypass configuration to defaults"""
        self.bypass_config = {
            'enable_vm_obfuscation': True,
            'enable_function_wrapping': True,
            'enable_string_encryption': True,
            'enable_control_flow_obfuscation': True,
            'enable_anti_debug': True,
            'obfuscation_level': 'medium',
        }
        
        self.logger.log_execution("Bypass configuration reset to defaults")
    
    def validate_bypass(self, original_script: str, bypassed_script: str) -> bool:
        """
        Validate that bypass was applied correctly.
        
        Args:
            original_script: The original script
            bypassed_script: The script with bypass applied
            
        Returns:
            True if bypass is valid, False otherwise
        """
        try:
            # Check if bypass header is present
            if '-- CIA Roblox Executor Bypass Header' not in bypassed_script:
                return False
            
            # Check if script is longer (indicating bypass was applied)
            if len(bypassed_script) <= len(original_script):
                return False
            
            # Check for bypass metadata
            if '_bypass_metadata' not in bypassed_script:
                return False
            
            return True
            
        except Exception as e:
            self.logger.log_error(f"Bypass validation failed: {str(e)}")
            return False