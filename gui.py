#!/usr/bin/env python3
"""
CIA Roblox Executor - Main GUI Application
A secure, AI-powered Roblox script executor for internal use only.
"""

import sys
import os
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QFileDialog, QProgressBar,
    QTabWidget, QGroupBox, QSplitter, QMessageBox, QComboBox,
    QLineEdit, QCheckBox, QSpinBox, QTextBrowser
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon

# Import our modules
from executor.core import ExecutorCore
from executor.sandbox import SandboxManager
from executor.logger import ExecutionLogger
from ai_module.ai_interface import AIInterface
from ai_module.script_builder import ScriptBuilder
from ai_module.validation import ScriptValidator
from utils.config import Config
from utils.file_manager import FileManager


class AIWorkerThread(QThread):
    """Background thread for AI operations"""
    script_generated = pyqtSignal(str, str)  # script_name, script_content
    error_occurred = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, ai_interface: AIInterface, prompt: str):
        super().__init__()
        self.ai_interface = ai_interface
        self.prompt = prompt

    def run(self):
        try:
            self.progress_updated.emit(10)
            # Generate script using AI
            ai_response = self.ai_interface.generate_roblox_script(self.prompt)
            self.progress_updated.emit(50)
            
            # Build and validate script
            script_builder = ScriptBuilder()
            script_content = script_builder.build_script(ai_response)
            self.progress_updated.emit(80)
            
            # Validate script
            validator = ScriptValidator()
            if validator.validate_script(script_content):
                script_name = f"ai_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.lua"
                self.script_generated.emit(script_name, script_content)
            else:
                self.error_occurred.emit("Generated script failed validation checks")
            
            self.progress_updated.emit(100)
        except Exception as e:
            self.error_occurred.emit(f"AI generation failed: {str(e)}")


class ExecutionWorkerThread(QThread):
    """Background thread for script execution"""
    execution_completed = pyqtSignal(str, bool)  # result, success
    log_updated = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, executor: ExecutorCore, script_content: str):
        super().__init__()
        self.executor = executor
        self.script_content = script_content

    def run(self):
        try:
            self.progress_updated.emit(10)
            self.log_updated.emit("Initializing sandbox environment...")
            
            # Execute script in sandbox
            result = self.executor.execute_script(self.script_content)
            self.progress_updated.emit(100)
            
            self.execution_completed.emit(result, True)
        except Exception as e:
            self.execution_completed.emit(f"Execution failed: {str(e)}", False)


