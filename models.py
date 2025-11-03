# /models.py
'''berfungsi untuk mengolah data baru baik user atau message sebelum di masukan ke database'''
from flask_sqlalchemy import SQLAlchemy
from encryption.blowfish_db import encrypt_blowfish, decrypt_blowfish
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False) 
    
    # Menyimpan data terenkripsi (sesuai spesifikasi)
    _encrypted_profile_data = db.Column(db.String(512))

    @property
    def profile_data(self):
        """Properti untuk mendekripsi data saat diakses."""
        if self._encrypted_profile_data:
            return decrypt_blowfish(self._encrypted_profile_data)
        return None

    @profile_data.setter
    def profile_data(self, value: str):
        """Setter untuk mengenkripsi data sebelum disimpan."""
        self._encrypted_profile_data = encrypt_blowfish(value)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_type = db.Column(db.String(10), nullable=False) # 'text', 'image', 'file'
    
    # Menyimpan teks terenkripsi (Base64) ATAU path ke file/gambar terenkripsi
    encrypted_content = db.Column(db.Text, nullable=False)
    
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')