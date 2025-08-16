#!/usr/bin/env python3
"""
CIA Roblox Executor - Core Execution Engine
Main execution loop, VM abstraction, and script management
"""

import os
import time
import threading
from typing import Optional, Dict, Any, NamedTuple
from pathlib import Path
import httpx

from .sandbox import Sandbox
from .anti_cheat_bypass import AntiCheatBypass
from .logger import Logger
from utils.config import Config


class ExecutionResult(NamedTuple):
    """Result of script execution"""
    success: bool
    output: str
    error: Optional[str] = None
    execution_time: float = 0.0
    memory_usage: int = 0


class ExecutorCore:
    """Main executor core for Roblox script execution"""
    
    def __init__(self):
        self.config = Config()
        self.logger = Logger()
        self.sandbox = Sandbox()
        self.anti_cheat = AntiCheatBypass()
        
        self.is_running = False
        self.current_script = None
        self.execution_thread = None
        
        # Integration with existing AI backend
        self.ollama_api = "http://localhost:11434/api/generate"
        self.model_map = {
            "mistral": "mistral:7b-instruct-q4_0",
            "deepseek": "deepseek-coder:6.7b-instruct-q4_0",
            "starcoder2": "starcoder2:7b-q4_0"
        }
        
    def execute_script(self, script_path: str) -> ExecutionResult:
        """Execute a Lua script in the sandboxed environment"""
        start_time = time.time()
        
        try:
            # Log execution start
            self.logger.log_execution_start(script_path)
            
            # Load and validate script
            script_content = self._load_script(script_path)
            if not script_content:
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Failed to load script file",
                    execution_time=time.time() - start_time
                )
            
            # Apply anti-cheat bypass
            modified_script = self.anti_cheat.apply_bypass(script_content)
            
            # Execute in sandbox
            result = self.sandbox.execute(modified_script)
            
            execution_time = time.time() - start_time
            
            # Log execution completion
            self.logger.log_execution_complete(
                script_path, 
                result.success, 
                execution_time,
                result.error
            )
            
            return ExecutionResult(
                success=result.success,
                output=result.output,
                error=result.error,
                execution_time=execution_time,
                memory_usage=result.memory_usage
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Execution error: {str(e)}"
            
            self.logger.log_execution_error(script_path, error_msg, execution_time)
            
            return ExecutionResult(
                success=False,
                output="",
                error=error_msg,
                execution_time=execution_time
            )
    
    def execute_script_async(self, script_path: str) -> None:
        """Execute a script asynchronously"""
        if self.is_running:
            raise RuntimeError("Another script is already running")
        
        self.is_running = True
        self.current_script = script_path
        
        self.execution_thread = threading.Thread(
            target=self._execute_async,
            args=(script_path,)
        )
        self.execution_thread.start()
    
    def stop_execution(self) -> bool:
        """Stop current script execution"""
        if not self.is_running:
            return False
        
        self.is_running = False
        self.sandbox.stop()
        
        if self.execution_thread:
            self.execution_thread.join(timeout=5.0)
        
        self.current_script = None
        self.logger.log_execution_stopped()
        
        return True
    
    def get_execution_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        return {
            "is_running": self.is_running,
            "current_script": self.current_script,
            "sandbox_status": self.sandbox.get_status(),
            "memory_usage": self.sandbox.get_memory_usage()
        }
    
    def _load_script(self, script_path: str) -> Optional[str]:
        """Load script content from file"""
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.logger.log_script_loaded(script_path, len(content))
            return content
            
        except Exception as e:
            self.logger.log_error(f"Failed to load script {script_path}: {str(e)}")
            return None
    
    def _execute_async(self, script_path: str) -> None:
        """Internal async execution method"""
        try:
            result = self.execute_script(script_path)
            if not result.success:
                self.logger.log_error(f"Async execution failed: {result.error}")
        finally:
            self.is_running = False
            self.current_script = None
    
    def generate_script_with_ai(self, prompt: str, model: str = "mistral") -> Optional[str]:
        """Generate a Roblox script using the integrated AI backend"""
        try:
            # Use existing AI backend integration
            async def generate():
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        self.ollama_api,
                        json={
                            "model": self.model_map.get(model, self.model_map["mistral"]),
                            "prompt": self._build_roblox_prompt(prompt)
                        },
                        timeout=60.0
                    )
                    return response.json().get("response", "")
            
            # Run async function in sync context
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                script_content = loop.run_until_complete(generate())
            finally:
                loop.close()
            
            if script_content:
                self.logger.log_ai_generation(prompt, model, len(script_content))
                return script_content
            else:
                self.logger.log_error("AI returned empty response")
                return None
                
        except Exception as e:
            self.logger.log_error(f"AI generation failed: {str(e)}")
            return None
    
    def _build_roblox_prompt(self, user_prompt: str) -> str:
        """Build a comprehensive prompt for Roblox script generation"""
        base_prompt = f"""
You are an expert Roblox Lua developer. Generate a safe, ethical Roblox script based on the following request:

USER REQUEST: {user_prompt}

REQUIREMENTS:
- Use only safe, ethical Lua code
- No malicious operations or exploits
- Follow Roblox API best practices
- Include proper error handling
- Add comments explaining the code
- Ensure the script is for educational/testing purposes only

Generate only the Lua code without any explanations or markdown formatting.
"""
        return base_prompt.strip()
    
    def validate_script(self, script_content: str) -> bool:
        """Validate script content for safety"""
        # Check for dangerous patterns
        dangerous_patterns = [
            "os.execute",
            "io.popen",
            "loadstring",
            "dofile",
            "require",
            "pcall",
            "xpcall"
        ]
        
        script_lower = script_content.lower()
        for pattern in dangerous_patterns:
            if pattern in script_lower:
                self.logger.log_security_warning(f"Dangerous pattern detected: {pattern}")
                return False
        
        return True
    
    def get_script_info(self, script_path: str) -> Dict[str, Any]:
        """Get information about a script file"""
        try:
            stat = os.stat(script_path)
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "path": script_path,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "lines": len(content.splitlines()),
                "characters": len(content),
                "is_valid": self.validate_script(content)
            }
        except Exception as e:
            return {
                "path": script_path,
                "error": str(e),
                "is_valid": False
            }
    
    def cleanup(self):
        """Cleanup resources"""
        if self.is_running:
            self.stop_execution()
        
        self.sandbox.cleanup()
        self.logger.close()