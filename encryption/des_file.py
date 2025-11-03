# /encryption/des_file.py
from Crypto.Cipher import DES
from Crypto.Util.Padding import pad, unpad
import base64

DES_KEY = b'12345678' # Contoh kunci 8 byte

def encrypt_file_des(file_data: bytes) -> bytes:
    cipher = DES.new(DES_KEY, DES.MODE_CBC)
    iv = cipher.iv
    padded_data = pad(file_data, DES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    return iv + encrypted_data

def decrypt_file_des(encrypted_data: bytes) -> bytes:
    try:
        iv = encrypted_data[:DES.block_size]
        ct = encrypted_data[DES.block_size:]
        cipher = DES.new(DES_KEY, DES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(ct), DES.block_size)
        return decrypted_data
    except (ValueError, KeyError):
        return "Decryption DES Failed"