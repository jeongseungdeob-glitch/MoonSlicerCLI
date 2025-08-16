#!/usr/bin/env python3
"""
CIA Roblox Executor - Anti-Cheat Bypass Module
Handles Roblox anti-cheat detection and safe bypass mechanisms
"""

import re
import hashlib
import random
import string
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path


class AntiCheatBypass:
    """Anti-cheat bypass system for Roblox scripts"""
    
    def __init__(self):
        self.bypass_patterns = {
            "vm_detection": [
                r"getfenv",
                r"setfenv",
                r"debug\.getinfo",
                r"debug\.getupvalue",
                r"debug\.setupvalue",
                r"debug\.getlocal",
                r"debug\.setlocal"
            ],
            "execution_detection": [
                r"loadstring",
                r"dofile",
                r"loadfile",
                r"require",
                r"pcall",
                r"xpcall"
            ],
            "memory_detection": [
                r"collectgarbage",
                r"gcinfo",
                r"getmetatable",
                r"setmetatable"
            ],
            "io_detection": [
                r"io\.",
                r"os\.",
                r"file\.",
                r"fs\."
            ]
        }
        
        self.bypass_methods = {
            "vm_detection": self._bypass_vm_detection,
            "execution_detection": self._bypass_execution_detection,
            "memory_detection": self._bypass_memory_detection,
            "io_detection": self._bypass_io_detection
        }
        
        self.obfuscation_patterns = [
            r"local\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*([^;]+)",
            r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
            r"if\s+([^then]+)\s+then",
            r"for\s+([^do]+)\s+do",
            r"while\s+([^do]+)\s+do"
        ]
        
    def apply_bypass(self, script_content: str) -> str:
        """Apply anti-cheat bypass to script content"""
        try:
            # Detect anti-cheat patterns
            detected_patterns = self._detect_patterns(script_content)
            
            if not detected_patterns:
                # No anti-cheat patterns detected, return as-is
                return script_content
            
            # Apply bypass methods
            modified_script = script_content
            
            for pattern_type, patterns in detected_patterns.items():
                if pattern_type in self.bypass_methods:
                    modified_script = self.bypass_methods[pattern_type](modified_script, patterns)
            
            # Apply obfuscation if needed
            if self._should_obfuscate(script_content):
                modified_script = self._apply_obfuscation(modified_script)
            
            # Add safety wrapper
            modified_script = self._add_safety_wrapper(modified_script)
            
            return modified_script
            
        except Exception as e:
            # If bypass fails, return original script with warning
            return f"-- Anti-cheat bypass failed: {str(e)}\n{script_content}"
    
    def _detect_patterns(self, script_content: str) -> Dict[str, List[str]]:
        """Detect anti-cheat patterns in script"""
        detected = {}
        
        for pattern_type, patterns in self.bypass_patterns.items():
            found_patterns = []
            for pattern in patterns:
                matches = re.findall(pattern, script_content, re.IGNORECASE)
                if matches:
                    found_patterns.extend(matches)
            
            if found_patterns:
                detected[pattern_type] = found_patterns
        
        return detected
    
    def _bypass_vm_detection(self, script_content: str, patterns: List[str]) -> str:
        """Bypass VM detection patterns"""
        # Replace debug functions with safe alternatives
        replacements = {
            "getfenv": "_safe_getfenv",
            "setfenv": "_safe_setfenv",
            "debug.getinfo": "_safe_debug_getinfo",
            "debug.getupvalue": "_safe_debug_getupvalue",
            "debug.setupvalue": "_safe_debug_setupvalue",
            "debug.getlocal": "_safe_debug_getlocal",
            "debug.setlocal": "_safe_debug_setlocal"
        }
        
        modified = script_content
        for old, new in replacements.items():
            modified = re.sub(
                rf'\b{re.escape(old)}\b',
                new,
                modified,
                flags=re.IGNORECASE
            )
        
        # Add safe function definitions
        safe_functions = self._generate_safe_debug_functions()
        modified = safe_functions + "\n" + modified
        
        return modified
    
    def _bypass_execution_detection(self, script_content: str, patterns: List[str]) -> str:
        """Bypass execution detection patterns"""
        # Replace dangerous execution functions with safe alternatives
        replacements = {
            "loadstring": "_safe_loadstring",
            "dofile": "_safe_dofile",
            "loadfile": "_safe_loadfile",
            "require": "_safe_require",
            "pcall": "_safe_pcall",
            "xpcall": "_safe_xpcall"
        }
        
        modified = script_content
        for old, new in replacements.items():
            modified = re.sub(
                rf'\b{re.escape(old)}\b',
                new,
                modified,
                flags=re.IGNORECASE
            )
        
        # Add safe function definitions
        safe_functions = self._generate_safe_execution_functions()
        modified = safe_functions + "\n" + modified
        
        return modified
    
    def _bypass_memory_detection(self, script_content: str, patterns: List[str]) -> str:
        """Bypass memory detection patterns"""
        # Replace memory-related functions with safe alternatives
        replacements = {
            "collectgarbage": "_safe_collectgarbage",
            "gcinfo": "_safe_gcinfo",
            "getmetatable": "_safe_getmetatable",
            "setmetatable": "_safe_setmetatable"
        }
        
        modified = script_content
        for old, new in replacements.items():
            modified = re.sub(
                rf'\b{re.escape(old)}\b',
                new,
                modified,
                flags=re.IGNORECASE
            )
        
        # Add safe function definitions
        safe_functions = self._generate_safe_memory_functions()
        modified = safe_functions + "\n" + modified
        
        return modified
    
    def _bypass_io_detection(self, script_content: str, patterns: List[str]) -> str:
        """Bypass I/O detection patterns"""
        # Block I/O operations entirely
        io_patterns = [
            r'io\.[a-zA-Z_][a-zA-Z0-9_]*\s*\(',
            r'os\.[a-zA-Z_][a-zA-Z0-9_]*\s*\(',
            r'file\.[a-zA-Z_][a-zA-Z0-9_]*\s*\(',
            r'fs\.[a-zA-Z_][a-zA-Z0-9_]*\s*\('
        ]
        
        modified = script_content
        for pattern in io_patterns:
            modified = re.sub(
                pattern,
                '-- BLOCKED: I/O operation not allowed in sandbox',
                modified,
                flags=re.IGNORECASE
            )
        
        return modified
    
    def _generate_safe_debug_functions(self) -> str:
        """Generate safe debug function replacements"""
        return """
-- Safe debug function replacements
local function _safe_getfenv(level)
    level = level or 1
    return {
        script = {Name = "Script"},
        game = {Name = "Game"},
        workspace = {Name = "Workspace"}
    }
end

local function _safe_setfenv(func, env)
    return func
end

local function _safe_debug_getinfo(thread, what, count)
    return {
        source = "=[C]",
        short_src = "=[C]",
        linedefined = 0,
        lastlinedefined = 0,
        what = "C",
        currentline = 0,
        name = nil,
        namewhat = "",
        istailcall = false,
        isvararg = false,
        nups = 0,
        nparams = 0
    }
end

local function _safe_debug_getupvalue(func, index)
    return nil, nil
end

local function _safe_debug_setupvalue(func, index, value)
    return false
end

local function _safe_debug_getlocal(thread, level, index)
    return nil, nil
end

local function _safe_debug_setlocal(thread, level, index, value)
    return nil
end
"""
    
    def _generate_safe_execution_functions(self) -> str:
        """Generate safe execution function replacements"""
        return """
-- Safe execution function replacements
local function _safe_loadstring(chunk, chunkname)
    return function() return nil end, nil
end

local function _safe_dofile(filename)
    return nil
end

local function _safe_loadfile(filename)
    return function() return nil end, nil
end

local function _safe_require(modname)
    return {}
end

local function _safe_pcall(func, ...)
    local success, result = pcall(func, ...)
    return success, result
end

local function _safe_xpcall(func, msgh, ...)
    local success, result = pcall(func, ...)
    return success, result
end
"""
    
    def _generate_safe_memory_functions(self) -> str:
        """Generate safe memory function replacements"""
        return """
-- Safe memory function replacements
local function _safe_collectgarbage(opt, arg)
    return 0
end

local function _safe_gcinfo()
    return 0, 0
end

local function _safe_getmetatable(obj)
    return nil
end

local function _safe_setmetatable(obj, mt)
    return obj
end
"""
    
    def _should_obfuscate(self, script_content: str) -> bool:
        """Determine if script should be obfuscated"""
        # Check for obvious anti-cheat patterns
        obvious_patterns = [
            "getfenv",
            "setfenv",
            "debug",
            "loadstring",
            "dofile"
        ]
        
        script_lower = script_content.lower()
        for pattern in obvious_patterns:
            if pattern in script_lower:
                return True
        
        return False
    
    def _apply_obfuscation(self, script_content: str) -> str:
        """Apply basic obfuscation to script"""
        # Simple variable name obfuscation
        var_pattern = r'\b(local\s+)([a-zA-Z_][a-zA-Z0-9_]*)\b'
        
        def obfuscate_var(match):
            prefix = match.group(1)
            var_name = match.group(2)
            
            # Skip common Lua keywords and Roblox objects
            if var_name.lower() in ['local', 'function', 'if', 'then', 'else', 'end', 'for', 'while', 'do', 'repeat', 'until', 'break', 'return', 'game', 'workspace', 'script']:
                return match.group(0)
            
            # Generate obfuscated name
            obfuscated = '_' + ''.join(random.choices(string.ascii_lowercase, k=8))
            return prefix + obfuscated
        
        obfuscated = re.sub(var_pattern, obfuscate_var, script_content)
        
        # Add random comments to confuse pattern matching
        comment_lines = [
            "-- " + ''.join(random.choices(string.ascii_letters + string.digits, k=20)),
            "-- " + hashlib.md5(str(random.random()).encode()).hexdigest()[:16],
            "-- " + ''.join(random.choices(string.ascii_lowercase, k=15))
        ]
        
        lines = obfuscated.split('\n')
        if len(lines) > 10:
            # Insert random comments at random positions
            for _ in range(3):
                pos = random.randint(0, len(lines) - 1)
                lines.insert(pos, random.choice(comment_lines))
        
        return '\n'.join(lines)
    
    def _add_safety_wrapper(self, script_content: str) -> str:
        """Add safety wrapper around script"""
        wrapper = f"""
-- CIA Roblox Executor Safety Wrapper
-- Generated: {self._get_timestamp()}
-- Script Hash: {self._get_script_hash(script_content)}

local function _safe_execute()
    local success, result = pcall(function()
{self._indent_script(script_content)}
    end)
    
    if not success then
        warn("Script execution error: " .. tostring(result))
        return false
    end
    
    return true
end

-- Execute with error handling
local execution_success = _safe_execute()
if not execution_success then
    warn("Script execution failed")
end
"""
        return wrapper
    
    def _indent_script(self, script_content: str) -> str:
        """Indent script content for wrapper"""
        lines = script_content.split('\n')
        indented_lines = []
        
        for line in lines:
            if line.strip():  # Non-empty line
                indented_lines.append("        " + line)
            else:
                indented_lines.append("")
        
        return '\n'.join(indented_lines)
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _get_script_hash(self, script_content: str) -> str:
        """Get hash of script content"""
        return hashlib.sha256(script_content.encode()).hexdigest()[:16]
    
    def detect_anti_cheat(self, script_content: str) -> Dict[str, List[str]]:
        """Detect anti-cheat patterns in script"""
        return self._detect_patterns(script_content)
    
    def get_bypass_report(self, script_content: str) -> Dict[str, Any]:
        """Generate bypass report for script"""
        detected = self._detect_patterns(script_content)
        
        report = {
            "script_length": len(script_content),
            "detected_patterns": detected,
            "pattern_count": sum(len(patterns) for patterns in detected.values()),
            "needs_obfuscation": self._should_obfuscate(script_content),
            "risk_level": self._calculate_risk_level(detected)
        }
        
        return report
    
    def _calculate_risk_level(self, detected_patterns: Dict[str, List[str]]) -> str:
        """Calculate risk level based on detected patterns"""
        total_patterns = sum(len(patterns) for patterns in detected_patterns.values())
        
        if total_patterns == 0:
            return "LOW"
        elif total_patterns <= 3:
            return "MEDIUM"
        elif total_patterns <= 7:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def validate_bypass(self, original_script: str, bypassed_script: str) -> bool:
        """Validate that bypass was applied correctly"""
        # Check that dangerous patterns were replaced
        for pattern_type, patterns in self.bypass_patterns.items():
            for pattern in patterns:
                if re.search(pattern, bypassed_script, re.IGNORECASE):
                    # Pattern still exists, bypass may have failed
                    return False
        
        # Check that script still has content
        if len(bypassed_script.strip()) < 10:
            return False
        
        return True