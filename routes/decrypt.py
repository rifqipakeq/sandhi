# /routes/decrypt.py
from flask import Blueprint, request, jsonify, current_app, send_from_directory, session
from encryption.affine_xor import decrypt_text_super, encrypt_text_super
from encryption.des_file import decrypt_file_des
from encryption.dwt_stego import stego_extract_dwt
import os

decrypt_bp = Blueprint('decrypt', __name__)

@decrypt_bp.before_request
def require_login():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

@decrypt_bp.route('/text', methods=['POST'])
def decrypt_text():
    ciphertext_b64 = request.json.get('data')
    if not ciphertext_b64:
        return jsonify({'error': 'No data provided'}), 400
        
    plaintext = decrypt_text_super(ciphertext_b64)
    return jsonify({'plaintext': plaintext})

@decrypt_bp.route('/encrypt/text', methods=['POST'])
def encrypt_text():
    plaintext = request.json.get('data')
    if not plaintext:
        return jsonify({'error': 'No data provided'}), 400
    
    ciphertext = encrypt_text_super(plaintext)
    return jsonify({'ciphertext': ciphertext})

@decrypt_bp.route('/image_message', methods=['POST'])
def decrypt_image_message():
    filename = request.json.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
        
    stego_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(stego_image_path):
        return jsonify({'error': 'File not found'}), 404
        
    message = stego_extract_dwt(stego_image_path)
    return jsonify({'extracted_message': message})

@decrypt_bp.route('/download_decrypted_file', methods=['GET'])
def download_decrypted_file():
    filename = request.args.get('filename')
    if not filename:
        return "Filename required", 400
        
    encrypted_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(encrypted_path) or not filename.endswith('.des'):
        return "File not found or invalid", 404
        
    try:
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_data = decrypt_file_des(encrypted_data)
        
        if decrypted_data is None:
            return "Decryption failed", 500
            
        # Tentukan nama file asli (hapus .des)
        original_filename = filename[:-4]
        
        # Simpan file sementara untuk di-download
        temp_decrypted_path = os.path.join(current_app.config['UPLOAD_FOLDER'], "temp_" + original_filename)
        with open(temp_decrypted_path, 'wb') as f:
            f.write(decrypted_data)
            
        # Kirim file untuk di-download, lalu hapus
        response = send_from_directory(
            current_app.config['UPLOAD_FOLDER'], 
            "temp_" + original_filename, 
            as_attachment=True,
            download_name=original_filename
        )
        
        # Gunakan 'after_this_request' untuk menghapus file setelah request selesai
        @current_app.after_request
        def cleanup(response):
            try:
                if os.path.exists(temp_decrypted_path):
                    os.remove(temp_decrypted_path)
            except Exception as e:
                print(f"Error cleaning up temp file: {e}")
            return response
            
        return response
        
    except Exception as e:
        return str(e), 500