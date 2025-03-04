from config.db import db

async def create_access(user_id: str):
    
    client = db.get_client()

    
    access = await client.access.create(
        data={
            'userId': user_id
        }
    )

    print(f"Acceso registrado para el usuario: {user_id}")
    return access
