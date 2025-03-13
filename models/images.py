import face_recognition
import json
from config.db import db
def generate_face_encoding(image_path: str):
    image = face_recognition.load_image_file(image_path)
    face_encodings = face_recognition.face_encodings(image)

    if len(face_encodings) > 0:
        return face_encodings[0]  
    else:
        raise Exception("No se detectó ninguna cara en la imagen. " + image_path)
    
async def create_image(user_id: str, image_path: str):
    face_encoding = generate_face_encoding(image_path)
    
    face_encoding_json = json.dumps(face_encoding.tolist())  
    client = db.get_client()
    image = await client.image.create(
        data={
            'userId': user_id,
            'imagePath': image_path,
            'faceEncoding': face_encoding_json,
        }
    )
    return image

async def get_images():
    client = db.get_client()
    images = await client.image.find_many(
        include={
            'user': True,
        }
    )

    return images
