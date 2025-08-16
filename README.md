# MoonSlicerCLI

**MoonSlicer Pro CLI/GUI** — Hybrid open-source LLM ensemble for elite coding and cybersecurity, inspired by the best features of ChatGPT-5, Claude Opus, and Gemini 2.5 Pro.

- **Hybrid LLMs**: Quantized Mistral 7B, DeepSeek-Coder 6.7B, StarCoder2 7B
- **Router/Ensemble**: Best model for each task, consensus/fast mode
- **Neon Cyberpunk UI**: Electron + React (CLI fallback available)
- **AES Encryption**: All chat/config local, decrypt/export via sidebar
- **Modes**: White/Grey/Black Hat (with confirmation)
- **Automated installer and scripts**

## Quick Start
1. Clone this repo.
2. Run `installer/install_moonslicer.bat` (Windows) or follow manual steps in `/hybrid_models/README.md`.
3. Download models (see `/backend/download_models.sh`).
4. Start backend (`backend/main.py`) and frontend (`frontend/`).

---

## CIA-Grade Security
- All chat/config files AES-256 encrypted by default
- Decrypt/export via sidebar or CLI
- No cloud, no telemetry, all local

## Local Lua Sandbox Executor
- Safe, self-hosted Lua execution with strict sandboxing (no IO/OS access)
- AI-assisted script generation via existing `/backend` `/api/chat`
- Validation to block unsafe tokens and infinite loops
- Hard timeout using a separate process

### Run GUI
```bash
python gui.py
```

### Run CLI
```bash
# Generate script via AI and save to /sandboxed_scripts
python main.py generate "print a table of prime numbers up to 100 in Lua"

# List saved scripts
python main.py list

# Execute a script file
python main.py execute --file /workspace/sandboxed_scripts/script_YYYYMMDD-HHMMSS.lua

# Execute inline code
python main.py execute --code "print('Hello from Lua')"
```

## License
MIT (see LICENSE)
