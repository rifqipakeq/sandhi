# /models.py
from flask_sqlalchemy import SQLAlchemy
from encryption.blowfish_db import encrypt_blowfish, decrypt_blowfish
import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False) 
    # _encrypted_profile_data = db.Column(db.String(512))   
    _face_descriptors = db.Column(db.Text, nullable=True)


    @property
    def profile_data(self):
        """Properti untuk mendekripsi data saat diakses."""
        if self._encrypted_profile_data:
            return decrypt_blowfish(self._encrypted_profile_data)
        return None

    # @profile_data.setter
    # def profile_data(self, value: str):
    #     """Setter untuk mengenkripsi data sebelum disimpan."""
    #     self._encrypted_profile_data = encrypt_blowfish(value)
    
    @property
    def face_descriptors(self):
        """Mendekripsi JSON string dari face descriptors."""
        if self._face_descriptors:
            return decrypt_blowfish(self._face_descriptors)
        return None

    @face_descriptors.setter
    def face_descriptors(self, json_string_data: str):
        """Mengenkripsi JSON string dari face descriptors sebelum disimpan."""
        self._face_descriptors = encrypt_blowfish(json_string_data)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    _message_type = db.Column(db.String(255), nullable=False) 
    _encrypted_content = db.Column(db.Text, nullable=False)
    _original_filename = db.Column(db.String(512), nullable=True)
    
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')

    @property
    def message_type(self):
        return decrypt_blowfish(self._message_type)

    @message_type.setter
    def message_type(self, value: str):
        self._message_type = encrypt_blowfish(value)

    @property
    def encrypted_content(self):
        return decrypt_blowfish(self._encrypted_content)

    @encrypted_content.setter
    def encrypted_content(self, value: str):
        self._encrypted_content = encrypt_blowfish(value)

    @property
    def original_filename(self):
        if self._original_filename:
            return decrypt_blowfish(self._original_filename)
        return None

    @original_filename.setter
    def original_filename(self, value: str):
        if value:
            self._original_filename = encrypt_blowfish(value)
        else:
            self._original_filename = None