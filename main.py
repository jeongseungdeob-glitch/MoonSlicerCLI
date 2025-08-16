#!/usr/bin/env python3
"""
CIA Roblox Executor - CLI Entry Point
Command-line interface for the CIA Roblox executor.
"""

import sys
import argparse
import asyncio
from pathlib import Path
from typing import Optional

from executor.core import ExecutorCore
from executor.logger import ExecutionLogger
from ai_module.ai_interface import AIInterface
from ai_module.script_builder import ScriptBuilder
from ai_module.validation import ScriptValidator
from utils.config import Config
from utils.file_manager import FileManager


class CIAExecutorCLI:
    """Command-line interface for the CIA Roblox Executor"""
    
    def __init__(self):
        self.config = Config()
        self.logger = ExecutionLogger()
        self.executor = ExecutorCore()
        self.ai_interface = AIInterface()
        self.script_builder = ScriptBuilder()
        self.validator = ScriptValidator()
        self.file_manager = FileManager()
    
    def run(self, args):
        """Run the CLI with parsed arguments"""
        try:
            if args.generate:
                self.generate_script(args)
            elif args.execute:
                self.execute_script(args)
            elif args.validate:
                self.validate_script(args)
            elif args.log:
                self.show_logs(args)
            elif args.list:
                self.list_scripts(args)
            elif args.info:
                self.show_info(args)
            else:
                print("No action specified. Use --help for usage information.")
                
        except Exception as e:
            self.logger.log_error(f"CLI operation failed: {str(e)}")
            print(f"Error: {str(e)}")
            sys.exit(1)
    
    def generate_script(self, args):
        """Generate a script using AI"""
        print("🤖 Generating Roblox script with AI...")
        
        # Get prompt from arguments or input
        if args.prompt:
            prompt = args.prompt
        else:
            prompt = input("Enter your script request: ")
        
        if not prompt.strip():
            print("Error: No prompt provided")
            return
        
        try:
            # Generate script
            ai_response = self.ai_interface.generate_roblox_script(
                prompt, 
                model=args.model,
                prompt_type=args.prompt_type
            )
            
            # Build script
            script_content = self.script_builder.build_script(
                ai_response,
                script_type=args.script_type
            )
            
            # Validate script
            if not self.validator.validate_script(script_content):
                print("⚠️  Warning: Generated script failed validation")
                if not args.force:
                    print("Use --force to execute anyway")
                    return
            
            # Save script
            script_name = args.output or f"ai_generated_{self._generate_timestamp()}.lua"
            script_path = self.file_manager.save_generated_script(script_name, script_content)
            
            print(f"✅ Script generated successfully: {script_path}")
            
            if args.execute:
                print("🚀 Executing generated script...")
                self._execute_script_content(script_content, script_name)
            
        except Exception as e:
            print(f"❌ Script generation failed: {str(e)}")
            raise
    
    def execute_script(self, args):
        """Execute a script"""
        script_path = args.script
        
        if not Path(script_path).exists():
            print(f"Error: Script file not found: {script_path}")
            return
        
        try:
            # Load script
            script_content, metadata = self.file_manager.load_script(script_path)
            
            print(f"🚀 Executing script: {script_path}")
            
            # Execute script
            self._execute_script_content(script_content, Path(script_path).name)
            
        except Exception as e:
            print(f"❌ Script execution failed: {str(e)}")
            raise
    
    def validate_script(self, args):
        """Validate a script"""
        script_path = args.script
        
        if not Path(script_path).exists():
            print(f"Error: Script file not found: {script_path}")
            return
        
        try:
            # Load script
            script_content, metadata = self.file_manager.load_script(script_path)
            
            print(f"🔍 Validating script: {script_path}")
            
            # Validate script
            is_valid = self.validator.validate_script(script_content)
            
            if is_valid:
                print("✅ Script validation passed")
            else:
                print("❌ Script validation failed")
            
            # Show detailed report
            if args.detailed:
                report = self.validator.get_validation_report(script_content)
                self._print_validation_report(report)
            
        except Exception as e:
            print(f"❌ Script validation failed: {str(e)}")
            raise
    
    def show_logs(self, args):
        """Show execution logs"""
        try:
            if args.log_type == "execution":
                logs = self.logger.get_execution_logs(limit=args.limit)
            elif args.log_type == "ai":
                logs = self.logger.get_ai_logs(limit=args.limit)
            elif args.log_type == "error":
                logs = self.logger.get_error_logs(limit=args.limit)
            elif args.log_type == "audit":
                logs = self.logger.get_audit_logs(limit=args.limit)
            else:
                print(f"Unknown log type: {args.log_type}")
                return
            
            if not logs:
                print("No logs found")
                return
            
            print(f"📋 Showing {len(logs)} {args.log_type} logs:")
            print("-" * 80)
            
            for log in logs:
                timestamp = log.get('timestamp', 'Unknown')
                message = log.get('message', log.get('error_message', 'No message'))
                print(f"[{timestamp}] {message}")
            
        except Exception as e:
            print(f"❌ Failed to show logs: {str(e)}")
            raise
    
    def list_scripts(self, args):
        """List available scripts"""
        try:
            scripts = self.file_manager.list_scripts()
            
            if not scripts:
                print("No scripts found")
                return
            
            print(f"📜 Found {len(scripts)} scripts:")
            print("-" * 80)
            
            for script in scripts:
                size = self._format_file_size(script['size'])
                modified = script['modified'][:19]  # Truncate timestamp
                print(f"{script['name']:<30} {size:>10} {modified}")
            
        except Exception as e:
            print(f"❌ Failed to list scripts: {str(e)}")
            raise
    
    def show_info(self, args):
        """Show system information"""
        try:
            # Configuration info
            config_summary = self.config.get_config_summary()
            print("⚙️  Configuration:")
            print(f"  Executor: {config_summary['executor_name']} v{config_summary['version']}")
            print(f"  Default AI Model: {config_summary['default_ai_model']}")
            print(f"  Security Level: {config_summary['security_level']}")
            print(f"  GUI Theme: {config_summary['gui_theme']}")
            print(f"  Max Execution Time: {config_summary['max_execution_time']}s")
            print(f"  Sandbox Mode: {'Enabled' if config_summary['enable_sandbox'] else 'Disabled'}")
            print(f"  Bypass Mode: {'Enabled' if config_summary['enable_bypass'] else 'Disabled'}")
            
            # Directory stats
            dir_stats = self.file_manager.get_directory_stats()
            print("\n📁 Directory Statistics:")
            for dir_name, stats in dir_stats.items():
                if stats.get('exists'):
                    print(f"  {dir_name}: {stats['file_count']} files, {stats['total_size_mb']:.1f} MB")
                else:
                    print(f"  {dir_name}: Not found")
            
            # Execution stats
            exec_stats = self.executor.get_execution_stats()
            print("\n📊 Execution Statistics:")
            print(f"  Total Executions: {exec_stats['total_executions']}")
            print(f"  Successful: {exec_stats['successful_executions']}")
            print(f"  Failed: {exec_stats['failed_executions']}")
            print(f"  Total Time: {exec_stats['total_execution_time']:.2f}s")
            
            # AI stats
            ai_stats = self.ai_interface.get_generation_statistics()
            print("\n🤖 AI Statistics:")
            print(f"  Total Generations: {ai_stats['total_generations']}")
            print(f"  Average Time: {ai_stats['average_generation_time']:.2f}s")
            print(f"  Model Usage: {ai_stats['model_usage']}")
            
        except Exception as e:
            print(f"❌ Failed to show info: {str(e)}")
            raise
    
    def _execute_script_content(self, script_content: str, script_name: str):
        """Execute script content"""
        try:
            # Configure executor
            self.executor.set_sandbox_mode(True)
            self.executor.set_bypass_mode(True)
            
            # Execute script
            result = self.executor.execute_script(script_content, script_name)
            
            print(f"✅ Execution completed: {result}")
            
        except Exception as e:
            print(f"❌ Execution failed: {str(e)}")
            raise
    
    def _print_validation_report(self, report: dict):
        """Print validation report"""
        print("\n📋 Validation Report:")
        print(f"  Security Score: {report['security_score']}/100")
        print(f"  Validation Passed: {'Yes' if report['validation_passed'] else 'No'}")
        
        if report['issues']:
            print("\n❌ Issues:")
            for issue in report['issues']:
                print(f"  - {issue}")
        
        if report['warnings']:
            print("\n⚠️  Warnings:")
            for warning in report['warnings']:
                print(f"  - {warning}")
        
        if report['recommendations']:
            print("\n💡 Recommendations:")
            for rec in report['recommendations']:
                print(f"  - {rec}")
    
    def _generate_timestamp(self) -> str:
        """Generate timestamp string"""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CIA Roblox Executor - Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --generate --prompt "Create a script that prints hello world"
  %(prog)s --execute script.lua
  %(prog)s --validate script.lua --detailed
  %(prog)s --log --log-type execution --limit 10
  %(prog)s --list
  %(prog)s --info
        """
    )
    
    # Action arguments
    action_group = parser.add_mutually_exclusive_group(required=False)
    action_group.add_argument('--generate', action='store_true',
                             help='Generate a script using AI')
    action_group.add_argument('--execute', action='store_true',
                             help='Execute a script')
    action_group.add_argument('--validate', action='store_true',
                             help='Validate a script')
    action_group.add_argument('--log', action='store_true',
                             help='Show logs')
    action_group.add_argument('--list', action='store_true',
                             help='List available scripts')
    action_group.add_argument('--info', action='store_true',
                             help='Show system information')
    
    # Generate arguments
    parser.add_argument('--prompt', type=str,
                       help='AI prompt for script generation')
    parser.add_argument('--model', type=str, choices=['mistral', 'deepseek', 'starcoder2'],
                       help='AI model to use for generation')
    parser.add_argument('--prompt-type', type=str, 
                       choices=['basic', 'advanced', 'security', 'game_specific'],
                       default='basic',
                       help='Type of prompt template to use')
    parser.add_argument('--script-type', type=str,
                       choices=['basic', 'game_script', 'utility', 'test'],
                       default='basic',
                       help='Type of script to generate')
    parser.add_argument('--output', type=str,
                       help='Output filename for generated script')
    parser.add_argument('--force', action='store_true',
                       help='Force execution even if validation fails')
    
    # Execute arguments
    parser.add_argument('--script', type=str,
                       help='Script file to execute or validate')
    
    # Log arguments
    parser.add_argument('--log-type', type=str,
                       choices=['execution', 'ai', 'error', 'audit'],
                       default='execution',
                       help='Type of logs to show')
    parser.add_argument('--limit', type=int, default=50,
                       help='Maximum number of log entries to show')
    parser.add_argument('--detailed', action='store_true',
                       help='Show detailed validation report')
    
    args = parser.parse_args()
    
    # Create CLI instance and run
    cli = CIAExecutorCLI()
    cli.run(args)


if __name__ == "__main__":
    main()