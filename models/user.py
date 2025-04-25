import face_recognition
from config.db import db
import numpy as np


async def create_user(nControl: str, name: str, email: str, role: str, career: str):

    client = db.get_client()
    user = await client.user.create(
        data={
            'nControl': nControl,
            'name': name,
            'email': email,
            'role': role,
            'career': career,
        }
    )
    return user

async def delete_user(nControl: str):
    client = db.get_client()
    await client.user.delete(where={'nControl': nControl})

async def get_user_by_face_encodingd(face_encoding_list: list):
    client = db.get_client()
    
    images = await client.image.find_many()

    min_distance = 0.6
    best_match = None

    for image in images:
        stored_encoding = np.array(image.faceEncoding)
        distance = np.linalg.norm(np.array(face_encoding_list) - stored_encoding) 

        if distance < min_distance:
            min_distance = distance
            best_match = image.user 

    return best_match

async def get_user_by_name(name: str):
    client = db.get_client()
    user = await client.user.find_first(where={'name': name})
    return user

async def get_user_info(user_id: str):
    client = db.get_client()
    user = await client.user.find_first(where={'nControl': user_id})
    return user