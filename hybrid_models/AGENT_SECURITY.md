# MoonSlicerCLI Encryption/Decryption

All sensitive chat/config files are AES-256 encrypted.

- **Decrypt via GUI**: Click “Export (Decrypt)” to get a plaintext copy.
- **Decrypt via CLI**:  
    ```
    python backend/crypto_utils.py decrypt /path/to/chat_history.json.enc
    ```
- **Encrypt manually**:  
    ```
    python backend/crypto_utils.py encrypt /path/to/file
    ```
- **Key location**:  
    - Key is stored at `~/.moonslicer_key`
    - To reset/rotate key: delete the file (will break decryption on old files).

For maximum security, always store decrypted files in a secure, temporary location and delete after use.
