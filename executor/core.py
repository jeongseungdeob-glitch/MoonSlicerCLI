#!/usr/bin/env python3
"""
CIA Roblox Executor - Core Execution Engine
Main execution loop, VM abstraction, and script management.
"""

import os
import sys
import time
import threading
import traceback
from typing import Optional, Dict, Any, List
from datetime import datetime
from pathlib import Path

import lupa
from lupa import LuaRuntime

from .sandbox import SandboxManager
from .anti_cheat_bypass import AntiCheatBypass
from .logger import ExecutionLogger
from utils.config import Config


class ExecutorCore:
    """
    Core execution engine for Roblox Lua scripts.
    Handles script loading, execution, and VM management.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        self.sandbox = SandboxManager()
        self.anti_cheat = AntiCheatBypass()
        
        # Execution state
        self.is_running = False
        self.current_script = None
        self.execution_thread = None
        self.execution_timeout = 30  # seconds
        
        # VM state
        self.lua_runtime: Optional[LuaRuntime] = None
        self.script_registry: Dict[str, Any] = {}
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0
        }
        
        # Security settings
        self.sandbox_mode = True
        self.bypass_mode = True
        self.max_execution_time = 30
        self.max_memory_usage = 100 * 1024 * 1024  # 100MB
        
        self._initialize_lua_runtime()
    
    def _initialize_lua_runtime(self):
        """Initialize the Lua runtime with security restrictions"""
        try:
            # Create Lua runtime with restricted environment
            self.lua_runtime = lupa.LuaRuntime(
                unpack_returned_tuples=True,
                register_eval=False,  # Disable eval for security
                register_builtins=False  # Disable builtins for security
            )
            
            # Set up restricted globals
            self._setup_restricted_globals()
            
            self.logger.log_execution("Lua runtime initialized successfully")
        except Exception as e:
            self.logger.log_error(f"Failed to initialize Lua runtime: {str(e)}")
            raise
    
    def _setup_restricted_globals(self):
        """Set up restricted global environment for Lua scripts"""
        if not self.lua_runtime:
            return
        
        # Define safe globals
        safe_globals = {
            'print': self._safe_print,
            'tonumber': self.lua_runtime.globals().tonumber,
            'tostring': self.lua_runtime.globals().tostring,
            'type': self.lua_runtime.globals().type,
            'pairs': self.lua_runtime.globals().pairs,
            'ipairs': self.lua_runtime.globals().ipairs,
            'next': self.lua_runtime.globals().next,
            'table': self.lua_runtime.globals().table,
            'string': self.lua_runtime.globals().string,
            'math': self.lua_runtime.globals().math,
            'os': {
                'time': self.lua_runtime.globals().os.time,
                'date': self.lua_runtime.globals().os.date,
                'clock': self.lua_runtime.globals().os.clock,
            }
        }
        
        # Set globals in Lua environment
        for name, value in safe_globals.items():
            self.lua_runtime.globals()[name] = value
    
    def _safe_print(self, *args):
        """Safe print function that logs to our system"""
        output = ' '.join(str(arg) for arg in args)
        self.logger.log_output(f"Script output: {output}")
        return output
    
    def set_sandbox_mode(self, enabled: bool):
        """Enable or disable sandbox mode"""
        self.sandbox_mode = enabled
        self.logger.log_execution(f"Sandbox mode {'enabled' if enabled else 'disabled'}")
    
    def set_bypass_mode(self, enabled: bool):
        """Enable or disable anti-cheat bypass mode"""
        self.bypass_mode = enabled
        self.logger.log_execution(f"Anti-cheat bypass mode {'enabled' if enabled else 'disabled'}")
    
    def set_execution_timeout(self, timeout: int):
        """Set maximum execution time in seconds"""
        self.execution_timeout = timeout
        self.max_execution_time = timeout
    
    def execute_script(self, script_content: str, script_name: str = "anonymous") -> str:
        """
        Execute a Lua script in the sandboxed environment.
        
        Args:
            script_content: The Lua script to execute
            script_name: Name of the script for logging
            
        Returns:
            Execution result as string
        """
        if not self.lua_runtime:
            raise RuntimeError("Lua runtime not initialized")
        
        start_time = time.time()
        self.execution_stats['total_executions'] += 1
        
        try:
            self.logger.log_execution(f"Starting execution of script: {script_name}")
            
            # Validate script before execution
            if not self._validate_script(script_content):
                raise ValueError("Script validation failed")
            
            # Apply anti-cheat bypass if enabled
            if self.bypass_mode:
                script_content = self.anti_cheat.apply_bypass(script_content)
            
            # Create execution context
            execution_context = {
                'script_name': script_name,
                'start_time': start_time,
                'sandbox_mode': self.sandbox_mode,
                'bypass_mode': self.bypass_mode
            }
            
            # Execute in sandbox if enabled
            if self.sandbox_mode:
                result = self._execute_in_sandbox(script_content, execution_context)
            else:
                result = self._execute_directly(script_content, execution_context)
            
            # Update statistics
            execution_time = time.time() - start_time
            self.execution_stats['successful_executions'] += 1
            self.execution_stats['total_execution_time'] += execution_time
            
            self.logger.log_execution(
                f"Script execution completed successfully in {execution_time:.2f}s"
            )
            
            return f"Execution successful. Result: {result}"
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.execution_stats['failed_executions'] += 1
            
            error_msg = f"Script execution failed: {str(e)}"
            self.logger.log_error(error_msg)
            
            # Log full traceback for debugging
            self.logger.log_error(f"Traceback: {traceback.format_exc()}")
            
            raise ExecutionError(error_msg)
    
    def _validate_script(self, script_content: str) -> bool:
        """Validate script for security and safety"""
        # Check for dangerous patterns
        dangerous_patterns = [
            'os.execute',
            'io.popen',
            'loadstring',
            'dofile',
            'loadfile',
            'require',
            'package',
            'debug',
            'collectgarbage',
            'coroutine',
            'jit'
        ]
        
        script_lower = script_content.lower()
        for pattern in dangerous_patterns:
            if pattern in script_lower:
                self.logger.log_error(f"Script contains dangerous pattern: {pattern}")
                return False
        
        # Check for infinite loops (basic check)
        if script_content.count('while') > 5 or script_content.count('for') > 10:
            self.logger.log_warning("Script contains many loops - potential infinite loop risk")
        
        return True
    
    def _execute_in_sandbox(self, script_content: str, context: Dict[str, Any]) -> str:
        """Execute script in sandboxed environment"""
        try:
            # Create isolated Lua state
            sandboxed_runtime = lupa.LuaRuntime(
                unpack_returned_tuples=True,
                register_eval=False,
                register_builtins=False
            )
            
            # Set up sandboxed environment
            self.sandbox.setup_environment(sandboxed_runtime)
            
            # Execute with timeout
            result = self._execute_with_timeout(sandboxed_runtime, script_content)
            
            return str(result) if result is not None else "Execution completed"
            
        except Exception as e:
            raise ExecutionError(f"Sandbox execution failed: {str(e)}")
    
    def _execute_directly(self, script_content: str, context: Dict[str, Any]) -> str:
        """Execute script directly in main runtime"""
        try:
            result = self._execute_with_timeout(self.lua_runtime, script_content)
            return str(result) if result is not None else "Execution completed"
            
        except Exception as e:
            raise ExecutionError(f"Direct execution failed: {str(e)}")
    
    def _execute_with_timeout(self, runtime: LuaRuntime, script_content: str) -> Any:
        """Execute script with timeout protection"""
        result = [None]
        exception = [None]
        
        def execute_script():
            try:
                result[0] = runtime.execute(script_content)
            except Exception as e:
                exception[0] = e
        
        # Start execution in separate thread
        thread = threading.Thread(target=execute_script)
        thread.daemon = True
        thread.start()
        
        # Wait for completion or timeout
        thread.join(timeout=self.execution_timeout)
        
        if thread.is_alive():
            # Force thread termination (not ideal but necessary for security)
            self.logger.log_error("Script execution timed out")
            raise ExecutionError("Script execution timed out")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return self.execution_stats.copy()
    
    def clear_execution_stats(self):
        """Clear execution statistics"""
        self.execution_stats = {
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'total_execution_time': 0.0
        }
    
    def shutdown(self):
        """Shutdown the executor and cleanup resources"""
        self.is_running = False
        self.logger.log_execution("Executor shutting down")
        
        # Cleanup Lua runtime
        if self.lua_runtime:
            self.lua_runtime = None


class ExecutionError(Exception):
    """Custom exception for execution errors"""
    pass