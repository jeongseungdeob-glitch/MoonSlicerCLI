#!/usr/bin/env python3
"""
CIA Roblox Executor - Desktop GUI
Main entry point for the desktop application with AI integration
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QFileDialog, QProgressBar,
    QTabWidget, QSplitter, QGroupBox, QLineEdit, QComboBox,
    QMessageBox, QStatusBar, QMenuBar, QMenu, QAction
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QTextCursor

from executor.core import ExecutorCore
from executor.logger import Logger
from ai_module.ai_interface import AIInterface
from ai_module.script_builder import ScriptBuilder
from ai_module.validation import ScriptValidator
from utils.config import Config
from utils.file_manager import FileManager


class AIWorker(QThread):
    """Background worker for AI script generation"""
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
            script_content = self.ai_interface.generate_roblox_script(self.prompt)
            self.progress_updated.emit(50)
            
            # Validate and build script
            validator = ScriptValidator()
            if validator.validate_script(script_content):
                builder = ScriptBuilder()
                final_script = builder.build_script(script_content)
                self.progress_updated.emit(90)
                
                script_name = f"ai_generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.lua"
                self.script_generated.emit(script_name, final_script)
            else:
                self.error_occurred.emit("Generated script failed validation")
            
            self.progress_updated.emit(100)
        except Exception as e:
            self.error_occurred.emit(f"AI generation failed: {str(e)}")


class ExecutorWorker(QThread):
    """Background worker for script execution"""
    execution_complete = pyqtSignal(str, bool)  # message, success
    log_updated = pyqtSignal(str)
    progress_updated = pyqtSignal(int)

    def __init__(self, executor: ExecutorCore, script_path: str):
        super().__init__()
        self.executor = executor
        self.script_path = script_path

    def run(self):
        try:
            self.progress_updated.emit(10)
            self.log_updated.emit("Loading script into sandbox...")
            
            # Execute script
            result = self.executor.execute_script(self.script_path)
            self.progress_updated.emit(100)
            
            if result.success:
                self.execution_complete.emit("Script executed successfully!", True)
            else:
                self.execution_complete.emit(f"Execution failed: {result.error}", False)
                
        except Exception as e:
            self.error_occurred.emit(f"Execution error: {str(e)}")


class CIAExecutorGUI(QMainWindow):
    """Main GUI window for CIA Roblox Executor"""
    
    def __init__(self):
        super().__init__()
        self.config = Config()
        self.file_manager = FileManager()
        self.logger = Logger()
        self.ai_interface = AIInterface()
        self.executor = ExecutorCore()
        
        self.current_script_path = None
        self.ai_worker = None
        self.executor_worker = None
        
        self.init_ui()
        self.setup_theme()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("CIA Roblox Executor v1.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
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
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
    def create_left_panel(self):
        """Create the left panel with script management and AI features"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Script Management Group
        script_group = QGroupBox("Script Management")
        script_layout = QVBoxLayout(script_group)
        
        # File selection
        file_layout = QHBoxLayout()
        self.script_path_label = QLabel("No script selected")
        self.script_path_label.setStyleSheet("color: #888; font-style: italic;")
        file_layout.addWidget(self.script_path_label)
        
        self.load_script_btn = QPushButton("Load Script")
        self.load_script_btn.clicked.connect(self.load_script)
        self.load_script_btn.setStyleSheet(self.get_button_style())
        file_layout.addWidget(self.load_script_btn)
        
        script_layout.addLayout(file_layout)
        
        # AI Script Generation Group
        ai_group = QGroupBox("AI Script Generation")
        ai_layout = QVBoxLayout(ai_group)
        
        # AI prompt input
        self.ai_prompt_input = QTextEdit()
        self.ai_prompt_input.setPlaceholderText("Describe the Roblox script you want to generate...")
        self.ai_prompt_input.setMaximumHeight(100)
        ai_layout.addWidget(self.ai_prompt_input)
        
        # AI model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("AI Model:"))
        self.ai_model_combo = QComboBox()
        self.ai_model_combo.addItems(["mistral", "deepseek", "starcoder2"])
        model_layout.addWidget(self.ai_model_combo)
        ai_layout.addLayout(model_layout)
        
        # Generate button
        self.generate_btn = QPushButton("Generate Script")
        self.generate_btn.clicked.connect(self.generate_script)
        self.generate_btn.setStyleSheet(self.get_button_style())
        ai_layout.addWidget(self.generate_btn)
        
        # AI progress
        self.ai_progress = QProgressBar()
        self.ai_progress.setVisible(False)
        ai_layout.addWidget(self.ai_progress)
        
        # Generated script preview
        self.generated_script_preview = QTextEdit()
        self.generated_script_preview.setPlaceholderText("Generated script will appear here...")
        self.generated_script_preview.setMaximumHeight(200)
        ai_layout.addWidget(self.generated_script_preview)
        
        # Save generated script button
        self.save_generated_btn = QPushButton("Save Generated Script")
        self.save_generated_btn.clicked.connect(self.save_generated_script)
        self.save_generated_btn.setEnabled(False)
        self.save_generated_btn.setStyleSheet(self.get_button_style())
        ai_layout.addWidget(self.save_generated_btn)
        
        layout.addWidget(script_group)
        layout.addWidget(ai_group)
        layout.addStretch()
        
        return panel
        
    def create_right_panel(self):
        """Create the right panel with execution controls and logs"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Execution Controls Group
        exec_group = QGroupBox("Execution Controls")
        exec_layout = QVBoxLayout(exec_group)
        
        # Execution buttons
        button_layout = QHBoxLayout()
        
        self.execute_btn = QPushButton("Execute Script")
        self.execute_btn.clicked.connect(self.execute_script)
        self.execute_btn.setEnabled(False)
        self.execute_btn.setStyleSheet(self.get_button_style("success"))
        button_layout.addWidget(self.execute_btn)
        
        self.stop_btn = QPushButton("Stop Execution")
        self.stop_btn.clicked.connect(self.stop_execution)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(self.get_button_style("danger"))
        button_layout.addWidget(self.stop_btn)
        
        exec_layout.addLayout(button_layout)
        
        # Execution progress
        self.exec_progress = QProgressBar()
        self.exec_progress.setVisible(False)
        exec_layout.addWidget(self.exec_progress)
        
        # Execution status
        self.exec_status_label = QLabel("Ready to execute")
        self.exec_status_label.setStyleSheet("color: #888;")
        exec_layout.addWidget(self.exec_status_label)
        
        # Logs Group
        logs_group = QGroupBox("Execution Logs")
        logs_layout = QVBoxLayout(logs_group)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        self.clear_logs_btn = QPushButton("Clear Logs")
        self.clear_logs_btn.clicked.connect(self.clear_logs)
        self.clear_logs_btn.setStyleSheet(self.get_button_style())
        log_controls.addWidget(self.clear_logs_btn)
        
        self.export_logs_btn = QPushButton("Export Logs")
        self.export_logs_btn.clicked.connect(self.export_logs)
        self.export_logs_btn.setStyleSheet(self.get_button_style())
        log_controls.addWidget(self.export_logs_btn)
        
        logs_layout.addLayout(log_controls)
        
        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        logs_layout.addWidget(self.log_display)
        
        layout.addWidget(exec_group)
        layout.addWidget(logs_group)
        
        return panel
        
    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        load_action = QAction("Load Script", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_script)
        file_menu.addAction(load_action)
        
        save_action = QAction("Save Generated Script", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_generated_script)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        generate_action = QAction("Generate AI Script", self)
        generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.generate_script)
        tools_menu.addAction(generate_action)
        
        execute_action = QAction("Execute Script", self)
        execute_action.setShortcut("F5")
        execute_action.triggered.connect(self.execute_script)
        tools_menu.addAction(execute_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_theme(self):
        """Setup dark theme with neon highlights"""
        # Dark palette
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Link, QColor(0, 150, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 150, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
        
        self.setPalette(palette)
        
        # Stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #00aaff;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
                color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #00aaff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555;
                border-radius: 3px;
                color: #ffffff;
                padding: 5px;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
                border-color: #00aaff;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 3px;
                text-align: center;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #00aaff;
                border-radius: 2px;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                color: #ffffff;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #ffffff;
            }
        """)
        
    def get_button_style(self, variant="default"):
        """Get button style based on variant"""
        base_style = """
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px 16px;
                color: #ffffff;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4c4c4c;
                border-color: #00aaff;
            }
            QPushButton:pressed {
                background-color: #2c2c2c;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #666;
            }
        """
        
        if variant == "success":
            return base_style.replace("#00aaff", "#00ff00")
        elif variant == "danger":
            return base_style.replace("#00aaff", "#ff0000")
        else:
            return base_style
            
    def load_settings(self):
        """Load application settings"""
        settings = QSettings("CIA", "RobloxExecutor")
        geometry = settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
    def save_settings(self):
        """Save application settings"""
        settings = QSettings("CIA", "RobloxExecutor")
        settings.setValue("geometry", self.saveGeometry())
        
    def load_script(self):
        """Load a Lua script file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load Lua Script", "", "Lua Files (*.lua);;All Files (*)"
        )
        
        if file_path:
            self.current_script_path = file_path
            self.script_path_label.setText(f"Loaded: {os.path.basename(file_path)}")
            self.execute_btn.setEnabled(True)
            self.status_bar.showMessage(f"Script loaded: {file_path}")
            
            # Log the action
            self.log_message(f"Script loaded: {file_path}")
            
    def generate_script(self):
        """Generate a script using AI"""
        prompt = self.ai_prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Warning", "Please enter a prompt for script generation.")
            return
            
        # Disable generate button and show progress
        self.generate_btn.setEnabled(False)
        self.ai_progress.setVisible(True)
        self.ai_progress.setValue(0)
        
        # Start AI worker
        self.ai_worker = AIWorker(self.ai_interface, prompt)
        self.ai_worker.script_generated.connect(self.on_script_generated)
        self.ai_worker.error_occurred.connect(self.on_ai_error)
        self.ai_worker.progress_updated.connect(self.ai_progress.setValue)
        self.ai_worker.start()
        
        self.status_bar.showMessage("Generating script with AI...")
        self.log_message("AI script generation started...")
        
    def on_script_generated(self, script_name: str, script_content: str):
        """Handle generated script from AI"""
        self.generated_script_preview.setPlainText(script_content)
        self.save_generated_btn.setEnabled(True)
        self.generate_btn.setEnabled(True)
        self.ai_progress.setVisible(False)
        
        self.status_bar.showMessage("Script generated successfully!")
        self.log_message(f"AI script generated: {script_name}")
        
    def on_ai_error(self, error: str):
        """Handle AI generation error"""
        self.generate_btn.setEnabled(True)
        self.ai_progress.setVisible(False)
        
        QMessageBox.critical(self, "AI Error", f"Failed to generate script: {error}")
        self.log_message(f"AI generation error: {error}")
        
    def save_generated_script(self):
        """Save the generated script to file"""
        script_content = self.generated_script_preview.toPlainText()
        if not script_content:
            QMessageBox.warning(self, "Warning", "No script to save.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Generated Script", "", "Lua Files (*.lua);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(script_content)
                    
                self.current_script_path = file_path
                self.script_path_label.setText(f"Saved: {os.path.basename(file_path)}")
                self.execute_btn.setEnabled(True)
                
                self.status_bar.showMessage(f"Script saved: {file_path}")
                self.log_message(f"Generated script saved: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save script: {str(e)}")
                
    def execute_script(self):
        """Execute the loaded script"""
        if not self.current_script_path:
            QMessageBox.warning(self, "Warning", "No script loaded.")
            return
            
        # Disable execute button and show progress
        self.execute_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.exec_progress.setVisible(True)
        self.exec_progress.setValue(0)
        self.exec_status_label.setText("Executing script...")
        
        # Start executor worker
        self.executor_worker = ExecutorWorker(self.executor, self.current_script_path)
        self.executor_worker.execution_complete.connect(self.on_execution_complete)
        self.executor_worker.log_updated.connect(self.log_message)
        self.executor_worker.progress_updated.connect(self.exec_progress.setValue)
        self.executor_worker.start()
        
        self.status_bar.showMessage("Executing script...")
        self.log_message(f"Script execution started: {self.current_script_path}")
        
    def on_execution_complete(self, message: str, success: bool):
        """Handle script execution completion"""
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.exec_progress.setVisible(False)
        
        if success:
            self.exec_status_label.setText("Execution completed successfully")
            self.exec_status_label.setStyleSheet("color: #00ff00;")
        else:
            self.exec_status_label.setText("Execution failed")
            self.exec_status_label.setStyleSheet("color: #ff0000;")
            
        self.status_bar.showMessage(message)
        self.log_message(f"Execution result: {message}")
        
    def stop_execution(self):
        """Stop script execution"""
        if self.executor_worker and self.executor_worker.isRunning():
            self.executor_worker.terminate()
            self.executor_worker.wait()
            
        self.execute_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.exec_progress.setVisible(False)
        self.exec_status_label.setText("Execution stopped")
        self.exec_status_label.setStyleSheet("color: #ffaa00;")
        
        self.status_bar.showMessage("Execution stopped")
        self.log_message("Script execution stopped by user")
        
    def log_message(self, message: str):
        """Add a message to the log display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        
        self.log_display.append(log_entry)
        
        # Auto-scroll to bottom
        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_display.setTextCursor(cursor)
        
    def clear_logs(self):
        """Clear the log display"""
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
                    
                self.status_bar.showMessage(f"Logs exported: {file_path}")
                self.log_message(f"Logs exported to: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export logs: {str(e)}")
                
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About CIA Roblox Executor",
            """
            <h3>CIA Roblox Executor v1.0</h3>
            <p>A secure, AI-powered Roblox script executor for internal use.</p>
            <p><b>Features:</b></p>
            <ul>
                <li>AI-powered script generation</li>
                <li>Secure sandboxed execution</li>
                <li>Comprehensive logging and auditing</li>
                <li>Modern dark theme interface</li>
            </ul>
            <p><b>Ethical Use Only</b></p>
            <p>This tool is designed for internal testing and development purposes only.</p>
            """
        )
        
    def closeEvent(self, event):
        """Handle application close event"""
        self.save_settings()
        
        # Stop any running workers
        if self.ai_worker and self.ai_worker.isRunning():
            self.ai_worker.terminate()
            self.ai_worker.wait()
            
        if self.executor_worker and self.executor_worker.isRunning():
            self.executor_worker.terminate()
            self.executor_worker.wait()
            
        event.accept()


def main():
    """Main entry point"""
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