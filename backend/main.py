import os
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from crypto_utils import encrypt_file, decrypt_file
import httpx
import tempfile

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_MAP = {
    "mistral": "mistral:7b-instruct-q4_0",
    "deepseek": "deepseek-coder:6.7b-instruct-q4_0",
    "starcoder2": "starcoder2:7b-q4_0"
}
OLLAMA_API = "http://localhost:11434/api/generate"

def route_prompt(prompt):
    p = prompt.lower()
    if "python" in p or "automation" in p:
        return "deepseek"
    if "repo" in p or "multi-file" in p or "github" in p:
        return "starcoder2"
    return "mistral"

@app.post("/api/chat")
async def chat(req: Request):
    data = await req.json()
    prompt = data.get("prompt", "")
    fast_mode = data.get("fast_mode", True)
    chosen = route_prompt(prompt)
    responses = {}

    async with httpx.AsyncClient() as client:
        if fast_mode:
            resp = await client.post(OLLAMA_API, json={"model": MODEL_MAP[chosen], "prompt": prompt})
            return {"response": resp.json().get("response", "")}
        else:
            for name, model in MODEL_MAP.items():
                resp = await client.post(OLLAMA_API, json={"model": model, "prompt": prompt})
                responses[name] = resp.json().get("response", "")
            combined = "\n---\n".join([f"{k}: {v}" for k, v in responses.items()])
            return {"response": combined}

@app.post("/api/encrypt")
async def encrypt_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(file.file.read())
        temp.flush()
        enc_path = temp.name + ".enc"
        encrypt_file(temp.name, enc_path)
    return FileResponse(enc_path, filename=file.filename + ".enc")

@app.post("/api/decrypt")
async def decrypt_endpoint(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(file.file.read())
        temp.flush()
        dec_path = temp.name + ".dec"
        try:
            decrypt_file(temp.name, dec_path)
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=400)
    return FileResponse(dec_path, filename=file.filename.replace(".enc", ""))

@app.post("/api/export")
async def export_endpoint(req: Request):
    data = await req.json()
    chat_path = os.path.expanduser("~/moonslicer_chat_history.json")
    with open(chat_path, "w", encoding="utf-8") as f:
        f.write(data.get("history", "[]"))
    enc_path = chat_path + ".enc"
    encrypt_file(chat_path, enc_path)
    return FileResponse(enc_path, filename="moonslicer_chat_history.json.enc")
