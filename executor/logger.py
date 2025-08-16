#!/usr/bin/env python3
"""
CIA Roblox Executor - Logger Module
Comprehensive logging and auditing for script executions and AI interactions
"""

import os
import json
import time
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading


class Logger:
    """Comprehensive logging system for CIA Roblox Executor"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Log file paths
        self.execution_log = self.log_dir / "execution.log"
        self.ai_log = self.log_dir / "ai_generation.log"
        self.security_log = self.log_dir / "security.log"
        self.audit_log = self.log_dir / "audit.log"
        self.error_log = self.log_dir / "errors.log"
        
        # Session tracking
        self.session_id = self._generate_session_id()
        self.session_start = datetime.now()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Initialize log files
        self._init_log_files()
        
        # Log session start
        self.log_session_start()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"session_{timestamp}_{random_suffix}"
    
    def _init_log_files(self):
        """Initialize log files with headers"""
        headers = {
            self.execution_log: "=== CIA Roblox Executor - Execution Log ===\n",
            self.ai_log: "=== CIA Roblox Executor - AI Generation Log ===\n",
            self.security_log: "=== CIA Roblox Executor - Security Log ===\n",
            self.audit_log: "=== CIA Roblox Executor - Audit Log ===\n",
            self.error_log: "=== CIA Roblox Executor - Error Log ===\n"
        }
        
        for log_file, header in headers.items():
            if not log_file.exists():
                with open(log_file, 'w', encoding='utf-8') as f:
                    f.write(header + f"Session: {self.session_id}\n")
                    f.write(f"Started: {self.session_start.isoformat()}\n")
                    f.write("=" * 50 + "\n\n")
    
    def log_session_start(self):
        """Log session start"""
        self._write_log(self.audit_log, "SESSION_START", {
            "session_id": self.session_id,
            "timestamp": self.session_start.isoformat(),
            "pid": os.getpid(),
            "user": os.getenv("USER", "unknown")
        })
    
    def log_session_end(self):
        """Log session end"""
        session_end = datetime.now()
        duration = (session_end - self.session_start).total_seconds()
        
        self._write_log(self.audit_log, "SESSION_END", {
            "session_id": self.session_id,
            "start_time": self.session_start.isoformat(),
            "end_time": session_end.isoformat(),
            "duration_seconds": duration
        })
    
    def log_execution_start(self, script_path: str):
        """Log script execution start"""
        script_hash = self._get_file_hash(script_path)
        script_info = self._get_script_info(script_path)
        
        self._write_log(self.execution_log, "EXECUTION_START", {
            "session_id": self.session_id,
            "script_path": script_path,
            "script_hash": script_hash,
            "script_size": script_info.get("size", 0),
            "script_lines": script_info.get("lines", 0),
            "timestamp": datetime.now().isoformat()
        })
    
    def log_execution_complete(self, script_path: str, success: bool, execution_time: float, error: Optional[str] = None):
        """Log script execution completion"""
        script_hash = self._get_file_hash(script_path)
        
        self._write_log(self.execution_log, "EXECUTION_COMPLETE", {
            "session_id": self.session_id,
            "script_path": script_path,
            "script_hash": script_hash,
            "success": success,
            "execution_time": execution_time,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_execution_error(self, script_path: str, error: str, execution_time: float):
        """Log script execution error"""
        script_hash = self._get_file_hash(script_path)
        
        self._write_log(self.error_log, "EXECUTION_ERROR", {
            "session_id": self.session_id,
            "script_path": script_path,
            "script_hash": script_hash,
            "error": error,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_execution_stopped(self):
        """Log execution stopped by user"""
        self._write_log(self.execution_log, "EXECUTION_STOPPED", {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "reason": "user_request"
        })
    
    def log_script_loaded(self, script_path: str, content_length: int):
        """Log script loading"""
        script_hash = self._get_file_hash(script_path)
        
        self._write_log(self.audit_log, "SCRIPT_LOADED", {
            "session_id": self.session_id,
            "script_path": script_path,
            "script_hash": script_hash,
            "content_length": content_length,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_ai_generation(self, prompt: str, model: str, output_length: int):
        """Log AI script generation"""
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
        
        self._write_log(self.ai_log, "AI_GENERATION", {
            "session_id": self.session_id,
            "prompt_hash": prompt_hash,
            "prompt_length": len(prompt),
            "model": model,
            "output_length": output_length,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_security_warning(self, warning: str):
        """Log security warning"""
        self._write_log(self.security_log, "SECURITY_WARNING", {
            "session_id": self.session_id,
            "warning": warning,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_security_violation(self, violation: str, script_path: Optional[str] = None):
        """Log security violation"""
        data = {
            "session_id": self.session_id,
            "violation": violation,
            "timestamp": datetime.now().isoformat()
        }
        
        if script_path:
            data["script_path"] = script_path
            data["script_hash"] = self._get_file_hash(script_path)
        
        self._write_log(self.security_log, "SECURITY_VIOLATION", data)
    
    def log_error(self, error: str, context: Optional[Dict[str, Any]] = None):
        """Log general error"""
        data = {
            "session_id": self.session_id,
            "error": error,
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            data.update(context)
        
        self._write_log(self.error_log, "ERROR", data)
    
    def log_audit_event(self, event_type: str, data: Dict[str, Any]):
        """Log audit event"""
        data.update({
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat()
        })
        
        self._write_log(self.audit_log, event_type.upper(), data)
    
    def _write_log(self, log_file: Path, event_type: str, data: Dict[str, Any]):
        """Write log entry to file"""
        with self.lock:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = {
                    "timestamp": timestamp,
                    "event_type": event_type,
                    "data": data
                }
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                    
            except Exception as e:
                # Fallback to simple logging if JSON fails
                try:
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"{timestamp} [{event_type}] {str(data)}\n")
                except:
                    pass  # Last resort - ignore logging errors
    
    def _get_file_hash(self, file_path: str) -> str:
        """Get SHA256 hash of file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()[:16]
        except:
            return "unknown"
    
    def _get_script_info(self, script_path: str) -> Dict[str, Any]:
        """Get script file information"""
        try:
            stat = os.stat(script_path)
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "size": stat.st_size,
                "lines": len(content.splitlines()),
                "modified": stat.st_mtime
            }
        except:
            return {"size": 0, "lines": 0, "modified": 0}
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get execution summary for current session"""
        summary = {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "ai_generations": 0,
            "security_warnings": 0,
            "errors": 0
        }
        
        # Count events from log files
        summary.update(self._count_log_events())
        
        return summary
    
    def _count_log_events(self) -> Dict[str, int]:
        """Count events in log files"""
        counts = {
            "executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "ai_generations": 0,
            "security_warnings": 0,
            "errors": 0
        }
        
        try:
            # Count execution events
            if self.execution_log.exists():
                with open(self.execution_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '"event_type": "EXECUTION_START"' in line:
                            counts["executions"] += 1
                        elif '"event_type": "EXECUTION_COMPLETE"' in line:
                            if '"success": true' in line:
                                counts["successful_executions"] += 1
                            else:
                                counts["failed_executions"] += 1
            
            # Count AI generations
            if self.ai_log.exists():
                with open(self.ai_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '"event_type": "AI_GENERATION"' in line:
                            counts["ai_generations"] += 1
            
            # Count security warnings
            if self.security_log.exists():
                with open(self.security_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '"event_type": "SECURITY_WARNING"' in line:
                            counts["security_warnings"] += 1
            
            # Count errors
            if self.error_log.exists():
                with open(self.error_log, 'r', encoding='utf-8') as f:
                    for line in f:
                        if '"event_type": "ERROR"' in line or '"event_type": "EXECUTION_ERROR"' in line:
                            counts["errors"] += 1
                            
        except Exception:
            pass  # Ignore counting errors
        
        return counts
    
    def export_logs(self, output_path: str, log_types: Optional[List[str]] = None):
        """Export logs to file"""
        if log_types is None:
            log_types = ["execution", "ai", "security", "audit", "error"]
        
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "session_id": self.session_id,
                "log_types": log_types
            },
            "summary": self.get_execution_summary(),
            "logs": {}
        }
        
        log_file_map = {
            "execution": self.execution_log,
            "ai": self.ai_log,
            "security": self.security_log,
            "audit": self.audit_log,
            "error": self.error_log
        }
        
        for log_type in log_types:
            if log_type in log_file_map and log_file_map[log_type].exists():
                try:
                    with open(log_file_map[log_type], 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        export_data["logs"][log_type] = [
                            json.loads(line.strip()) for line in lines 
                            if line.strip() and not line.startswith("===")
                        ]
                except Exception as e:
                    export_data["logs"][log_type] = f"Error reading log: {str(e)}"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            self.log_audit_event("LOGS_EXPORTED", {
                "output_path": output_path,
                "log_types": log_types
            })
            
        except Exception as e:
            raise Exception(f"Failed to export logs: {str(e)}")
    
    def clear_logs(self, log_types: Optional[List[str]] = None):
        """Clear log files"""
        if log_types is None:
            log_types = ["execution", "ai", "security", "audit", "error"]
        
        log_file_map = {
            "execution": self.execution_log,
            "ai": self.ai_log,
            "security": self.security_log,
            "audit": self.audit_log,
            "error": self.error_log
        }
        
        for log_type in log_types:
            if log_type in log_file_map:
                try:
                    log_file = log_file_map[log_type]
                    if log_file.exists():
                        # Backup before clearing
                        backup_file = log_file.with_suffix('.backup')
                        log_file.rename(backup_file)
                        
                        # Reinitialize
                        self._init_log_files()
                        
                except Exception as e:
                    self.log_error(f"Failed to clear {log_type} log: {str(e)}")
        
        self.log_audit_event("LOGS_CLEARED", {"log_types": log_types})
    
    def close(self):
        """Close logger and cleanup"""
        self.log_session_end()