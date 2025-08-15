#!/bin/bash

# Install Ollama if missing
if ! command -v ollama &> /dev/null; then
  echo "Ollama not found. Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "Pulling quantized models..."

ollama pull mistral:7b-instruct-q4_0
ollama pull deepseek-coder:6.7b-instruct-q4_0
ollama pull starcoder2:7b-q4_0

echo "All models downloaded and ready for local use."
