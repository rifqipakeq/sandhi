# /encryption/md5_login.py
import hashlib

def hash_password_md5(password: str) -> str:
    """
    Hashes a password using MD5 and returns the hex digest.
    PERINGATAN: MD5 tidak aman untuk password.
    """
    return hashlib.md5(password.encode('utf-8')).hexdigest()