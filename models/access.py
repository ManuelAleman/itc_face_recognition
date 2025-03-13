from config.db import db

from datetime import datetime, timedelta, timezone

async def create_access(user_id: str):
    client = db.get_client()
    
    cooldown_time = timedelta(seconds=5)  
    now = datetime.now(timezone.utc)

    last_access = await client.access.find_first(
        where={"userId": user_id},
        order={"timestamp": "desc"} 
    )
    user = await client.user.find_first(where={"nControl": user_id})
    if last_access and (now - last_access.timestamp).total_seconds() < cooldown_time.total_seconds():
        print(f"⏳ Acceso no registrado (espera {cooldown_time.seconds} segundos) - Usuario: {user.name}")
        return None  

    access = await client.access.create(
        data={"userId": user_id}
    )


    print(f"✅ Acceso registrado para el usuario: {user.name}")
    return access


async def get_last_access_from_user(user_id: str):
    client = db.get_client()
    access_records = await client.access.find_many(
        where={'userId': user_id}
    )
    access_records.sort(key=lambda x: x.timestamp, reverse=True)
    return access_records[0] if access_records else None

async def log_unauthorized_access(imagePath: str):
    client = db.get_client()
    
    unauthorize_access = await client.unauthorizedaccess.create( 
        data= {
            "imagePath": imagePath
        }
    )
    return unauthorize_access
