# /websocket/chat_ws.py
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from models import db, Message, User
# from encryption.affine_xor import encrypt_text_super

def register_socket_handlers(socketio, clients):

    @socketio.on('connect')
    def handle_connect():
        if 'user_id' not in session:
            return False # Tolak koneksi jika belum login
            
        user_id = session['user_id']
        clients[user_id] = request.sid # Simpan SID (Socket ID)
        
        # Kirim daftar pengguna yang online
        online_user_ids = list(clients.keys())
        emit('update_user_list', {'online_users': online_user_ids}, broadcast=True)
        print(f"Client connected: {session['username']} (SID: {request.sid})")
        print(f"Current clients: {clients}")

    @socketio.on('disconnect')
    def handle_disconnect():
        if 'user_id' in session:
            user_id = session['user_id']
            if user_id in clients:
                del clients[user_id] # Hapus SID
                
            # Kirim update daftar pengguna
            online_user_ids = list(clients.keys())
            emit('update_user_list', {'online_users': online_user_ids}, broadcast=True)
            print(f"Client disconnected: {session['username']}")
            print(f"Current clients: {clients}")

    @socketio.on('send_message')
    def handle_send_message(data):
        """
        Menangani pesan TEKS. File/Gambar ditangani via rute HTTP.
        """
        if 'user_id' not in session:
            return
            
        sender_id = session['user_id']
        sender_username = session['username']
        recipient_id = int(data['recipient_id'])
        plaintext = data['message']
        
        # 1. Enkripsi pesan (Super Encryption)
        # encrypted_text = encrypt_text_super(plaintext)
        
        # 2. Simpan ke database
        new_message = Message(
            sender_id=sender_id,
            receiver_id=recipient_id,
            message_type='text',
            # encrypted_content=encrypted_text
            encrypted_content=plaintext
        )
        db.session.add(new_message)
        db.session.commit()
        
        # Data untuk dikirim ke klien
        message_data = {
            'sender_username': sender_username,
            'type': 'text',
            'content': plaintext, # Kirim teks terenkripsi
            'timestamp': new_message.timestamp.isoformat()
        }

        # 3. Kirim ke penerima (jika online)
        recipient_sid = clients.get(recipient_id)
        if recipient_sid:
            socketio.emit('new_message', message_data, room=recipient_sid)
            
        # 4. Kirim kembali ke pengirim (untuk ditampilkan di UI)
        socketio.emit('new_message', message_data, room=request.sid)

    @socketio.on('request_chat_history')
    def handle_chat_history(data):
        """Mengirim riwayat chat saat user memilih chat lain."""
        if 'user_id' not in session:
            return
        
        my_id = session['user_id']
        other_user_id = int(data['other_user_id'])
        
        messages = Message.query.filter(
            ((Message.sender_id == my_id) & (Message.receiver_id == other_user_id)) |
            ((Message.sender_id == other_user_id) & (Message.receiver_id == my_id))
        ).order_by(Message.timestamp.asc()).all()
        
        history = []
        for msg in messages:
            sender = User.query.get(msg.sender_id)
            history.append({
                'sender_username': sender.username,
                'type': msg.message_type,
                'content': msg.encrypted_content,
                'original_filename': msg.original_filename,
                'timestamp': msg.timestamp.isoformat()
            })
            
        emit('chat_history', history, room=request.sid)