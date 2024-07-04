import json
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib

def password_to_key(password: str) -> bytes:
    password_bytes = password.encode('utf-8')
    key = hashlib.sha256(password_bytes).digest()

    return base64.urlsafe_b64encode(key)

def load_json(filepath: Path | str):
    with open(filepath, "r") as file:
        return json.load(file)

def save_json(filepath: Path | str, data: dict):
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)

def encrypt_json(filepath: Path | str, data: dict, password: str) -> str:
    key = password_to_key(password)
    fernet = Fernet(key)

    json_data = json.dumps(data).encode('utf-8')
    encrypted_data = fernet.encrypt(json_data)

    with open(filepath + ".enc", "wb") as file:
        file.write(encrypted_data)

def decrypt_json(filepath: Path | str, password: str) -> dict:
    key = password_to_key(password)
    fernet = Fernet(key)

    with open(filepath + ".enc", "rb") as file:
        encrypted_data = file.read()

    decrypted_data = fernet.decrypt(encrypted_data)
    return json.loads(decrypted_data.decode('utf-8'))