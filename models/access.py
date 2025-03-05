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

async def get_last_access_from_user(user_id: str):
    client = db.get_client()
    access_records = await client.access.find_many(
        where={'userId': user_id}
    )
    access_records.sort(key=lambda x: x.timestamp, reverse=True)
    return access_records[0] if access_records else None
