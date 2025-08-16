import sys
from PyQt6 import QtWidgets, QtGui, QtCore
from ai_module.ai_interface import AIScriptAssistant
from ai_module.script_builder import build_lua_script_from_text
from ai_module.validation import validate_lua
from executor.core import ExecutorCore
from utils.file_manager import save_script


class GUI(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("MoonSlicer Sandbox Executor")
		self.resize(900, 700)

		self.prompt_edit = QtWidgets.QPlainTextEdit()
		self.prompt_edit.setPlaceholderText("Describe the Lua script you want to generate...")
		self.generate_btn = QtWidgets.QPushButton("Generate Script")
		self.execute_btn = QtWidgets.QPushButton("Execute Script")
		self.script_view = QtWidgets.QPlainTextEdit()
		self.script_view.setReadOnly(False)
		self.log_view = QtWidgets.QPlainTextEdit()
		self.log_view.setReadOnly(True)

		layout = QtWidgets.QGridLayout(self)
		layout.addWidget(QtWidgets.QLabel("Prompt"), 0, 0)
		layout.addWidget(self.prompt_edit, 1, 0, 1, 2)
		layout.addWidget(self.generate_btn, 2, 0)
		layout.addWidget(self.execute_btn, 2, 1)
		layout.addWidget(QtWidgets.QLabel("Lua Script"), 3, 0)
		layout.addWidget(self.script_view, 4, 0, 1, 2)
		layout.addWidget(QtWidgets.QLabel("Logs"), 5, 0)
		layout.addWidget(self.log_view, 6, 0, 1, 2)

		self.ai = AIScriptAssistant()
		self.executor = ExecutorCore()

		self.generate_btn.clicked.connect(self.on_generate)
		self.execute_btn.clicked.connect(self.on_execute)

	def append_log(self, text: str) -> None:
		self.log_view.appendPlainText(text)

	def on_generate(self):
		prompt = self.prompt_edit.toPlainText().strip()
		if not prompt:
			self.append_log("No prompt provided.")
			return
		try:
			text = self.ai.generate_script_text_sync(prompt)
			code = build_lua_script_from_text(text)
			ok, errs = validate_lua(code)
			if not ok:
				self.append_log("Validation failed: " + "; ".join(errs))
				return
			self.script_view.setPlainText(code)
			path = save_script(code)
			self.append_log(f"Script saved: {path}")
		except Exception as e:
			self.append_log(f"Error generating script: {e}")

	def on_execute(self):
		code = self.script_view.toPlainText()
		res = self.executor.execute_code(code)
		self.append_log(str(res))


def run():
	app = QtWidgets.QApplication(sys.argv)
	w = GUI()
	w.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	run()