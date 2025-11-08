# /encryption/affine_xor.py
import base64

AFFINE_A = 5
AFFINE_B = 20

def mod_inverse(a, m):
    for i in range(1, m):
        if (a * i) % m == 1:
            return i
    return None

AFFINE_A_INV = mod_inverse(AFFINE_A, 256)

if AFFINE_A_INV is None:
    raise ValueError(f"Nilai 'a'={AFFINE_A} tidak koprima dengan 256.")

def encrypt_affine(data_bytes: bytes) -> bytes:
    return bytes([(AFFINE_A * b + AFFINE_B) % 256 for b in data_bytes])

def decrypt_affine(data_bytes: bytes) -> bytes:
    return bytes([(AFFINE_A_INV * (b - AFFINE_B)) % 256 for b in data_bytes])

XOR_KEY = "kriptografi-itu-asik-ya"

def encrypt_xor(data_bytes: bytes, key_str: str) -> bytes:
    key_bytes = key_str.encode('utf-8')
    return bytes([data_bytes[i] ^ key_bytes[i % len(key_bytes)] for i in range(len(data_bytes))])

def decrypt_xor(data_bytes: bytes, key_str: str) -> bytes:
    return encrypt_xor(data_bytes, key_str)

# --- Fungsi Super Encryption ---
def encrypt_text_super(plaintext: str) -> str:
    text_bytes = plaintext.encode('utf-8')
    affine_encrypted = encrypt_affine(text_bytes)
    xor_encrypted = encrypt_xor(affine_encrypted, XOR_KEY)
    return base64.b64encode(xor_encrypted).decode('utf-8')

def decrypt_text_super(ciphertext_b64: str) -> str:
    try:
        xor_encrypted = base64.b64decode(ciphertext_b64)
        affine_encrypted = decrypt_xor(xor_encrypted, XOR_KEY)
        text_bytes = decrypt_affine(affine_encrypted)
        return text_bytes.decode('utf-8')
    except Exception:
        return "Decryption Affine Failed"