#!/usr/bin/env python3
"""
CIA Roblox Executor - Sandbox Module
Isolated Lua environment for safe script execution
"""

import os
import sys
import time
import threading
import psutil
from typing import Optional, Dict, Any, NamedTuple
from pathlib import Path

try:
    import lupa
    from lupa import LuaRuntime
except ImportError:
    print("Warning: lupa not available, using mock sandbox")
    LuaRuntime = None


class SandboxResult(NamedTuple):
    """Result of sandbox execution"""
    success: bool
    output: str
    error: Optional[str] = None
    memory_usage: int = 0
    execution_time: float = 0.0


class MockLuaRuntime:
    """Mock Lua runtime for when lupa is not available"""
    
    def __init__(self):
        self.globals = {}
        self.output = []
        
    def execute(self, code):
        # Simulate execution
        self.output.append(f"Mock execution: {code[:50]}...")
        return True
        
    def globals(self):
        return self.globals


class Sandbox:
    """Secure Lua sandbox for script execution"""
    
    def __init__(self):
        self.config = {
            "max_execution_time": 30.0,  # seconds
            "max_memory_mb": 100,        # MB
            "max_output_size": 1024 * 1024,  # 1MB
            "enable_io": False,
            "enable_os": False,
            "enable_debug": False
        }
        
        self.lua_runtime = None
        self.is_running = False
        self.execution_thread = None
        self.stop_flag = threading.Event()
        
        self._init_lua_runtime()
        
    def _init_lua_runtime(self):
        """Initialize Lua runtime with security restrictions"""
        try:
            if LuaRuntime:
                self.lua_runtime = LuaRuntime(
                    unpack_returned_tuples=True,
                    register_eval=False,
                    register_builtins=False
                )
                self._setup_secure_environment()
            else:
                self.lua_runtime = MockLuaRuntime()
                print("Using mock Lua runtime - install lupa for full functionality")
                
        except Exception as e:
            print(f"Failed to initialize Lua runtime: {e}")
            self.lua_runtime = MockLuaRuntime()
    
    def _setup_secure_environment(self):
        """Setup secure Lua environment with restricted access"""
        if not self.lua_runtime or isinstance(self.lua_runtime, MockLuaRuntime):
            return
            
        # Create restricted globals
        globals_dict = self.lua_runtime.globals()
        
        # Basic Lua functions (safe subset)
        safe_functions = {
            'print': self._safe_print,
            'tonumber': self._safe_tonumber,
            'tostring': self._safe_tostring,
            'type': self._safe_type,
            'pairs': self._safe_pairs,
            'ipairs': self._safe_ipairs,
            'next': self._safe_next,
            'select': self._safe_select,
            'table': self._create_safe_table(),
            'string': self._create_safe_string(),
            'math': self._create_safe_math(),
            'coroutine': self._create_safe_coroutine()
        }
        
        # Add safe functions to globals
        for name, func in safe_functions.items():
            globals_dict[name] = func
            
        # Add Roblox-like environment
        self._setup_roblox_environment(globals_dict)
        
        # Remove dangerous functions
        dangerous_functions = [
            'os', 'io', 'debug', 'load', 'loadfile', 'dofile',
            'require', 'package', 'collectgarbage', 'getmetatable',
            'setmetatable', 'rawget', 'rawset', 'rawequal'
        ]
        
        for func_name in dangerous_functions:
            if func_name in globals_dict:
                del globals_dict[func_name]
    
    def _setup_roblox_environment(self, globals_dict):
        """Setup Roblox-like environment for script execution"""
        # Mock Roblox services and objects
        roblox_env = {
            'game': self._create_mock_game(),
            'workspace': self._create_mock_workspace(),
            'script': self._create_mock_script(),
            'wait': self._safe_wait,
            'spawn': self._safe_spawn,
            'Instance': self._create_mock_instance(),
            'Vector3': self._create_mock_vector3(),
            'CFrame': self._create_mock_cframe(),
            'Color3': self._create_mock_color3(),
            'TweenInfo': self._create_mock_tween_info()
        }
        
        for name, obj in roblox_env.items():
            globals_dict[name] = obj
    
    def _create_safe_table(self):
        """Create safe table library"""
        return {
            'insert': lambda t, pos, value: t.insert(pos, value) if isinstance(t, list) else None,
            'remove': lambda t, pos: t.pop(pos) if isinstance(t, list) else None,
            'concat': lambda t, sep: sep.join(map(str, t)) if isinstance(t, list) else str(t),
            'sort': lambda t: t.sort() if isinstance(t, list) else None,
            'unpack': lambda t: tuple(t) if isinstance(t, list) else (t,)
        }
    
    def _create_safe_string(self):
        """Create safe string library"""
        return {
            'sub': lambda s, i, j: str(s)[i-1:j] if isinstance(s, str) else str(s),
            'len': lambda s: len(str(s)),
            'upper': lambda s: str(s).upper(),
            'lower': lambda s: str(s).lower(),
            'find': lambda s, pattern: str(s).find(str(pattern)) + 1,
            'gsub': lambda s, pattern, repl: str(s).replace(str(pattern), str(repl)),
            'format': lambda fmt, *args: fmt % args if isinstance(fmt, str) else str(fmt)
        }
    
    def _create_safe_math(self):
        """Create safe math library"""
        return {
            'abs': abs,
            'floor': lambda x: int(float(x)),
            'ceil': lambda x: int(float(x) + 0.5),
            'max': max,
            'min': min,
            'random': lambda: time.time() % 1,  # Mock random
            'sin': lambda x: 0,  # Mock trig functions
            'cos': lambda x: 1,
            'tan': lambda x: 0,
            'pi': 3.141592653589793
        }
    
    def _create_safe_coroutine(self):
        """Create safe coroutine library"""
        return {
            'create': lambda f: f,  # Mock coroutine
            'resume': lambda co, *args: (True, co(*args)),
            'yield': lambda: None,
            'status': lambda co: 'running'
        }
    
    def _create_mock_game(self):
        """Create mock game object"""
        return {
            'Players': self._create_mock_players(),
            'Workspace': self._create_mock_workspace(),
            'Lighting': self._create_mock_lighting(),
            'StarterGui': self._create_mock_starter_gui()
        }
    
    def _create_mock_workspace(self):
        """Create mock workspace object"""
        return {
            'CurrentCamera': self._create_mock_camera(),
            'Terrain': self._create_mock_terrain()
        }
    
    def _create_mock_players(self):
        """Create mock Players service"""
        return {
            'LocalPlayer': self._create_mock_local_player(),
            'GetPlayers': lambda: [self._create_mock_local_player()]
        }
    
    def _create_mock_local_player(self):
        """Create mock LocalPlayer"""
        return {
            'Character': self._create_mock_character(),
            'Backpack': self._create_mock_backpack(),
            'PlayerGui': self._create_mock_player_gui()
        }
    
    def _create_mock_character(self):
        """Create mock Character"""
        return {
            'Humanoid': self._create_mock_humanoid(),
            'HumanoidRootPart': self._create_mock_humanoid_root_part(),
            'Head': self._create_mock_head()
        }
    
    def _create_mock_humanoid(self):
        """Create mock Humanoid"""
        return {
            'WalkSpeed': 16,
            'JumpPower': 50,
            'Health': 100,
            'MaxHealth': 100
        }
    
    def _create_mock_humanoid_root_part(self):
        """Create mock HumanoidRootPart"""
        return {
            'Position': self._create_mock_vector3(),
            'CFrame': self._create_mock_cframe()
        }
    
    def _create_mock_head(self):
        """Create mock Head"""
        return {
            'Position': self._create_mock_vector3(),
            'CFrame': self._create_mock_cframe()
        }
    
    def _create_mock_camera(self):
        """Create mock Camera"""
        return {
            'CFrame': self._create_mock_cframe(),
            'FieldOfView': 70
        }
    
    def _create_mock_script(self):
        """Create mock script object"""
        return {
            'Parent': None,
            'Name': 'Script'
        }
    
    def _create_mock_instance(self):
        """Create mock Instance constructor"""
        return lambda class_name: {'ClassName': class_name, 'Name': class_name}
    
    def _create_mock_vector3(self):
        """Create mock Vector3 constructor"""
        return lambda x=0, y=0, z=0: {'X': float(x), 'Y': float(y), 'Z': float(z)}
    
    def _create_mock_cframe(self):
        """Create mock CFrame constructor"""
        return lambda x=0, y=0, z=0: {'Position': self._create_mock_vector3(x, y, z)}
    
    def _create_mock_color3(self):
        """Create mock Color3 constructor"""
        return lambda r=0, g=0, b=0: {'R': float(r), 'G': float(g), 'B': float(b)}
    
    def _create_mock_tween_info(self):
        """Create mock TweenInfo constructor"""
        return lambda time=1: {'Time': float(time)}
    
    def _create_mock_backpack(self):
        """Create mock Backpack"""
        return {'Name': 'Backpack'}
    
    def _create_mock_player_gui(self):
        """Create mock PlayerGui"""
        return {'Name': 'PlayerGui'}
    
    def _create_mock_lighting(self):
        """Create mock Lighting"""
        return {'Name': 'Lighting'}
    
    def _create_mock_starter_gui(self):
        """Create mock StarterGui"""
        return {'Name': 'StarterGui'}
    
    def _create_mock_terrain(self):
        """Create mock Terrain"""
        return {'Name': 'Terrain'}
    
    # Safe function wrappers
    def _safe_print(self, *args):
        """Safe print function that captures output"""
        output = ' '.join(str(arg) for arg in args)
        if hasattr(self, 'output_buffer'):
            self.output_buffer.append(output)
        return None
    
    def _safe_tonumber(self, value, base=10):
        """Safe tonumber function"""
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_tostring(self, value):
        """Safe tostring function"""
        return str(value)
    
    def _safe_type(self, value):
        """Safe type function"""
        return type(value).__name__
    
    def _safe_pairs(self, table):
        """Safe pairs function"""
        if isinstance(table, dict):
            return table.items()
        return []
    
    def _safe_ipairs(self, table):
        """Safe ipairs function"""
        if isinstance(table, list):
            return enumerate(table, 1)
        return []
    
    def _safe_next(self, table, index=None):
        """Safe next function"""
        if isinstance(table, dict):
            if index is None:
                return next(iter(table.items()), (None, None))
            # Simplified next implementation
            return (None, None)
        return (None, None)
    
    def _safe_select(self, index, *args):
        """Safe select function"""
        if index == '#':
            return len(args)
        try:
            return args[index - 1]
        except IndexError:
            return None
    
    def _safe_wait(self, seconds=0.1):
        """Safe wait function"""
        time.sleep(min(float(seconds), 1.0))  # Cap at 1 second
        return None
    
    def _safe_spawn(self, func):
        """Safe spawn function"""
        if callable(func):
            threading.Thread(target=func, daemon=True).start()
        return None
    
    def execute(self, script_content: str) -> SandboxResult:
        """Execute Lua script in sandbox"""
        start_time = time.time()
        self.output_buffer = []
        
        try:
            if not self.lua_runtime:
                return SandboxResult(
                    success=False,
                    output="",
                    error="Lua runtime not available",
                    execution_time=time.time() - start_time
                )
            
            # Check script size
            if len(script_content) > self.config["max_output_size"]:
                return SandboxResult(
                    success=False,
                    output="",
                    error="Script too large",
                    execution_time=time.time() - start_time
                )
            
            # Execute with timeout
            self.is_running = True
            self.stop_flag.clear()
            
            execution_thread = threading.Thread(
                target=self._execute_with_timeout,
                args=(script_content,)
            )
            execution_thread.daemon = True
            execution_thread.start()
            
            # Wait for completion or timeout
            execution_thread.join(timeout=self.config["max_execution_time"])
            
            if execution_thread.is_alive():
                self.stop_flag.set()
                execution_thread.join(timeout=1.0)
                return SandboxResult(
                    success=False,
                    output="\n".join(self.output_buffer),
                    error="Execution timeout",
                    execution_time=time.time() - start_time
                )
            
            execution_time = time.time() - start_time
            memory_usage = self.get_memory_usage()
            
            return SandboxResult(
                success=True,
                output="\n".join(self.output_buffer),
                execution_time=execution_time,
                memory_usage=memory_usage
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                output="\n".join(self.output_buffer),
                error=str(e),
                execution_time=execution_time
            )
        finally:
            self.is_running = False
    
    def _execute_with_timeout(self, script_content: str):
        """Execute script with timeout checking"""
        try:
            if isinstance(self.lua_runtime, MockLuaRuntime):
                # Mock execution
                self.lua_runtime.execute(script_content)
                self.output_buffer.extend(self.lua_runtime.output)
            else:
                # Real Lua execution
                self.lua_runtime.execute(script_content)
                
        except Exception as e:
            if not self.stop_flag.is_set():
                raise e
    
    def stop(self):
        """Stop current execution"""
        self.stop_flag.set()
        self.is_running = False
    
    def get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except:
            return 0
    
    def get_status(self) -> Dict[str, Any]:
        """Get sandbox status"""
        return {
            "is_running": self.is_running,
            "memory_usage_mb": self.get_memory_usage() / (1024 * 1024),
            "lua_available": LuaRuntime is not None,
            "config": self.config.copy()
        }
    
    def cleanup(self):
        """Cleanup sandbox resources"""
        self.stop()
        if self.lua_runtime and not isinstance(self.lua_runtime, MockLuaRuntime):
            del self.lua_runtime
            self.lua_runtime = None