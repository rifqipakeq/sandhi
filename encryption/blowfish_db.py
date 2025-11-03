# /encryption/blowfish_db.py
from Crypto.Cipher import Blowfish
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

# Kunci ini HARUS 16 byte (128 bit) dan RAHASIA.
# Ganti dengan kunci Anda sendiri, idealnya simpan di .env
BLOWFISH_KEY = b'ABCDEFGHIJKLMNOP' # Contoh kunci 16 byte

def encrypt_blowfish(data: str) -> str:
    try:
        cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_CBC)
        data_bytes = data.encode('utf-8')
        padded_data = pad(data_bytes, Blowfish.block_size)
        iv = cipher.iv
        encrypted_data = cipher.encrypt(padded_data)
        # Mengembalikan IV + data terenkripsi, di-encode ke Base64
        return base64.b64encode(iv + encrypted_data).decode('utf-8')
    except Exception as e:
        print(f"Blowfish Encryption Error: {e}")
        return ""

def decrypt_blowfish(encrypted_data_b64: str) -> str:
    try:
        encrypted_data = base64.b64decode(encrypted_data_b64)
        iv = encrypted_data[:Blowfish.block_size]
        ct = encrypted_data[Blowfish.block_size:]
        cipher = Blowfish.new(BLOWFISH_KEY, Blowfish.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ct), Blowfish.block_size)
        return decrypted_data.decode('utf-8')
    except (ValueError, KeyError, TypeError):
        return "Decryption Blowfish Failed" # Gagal dekripsi (mungkin data korup/kunci salah)