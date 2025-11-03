# /routes/decrypt.py
from flask import (
    Blueprint, request, jsonify, current_app, 
    send_from_directory, session, send_file, abort
)
from encryption.affine_xor import encrypt_text_super, decrypt_text_super
from encryption.des_file import decrypt_file_des
from encryption.dwt_stego import stego_extract_dwt
import os
from io import BytesIO
import mimetypes

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

# --- FUNGSI BARU UNTUK MELAYANI FILE (LEBIH EFISIEN) ---

def serve_decrypted_des_file(filename, as_attachment):
    """
    Fungsi helper untuk mendekripsi dan mengirim file DES,
    baik sebagai tampilan (attachment=False) atau download (attachment=True).
    """
    if not filename or not filename.endswith('.des'):
        abort(400, "Invalid filename")

    encrypted_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(encrypted_path):
        abort(404, "File not found")
        
    try:
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
            
        decrypted_data = decrypt_file_des(encrypted_data)
        
        if decrypted_data is None:
            abort(500, "Decryption failed")
            
        # Tentukan nama asli dan mimetype
        original_filename = filename[:-4] # Hapus .des
        mimetype = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        
        return send_file(
            BytesIO(decrypted_data),
            mimetype=mimetype,
            as_attachment=as_attachment,
            download_name=original_filename
        )
        
    except Exception as e:
        print(f"Error serving decrypted file: {e}")
        abort(500)

@decrypt_bp.route('/view_file')
def view_decrypted_file():
    """
    Mendekripsi file DES on-the-fly untuk <img src="...">.
    """
    filename = request.args.get('filename')
    return serve_decrypted_des_file(filename, as_attachment=False)

# @decrypt_bp.route('/download_decrypted_file', methods=['GET'])
# def download_decrypted_file():
#     """
#     Mendekripsi file DES on-the-fly untuk di-download.
#     (Versi perbaikan: tidak pakai temp file)
#     """
#     filename = request.args.get('filename')
#     return serve_decrypted_des_file(filename, as_attachment=True)  

@decrypt_bp.route('/download_decrypted_file', methods=['GET'])
def download_decrypted_file():
    """
    (REVISI) Mengirim file .des MENTAH (terenkripsi) untuk di-download.
    """
    filename = request.args.get('filename')
    
    # Validasi tetap penting
    if not filename or not filename.endswith('.des'):
        abort(400, "Invalid filename")
        
    try:
        # Mengirim file mentah langsung dari folder UPLOAD_FOLDER
        return send_from_directory(
            current_app.config['UPLOAD_FOLDER'],
            filename,
            as_attachment=True
        )
    except FileNotFoundError:
        abort(404, "File not found") 