#!/usr/bin/env python3
"""
CIA Roblox Executor - Execution Logger
Records all script executions and AI interactions for auditing.
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import threading

from utils.config import Config


class ExecutionLogger:
    """
    Comprehensive logging system for script execution and AI interactions.
    Provides audit trails and debugging information.
    """
    
    def __init__(self):
        self.config = Config()
        
        # Create logs directory if it doesn't exist
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Log file paths
        self.execution_log_path = self.logs_dir / "execution.log"
        self.ai_log_path = self.logs_dir / "ai_interactions.log"
        self.error_log_path = self.logs_dir / "errors.log"
        self.audit_log_path = self.logs_dir / "audit.log"
        
        # Initialize logging
        self._setup_logging()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Log rotation settings
        self.max_log_size = 10 * 1024 * 1024  # 10MB
        self.max_log_files = 5
    
    def _setup_logging(self):
        """Set up logging configuration"""
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Execution logger
        self.execution_logger = logging.getLogger('execution')
        self.execution_logger.setLevel(logging.INFO)
        
        execution_handler = logging.FileHandler(self.execution_log_path)
        execution_handler.setFormatter(detailed_formatter)
        self.execution_logger.addHandler(execution_handler)
        
        # AI logger
        self.ai_logger = logging.getLogger('ai')
        self.ai_logger.setLevel(logging.INFO)
        
        ai_handler = logging.FileHandler(self.ai_log_path)
        ai_handler.setFormatter(detailed_formatter)
        self.ai_logger.addHandler(ai_handler)
        
        # Error logger
        self.error_logger = logging.getLogger('errors')
        self.error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(self.error_log_path)
        error_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Audit logger
        self.audit_logger = logging.getLogger('audit')
        self.audit_logger.setLevel(logging.INFO)
        
        audit_handler = logging.FileHandler(self.audit_log_path)
        audit_handler.setFormatter(detailed_formatter)
        self.audit_logger.addHandler(audit_handler)
    
    def log_execution(self, message: str, script_name: str = "unknown", 
                     execution_id: str = None, metadata: Dict[str, Any] = None):
        """
        Log script execution events.
        
        Args:
            message: The log message
            script_name: Name of the script being executed
            execution_id: Unique execution identifier
            metadata: Additional metadata
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'execution',
                'message': message,
                'script_name': script_name,
                'execution_id': execution_id or self._generate_id(),
                'metadata': metadata or {}
            }
            
            self.execution_logger.info(json.dumps(log_entry))
            self._check_log_rotation(self.execution_log_path)
    
    def log_ai_interaction(self, prompt: str, response: str, model: str = "unknown",
                          generation_time: float = 0.0, metadata: Dict[str, Any] = None):
        """
        Log AI interactions.
        
        Args:
            prompt: The AI prompt
            response: The AI response
            model: The AI model used
            generation_time: Time taken for generation
            metadata: Additional metadata
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'ai_interaction',
                'prompt': prompt,
                'response': response,
                'model': model,
                'generation_time': generation_time,
                'metadata': metadata or {}
            }
            
            self.ai_logger.info(json.dumps(log_entry))
            self._check_log_rotation(self.ai_log_path)
    
    def log_error(self, error_message: str, error_type: str = "unknown",
                  script_name: str = "unknown", traceback: str = None,
                  metadata: Dict[str, Any] = None):
        """
        Log error events.
        
        Args:
            error_message: The error message
            error_type: Type of error
            script_name: Name of the script that caused the error
            traceback: Full traceback information
            metadata: Additional metadata
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'error',
                'error_message': error_message,
                'error_type': error_type,
                'script_name': script_name,
                'traceback': traceback,
                'metadata': metadata or {}
            }
            
            self.error_logger.error(json.dumps(log_entry))
            self._check_log_rotation(self.error_log_path)
    
    def log_warning(self, message: str, script_name: str = "unknown",
                   metadata: Dict[str, Any] = None):
        """
        Log warning events.
        
        Args:
            message: The warning message
            script_name: Name of the script
            metadata: Additional metadata
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'warning',
                'message': message,
                'script_name': script_name,
                'metadata': metadata or {}
            }
            
            self.execution_logger.warning(json.dumps(log_entry))
    
    def log_output(self, output: str, script_name: str = "unknown",
                  metadata: Dict[str, Any] = None):
        """
        Log script output.
        
        Args:
            output: The script output
            script_name: Name of the script
            metadata: Additional metadata
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'output',
                'output': output,
                'script_name': script_name,
                'metadata': metadata or {}
            }
            
            self.execution_logger.info(json.dumps(log_entry))
    
    def log_audit(self, action: str, user: str = "system", 
                  resource: str = "unknown", details: Dict[str, Any] = None):
        """
        Log audit events for security and compliance.
        
        Args:
            action: The action performed
            user: User performing the action
            resource: Resource being accessed
            details: Additional details
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'audit',
                'action': action,
                'user': user,
                'resource': resource,
                'details': details or {}
            }
            
            self.audit_logger.info(json.dumps(log_entry))
            self._check_log_rotation(self.audit_log_path)
    
    def log_security_event(self, event_type: str, description: str,
                          severity: str = "medium", metadata: Dict[str, Any] = None):
        """
        Log security-related events.
        
        Args:
            event_type: Type of security event
            description: Description of the event
            severity: Severity level (low, medium, high, critical)
            metadata: Additional metadata
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'security',
                'event_type': event_type,
                'description': description,
                'severity': severity,
                'metadata': metadata or {}
            }
            
            self.audit_logger.warning(json.dumps(log_entry))
    
    def log_performance(self, operation: str, duration: float,
                       script_name: str = "unknown", metadata: Dict[str, Any] = None):
        """
        Log performance metrics.
        
        Args:
            operation: The operation being measured
            duration: Duration in seconds
            script_name: Name of the script
            metadata: Additional metadata
        """
        with self._lock:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'type': 'performance',
                'operation': operation,
                'duration': duration,
                'script_name': script_name,
                'metadata': metadata or {}
            }
            
            self.execution_logger.info(json.dumps(log_entry))
    
    def get_execution_logs(self, limit: int = 100, 
                          script_name: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve execution logs.
        
        Args:
            limit: Maximum number of logs to retrieve
            script_name: Filter by script name
            
        Returns:
            List of log entries
        """
        return self._read_logs(self.execution_log_path, limit, script_name)
    
    def get_ai_logs(self, limit: int = 100, model: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve AI interaction logs.
        
        Args:
            limit: Maximum number of logs to retrieve
            model: Filter by AI model
            
        Returns:
            List of log entries
        """
        logs = self._read_logs(self.ai_log_path, limit)
        
        if model:
            logs = [log for log in logs if log.get('model') == model]
        
        return logs
    
    def get_error_logs(self, limit: int = 100, 
                      error_type: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve error logs.
        
        Args:
            limit: Maximum number of logs to retrieve
            error_type: Filter by error type
            
        Returns:
            List of log entries
        """
        logs = self._read_logs(self.error_log_path, limit)
        
        if error_type:
            logs = [log for log in logs if log.get('error_type') == error_type]
        
        return logs
    
    def get_audit_logs(self, limit: int = 100, 
                      action: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve audit logs.
        
        Args:
            limit: Maximum number of logs to retrieve
            action: Filter by action
            
        Returns:
            List of log entries
        """
        logs = self._read_logs(self.audit_log_path, limit)
        
        if action:
            logs = [log for log in logs if log.get('action') == action]
        
        return logs
    
    def _read_logs(self, log_path: Path, limit: int, 
                   filter_key: str = None, filter_value: str = None) -> List[Dict[str, Any]]:
        """Read logs from file with optional filtering"""
        logs = []
        
        try:
            if not log_path.exists():
                return logs
            
            with open(log_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Parse JSON logs (skip lines that aren't JSON)
            for line in lines[-limit:]:  # Get last N lines
                line = line.strip()
                if not line:
                    continue
                
                try:
                    # Extract JSON from log line (after timestamp and level)
                    json_start = line.find('{')
                    if json_start == -1:
                        continue
                    
                    json_part = line[json_start:]
                    log_entry = json.loads(json_part)
                    
                    # Apply filter if specified
                    if filter_key and filter_value:
                        if log_entry.get(filter_key) != filter_value:
                            continue
                    
                    logs.append(log_entry)
                    
                except json.JSONDecodeError:
                    continue
            
            return logs[-limit:]  # Return last N entries
            
        except Exception as e:
            self.error_logger.error(f"Failed to read logs from {log_path}: {str(e)}")
            return []
    
    def _generate_id(self) -> str:
        """Generate a unique identifier"""
        return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now())}"
    
    def _check_log_rotation(self, log_path: Path):
        """Check if log rotation is needed"""
        try:
            if log_path.exists() and log_path.stat().st_size > self.max_log_size:
                self._rotate_log(log_path)
        except Exception as e:
            self.error_logger.error(f"Log rotation check failed: {str(e)}")
    
    def _rotate_log(self, log_path: Path):
        """Rotate log file"""
        try:
            # Remove oldest log file if we have too many
            for i in range(self.max_log_files - 1, 0, -1):
                old_file = log_path.with_suffix(f'.{i}')
                new_file = log_path.with_suffix(f'.{i + 1}')
                
                if old_file.exists():
                    if new_file.exists():
                        new_file.unlink()
                    old_file.rename(new_file)
            
            # Rename current log file
            backup_file = log_path.with_suffix('.1')
            if backup_file.exists():
                backup_file.unlink()
            log_path.rename(backup_file)
            
            # Recreate log file
            log_path.touch()
            
        except Exception as e:
            self.error_logger.error(f"Log rotation failed: {str(e)}")
    
    def export_logs(self, output_path: str, log_types: List[str] = None,
                   start_date: str = None, end_date: str = None) -> bool:
        """
        Export logs to a file.
        
        Args:
            output_path: Path to export logs to
            log_types: Types of logs to export (execution, ai, error, audit)
            start_date: Start date filter (ISO format)
            end_date: End date filter (ISO format)
            
        Returns:
            True if export was successful
        """
        try:
            if log_types is None:
                log_types = ['execution', 'ai', 'error', 'audit']
            
            all_logs = []
            
            for log_type in log_types:
                if log_type == 'execution':
                    logs = self.get_execution_logs(limit=10000)
                elif log_type == 'ai':
                    logs = self.get_ai_logs(limit=10000)
                elif log_type == 'error':
                    logs = self.get_error_logs(limit=10000)
                elif log_type == 'audit':
                    logs = self.get_audit_logs(limit=10000)
                else:
                    continue
                
                all_logs.extend(logs)
            
            # Apply date filtering
            if start_date or end_date:
                filtered_logs = []
                for log in all_logs:
                    timestamp = log.get('timestamp', '')
                    if start_date and timestamp < start_date:
                        continue
                    if end_date and timestamp > end_date:
                        continue
                    filtered_logs.append(log)
                all_logs = filtered_logs
            
            # Sort by timestamp
            all_logs.sort(key=lambda x: x.get('timestamp', ''))
            
            # Export to file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_logs, f, indent=2, ensure_ascii=False)
            
            return True
            
        except Exception as e:
            self.error_logger.error(f"Log export failed: {str(e)}")
            return False
    
    def clear_logs(self, log_types: List[str] = None):
        """
        Clear log files.
        
        Args:
            log_types: Types of logs to clear (execution, ai, error, audit)
        """
        if log_types is None:
            log_types = ['execution', 'ai', 'error', 'audit']
        
        for log_type in log_types:
            if log_type == 'execution':
                self._clear_log_file(self.execution_log_path)
            elif log_type == 'ai':
                self._clear_log_file(self.ai_log_path)
            elif log_type == 'error':
                self._clear_log_file(self.error_log_path)
            elif log_type == 'audit':
                self._clear_log_file(self.audit_log_path)
    
    def _clear_log_file(self, log_path: Path):
        """Clear a specific log file"""
        try:
            if log_path.exists():
                log_path.unlink()
            log_path.touch()
        except Exception as e:
            self.error_logger.error(f"Failed to clear log file {log_path}: {str(e)}")
    
    def get_log_statistics(self) -> Dict[str, Any]:
        """Get statistics about log files"""
        stats = {}
        
        for log_type, log_path in [
            ('execution', self.execution_log_path),
            ('ai', self.ai_log_path),
            ('error', self.error_log_path),
            ('audit', self.audit_log_path)
        ]:
            try:
                if log_path.exists():
                    size = log_path.stat().st_size
                    line_count = sum(1 for _ in open(log_path, 'r', encoding='utf-8'))
                    stats[log_type] = {
                        'size_bytes': size,
                        'size_mb': size / (1024 * 1024),
                        'line_count': line_count,
                        'exists': True
                    }
                else:
                    stats[log_type] = {
                        'size_bytes': 0,
                        'size_mb': 0,
                        'line_count': 0,
                        'exists': False
                    }
            except Exception as e:
                stats[log_type] = {
                    'error': str(e),
                    'exists': False
                }
        
        return stats