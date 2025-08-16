#!/usr/bin/env python3
"""
CIA Roblox Executor - Helper Functions
Miscellaneous utility functions for the executor.
"""

import os
import sys
import time
import hashlib
import random
import string
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from pathlib import Path


def generate_unique_id(prefix: str = "script") -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Prefix for the ID
        
    Returns:
        Unique identifier string
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_suffix}"


def calculate_checksum(content: str, algorithm: str = "md5") -> str:
    """
    Calculate checksum of content.
    
    Args:
        content: Content to hash
        algorithm: Hash algorithm to use
        
    Returns:
        Hexadecimal checksum
    """
    if algorithm == "md5":
        return hashlib.md5(content.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(content.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(content.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.1f} ms"
    elif seconds < 60:
        return f"{seconds:.1f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe file system usage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"
    
    # Limit length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext
    
    return filename


def ensure_directory_exists(directory_path: Union[str, Path]) -> bool:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created successfully
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_extension(file_path: Union[str, Path]) -> str:
    """
    Get file extension from path.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (without dot)
    """
    return Path(file_path).suffix.lstrip('.')


def is_lua_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a Lua file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is a Lua file
    """
    return get_file_extension(file_path).lower() == 'lua'


def count_lines(content: str) -> int:
    """
    Count lines in content.
    
    Args:
        content: Content to count lines in
        
    Returns:
        Number of lines
    """
    return len(content.split('\n'))


def count_words(content: str) -> int:
    """
    Count words in content.
    
    Args:
        content: Content to count words in
        
    Returns:
        Number of words
    """
    return len(content.split())


def extract_code_blocks(content: str) -> List[str]:
    """
    Extract code blocks from markdown content.
    
    Args:
        content: Content containing code blocks
        
    Returns:
        List of code blocks
    """
    import re
    
    code_blocks = []
    pattern = r'```(?:lua)?\s*(.*?)\s*```'
    
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
    code_blocks.extend(matches)
    
    return code_blocks


def validate_lua_syntax_basic(content: str) -> Dict[str, Any]:
    """
    Basic Lua syntax validation.
    
    Args:
        content: Lua code to validate
        
    Returns:
        Validation result dictionary
    """
    result = {
        'valid': True,
        'errors': [],
        'warnings': [],
        'statistics': {}
    }
    
    lines = content.split('\n')
    
    # Basic statistics
    result['statistics'] = {
        'total_lines': len(lines),
        'non_empty_lines': len([line for line in lines if line.strip()]),
        'comment_lines': len([line for line in lines if line.strip().startswith('--')]),
        'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('--')])
    }
    
    # Check for balanced keywords
    if_count = content.lower().count('if')
    then_count = content.lower().count('then')
    if if_count != then_count:
        result['errors'].append(f"Unmatched if/then: {if_count} if, {then_count} then")
        result['valid'] = False
    
    function_count = content.lower().count('function')
    end_count = content.lower().count('end')
    if function_count != end_count:
        result['errors'].append(f"Unmatched function/end: {function_count} function, {end_count} end")
        result['valid'] = False
    
    # Check for balanced parentheses
    open_parens = content.count('(')
    close_parens = content.count(')')
    if open_parens != close_parens:
        result['warnings'].append(f"Unmatched parentheses: {open_parens} open, {close_parens} close")
    
    return result


def create_backup_filename(original_name: str, suffix: str = "backup") -> str:
    """
    Create a backup filename.
    
    Args:
        original_name: Original filename
        suffix: Backup suffix
        
    Returns:
        Backup filename
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    name, ext = os.path.splitext(original_name)
    return f"{name}.{timestamp}.{suffix}{ext}"


def get_system_info() -> Dict[str, Any]:
    """
    Get system information.
    
    Returns:
        System information dictionary
    """
    import platform
    import psutil
    
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.architecture()[0],
        'processor': platform.processor(),
        'python_version': sys.version,
        'memory_total': psutil.virtual_memory().total,
        'memory_available': psutil.virtual_memory().available,
        'cpu_count': psutil.cpu_count(),
        'disk_usage': psutil.disk_usage('/')._asdict() if os.path.exists('/') else {}
    }


def format_timestamp(timestamp: Union[datetime, str, float], 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format timestamp consistently.
    
    Args:
        timestamp: Timestamp to format
        format_str: Format string
        
    Returns:
        Formatted timestamp string
    """
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError:
            return timestamp
    
    if isinstance(timestamp, float):
        timestamp = datetime.fromtimestamp(timestamp)
    
    if isinstance(timestamp, datetime):
        return timestamp.strftime(format_str)
    
    return str(timestamp)


def parse_duration(duration_str: str) -> float:
    """
    Parse duration string to seconds.
    
    Args:
        duration_str: Duration string (e.g., "1h 30m 45s")
        
    Returns:
        Duration in seconds
    """
    total_seconds = 0
    
    # Parse hours
    if 'h' in duration_str:
        hours = float(duration_str.split('h')[0])
        total_seconds += hours * 3600
        duration_str = duration_str.split('h')[1]
    
    # Parse minutes
    if 'm' in duration_str:
        minutes = float(duration_str.split('m')[0])
        total_seconds += minutes * 60
        duration_str = duration_str.split('m')[1]
    
    # Parse seconds
    if 's' in duration_str:
        seconds = float(duration_str.split('s')[0])
        total_seconds += seconds
    
    return total_seconds


def create_progress_callback(total_items: int):
    """
    Create a progress callback function.
    
    Args:
        total_items: Total number of items
        
    Returns:
        Progress callback function
    """
    def progress_callback(current_item: int, message: str = ""):
        percentage = (current_item / total_items) * 100
        print(f"Progress: {percentage:.1f}% ({current_item}/{total_items}) {message}")
    
    return progress_callback


def retry_operation(operation, max_retries: int = 3, delay: float = 1.0):
    """
    Retry an operation with exponential backoff.
    
    Args:
        operation: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay between retries
        
    Returns:
        Operation result
        
    Raises:
        Exception: If all retries fail
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return operation()
        except Exception as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    raise last_exception


def validate_file_path(file_path: Union[str, Path]) -> bool:
    """
    Validate if a file path is safe and accessible.
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if path is valid
    """
    try:
        path = Path(file_path)
        
        # Check for path traversal attempts
        if '..' in str(path):
            return False
        
        # Check if path is absolute and within allowed directories
        if path.is_absolute():
            # Add your security checks here
            pass
        
        return True
    except Exception:
        return False


def get_memory_usage() -> Dict[str, int]:
    """
    Get current memory usage.
    
    Returns:
        Memory usage information
    """
    import psutil
    
    process = psutil.Process()
    memory_info = process.memory_info()
    
    return {
        'rss': memory_info.rss,  # Resident Set Size
        'vms': memory_info.vms,  # Virtual Memory Size
        'percent': process.memory_percent()
    }


def cleanup_old_files(directory: Union[str, Path], 
                     max_age_days: int = 30,
                     pattern: str = "*") -> int:
    """
    Clean up old files in a directory.
    
    Args:
        directory: Directory to clean
        max_age_days: Maximum age of files in days
        pattern: File pattern to match
        
    Returns:
        Number of files cleaned up
    """
    try:
        directory = Path(directory)
        if not directory.exists():
            return 0
        
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        cleaned_count = 0
        
        for file_path in directory.glob(pattern):
            if file_path.is_file():
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
        
        return cleaned_count
    except Exception:
        return 0


def create_temp_file(content: str = "", suffix: str = ".tmp") -> Path:
    """
    Create a temporary file with content.
    
    Args:
        content: Content to write to file
        suffix: File suffix
        
    Returns:
        Path to temporary file
    """
    import tempfile
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False)
    temp_file.write(content)
    temp_file.close()
    
    return Path(temp_file.name)


def read_file_safely(file_path: Union[str, Path], 
                    max_size: int = 10 * 1024 * 1024) -> Optional[str]:
    """
    Safely read a file with size limits.
    
    Args:
        file_path: Path to file
        max_size: Maximum file size in bytes
        
    Returns:
        File content or None if failed
    """
    try:
        file_path = Path(file_path)
        
        if not file_path.exists():
            return None
        
        if file_path.stat().st_size > max_size:
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return None