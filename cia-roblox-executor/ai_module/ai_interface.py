import json
import requests
from typing import Dict
from ..utils.config import get_config


class AIInterface:
	def __init__(self):
		self.cfg = get_config()
		self.backend_api = self.cfg["backend_api_url"]
		self.ollama_api = self.cfg["ollama_api_url"]
		self.default_model = self.cfg["ollama_default_model"]

	def build_prompt(self, goal: str) -> str:
		prefix = (
			"You are a helpful internal assistant that writes SAFE Roblox-like Lua scripts for a local sandbox. "
			"Do not use any file I/O or OS APIs. Avoid infinite loops. Use only basic language constructs."
		)
		return f"{prefix}\n\nTask: {goal}\n\nReturn only Lua code."

	def _call_backend(self, prompt: str) -> str:
		resp = requests.post(self.backend_api, json={"prompt": prompt, "fast_mode": True}, timeout=30)
		resp.raise_for_status()
		data: Dict = resp.json()
		return data.get("response", "")

	def _call_ollama(self, prompt: str) -> str:
		resp = requests.post(self.ollama_api, json={"model": self.default_model, "prompt": prompt}, timeout=60)
		resp.raise_for_status()
		raw = resp.json()
		# Ollama streaming may return chunks; here we expect final combined
		return raw.get("response", "")

	def generate_lua(self, goal: str) -> str:
		prompt = self.build_prompt(goal)
		backend_error = None
		try:
			return self._call_backend(prompt)
		except Exception as e:
			backend_error = e
		try:
			return self._call_ollama(prompt)
		except Exception as e:
			raise RuntimeError(f"AI generation failed (backend error: {backend_error}); Ollama fallback failed: {e}")