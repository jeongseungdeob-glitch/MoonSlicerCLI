# Hybrid LLM Setup Guide (MoonSlicerCLI)

MoonSlicerCLI uses a hybrid of three open-source LLMs (all quantized for minimal RAM/disk):
- Mistral 7B (4-bit)
- DeepSeek-Coder 6.7B (4-bit)
- StarCoder2 7B (4-bit)

All models run locally via Ollama. See `backend/download_models.sh`.

## Downloading & Serving Models

```bash
cd backend
bash download_models.sh
bash start_llms.sh
```

This will fetch all models and start Ollama server on localhost:11434.

## Backend

Run the backend router:
```bash
python main.py
```

---

## AES Encryption/Decryption
All chat/config files are encrypted. See `/backend/crypto_utils.py` for CLI tools and `/api` endpoints for GUI integrations.
