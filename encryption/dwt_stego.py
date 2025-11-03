# /encryption/dwt_stego.py
import numpy as np
import pywt
from PIL import Image

# ubah pesan menjadi list bit
def _to_bits(message: str) -> list:
    bits = []
    for char in message:
        bin_val = bin(ord(char))[2:].zfill(8)
        bits.extend([int(b) for b in bin_val])
    # Tambahkan delimiter 8-bit null untuk menandai akhir pesan
    bits.extend([0] * 8)
    return bits

# ubah list menjadi string
def _from_bits(bits: list) -> str:
    chars = []
    for i in range(0, len(bits), 8):
        byte_bits = bits[i:i+8]
        # Jika bertemu delimiter (8 bit nol), berhenti
        if sum(byte_bits) == 0:
            break
        byte_val = int("".join(map(str, byte_bits)), 2)
        chars.append(chr(byte_val))
    return "".join(chars)

def _embed_bits_to_coeffs(coeffs, bits):
    """
    Menyisipkan bit ke koefisien DWT menggunakan LSB.
    (VERSI PERBAIKAN: Bekerja pada integer)
    """
    # 1. Konversi float ke integer
    coeffs_int = np.round(coeffs).astype(np.int32)
    coeffs_flat = coeffs_int.flatten()

    if len(bits) > len(coeffs_flat):
        raise ValueError("Pesan terlalu besar untuk disembunyikan di sub-band gambar ini.")
    
    for i, bit in enumerate(bits):
        # 2. Lakukan LSB pada integer
        coeffs_flat[i] = (coeffs_flat[i] & ~1) | bit
    
    # 3. Ubah kembali ke float untuk Inverse DWT
    return coeffs_flat.reshape(coeffs.shape).astype(np.float32)

def _extract_bits_from_coeffs(coeffs, max_len):
    """
    Mengekstrak bit LSB dari koefisien DWT.
    (VERSI PERBAIKAN: Bekerja pada integer)
    """
    bits = []
    # 1. Konversi float ke integer (harus konsisten)
    coeffs_int = np.round(coeffs).astype(np.int32)
    coeffs_flat = coeffs_int.flatten()
    
    for i in range(max_len):
        # 2. Ekstrak LSB dari integer
        bits.append(int(coeffs_flat[i]) & 1)
        
        # Cek delimiter
        if len(bits) >= 8 and sum(bits[-8:]) == 0:
            break
            
    if len(bits) < 8:
        return [] # Tidak ada delimiter ditemukan
        
    return bits[:-8] # Hapus delimiter

# hidden secret message to image with dwt-stegano
def stego_embed_dwt(image_path: str, message: str) -> str:
    try:
        img = Image.open(image_path).convert('YCbCr')
        img_data = np.array(img, dtype=np.float32)
        
        # Ambil channel Y (Luminance)
        y = img_data[:, :, 0]
        
        # Terapkan DWT (Haar)
        coeffs = pywt.dwt2(y, 'haar')
        cA, (cH, cV, cD) = coeffs # cA=Approximation, cH=Horizontal, cV=Vertical, cD=Diagonal
        
        # Konversi pesan ke bits
        bits = _to_bits(message)
        
        # Sematkan pesan di sub-band cD (Diagonal)
        # (Bisa juga di cH atau cV jika kapasitas lebih besar diperlukan)
        cD_stego = _embed_bits_to_coeffs(cD, bits)
        
        # Rekonstruksi gambar (Inverse DWT)
        coeffs_stego = cA, (cH, cV, cD_stego)
        y_stego = pywt.idwt2(coeffs_stego, 'haar')
        
        # Pastikan dimensi sama dengan channel Y asli
        y_stego = y_stego[:y.shape[0], :y.shape[1]]
        
        # Buat data gambar stego baru
        img_data_stego = img_data.copy()
        img_data_stego[:, :, 0] = y_stego
        
        # Konversi kembali ke format gambar yang bisa disimpan
        img_data_stego = np.uint8(np.clip(img_data_stego, 0, 255))
        stego_img = Image.fromarray(img_data_stego, 'YCbCr').convert('RGB')
        
        # Simpan sebagai PNG agar tidak ada lossy compression
        stego_image_path = image_path.rsplit('.', 1)[0] + '_stego.png'
        stego_img.save(stego_image_path, 'PNG')
        return stego_image_path
    
    except Exception as e:
        print(f"Error embedding DWT: {e}")
        return None

def stego_extract_dwt(stego_image_path: str) -> str:
    """
    Mengekstrak pesan teks dari gambar stego DWT.
    """
    try:
        img = Image.open(stego_image_path).convert('YCbCr')
        img_data = np.array(img, dtype=np.float32)
        
        # Ambil channel Y
        y = img_data[:, :, 0]
        
        # Terapkan DWT
        coeffs = pywt.dwt2(y, 'haar')
        cA, (cH, cV, cD) = coeffs
        
        # Ekstrak bit dari sub-band cD
        max_len = cD.shape[0] * cD.shape[1]
        bits = _extract_bits_from_coeffs(cD, max_len)
        
        # Konversi bits ke pesan
        message = _from_bits(bits)
        return message
    
    except Exception as e:
        print(f"Error extracting DWT: {e}")
        return "Extraction Failed"