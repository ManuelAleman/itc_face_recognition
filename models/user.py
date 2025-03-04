import face_recognition
from config.db import db

def generate_face_encoding(image_path: str):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) > 0:
        return face_encodings[0]
    else:
        raise Exception("No se detectó ninguna cara en la imagen.")


async def create_user(name: str, email: str, role: str, career: str, image_path: str):
    face_encoding = generate_face_encoding(image_path)
    
    face_encoding_list = face_encoding.tolist()

    client = db.get_client()
    user = await client.user.create(
        data={
            'name': name,
            'email': email,
            'role': role,
            'carreer': career,
            'faceEncoding': face_encoding_list,
        }
    )
    return user


async def get_user_by_face_id(face_encoding_list: list):
    return await db.get_client().user.find_first(
        where={"faceEncoding": {"equals": face_encoding_list}}
    )
