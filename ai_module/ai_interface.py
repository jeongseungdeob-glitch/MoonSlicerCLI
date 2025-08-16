import httpx
from utils.config import Config


class AIInterface:
    """Interface for interacting with local hybrid LLM backend to generate Lua scripts."""

    def __init__(self):
        cfg = Config.load()
        self.base_url: str = cfg["backend_base_url"].rstrip("/")

    async def generate_script(self, prompt: str, fast_mode: bool = True) -> str:
        """Send prompt to backend /api/chat and return the text response."""
        payload = {"prompt": prompt, "fast_mode": fast_mode}
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
        return data.get("response", "")