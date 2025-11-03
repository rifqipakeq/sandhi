# /routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db, User
from encryption.md5_login import hash_password_md5

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

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah ada.', 'warning')
            return redirect(url_for('auth.register'))
            
        hashed_password = hash_password_md5(password)
        
        # Buat user baru dan simpan data terenkripsi (Blowfish)
        new_user = User(username=username, password_hash=hashed_password)
        new_user.profile_data = f"Data profil rahasia untuk {username}" # Contoh data
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

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