# /encryption/md5_login.py
import hashlib

def hash_password_md5(password: str) -> str:
    return hashlib.md5(password.encode('utf-8')).hexdigest()