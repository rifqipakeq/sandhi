# /encryption/blowfish_db.py
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

# Kunci ini harus 16 bit 
BLOWFISH_KEY = b'ABCDEFGHIJKLMNOP' 

def encrypt_blowfish(data: str) -> str:
    try:
        cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_CBC)
        data_bytes = data.encode('utf-8')
        padded_data = pad(data_bytes, Blowfish.block_size)
        iv = cipher.iv
        encrypted_data = cipher.encrypt(padded_data)
        return base64.b64encode(iv + encrypted_data).decode('utf-8')
    except Exception as e:
        print(f"Blowfish Encryption Error: {e}")
        return ""

def decrypt_blowfish(encrypted_data_b64: str) -> str:
    if not encrypted_data_b64:
        return "Decryption Failed (Empty)" 

    try:
        encrypted_data = base64.b64decode(encrypted_data_b64)
        iv = encrypted_data[:Blowfish.block_size]
        ct = encrypted_data[Blowfish.block_size:]
        cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ct), Blowfish.block_size)
        return decrypted_data.decode('utf-8')
    except (ValueError, KeyError, TypeError, base64.binascii.Error) as e:
        print(f"Blowfish Decryption Error: {e}")
        return "Decryption Failed (Data Corrupt)"