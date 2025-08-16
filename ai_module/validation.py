#!/usr/bin/env python3
"""
CIA Roblox Executor - Script Validation
Ensures AI-generated scripts are safe and free of malicious code.
"""

import re
import ast
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

from utils.config import Config
from executor.logger import ExecutionLogger


class ScriptValidator:
    """
    Validates Lua scripts for safety and security.
    Checks for malicious patterns, infinite loops, and unsafe operations.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        
        # Dangerous patterns that should be blocked
        self.dangerous_patterns = {
            'system_access': [
                r'os\.execute\s*\(',
                r'io\.popen\s*\(',
                r'io\.open\s*\(',
                r'io\.close\s*\(',
                r'io\.read\s*\(',
                r'io\.write\s*\(',
                r'os\.remove\s*\(',
                r'os\.rename\s*\(',
                r'os\.tmpname\s*\(',
            ],
            'code_execution': [
                r'loadstring\s*\(',
                r'loadfile\s*\(',
                r'dofile\s*\(',
                r'require\s*\(',
                r'package\.loadlib\s*\(',
            ],
            'debug_access': [
                r'debug\.getinfo\s*\(',
                r'debug\.getlocal\s*\(',
                r'debug\.getupvalue\s*\(',
                r'debug\.setlocal\s*\(',
                r'debug\.setupvalue\s*\(',
                r'debug\.traceback\s*\(',
            ],
            'memory_manipulation': [
                r'collectgarbage\s*\(',
                r'coroutine\.create\s*\(',
                r'coroutine\.resume\s*\(',
                r'coroutine\.yield\s*\(',
                r'jit\.',
            ],
            'network_access': [
                r'http\s*\(',
                r'https\s*\(',
                r'request\s*\(',
                r'fetch\s*\(',
                r'webhook\s*\(',
            ]
        }
        
        # Suspicious patterns that should be flagged
        self.suspicious_patterns = {
            'infinite_loops': [
                r'while\s+true\s+do',
                r'for\s+\w+\s*=\s*1\s*,\s*999999\s+do',
                r'repeat\s+until\s+false',
                r'while\s+1\s*==\s*1\s+do',
            ],
            'excessive_iterations': [
                r'for\s+\w+\s*=\s*1\s*,\s*\d{6,}\s+do',  # Loops with 100000+ iterations
                r'for\s+\w+\s*=\s*1\s*,\s*math\.huge\s+do',
            ],
            'suspicious_strings': [
                r'exploit',
                r'hack',
                r'cheat',
                r'bypass',
                r'inject',
                r'malware',
                r'virus',
                r'backdoor',
            ],
            'obfuscation': [
                r'string\.char\s*\(\s*\d+\s*\)',
                r'string\.byte\s*\(',
                r'\\x[0-9a-fA-F]{2}',
                r'\\u[0-9a-fA-F]{4}',
            ]
        }
        
        # Safe Roblox APIs
        self.safe_roblox_apis = [
            'game', 'workspace', 'players', 'player', 'script',
            'Vector3', 'CFrame', 'Color3', 'Instance', 'TweenInfo',
            'wait', 'spawn', 'tick', 'time', 'warn', 'error', 'print',
            'math', 'string', 'table', 'tonumber', 'tostring', 'type',
            'pairs', 'ipairs', 'next', 'select', 'pcall', 'xpcall',
            'assert', 'error', 'warn'
        ]
        
        # Validation rules
        self.validation_rules = {
            'max_script_length': 50000,  # 50KB
            'max_function_count': 50,
            'max_variable_count': 100,
            'max_loop_count': 10,
            'max_string_length': 1000,
            'max_comment_ratio': 0.8,  # 80% comments is suspicious
            'min_code_lines': 3,  # At least 3 lines of actual code
        }
    
    def validate_script(self, script_content: str) -> bool:
        """
        Validate a Lua script for safety and security.
        
        Args:
            script_content: The script to validate
            
        Returns:
            True if script is safe, False otherwise
        """
        try:
            # Basic validation checks
            if not self._basic_validation(script_content):
                return False
            
            # Security validation
            if not self._security_validation(script_content):
                return False
            
            # Performance validation
            if not self._performance_validation(script_content):
                return False
            
            # Content validation
            if not self._content_validation(script_content):
                return False
            
            self.logger.log_execution("Script validation passed successfully")
            return True
            
        except Exception as e:
            self.logger.log_error(
                f"Script validation failed: {str(e)}",
                error_type="validation_error"
            )
            return False
    
    def _basic_validation(self, script_content: str) -> bool:
        """Perform basic validation checks"""
        if not script_content or len(script_content.strip()) < 10:
            self.logger.log_warning("Script is too short")
            return False
        
        if len(script_content) > self.validation_rules['max_script_length']:
            self.logger.log_warning("Script is too long")
            return False
        
        # Check for balanced brackets and parentheses
        if not self._check_balanced_delimiters(script_content):
            self.logger.log_warning("Unbalanced delimiters detected")
            return False
        
        return True
    
    def _security_validation(self, script_content: str) -> bool:
        """Perform security validation checks"""
        script_lower = script_content.lower()
        
        # Check for dangerous patterns
        for category, patterns in self.dangerous_patterns.items():
            for pattern in patterns:
                if re.search(pattern, script_lower, re.IGNORECASE):
                    self.logger.log_security_event(
                        f"Dangerous pattern detected: {pattern}",
                        f"Script contains {category} pattern",
                        severity="high"
                    )
                    return False
        
        # Check for suspicious patterns
        suspicious_count = 0
        for category, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                if re.search(pattern, script_lower, re.IGNORECASE):
                    suspicious_count += 1
                    self.logger.log_warning(f"Suspicious pattern detected: {pattern}")
        
        if suspicious_count > 5:
            self.logger.log_security_event(
                "Too many suspicious patterns",
                f"Script contains {suspicious_count} suspicious patterns",
                severity="medium"
            )
            return False
        
        return True
    
    def _performance_validation(self, script_content: str) -> bool:
        """Perform performance validation checks"""
        # Check for infinite loops
        for pattern in self.suspicious_patterns['infinite_loops']:
            if re.search(pattern, script_content, re.IGNORECASE):
                self.logger.log_warning("Potential infinite loop detected")
                return False
        
        # Check for excessive iterations
        for pattern in self.suspicious_patterns['excessive_iterations']:
            if re.search(pattern, script_content, re.IGNORECASE):
                self.logger.log_warning("Excessive iteration count detected")
                return False
        
        # Check function count
        function_count = len(re.findall(r'function\s+\w+', script_content, re.IGNORECASE))
        if function_count > self.validation_rules['max_function_count']:
            self.logger.log_warning(f"Too many functions: {function_count}")
            return False
        
        # Check variable count
        variable_count = len(re.findall(r'local\s+\w+', script_content, re.IGNORECASE))
        if variable_count > self.validation_rules['max_variable_count']:
            self.logger.log_warning(f"Too many variables: {variable_count}")
            return False
        
        return True
    
    def _content_validation(self, script_content: str) -> bool:
        """Perform content validation checks"""
        lines = script_content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith('--')]
        code_lines = [line for line in non_empty_lines if not line.strip().startswith('--')]
        
        # Check minimum code lines
        if len(code_lines) < self.validation_rules['min_code_lines']:
            self.logger.log_warning("Not enough actual code lines")
            return False
        
        # Check comment ratio
        if non_empty_lines:
            comment_ratio = len(comment_lines) / len(non_empty_lines)
            if comment_ratio > self.validation_rules['max_comment_ratio']:
                self.logger.log_warning(f"Too many comments: {comment_ratio:.2f}")
                return False
        
        # Check for suspicious strings
        for pattern in self.suspicious_patterns['suspicious_strings']:
            if re.search(pattern, script_content, re.IGNORECASE):
                self.logger.log_warning(f"Suspicious string detected: {pattern}")
                return False
        
        return True
    
    def _check_balanced_delimiters(self, content: str) -> bool:
        """Check if brackets and parentheses are balanced"""
        stack = []
        delimiters = {'(': ')', '[': ']', '{': '}'}
        
        for char in content:
            if char in delimiters:
                stack.append(char)
            elif char in delimiters.values():
                if not stack:
                    return False
                if delimiters[stack.pop()] != char:
                    return False
        
        return len(stack) == 0
    
    def get_validation_report(self, script_content: str) -> Dict[str, Any]:
        """
        Generate a comprehensive validation report for a script.
        
        Args:
            script_content: The script to analyze
            
        Returns:
            Detailed validation report
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'script_length': len(script_content),
            'validation_passed': False,
            'issues': [],
            'warnings': [],
            'statistics': {},
            'security_score': 0,
            'recommendations': []
        }
        
        try:
            # Basic statistics
            lines = script_content.split('\n')
            non_empty_lines = [line for line in lines if line.strip()]
            comment_lines = [line for line in lines if line.strip().startswith('--')]
            code_lines = [line for line in non_empty_lines if not line.strip().startswith('--')]
            
            report['statistics'] = {
                'total_lines': len(lines),
                'non_empty_lines': len(non_empty_lines),
                'comment_lines': len(comment_lines),
                'code_lines': len(code_lines),
                'function_count': len(re.findall(r'function\s+\w+', script_content, re.IGNORECASE)),
                'variable_count': len(re.findall(r'local\s+\w+', script_content, re.IGNORECASE)),
                'loop_count': len(re.findall(r'for\s+|while\s+|repeat\s+', script_content, re.IGNORECASE)),
                'print_count': len(re.findall(r'print\s*\(', script_content, re.IGNORECASE)),
                'wait_count': len(re.findall(r'wait\s*\(', script_content, re.IGNORECASE)),
            }
            
            # Security analysis
            security_issues = []
            for category, patterns in self.dangerous_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, script_content, re.IGNORECASE):
                        security_issues.append(f"{category}: {pattern}")
            
            if security_issues:
                report['issues'].extend(security_issues)
                report['security_score'] -= 50
            
            # Suspicious pattern analysis
            suspicious_patterns = []
            for category, patterns in self.suspicious_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, script_content, re.IGNORECASE):
                        suspicious_patterns.append(f"{category}: {pattern}")
            
            if suspicious_patterns:
                report['warnings'].extend(suspicious_patterns)
                report['security_score'] -= 10
            
            # Performance analysis
            if report['statistics']['loop_count'] > self.validation_rules['max_loop_count']:
                report['warnings'].append(f"Too many loops: {report['statistics']['loop_count']}")
                report['security_score'] -= 5
            
            # Content analysis
            if report['statistics']['code_lines'] < self.validation_rules['min_code_lines']:
                report['issues'].append("Not enough actual code lines")
                report['security_score'] -= 20
            
            # Calculate final security score
            report['security_score'] = max(0, min(100, report['security_score'] + 100))
            
            # Determine if validation passed
            report['validation_passed'] = len(report['issues']) == 0 and report['security_score'] >= 70
            
            # Generate recommendations
            report['recommendations'] = self._generate_recommendations(report)
            
        except Exception as e:
            report['issues'].append(f"Validation analysis failed: {str(e)}")
            report['security_score'] = 0
        
        return report
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on validation report"""
        recommendations = []
        
        if report['security_score'] < 80:
            recommendations.append("Consider reviewing the script for security issues")
        
        if report['statistics']['comment_lines'] < 2:
            recommendations.append("Add more comments to improve code readability")
        
        if report['statistics']['function_count'] > 20:
            recommendations.append("Consider breaking down large scripts into smaller functions")
        
        if report['statistics']['loop_count'] > 5:
            recommendations.append("Review loops for potential performance issues")
        
        if len(report['warnings']) > 0:
            recommendations.append("Review warnings before execution")
        
        return recommendations
    
    def validate_script_syntax(self, script_content: str) -> Tuple[bool, List[str]]:
        """
        Validate Lua script syntax (basic check).
        
        Args:
            script_content: The script to validate
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check for basic Lua syntax patterns
        lines = script_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('--'):
                continue
            
            # Check for unmatched keywords
            if line.startswith('if') and not 'then' in line:
                errors.append(f"Line {i}: 'if' statement missing 'then'")
            
            if line.startswith('function') and not '(' in line:
                errors.append(f"Line {i}: 'function' declaration missing parentheses")
            
            if line.startswith('for') and not 'do' in line:
                errors.append(f"Line {i}: 'for' loop missing 'do'")
            
            if line.startswith('while') and not 'do' in line:
                errors.append(f"Line {i}: 'while' loop missing 'do'")
        
        # Check for balanced keywords
        if_count = script_content.lower().count('if')
        then_count = script_content.lower().count('then')
        if if_count != then_count:
            errors.append(f"Unmatched 'if'/'then' statements: {if_count} if, {then_count} then")
        
        function_count = script_content.lower().count('function')
        end_count = script_content.lower().count('end')
        if function_count != end_count:
            errors.append(f"Unmatched 'function'/'end' statements: {function_count} function, {end_count} end")
        
        return len(errors) == 0, errors
    
    def get_script_complexity_score(self, script_content: str) -> Dict[str, Any]:
        """
        Calculate script complexity score.
        
        Args:
            script_content: The script to analyze
            
        Returns:
            Complexity analysis
        """
        complexity = {
            'cyclomatic_complexity': 0,
            'nesting_depth': 0,
            'function_complexity': 0,
            'overall_score': 0
        }
        
        try:
            # Calculate cyclomatic complexity
            decision_points = len(re.findall(r'\bif\b|\belseif\b|\bwhile\b|\bfor\b|\band\b|\bor\b', script_content, re.IGNORECASE))
            complexity['cyclomatic_complexity'] = decision_points + 1
            
            # Calculate nesting depth
            lines = script_content.split('\n')
            max_depth = 0
            current_depth = 0
            
            for line in lines:
                line = line.strip()
                if line.startswith('if') or line.startswith('for') or line.startswith('while') or line.startswith('function'):
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
                elif line.startswith('end'):
                    current_depth = max(0, current_depth - 1)
            
            complexity['nesting_depth'] = max_depth
            
            # Calculate function complexity
            function_count = len(re.findall(r'function\s+\w+', script_content, re.IGNORECASE))
            complexity['function_complexity'] = function_count
            
            # Calculate overall score (lower is better)
            complexity['overall_score'] = (
                complexity['cyclomatic_complexity'] * 2 +
                complexity['nesting_depth'] * 3 +
                complexity['function_complexity'] * 1
            )
            
        except Exception as e:
            self.logger.log_error(f"Complexity calculation failed: {str(e)}")
        
        return complexity