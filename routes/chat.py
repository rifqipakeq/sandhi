# /routes/chat.py
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, current_app
from models import db, User, Message
from werkzeug.utils import secure_filename
import os
from encryption.des_file import encrypt_file_des
from encryption.dwt_stego import stego_embed_dwt
from encryption.affine_xor import encrypt_text_super

chat_bp = Blueprint('chat', __name__)

# Middleware sederhana untuk cek login
@chat_bp.before_request
def require_login():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@chat_bp.route('/')
def chat_room():
    # Halaman chat utama
    users = User.query.filter(User.id != session['user_id']).all()
    return render_template('chat.html', current_user=session['username'], users=users)

@chat_bp.route('/upload_file', methods=['POST'])
def upload_file():
    """
    Menangani upload file (gambar stego atau file DES).
    Ini BUKAN WebSocket, tapi rute HTTP standar.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    upload_type = request.form.get('type') # 'image' atau 'file'
    recipient_id = request.form.get('recipient_id')
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if not recipient_id:
        return jsonify({'error': 'No recipient'}), 400

    filename = secure_filename(file.filename)
    raw_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(raw_path) # Simpan file asli sementara
    
    encrypted_path = ""
    message_type = ""
    
    try:
        if upload_type == 'image':
            # Ini untuk DWT Steganography
            message_to_hide = request.form.get('stego_message', 'Pesan rahasia')
            encrypted_path = stego_embed_dwt(raw_path, message_to_hide)
            message_type = 'image'
            
        elif upload_type == 'file':
            # Ini untuk Enkripsi DES
            with open(raw_path, 'rb') as f:
                file_data = f.read()
            encrypted_data = encrypt_file_des(file_data)
            
            encrypted_path = raw_path + ".des" # Simpan file terenkripsi
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            message_type = 'file'
        
        else:
            return jsonify({'error': 'Invalid upload type'}), 400

        # Hapus file asli
        os.remove(raw_path)

        if not encrypted_path:
             return jsonify({'error': 'Encryption failed'}), 500

        # Simpan path ke DB
        new_message = Message(
            sender_id=session['user_id'],
            receiver_id=recipient_id,
            message_type=message_type,
            encrypted_content=os.path.basename(encrypted_path) # Hanya simpan nama file
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Kirim notifikasi via WebSocket (dijelaskan di chat_ws.py)
        # Kita perlu mengimpor socketio, tapi itu bisa menyebabkan circular import.
        # Cara lebih baik: panggil fungsi dari app.py
        from app import socketio, clients
        recipient_sid = clients.get(int(recipient_id))
        
        message_data = {
            'sender_username': session['username'],
            'type': message_type,
            'content': os.path.basename(encrypted_path),
            'timestamp': new_message.timestamp.isoformat()
        }
        
        # Kirim ke penerima jika online
        if recipient_sid:
            socketio.emit('new_message', message_data, room=recipient_sid)
        
        # Kirim juga ke diri sendiri (untuk UI)
        my_sid = clients.get(session['user_id'])
        if my_sid:
             socketio.emit('new_message', message_data, room=my_sid)

        return jsonify({'status': 'success', 'path': os.path.basename(encrypted_path)})

    except Exception as e:
        # Hapus file asli jika gagal
        if os.path.exists(raw_path):
            os.remove(raw_path)
        return jsonify({'error': str(e)}), 500