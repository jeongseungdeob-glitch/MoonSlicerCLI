#!/usr/bin/env python3
"""
CIA Roblox Executor - File Manager
Handles file I/O operations and project path management.
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from utils.config import Config
from executor.logger import ExecutionLogger


class FileManager:
    """
    Manages file operations for the CIA Roblox Executor.
    Handles script saving, loading, and project organization.
    """
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        
        # Get paths from configuration
        paths_config = self.config.get_paths_config()
        self.logs_dir = Path(paths_config.get('logs_dir', 'logs'))
        self.scripts_dir = Path(paths_config.get('scripts_dir', 'sandboxed_scripts'))
        self.backup_dir = Path(paths_config.get('backup_dir', 'backups'))
        self.temp_dir = Path(paths_config.get('temp_dir', 'temp'))
        
        # Create directories if they don't exist
        self._create_directories()
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [self.logs_dir, self.scripts_dir, self.backup_dir, self.temp_dir]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def save_generated_script(self, script_name: str, script_content: str,
                            metadata: Dict[str, Any] = None) -> str:
        """
        Save a generated script to the scripts directory.
        
        Args:
            script_name: Name of the script file
            script_content: The script content
            metadata: Additional metadata about the script
            
        Returns:
            Path to the saved script
        """
        try:
            # Ensure script name has .lua extension
            if not script_name.endswith('.lua'):
                script_name += '.lua'
            
            # Create full path
            script_path = self.scripts_dir / script_name
            
            # Add metadata header if provided
            if metadata:
                header = self._create_metadata_header(metadata)
                full_content = header + '\n\n' + script_content
            else:
                full_content = script_content
            
            # Save the script
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            # Log the save operation
            self.logger.log_execution(
                f"Script saved: {script_path}",
                script_name=script_name,
                metadata={
                    'file_size': len(full_content),
                    'metadata': metadata
                }
            )
            
            return str(script_path)
            
        except Exception as e:
            self.logger.log_error(
                f"Failed to save script {script_name}: {str(e)}",
                error_type="file_save_error"
            )
            raise
    
    def load_script(self, script_path: str) -> Tuple[str, Dict[str, Any]]:
        """
        Load a script from file.
        
        Args:
            script_path: Path to the script file
            
        Returns:
            Tuple of (script_content, metadata)
        """
        try:
            script_path = Path(script_path)
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script file not found: {script_path}")
            
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract metadata if present
            metadata = self._extract_metadata(content)
            
            # Remove metadata header from content
            if metadata:
                content = self._remove_metadata_header(content)
            
            self.logger.log_execution(
                f"Script loaded: {script_path}",
                script_name=script_path.name,
                metadata={'file_size': len(content)}
            )
            
            return content, metadata
            
        except Exception as e:
            self.logger.log_error(
                f"Failed to load script {script_path}: {str(e)}",
                error_type="file_load_error"
            )
            raise
    
    def list_scripts(self, directory: str = None) -> List[Dict[str, Any]]:
        """
        List all scripts in the scripts directory.
        
        Args:
            directory: Optional subdirectory to list
            
        Returns:
            List of script information
        """
        try:
            if directory:
                target_dir = self.scripts_dir / directory
            else:
                target_dir = self.scripts_dir
            
            if not target_dir.exists():
                return []
            
            scripts = []
            for script_file in target_dir.glob('*.lua'):
                try:
                    stat = script_file.stat()
                    scripts.append({
                        'name': script_file.name,
                        'path': str(script_file),
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
                except Exception as e:
                    self.logger.log_warning(f"Failed to get info for {script_file}: {str(e)}")
            
            return sorted(scripts, key=lambda x: x['modified'], reverse=True)
            
        except Exception as e:
            self.logger.log_error(f"Failed to list scripts: {str(e)}")
            return []
    
    def delete_script(self, script_name: str) -> bool:
        """
        Delete a script file.
        
        Args:
            script_name: Name of the script to delete
            
        Returns:
            True if deletion was successful
        """
        try:
            script_path = self.scripts_dir / script_name
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_name}")
            
            # Create backup before deletion
            backup_path = self.backup_dir / f"{script_name}.backup"
            shutil.copy2(script_path, backup_path)
            
            # Delete the original file
            script_path.unlink()
            
            self.logger.log_execution(
                f"Script deleted: {script_name}",
                metadata={'backup_created': str(backup_path)}
            )
            
            return True
            
        except Exception as e:
            self.logger.log_error(
                f"Failed to delete script {script_name}: {str(e)}",
                error_type="file_delete_error"
            )
            return False
    
    def backup_script(self, script_name: str, backup_name: str = None) -> str:
        """
        Create a backup of a script.
        
        Args:
            script_name: Name of the script to backup
            backup_name: Optional custom backup name
            
        Returns:
            Path to the backup file
        """
        try:
            script_path = self.scripts_dir / script_name
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_name}")
            
            if backup_name is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_name = f"{script_name}.{timestamp}.backup"
            
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(script_path, backup_path)
            
            self.logger.log_execution(
                f"Script backed up: {script_name} -> {backup_name}",
                metadata={'backup_path': str(backup_path)}
            )
            
            return str(backup_path)
            
        except Exception as e:
            self.logger.log_error(
                f"Failed to backup script {script_name}: {str(e)}",
                error_type="backup_error"
            )
            raise
    
    def restore_script(self, backup_name: str, target_name: str = None) -> str:
        """
        Restore a script from backup.
        
        Args:
            backup_name: Name of the backup file
            target_name: Optional target name for restoration
            
        Returns:
            Path to the restored script
        """
        try:
            backup_path = self.backup_dir / backup_name
            
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup not found: {backup_name}")
            
            if target_name is None:
                # Extract original name from backup
                if backup_name.endswith('.backup'):
                    target_name = backup_name[:-7]  # Remove .backup
                else:
                    target_name = backup_name
            
            target_path = self.scripts_dir / target_name
            
            shutil.copy2(backup_path, target_path)
            
            self.logger.log_execution(
                f"Script restored: {backup_name} -> {target_name}",
                metadata={'restored_path': str(target_path)}
            )
            
            return str(target_path)
            
        except Exception as e:
            self.logger.log_error(
                f"Failed to restore script {backup_name}: {str(e)}",
                error_type="restore_error"
            )
            raise
    
    def get_script_info(self, script_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a script.
        
        Args:
            script_name: Name of the script
            
        Returns:
            Script information dictionary
        """
        try:
            script_path = self.scripts_dir / script_name
            
            if not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_name}")
            
            stat = script_path.stat()
            
            # Read content to extract metadata
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata = self._extract_metadata(content)
            
            # Calculate checksum
            checksum = hashlib.md5(content.encode()).hexdigest()
            
            info = {
                'name': script_path.name,
                'path': str(script_path),
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'checksum': checksum,
                'line_count': len(content.split('\n')),
                'metadata': metadata
            }
            
            return info
            
        except Exception as e:
            self.logger.log_error(
                f"Failed to get script info for {script_name}: {str(e)}",
                error_type="file_info_error"
            )
            raise
    
    def search_scripts(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for scripts by content or name.
        
        Args:
            query: Search query
            
        Returns:
            List of matching scripts
        """
        try:
            results = []
            query_lower = query.lower()
            
            for script_file in self.scripts_dir.glob('*.lua'):
                try:
                    # Check filename
                    if query_lower in script_file.name.lower():
                        results.append({
                            'name': script_file.name,
                            'path': str(script_file),
                            'match_type': 'filename',
                            'match_line': None
                        })
                        continue
                    
                    # Check content
                    with open(script_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if query_lower in content.lower():
                        # Find matching line
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if query_lower in line.lower():
                                results.append({
                                    'name': script_file.name,
                                    'path': str(script_file),
                                    'match_type': 'content',
                                    'match_line': i,
                                    'match_text': line.strip()
                                })
                                break
                
                except Exception as e:
                    self.logger.log_warning(f"Failed to search {script_file}: {str(e)}")
            
            return results
            
        except Exception as e:
            self.logger.log_error(f"Failed to search scripts: {str(e)}")
            return []
    
    def _create_metadata_header(self, metadata: Dict[str, Any]) -> str:
        """Create metadata header for script files"""
        header_lines = [
            "-- CIA Roblox Executor - Script Metadata",
            f"-- Generated: {datetime.now().isoformat()}",
            f"-- File Manager: {self.__class__.__name__}",
            "--",
        ]
        
        for key, value in metadata.items():
            if isinstance(value, (dict, list)):
                header_lines.append(f"-- {key}: {json.dumps(value)}")
            else:
                header_lines.append(f"-- {key}: {value}")
        
        header_lines.append("-- End Metadata")
        return '\n'.join(header_lines)
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from script content"""
        metadata = {}
        
        lines = content.split('\n')
        in_metadata = False
        
        for line in lines:
            line = line.strip()
            
            if line == "-- CIA Roblox Executor - Script Metadata":
                in_metadata = True
                continue
            elif line == "-- End Metadata":
                break
            elif in_metadata and line.startswith("-- "):
                # Parse metadata line
                parts = line[3:].split(": ", 1)
                if len(parts) == 2:
                    key, value = parts
                    try:
                        # Try to parse JSON values
                        metadata[key] = json.loads(value)
                    except json.JSONDecodeError:
                        metadata[key] = value
        
        return metadata
    
    def _remove_metadata_header(self, content: str) -> str:
        """Remove metadata header from script content"""
        lines = content.split('\n')
        start_idx = -1
        end_idx = -1
        
        for i, line in enumerate(lines):
            if line.strip() == "-- CIA Roblox Executor - Script Metadata":
                start_idx = i
            elif line.strip() == "-- End Metadata":
                end_idx = i
                break
        
        if start_idx != -1 and end_idx != -1:
            return '\n'.join(lines[end_idx + 1:])
        
        return content
    
    def cleanup_temp_files(self) -> int:
        """
        Clean up temporary files.
        
        Returns:
            Number of files cleaned up
        """
        try:
            cleaned_count = 0
            
            for temp_file in self.temp_dir.glob('*'):
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                        cleaned_count += 1
                    elif temp_file.is_dir():
                        shutil.rmtree(temp_file)
                        cleaned_count += 1
                except Exception as e:
                    self.logger.log_warning(f"Failed to clean up {temp_file}: {str(e)}")
            
            self.logger.log_execution(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            self.logger.log_error(f"Failed to cleanup temp files: {str(e)}")
            return 0
    
    def get_directory_stats(self) -> Dict[str, Any]:
        """Get statistics about the project directories"""
        stats = {}
        
        for dir_name, dir_path in [
            ('scripts', self.scripts_dir),
            ('logs', self.logs_dir),
            ('backups', self.backup_dir),
            ('temp', self.temp_dir)
        ]:
            try:
                if dir_path.exists():
                    file_count = len(list(dir_path.glob('*')))
                    total_size = sum(f.stat().st_size for f in dir_path.glob('*') if f.is_file())
                    stats[dir_name] = {
                        'file_count': file_count,
                        'total_size': total_size,
                        'total_size_mb': total_size / (1024 * 1024),
                        'exists': True
                    }
                else:
                    stats[dir_name] = {
                        'file_count': 0,
                        'total_size': 0,
                        'total_size_mb': 0,
                        'exists': False
                    }
            except Exception as e:
                stats[dir_name] = {
                    'error': str(e),
                    'exists': False
                }
        
        return stats