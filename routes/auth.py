# /routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db, User
from encryption.md5_login import hash_password_md5
from encryption.face_auth import verify_face
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = hash_password_md5(password)
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.password_hash == hashed_password:
            # Simpan user di sesi
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Login berhasil!', 'success')
            return redirect(url_for('chat.chat_room'))
        else:
            flash('Username atau password salah.', 'danger')
    return render_template('login.html')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
        
#         if User.query.filter_by(username=username).first():
#             flash('Username sudah ada.', 'warning')
#             return redirect(url_for('auth.register'))
            
#         hashed_password = hash_password_md5(password)
        
#         # Buat user baru dan simpan data terenkripsi (Blowfish)
#         new_user = User(username=username, password_hash=hashed_password)
#         new_user.profile_data = f"Data profil rahasia untuk {username}" # Contoh data
        
#         db.session.add(new_user)
#         db.session.commit()
        
#         flash('Registrasi berhasil! Silakan login.', 'success')
#         return redirect(url_for('auth.login'))
#     return render_template('register.html')

@auth_bp.route('/register', methods=['GET'])
def register():
    return render_template('register.html')

@auth_bp.route('/register_face', methods=['POST'])
def register_face():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    descriptors_json = data.get('descriptors') 

    if not username or not password or not descriptors_json:
        return jsonify({'status': 'error', 'message': 'Data tidak lengkap'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'status': 'error', 'message': 'Username sudah ada'}), 400
        
    hashed_password = hash_password_md5(password)
    
    new_user = User(username=username, password_hash=hashed_password)
    # new_user.profile_data = f"Profil untuk {username}" # Contoh data
    
    new_user.face_descriptors = descriptors_json
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': 'Registrasi berhasil!'})

@auth_bp.route('/login_face', methods=['POST'])
def login_face():
    data = request.json
    username = data.get('username')
    descriptor_json = data.get('descriptor') 

    if not username or not descriptor_json:
        return jsonify({'status': 'error', 'message': 'Username atau data wajah tidak ada'}), 400
        
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({'status': 'error', 'message': 'Username tidak ditemukan'}), 404
        
    if not user.face_descriptors:
        return jsonify({'status': 'error', 'message': 'User ini tidak terdaftar menggunakan wajah'}), 400
        
    try:
        saved_descriptors = json.loads(user.face_descriptors) 
        new_descriptor = json.loads(descriptor_json) 
    except json.JSONDecodeError:
        return jsonify({'status': 'error', 'message': 'Format data wajah korup'}), 500

    is_match = verify_face(new_descriptor, saved_descriptors)
    
    if is_match:
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'status': 'success', 'message': 'Login wajah berhasil!'})
    else:
        return jsonify({'status': 'error', 'message': 'Wajah tidak dikenali'}), 401

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('chat.chat_room'))
    return redirect(url_for('auth.login'))