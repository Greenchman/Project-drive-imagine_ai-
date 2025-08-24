import face_recognition
import numpy as np
from .models import Image

# Find smiling or dancing faces (custom function placeholder)
def find_smiling_faces():
    # This would ideally use an ML model for detecting smiles
    return Image.objects.all()  # Placeholder: return all images

def find_dancing_people():
    # Placeholder for an ML model detecting dancing
    return Image.objects.all()  # Placeholder: return all images

# Find user's face in images
def find_user_in_images(uploaded_image_path):
    # Load the uploaded image (from the user)
    uploaded_image = face_recognition.load_image_file(uploaded_image_path)
    uploaded_encoding = face_recognition.face_encodings(uploaded_image)

    if not uploaded_encoding:
        return []  # No face found in the uploaded image

    uploaded_encoding = uploaded_encoding[0]
    
    matching_images = []
    for img in Image.objects.exclude(face_encoding=None):
        # Load face encoding from the database
        stored_encoding = np.frombuffer(img.face_encoding, dtype=np.float64)

        # Compare the uploaded image encoding with stored encoding
        match_results = face_recognition.compare_faces([stored_encoding], uploaded_encoding)

        if match_results[0]:  # If a match is found
            matching_images.append(img)

    return matching_images