class CIAExecutorGUI(QMainWindow):
    """Main GUI window for the CIA Roblox Executor"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.file_manager = FileManager()
        self.logger = ExecutionLogger()
        self.ai_interface = AIInterface()
        self.executor = ExecutorCore()
        self.sandbox = SandboxManager()
        
        self.init_ui()
        self.setup_dark_theme()
        self.setup_connections()
        
        # Start log monitoring
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self.update_log_display)
        self.log_timer.start(1000)  # Update every second

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CIA Roblox Executor v1.0 - Internal Use Only")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Script management and AI
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Execution and logs
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # Set splitter proportions
        splitter.setSizes([600, 800])

    def create_left_panel(self):
        """Create the left panel with script management and AI features"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # AI Script Generation Group
        ai_group = QGroupBox("🤖 AI Script Generation")
        ai_layout = QVBoxLayout(ai_group)
        
        # AI Prompt input
        self.ai_prompt_input = QTextEdit()
        self.ai_prompt_input.setPlaceholderText("Describe the Roblox script you want to generate...\nExample: 'Create a script that teleports players to a specific location'")
        self.ai_prompt_input.setMaximumHeight(100)
        ai_layout.addWidget(QLabel("AI Prompt:"))
        ai_layout.addWidget(self.ai_prompt_input)
        
        # AI Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("AI Model:"))
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItems(["mistral", "deepseek", "starcoder2"])
        model_layout.addWidget(self.ai_model_combo)
        ai_layout.addLayout(model_layout)
        
        # Generate button and progress
        self.generate_btn = QPushButton("🚀 Generate Script")
        self.generate_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; }")
        ai_layout.addWidget(self.generate_btn)
        
        self.ai_progress = QProgressBar()
        self.ai_progress.setVisible(False)
        ai_layout.addWidget(self.ai_progress)
        
        layout.addWidget(ai_group)
        
        # Script Management Group
        script_group = QGroupBox("📜 Script Management")
        script_layout = QVBoxLayout(script_group)
        
        # Script selection
        script_buttons_layout = QHBoxLayout()
        self.load_script_btn = QPushButton("📁 Load Script")
        self.save_script_btn = QPushButton("💾 Save Script")
        script_buttons_layout.addWidget(self.load_script_btn)
        script_buttons_layout.addWidget(self.save_script_btn)
        script_layout.addLayout(script_buttons_layout)
        
        # Script editor
        self.script_editor = QTextEdit()
        self.script_editor.setPlaceholderText("Enter or paste your Roblox Lua script here...")
        script_layout.addWidget(QLabel("Script Editor:"))
        script_layout.addWidget(self.script_editor)
        
        layout.addWidget(script_group)
        
        # Execution Controls Group
        exec_group = QGroupBox("⚡ Execution Controls")
        exec_layout = QVBoxLayout(exec_group)
        
        # Execution options
        options_layout = QHBoxLayout()
        self.sandbox_checkbox = QCheckBox("Sandbox Mode")
        self.sandbox_checkbox.setChecked(True)
        self.bypass_checkbox = QCheckBox("Anti-Cheat Bypass")
        self.bypass_checkbox.setChecked(True)
        options_layout.addWidget(self.sandbox_checkbox)
        options_layout.addWidget(self.bypass_checkbox)
        exec_layout.addLayout(options_layout)
        
        # Execute button
        self.execute_btn = QPushButton("▶ Execute Script")
        self.execute_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 10px; }")
        exec_layout.addWidget(self.execute_btn)
        
        self.exec_progress = QProgressBar()
        self.exec_progress.setVisible(False)
        exec_layout.addWidget(self.exec_progress)
        
        layout.addWidget(exec_group)
        
        layout.addStretch()
        return panel

    def create_right_panel(self):
        """Create the right panel with execution logs and monitoring"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Execution Logs Tab
        logs_tab = QWidget()
        logs_layout = QVBoxLayout(logs_tab)
        
        self.log_display = QTextBrowser()
        self.log_display.setFont(QFont("Consolas", 10))
        logs_layout.addWidget(self.log_display)
        
        # Log controls
        log_controls = QHBoxLayout()
        self.clear_logs_btn = QPushButton("🗑 Clear Logs")
        self.export_logs_btn = QPushButton("📤 Export Logs")
        log_controls.addWidget(self.clear_logs_btn)
        log_controls.addWidget(self.export_logs_btn)
        logs_layout.addLayout(log_controls)
        
        tab_widget.addTab(logs_tab, "📋 Execution Logs")
        
        # AI History Tab
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)
        
        self.ai_history = QTextBrowser()
        ai_layout.addWidget(self.ai_history)
        
        tab_widget.addTab(ai_tab, "🤖 AI History")
        
        # System Status Tab
        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)
        
        self.status_display = QTextBrowser()
        status_layout.addWidget(self.status_display)
        
        tab_widget.addTab(status_tab, "⚙ System Status")
        
        layout.addWidget(tab_widget)
        
        # Status bar
        self.status_bar = QLabel("Ready - CIA Roblox Executor v1.0")
        self.status_bar.setStyleSheet("QLabel { background-color: #2b2b2b; color: #00ff00; padding: 5px; }")
        layout.addWidget(self.status_bar)
        
        return panel

    def setup_dark_theme(self):
        """Apply dark theme to the application"""
        palette = QPalette()
        
        # Set dark colors
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
        
        # Set stylesheet for additional styling
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QTextEdit, QTextBrowser {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 3px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #303030;
            }
        """)

    def setup_connections(self):
        """Setup signal connections"""
        self.generate_btn.clicked.connect(self.generate_ai_script)
        self.execute_btn.clicked.connect(self.execute_script)
        self.load_script_btn.clicked.connect(self.load_script)
        self.save_script_btn.clicked.connect(self.save_script)
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.export_logs_btn.clicked.connect(self.export_logs)

    def generate_ai_script(self):
        """Generate script using AI"""
        prompt = self.ai_prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt for AI script generation.")
            return
        
        # Disable button and show progress
        self.generate_btn.setEnabled(False)
        self.ai_progress.setVisible(True)
        self.ai_progress.setValue(0)
        
        # Start AI worker thread
        self.ai_worker = AIWorkerThread(self.ai_interface, prompt)
        self.ai_worker.script_generated.connect(self.on_script_generated)
        self.ai_worker.error_occurred.connect(self.on_ai_error)
        self.ai_worker.progress_updated.connect(self.ai_progress.setValue)
        self.ai_worker.start()

    def on_script_generated(self, script_name: str, script_content: str):
        """Handle AI-generated script"""
        self.script_editor.setPlainText(script_content)
        self.ai_progress.setVisible(False)
        self.generate_btn.setEnabled(True)
        
        # Save generated script
        try:
            self.file_manager.save_generated_script(script_name, script_content)
            self.log_message(f"AI script generated and saved: {script_name}")
        except Exception as e:
            self.log_message(f"Error saving generated script: {str(e)}")

    def on_ai_error(self, error_msg: str):
        """Handle AI generation errors"""
        self.ai_progress.setVisible(False)
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "AI Error", error_msg)
        self.log_message(f"AI Error: {error_msg}")

    def execute_script(self):
        """Execute the current script"""
        script_content = self.script_editor.toPlainText().strip()
        if not script_content:
            QMessageBox.warning(self, "Warning", "Please enter a script to execute.")
            return
        
        # Disable button and show progress
        self.execute_btn.setEnabled(False)
        self.exec_progress.setVisible(True)
        self.exec_progress.setValue(0)
        
        # Configure execution options
        self.executor.set_sandbox_mode(self.sandbox_checkbox.isChecked())
        self.executor.set_bypass_mode(self.bypass_checkbox.isChecked())
        
        # Start execution worker thread
        self.exec_worker = ExecutionWorkerThread(self.executor, script_content)
        self.exec_worker.execution_completed.connect(self.on_execution_completed)
        self.exec_worker.log_updated.connect(self.log_message)
        self.exec_worker.progress_updated.connect(self.exec_progress.setValue)
        self.exec_worker.start()

    def on_execution_completed(self, result: str, success: bool):
        """Handle script execution completion"""
        self.exec_progress.setVisible(False)
        self.execute_btn.setEnabled(True)
        
        if success:
            self.log_message(f"Execution completed successfully: {result}")
            QMessageBox.information(self, "Success", "Script executed successfully!")
        else:
            self.log_message(f"Execution failed: {result}")
            QMessageBox.critical(self, "Execution Error", result)

    def load_script(self):
        """Load script from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Script", "", "Lua Files (*.lua);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.script_editor.setPlainText(content)
                self.log_message(f"Script loaded: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load script: {str(e)}")

    def save_script(self):
        """Save current script to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Script", "", "Lua Files (*.lua);;All Files (*)"
        )
        if file_path:
            try:
                content = self.script_editor.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log_message(f"Script saved: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save script: {str(e)}")

    def clear_logs(self):
        """Clear log display"""
        self.log_display.clear()
        self.log_message("Logs cleared")

    def export_logs(self):
        """Export logs to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Logs", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_display.toPlainText())
                self.log_message(f"Logs exported: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs: {str(e)}")

    def log_message(self, message: str):
        """Add message to log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.log_display.append(formatted_message)
        
        # Also log to file
        self.logger.log_execution(formatted_message)

    def update_log_display(self):
        """Update log display with latest logs"""
        # This would typically read from the logger's file
        pass

    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(
            self, 'Exit', 'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_message("Application shutting down...")
            event.accept()
        else:
            event.ignore()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("CIA Roblox Executor")
    app.setApplicationVersion("1.0")
    
    # Set application icon (if available)
    # app.setWindowIcon(QIcon("icon.png"))
    
    window = CIAExecutorGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()