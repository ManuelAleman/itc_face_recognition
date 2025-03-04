from config.db import db

async def create_image(user_id: str, image_path: str):
    client = db.get_client()

    image = await client.image.create(
        data={
            'userId': user_id,
            'imagePath': image_path,
        }
    )

    print(f"Imagen registrada para el usuario: {user_id}")
    return image
