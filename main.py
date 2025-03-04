import asyncio
from config.db import db
from models.user import create_user
from models.images import create_image
from models.access import create_access
from verify_access import verify_access

async def get_user_by_face_id(face_id: str):
    return await db.get_client().user.find_first(
        where={"faceId": face_id}
    )

async def main():
    await db.connect()
    
    image_path = "/Users/manuelaleman/Desktop/face_recognition/dataset/Carlos_Beltran/IMG_5833.jpg"

    """user = await create_user(
        name="Carlos Daniel Beltran Medina", 
        email="carlosbm@gmail.com", 
        role="Estudiante", 
        career="Sistemas", 
        image_path=image_path
    )"""

    #await create_image(user_id=user.id, image_path=image_path)
    #await create_access(user_id=user.id)
    await verify_access(image_path)

    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
