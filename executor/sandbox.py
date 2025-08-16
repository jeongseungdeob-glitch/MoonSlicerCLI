#!/usr/bin/env python3
"""
CIA Roblox Executor - Sandbox Manager
Provides isolated execution environments for safe script execution.
"""

import os
import sys
import time
import threading
import resource
import psutil
from typing import Dict, Any, Optional, Callable
from contextlib import contextmanager

import lupa
from lupa import LuaRuntime

from .logger import ExecutionLogger
from utils.config import Config


class SandboxManager:
    """
    Manages isolated sandboxed environments for safe script execution.
    Provides resource monitoring and security restrictions.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        
        # Sandbox configuration
        self.max_memory_mb = 100
        self.max_cpu_percent = 50
        self.max_execution_time = 30
        self.max_file_operations = 10
        
        # Resource monitoring
        self.current_process = psutil.Process()
        self.resource_monitors = {}
        
        # Security restrictions
        self.blocked_functions = {
            'os.execute', 'os.remove', 'os.rename', 'os.tmpname',
            'io.popen', 'io.open', 'io.close', 'io.read', 'io.write',
            'loadstring', 'loadfile', 'dofile', 'require',
            'debug.getinfo', 'debug.getlocal', 'debug.setlocal',
            'collectgarbage', 'coroutine.create', 'coroutine.resume',
            'package.loadlib', 'package.cpath', 'package.path'
        }
        
        # Safe API functions for Roblox simulation
        self.safe_roblox_apis = {
            'game', 'workspace', 'players', 'player', 'script',
            'Vector3', 'CFrame', 'Color3', 'Instance', 'TweenInfo',
            'wait', 'spawn', 'tick', 'time', 'warn', 'error'
        }
    
    def setup_environment(self, runtime: LuaRuntime) -> None:
        """
        Set up a sandboxed Lua environment with security restrictions.
        
        Args:
            runtime: The Lua runtime to configure
        """
        try:
            # Clear all globals first
            self._clear_globals(runtime)
            
            # Set up safe globals
            self._setup_safe_globals(runtime)
            
            # Set up Roblox API simulation
            self._setup_roblox_apis(runtime)
            
            # Set up resource monitoring
            self._setup_resource_monitoring(runtime)
            
            self.logger.log_execution("Sandbox environment configured successfully")
            
        except Exception as e:
            self.logger.log_error(f"Failed to setup sandbox environment: {str(e)}")
            raise
    
    def _clear_globals(self, runtime: LuaRuntime) -> None:
        """Clear all globals from the runtime"""
        globals_table = runtime.globals()
        for key in list(globals_table.keys()):
            if key != '_G':  # Keep the global table reference
                del globals_table[key]
    
    def _setup_safe_globals(self, runtime: LuaRuntime) -> None:
        """Set up safe global functions and libraries"""
        globals_table = runtime.globals()
        
        # Basic Lua functions (safe subset)
        safe_functions = {
            'print': self._sandboxed_print,
            'tonumber': globals_table.get('tonumber'),
            'tostring': globals_table.get('tostring'),
            'type': globals_table.get('type'),
            'pairs': globals_table.get('pairs'),
            'ipairs': globals_table.get('ipairs'),
            'next': globals_table.get('next'),
            'select': globals_table.get('select'),
            'pcall': globals_table.get('pcall'),
            'xpcall': globals_table.get('xpcall'),
            'assert': globals_table.get('assert'),
            'error': globals_table.get('error'),
            'warn': globals_table.get('warn'),
        }
        
        # Safe libraries
        safe_libraries = {
            'table': self._create_safe_table_lib(globals_table),
            'string': self._create_safe_string_lib(globals_table),
            'math': self._create_safe_math_lib(globals_table),
            'os': self._create_safe_os_lib(globals_table),
        }
        
        # Set globals
        for name, func in safe_functions.items():
            if func is not None:
                globals_table[name] = func
        
        for name, lib in safe_libraries.items():
            globals_table[name] = lib
    
    def _create_safe_table_lib(self, globals_table) -> Dict[str, Any]:
        """Create safe table library"""
        table_lib = globals_table.get('table', {})
        safe_table = {}
        
        safe_table_functions = ['insert', 'remove', 'sort', 'concat', 'unpack']
        for func_name in safe_table_functions:
            if hasattr(table_lib, func_name):
                safe_table[func_name] = getattr(table_lib, func_name)
        
        return safe_table
    
    def _create_safe_string_lib(self, globals_table) -> Dict[str, Any]:
        """Create safe string library"""
        string_lib = globals_table.get('string', {})
        safe_string = {}
        
        safe_string_functions = [
            'byte', 'char', 'dump', 'find', 'format', 'gmatch',
            'gsub', 'len', 'lower', 'match', 'rep', 'reverse',
            'sub', 'upper'
        ]
        
        for func_name in safe_string_functions:
            if hasattr(string_lib, func_name):
                safe_string[func_name] = getattr(string_lib, func_name)
        
        return safe_string
    
    def _create_safe_math_lib(self, globals_table) -> Dict[str, Any]:
        """Create safe math library"""
        math_lib = globals_table.get('math', {})
        safe_math = {}
        
        safe_math_functions = [
            'abs', 'acos', 'asin', 'atan', 'atan2', 'ceil', 'cos',
            'cosh', 'deg', 'exp', 'floor', 'fmod', 'frexp', 'ldexp',
            'log', 'log10', 'max', 'min', 'modf', 'pow', 'rad',
            'random', 'randomseed', 'sin', 'sinh', 'sqrt', 'tan', 'tanh'
        ]
        
        for func_name in safe_math_functions:
            if hasattr(math_lib, func_name):
                safe_math[func_name] = getattr(math_lib, func_name)
        
        # Add math constants
        safe_math['pi'] = math_lib.get('pi', 3.141592653589793)
        safe_math['huge'] = math_lib.get('huge', float('inf'))
        
        return safe_math
    
    def _create_safe_os_lib(self, globals_table) -> Dict[str, Any]:
        """Create safe OS library (very restricted)"""
        os_lib = globals_table.get('os', {})
        safe_os = {}
        
        # Only allow time-related functions
        safe_os_functions = ['time', 'date', 'clock']
        
        for func_name in safe_os_functions:
            if hasattr(os_lib, func_name):
                safe_os[func_name] = getattr(os_lib, func_name)
        
        return safe_os
    
    def _setup_roblox_apis(self, runtime: LuaRuntime) -> None:
        """Set up simulated Roblox APIs for testing"""
        globals_table = runtime.globals()
        
        # Simulate basic Roblox objects
        roblox_apis = {
            'game': self._create_game_object(),
            'workspace': self._create_workspace_object(),
            'players': self._create_players_object(),
            'player': self._create_player_object(),
            'script': self._create_script_object(),
            'Vector3': self._create_vector3_class(),
            'CFrame': self._create_cframe_class(),
            'Color3': self._create_color3_class(),
            'Instance': self._create_instance_class(),
            'TweenInfo': self._create_tweeninfo_class(),
            'wait': self._sandboxed_wait,
            'spawn': self._sandboxed_spawn,
            'tick': time.time,
            'time': time.time,
            'warn': self._sandboxed_warn,
            'error': self._sandboxed_error,
        }
        
        for name, api in roblox_apis.items():
            globals_table[name] = api
    
    def _create_game_object(self) -> Dict[str, Any]:
        """Create simulated game object"""
        return {
            'Workspace': {'Name': 'Workspace'},
            'Players': {'Name': 'Players'},
            'Lighting': {'Name': 'Lighting'},
            'StarterGui': {'Name': 'StarterGui'},
            'StarterPack': {'Name': 'StarterPack'},
            'StarterPlayer': {'Name': 'StarterPlayer'},
            'Teams': {'Name': 'Teams'},
            'ReplicatedStorage': {'Name': 'ReplicatedStorage'},
            'ReplicatedFirst': {'Name': 'ReplicatedFirst'},
        }
    
    def _create_workspace_object(self) -> Dict[str, Any]:
        """Create simulated workspace object"""
        return {
            'Name': 'Workspace',
            'CurrentCamera': {'Name': 'CurrentCamera'},
            'Terrain': {'Name': 'Terrain'},
        }
    
    def _create_players_object(self) -> Dict[str, Any]:
        """Create simulated players object"""
        return {
            'Name': 'Players',
            'LocalPlayer': {'Name': 'LocalPlayer'},
        }
    
    def _create_player_object(self) -> Dict[str, Any]:
        """Create simulated player object"""
        return {
            'Name': 'LocalPlayer',
            'Character': {'Name': 'Character'},
            'Backpack': {'Name': 'Backpack'},
        }
    
    def _create_script_object(self) -> Dict[str, Any]:
        """Create simulated script object"""
        return {
            'Name': 'Script',
            'Source': '',
            'Parent': None,
        }
    
    def _create_vector3_class(self) -> Callable:
        """Create Vector3 class"""
        def vector3_new(x=0, y=0, z=0):
            return {'X': x, 'Y': y, 'Z': z, 'Magnitude': (x*x + y*y + z*z)**0.5}
        return vector3_new
    
    def _create_cframe_class(self) -> Callable:
        """Create CFrame class"""
        def cframe_new(x=0, y=0, z=0):
            return {'X': x, 'Y': y, 'Z': z, 'Position': {'X': x, 'Y': y, 'Z': z}}
        return cframe_new
    
    def _create_color3_class(self) -> Callable:
        """Create Color3 class"""
        def color3_new(r=0, g=0, b=0):
            return {'R': r, 'G': g, 'B': b}
        return color3_new
    
    def _create_instance_class(self) -> Callable:
        """Create Instance class"""
        def instance_new(className):
            return {'ClassName': className, 'Name': className, 'Parent': None}
        return instance_new
    
    def _create_tweeninfo_class(self) -> Callable:
        """Create TweenInfo class"""
        def tweeninfo_new(time=1, style=0):
            return {'Time': time, 'Style': style}
        return tweeninfo_new
    
    def _sandboxed_print(self, *args) -> str:
        """Sandboxed print function"""
        output = ' '.join(str(arg) for arg in args)
        self.logger.log_output(f"[SANDBOX] {output}")
        return output
    
    def _sandboxed_wait(self, seconds: float = 0.03) -> float:
        """Sandboxed wait function"""
        if seconds > 1.0:  # Limit wait time
            seconds = 1.0
        time.sleep(seconds)
        return seconds
    
    def _sandboxed_spawn(self, func) -> None:
        """Sandboxed spawn function"""
        # In a real implementation, this would spawn a new thread
        # For now, just execute immediately
        try:
            func()
        except Exception as e:
            self.logger.log_error(f"Spawned function error: {str(e)}")
    
    def _sandboxed_warn(self, *args) -> str:
        """Sandboxed warn function"""
        output = ' '.join(str(arg) for arg in args)
        self.logger.log_warning(f"[SANDBOX] {output}")
        return output
    
    def _sandboxed_error(self, *args) -> str:
        """Sandboxed error function"""
        output = ' '.join(str(arg) for arg in args)
        self.logger.log_error(f"[SANDBOX] {output}")
        return output
    
    def _setup_resource_monitoring(self, runtime: LuaRuntime) -> None:
        """Set up resource monitoring for the sandbox"""
        # Monitor memory usage
        def check_memory():
            try:
                memory_info = self.current_process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                if memory_mb > self.max_memory_mb:
                    self.logger.log_warning(f"Memory usage exceeded limit: {memory_mb:.1f}MB")
                    return False
                return True
            except Exception:
                return True
        
        # Monitor CPU usage
        def check_cpu():
            try:
                cpu_percent = self.current_process.cpu_percent()
                if cpu_percent > self.max_cpu_percent:
                    self.logger.log_warning(f"CPU usage exceeded limit: {cpu_percent:.1f}%")
                    return False
                return True
            except Exception:
                return True
        
        # Store monitoring functions
        self.resource_monitors['memory'] = check_memory
        self.resource_monitors['cpu'] = check_cpu
    
    @contextmanager
    def resource_monitoring(self):
        """Context manager for resource monitoring"""
        start_time = time.time()
        
        try:
            yield
        finally:
            # Check resources after execution
            for monitor_name, monitor_func in self.resource_monitors.items():
                if not monitor_func():
                    self.logger.log_warning(f"Resource monitor {monitor_name} failed")
    
    def check_security(self, script_content: str) -> bool:
        """
        Check script for security violations.
        
        Args:
            script_content: The script to check
            
        Returns:
            True if script is safe, False otherwise
        """
        script_lower = script_content.lower()
        
        # Check for blocked functions
        for blocked_func in self.blocked_functions:
            if blocked_func in script_lower:
                self.logger.log_error(f"Script contains blocked function: {blocked_func}")
                return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            'while true do',
            'for i=1,999999 do',
            'repeat until false',
            'coroutine',
            'debug',
            'collectgarbage',
            'jit'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in script_lower:
                self.logger.log_warning(f"Script contains suspicious pattern: {pattern}")
        
        return True
    
    def get_resource_usage(self) -> Dict[str, float]:
        """Get current resource usage"""
        try:
            memory_info = self.current_process.memory_info()
            cpu_percent = self.current_process.cpu_percent()
            
            return {
                'memory_mb': memory_info.rss / 1024 / 1024,
                'cpu_percent': cpu_percent,
                'threads': self.current_process.num_threads(),
                'open_files': len(self.current_process.open_files()),
            }
        except Exception as e:
            self.logger.log_error(f"Failed to get resource usage: {str(e)}")
            return {}
    
    def cleanup(self):
        """Cleanup sandbox resources"""
        self.resource_monitors.clear()
        self.logger.log_execution("Sandbox manager cleaned up")