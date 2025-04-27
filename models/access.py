from config.db import db

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

async def create_access(user_id: str, classroom_id = None):
    client = db.get_client()
    
    cooldown_time = timedelta(seconds=5)  
    now = datetime.now(timezone.utc)

    last_access = await client.access.find_first(
        where={"userId": user_id},
        order={"accessTime": "desc"} 
    )
    user = await client.user.find_first(where={"nControl": user_id})
    if last_access and (now - last_access.accessTime).total_seconds() < cooldown_time.total_seconds():
        print(f"⏳ Acceso no registrado (espera {cooldown_time.seconds} segundos) - Usuario: {user.name}")
        return None  

    local_time = datetime.now(ZoneInfo("America/Mazatlan"))
    print(f"🕒 Hora local: {local_time}")
    local_time = local_time.replace(tzinfo=timezone.utc).astimezone(ZoneInfo("America/Mazatlan"))

    access = await client.access.create(
        data={
            "userId": user_id,
            "classroomId": classroom_id,
            "accessTime": local_time,
        }

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

async def get_access_by_classroom_and_date(classroom_id: str, date: str):
    client = db.get_client()
    access_records = await client.access.find_many(
        where={
            "classroomId": classroom_id,
            "accessTime": {
                "gte": datetime.strptime(date, "%m/%d/%Y"),
                "lt": datetime.strptime(date, "%m/%d/%Y") + timedelta(days=1)
            }
        },
        include={
            "user": True,
            "classroom": True
        },
        order={"accessTime": "asc"}

    )
    return access_records
