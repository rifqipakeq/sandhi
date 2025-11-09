# /encryption/face_auth.py
import math

FACE_RECOGNITION_THRESHOLD = 0.4 

def compute_euclidean_distance(desc1, desc2):
    """
    Menghitung jarak euclidean antara dua face descriptors (list 128-float).
    """
    if len(desc1) != 128 or len(desc2) != 128:
        return 2.0 # Kembalikan jarak yang besar jika data tidak valid
        
    distance = sum([(a - b) ** 2 for a, b in zip(desc1, desc2)])
    return math.sqrt(distance)

def verify_face(new_descriptor, saved_descriptors_list):
    """
    Memverifikasi 1 descriptor baru terhadap daftar descriptor tersimpan.
    """
    for saved_desc in saved_descriptors_list:
        distance = compute_euclidean_distance(new_descriptor, saved_desc)
        if distance < FACE_RECOGNITION_THRESHOLD:
            # Ditemukan kecocokan!
            return True
            
    # Tidak ada descriptor tersimpan yang cocok
    return False