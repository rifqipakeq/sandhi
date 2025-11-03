# /app.py
from flask import Flask, session # session untuk menyimpan user login
from flask_socketio import SocketIO # untuk memperluas komunikasi real time
from models import db # instance sql alchemy
import os # manipulasi system

# Inisialisasi SocketIO
socketio = SocketIO()
clients = {} # Menyimpan map {user_id: session_id} agar dapat memetakan user dengan session terkait

def create_app():
    app = Flask(__name__)
    
    # Konfigurasi
    app.config['SECRET_KEY'] = 'kriptografi-itu-asik-ya' # untuk enkripsi session. pake apa ya?
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # menonaktifkan notifikasi perubahan model 
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads') # lokasi upload
    
    # jika ngga ada maka buat
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Inisialisasi DB
    db.init_app(app) # connect instance ke flask

    # Inisialisasi SocketIO
    # Kita gunakan eventlet untuk performa async
    socketio.init_app(app, async_mode='eventlet', cors_allowed_origins="*") # apa itu eventlet dan cors berarti allow dari semua domain

    # Registrasi Blueprints (Rute)
    from routes.auth import auth_bp
    from routes.chat import chat_bp
    from routes.decrypt import decrypt_bp
    
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(chat_bp, url_prefix='/chat')
    app.register_blueprint(decrypt_bp, url_prefix='/decrypt')

    # Registrasi Penangan WebSocket
    from websocket.chat_ws import register_socket_handlers
    register_socket_handlers(socketio, clients)

    with app.app_context():
        db.create_all() # Membuat tabel database jika belum ada

    return app

if __name__ == '__main__':
    app = create_app()
    
    # Setup Ngrok
    # (Opsional) Masukkan authtoken Anda jika punya
    # ngrok.set_auth_token("34woqena3JAVEB0a9MRrMppkpG5_28Vkk6ZfcqXiQpJVJjCZB") 
    # http_tunnel = ngrok.connect(5000)
    # print(f" * Aplikasi dapat diakses publik di: {http_tunnel.public_url}")
    
    print(" * Menjalankan server Flask-SocketIO dengan eventlet...")
    # Jalankan aplikasi menggunakan server SocketIO (bukan app.run())
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)