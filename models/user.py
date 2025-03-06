import face_recognition
from config.db import db
import numpy as np
def generate_face_encoding(image_path: str):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) > 0:
        return face_encodings[0]
    else:
        raise Exception("No se detectó ninguna cara en la imagen.")


async def create_user(nControl: str, name: str, email: str, role: str, career: str, image_path: str):
    face_encoding = generate_face_encoding(image_path)
    
    face_encoding_list = face_encoding.tolist()

    client = db.get_client()
    user = await client.user.create(
        data={
            'nControl': nControl,
            'name': name,
            'email': email,
            'role': role,
            'career': career,
            'faceEncoding': face_encoding_list,
        }
    )
    return user



async def get_user_by_face_encodingd(face_encoding_list: list):
    client = db.get_client()
    
    users = await client.user.find_many()
    
    min_distance = 0.6
    best_match = None

    for user in users:
        stored_encoding = np.array(user.faceEncoding)
        distance = np.linalg.norm(np.array(face_encoding_list) - stored_encoding) 

        if distance < min_distance:
            min_distance = distance
            best_match = user

    return best_match


async def get_all_users_encodings():
    client = db.get_client()
    users = await client.user.find_many()
    
    return users