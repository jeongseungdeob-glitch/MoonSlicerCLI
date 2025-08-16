#!/usr/bin/env python3
"""
CIA Roblox Executor - Configuration Management
Manages configuration settings for the executor.
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from executor.logger import ExecutionLogger


class Config:
    """
    Configuration management for the CIA Roblox Executor.
    Handles loading, saving, and accessing configuration settings.
    """
    
    def __init__(self, config_path: str = None):
        self.logger = ExecutionLogger()
        
        # Default config path
        if config_path is None:
            self.config_path = Path("config.yaml")
        else:
            self.config_path = Path(config_path)
        
        # Default configuration
        self.default_config = {
            'executor': {
                'name': 'CIA Roblox Executor',
                'version': '1.0.0',
                'max_execution_time': 30,
                'max_memory_usage_mb': 100,
                'enable_sandbox': True,
                'enable_bypass': True,
                'log_level': 'INFO',
                'auto_save_logs': True,
                'log_retention_days': 30
            },
            'ai': {
                'default_model': 'mistral',
                'max_tokens': 2048,
                'temperature': 0.7,
                'timeout_seconds': 60,
                'enable_auto_model_selection': True,
                'models': {
                    'mistral': {
                        'name': 'mistral:7b-instruct-q4_0',
                        'api_url': 'http://localhost:11434/api/generate',
                        'max_tokens': 2048,
                        'temperature': 0.7
                    },
                    'deepseek': {
                        'name': 'deepseek-coder:6.7b-instruct-q4_0',
                        'api_url': 'http://localhost:11434/api/generate',
                        'max_tokens': 2048,
                        'temperature': 0.5
                    },
                    'starcoder2': {
                        'name': 'starcoder2:7b-q4_0',
                        'api_url': 'http://localhost:11434/api/generate',
                        'max_tokens': 2048,
                        'temperature': 0.6
                    }
                }
            },
            'security': {
                'enable_validation': True,
                'enable_sanitization': True,
                'max_script_length': 50000,
                'blocked_functions': [
                    'os.execute', 'io.popen', 'loadstring', 'dofile',
                    'require', 'debug.getinfo', 'collectgarbage'
                ],
                'allowed_roblox_apis': [
                    'game', 'workspace', 'players', 'player', 'script',
                    'Vector3', 'CFrame', 'Color3', 'Instance', 'TweenInfo',
                    'wait', 'spawn', 'tick', 'time', 'warn', 'error', 'print'
                ],
                'bypass_level': 'medium'  # low, medium, high
            },
            'gui': {
                'theme': 'dark',
                'window_width': 1400,
                'window_height': 900,
                'auto_save_interval': 300,  # 5 minutes
                'show_line_numbers': True,
                'font_size': 12,
                'font_family': 'Consolas'
            },
            'paths': {
                'logs_dir': 'logs',
                'scripts_dir': 'sandboxed_scripts',
                'backup_dir': 'backups',
                'temp_dir': 'temp'
            },
            'crypto': {
                'enable_encryption': True,
                'key_file': '~/.cia_executor_key',
                'algorithm': 'AES-256-GCM'
            }
        }
        
        # Load configuration
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                # Merge with defaults to ensure all keys exist
                config = self._merge_configs(self.default_config, config)
                self.logger.log_execution(f"Configuration loaded from {self.config_path}")
                return config
            else:
                # Create default configuration
                self.save_config(self.default_config)
                self.logger.log_execution("Default configuration created")
                return self.default_config.copy()
                
        except Exception as e:
            self.logger.log_error(f"Failed to load configuration: {str(e)}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to file"""
        try:
            if config is None:
                config = self.config
            
            # Create directory if it doesn't exist
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            self.logger.log_execution(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to save configuration: {str(e)}")
            return False
    
    def _merge_configs(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """Merge user configuration with defaults"""
        result = default.copy()
        
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            value = self.config
            
            for k in keys:
                value = value[k]
            
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value by key (supports dot notation)"""
        try:
            keys = key.split('.')
            config = self.config
            
            # Navigate to the parent of the target key
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            
            # Set the value
            config[keys[-1]] = value
            
            # Save the configuration
            return self.save_config()
            
        except Exception as e:
            self.logger.log_error(f"Failed to set configuration key {key}: {str(e)}")
            return False
    
    def get_executor_config(self) -> Dict[str, Any]:
        """Get executor-specific configuration"""
        return self.config.get('executor', {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI-specific configuration"""
        return self.config.get('ai', {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security-specific configuration"""
        return self.config.get('security', {})
    
    def get_gui_config(self) -> Dict[str, Any]:
        """Get GUI-specific configuration"""
        return self.config.get('gui', {})
    
    def get_paths_config(self) -> Dict[str, Any]:
        """Get paths configuration"""
        return self.config.get('paths', {})
    
    def get_crypto_config(self) -> Dict[str, Any]:
        """Get crypto configuration"""
        return self.config.get('crypto', {})
    
    def update_executor_config(self, updates: Dict[str, Any]) -> bool:
        """Update executor configuration"""
        try:
            self.config['executor'].update(updates)
            return self.save_config()
        except Exception as e:
            self.logger.log_error(f"Failed to update executor config: {str(e)}")
            return False
    
    def update_ai_config(self, updates: Dict[str, Any]) -> bool:
        """Update AI configuration"""
        try:
            self.config['ai'].update(updates)
            return self.save_config()
        except Exception as e:
            self.logger.log_error(f"Failed to update AI config: {str(e)}")
            return False
    
    def update_security_config(self, updates: Dict[str, Any]) -> bool:
        """Update security configuration"""
        try:
            self.config['security'].update(updates)
            return self.save_config()
        except Exception as e:
            self.logger.log_error(f"Failed to update security config: {str(e)}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            self.config = self.default_config.copy()
            return self.save_config()
        except Exception as e:
            self.logger.log_error(f"Failed to reset configuration: {str(e)}")
            return False
    
    def export_config(self, export_path: str) -> bool:
        """Export configuration to a file"""
        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            
            self.logger.log_execution(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.log_error(f"Failed to export configuration: {str(e)}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """Import configuration from a file"""
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                imported_config = yaml.safe_load(f)
            
            # Merge with current config
            self.config = self._merge_configs(self.config, imported_config)
            return self.save_config()
            
        except Exception as e:
            self.logger.log_error(f"Failed to import configuration: {str(e)}")
            return False
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return issues"""
        issues = []
        warnings = []
        
        # Check required paths
        paths_config = self.get_paths_config()
        for path_name, path_value in paths_config.items():
            if not path_value:
                issues.append(f"Path '{path_name}' is empty")
        
        # Check AI configuration
        ai_config = self.get_ai_config()
        if not ai_config.get('models'):
            issues.append("No AI models configured")
        
        # Check security configuration
        security_config = self.get_security_config()
        if not security_config.get('blocked_functions'):
            warnings.append("No blocked functions configured")
        
        # Check executor configuration
        executor_config = self.get_executor_config()
        if executor_config.get('max_execution_time', 0) <= 0:
            issues.append("Invalid max execution time")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration"""
        return {
            'executor_name': self.get('executor.name'),
            'version': self.get('executor.version'),
            'default_ai_model': self.get('ai.default_model'),
            'security_level': self.get('security.bypass_level'),
            'gui_theme': self.get('gui.theme'),
            'max_execution_time': self.get('executor.max_execution_time'),
            'enable_sandbox': self.get('executor.enable_sandbox'),
            'enable_bypass': self.get('executor.enable_bypass'),
            'log_level': self.get('executor.log_level'),
            'config_path': str(self.config_path),
            'last_modified': datetime.fromtimestamp(self.config_path.stat().st_mtime).isoformat() if self.config_path.exists() else None
        }