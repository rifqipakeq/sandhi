# /app.py
from flask import Flask, session 
from flask_socketio import SocketIO 
from models import db
import os 

# Inisialisasi SocketIO
socketio = SocketIO()
clients = {} 

def create_app():
    app = Flask(__name__)
    
    # Konfigurasi
    app.config['SECRET_KEY'] = 'kriptografi-itu-asik-ya' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db' 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads') 
    
    # jika ngga ada maka buat
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Inisialisasi DB
    db.init_app(app) 

    # Inisialisasi SocketIO
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
        db.create_all() 

    return app

if __name__ == '__main__':
    app = create_app()
    
    print(" * Menjalankan server Flask-SocketIO dengan eventlet...")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)