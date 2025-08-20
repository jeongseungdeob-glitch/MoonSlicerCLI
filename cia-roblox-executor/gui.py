import sys
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from executor.core import ExecutorCore


class MainWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("CIA Lua Sandbox - Internal")
		self.core = ExecutorCore()
		self._build_ui()

	def _build_ui(self):
		layout = QVBoxLayout()

		self.goal_input = QLineEdit()
		self.goal_input.setPlaceholderText("Describe the script you want to generate (safe Lua)")
		layout.addWidget(QLabel("Goal"))
		layout.addWidget(self.goal_input)

		btn_row = QHBoxLayout()
		self.btn_generate = QPushButton("Generate Script")
		self.btn_generate.clicked.connect(self.on_generate)
		btn_row.addWidget(self.btn_generate)

		self.btn_execute = QPushButton("Execute")
		self.btn_execute.clicked.connect(self.on_execute)
		btn_row.addWidget(self.btn_execute)
		layout.addLayout(btn_row)

		self.script_edit = QTextEdit()
		self.script_edit.setPlaceholderText("Lua script will appear here")
		layout.addWidget(QLabel("Script"))
		layout.addWidget(self.script_edit)

		self.output_edit = QTextEdit()
		self.output_edit.setReadOnly(True)
		layout.addWidget(QLabel("Output / Logs"))
		layout.addWidget(self.output_edit)

		self.setLayout(layout)
		self.resize(900, 700)

	def on_generate(self):
		goal = self.goal_input.text().strip()
		if not goal:
			return
		try:
			info = self.core.generate_and_save(goal)
			self.script_edit.setPlainText(info["code"])
			self.output_edit.append(f"Saved: {info['path']}")
		except Exception as e:
			self.output_edit.append(f"Generation error: {e}")

	def on_execute(self):
		code = self.script_edit.toPlainText()
		if not code.strip():
			return
		try:
			result = self.core.execute(code)
			self.output_edit.append(f"Result: {result}")
		except Exception as e:
			self.output_edit.append(f"Execution error: {e}")


def main():
	app = QApplication(sys.argv)
	w = MainWindow()
	w.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()