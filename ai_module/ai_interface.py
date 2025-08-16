import httpx
from typing import Dict
from utils.config import AIConfig


class AIScriptAssistant:
	def __init__(self, config: AIConfig | None = None):
		self.config = config or AIConfig()

	async def generate_script_text(self, prompt: str) -> str:
		async with httpx.AsyncClient() as client:
			resp = await client.post(self.config.chat_api_url, json={
				"prompt": prompt,
				"fast_mode": self.config.fast_mode
			})
			resp.raise_for_status()
			data: Dict = resp.json()
			return data.get("response", "")

	def generate_script_text_sync(self, prompt: str) -> str:
		with httpx.Client() as client:
			resp = client.post(self.config.chat_api_url, json={
				"prompt": prompt,
				"fast_mode": self.config.fast_mode
			})
			resp.raise_for_status()
			data: Dict = resp.json()
			return data.get("response", "")