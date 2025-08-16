import os
import yaml
from typing import Any, Dict


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
SANDBOXED_SCRIPTS_DIR = os.path.join(PROJECT_ROOT, "sandboxed_scripts")
CONFIG_PATH = os.path.join(PROJECT_ROOT, "config.yaml")

# Prefer the existing backend router if running; fallback to direct Ollama if not.
BACKEND_API_URL = os.environ.get("MOON_BACKEND_API", "http://localhost:8000/api/chat")
OLLAMA_API_URL = os.environ.get("OLLAMA_API", "http://localhost:11434/api/generate")
OLLAMA_DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "mistral:7b-instruct-q4_0")

# Sandbox constraints
LUA_EXECUTION_TIMEOUT_SECONDS = int(os.environ.get("LUA_TIMEOUT", "5"))
MAX_SCRIPT_BYTES = int(os.environ.get("MAX_SCRIPT_BYTES", "20000"))

# Validation rules
BANNED_TOKENS = [
	"os.", "io.", "debug.", "package.",
	"require(", "load(", "loadstring(", "dofile(", "loadfile(",
	"setfenv(", "getfenv(", "collectgarbage(", "coroutine.",
]

INFINITE_LOOP_PATTERNS = [
	"while true do",
	"repeat\n",
]


def ensure_directories() -> None:
	os.makedirs(LOG_DIR, exist_ok=True)
	os.makedirs(SANDBOXED_SCRIPTS_DIR, exist_ok=True)


def load_config_override() -> Dict[str, Any]:
	if not os.path.exists(CONFIG_PATH):
		return {}
	with open(CONFIG_PATH, "r", encoding="utf-8") as f:
		data = yaml.safe_load(f) or {}
	return data


def get_config() -> Dict[str, Any]:
	config = {
		"backend_api_url": BACKEND_API_URL,
		"ollama_api_url": OLLAMA_API_URL,
		"ollama_default_model": OLLAMA_DEFAULT_MODEL,
		"lua_timeout_seconds": LUA_EXECUTION_TIMEOUT_SECONDS,
		"max_script_bytes": MAX_SCRIPT_BYTES,
		"banned_tokens": BANNED_TOKENS,
		"infinite_loop_patterns": INFINITE_LOOP_PATTERNS,
		"log_dir": LOG_DIR,
		"scripts_dir": SANDBOXED_SCRIPTS_DIR,
	}
	override = load_config_override()
	config.update(override)
	return config