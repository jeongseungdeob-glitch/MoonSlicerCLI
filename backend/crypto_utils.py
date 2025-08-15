import os
import base64
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

KEY_FILE = os.path.expanduser("~/.moonslicer_key")

def get_key():
    if not os.path.exists(KEY_FILE):
        key = get_random_bytes(32)  # 256-bit key
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

def encrypt_file(src_path, dst_path=None):
    key = get_key()
    with open(src_path, "rb") as f:
        plaintext = f.read()
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    data = cipher.nonce + tag + ciphertext
    out_path = dst_path or (src_path + ".enc")
    with open(out_path, "wb") as f:
        f.write(data)
    return out_path

def decrypt_file(src_path, dst_path=None):
    key = get_key()
    with open(src_path, "rb") as f:
        data = f.read()
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
    out_path = dst_path or src_path.replace(".enc", "")
    with open(out_path, "wb") as f:
        f.write(plaintext)
    return out_path

def encrypt_string(text):
    key = get_key()
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(text.encode())
    return base64.b64encode(cipher.nonce + tag + ciphertext).decode()

def decrypt_string(token):
    key = get_key()
    data = base64.b64decode(token)
    nonce = data[:16]
    tag = data[16:32]
    ciphertext = data[32:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="MoonSlicer File Encryptor/Decryptor")
    parser.add_argument("mode", choices=["encrypt", "decrypt"])
    parser.add_argument("src")
    parser.add_argument("--dst", default=None)
    args = parser.parse_args()
    if args.mode == "encrypt":
        print("Encrypted file:", encrypt_file(args.src, args.dst))
    else:
        print("Decrypted file:", decrypt_file(args.src, args.dst))
