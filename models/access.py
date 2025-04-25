from config.db import db

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

async def create_access(user_id: str, classroom_id = None):
    client = db.get_client()
    
    cooldown_time = timedelta(seconds=5)  
    now = datetime.now(timezone.utc)

    last_access = await client.access.find_first(
        where={"userId": user_id},
        order={"listTime": "desc"} 
    )
    user = await client.user.find_first(where={"nControl": user_id})
    if last_access and (now - last_access.timestamp).total_seconds() < cooldown_time.total_seconds():
        print(f"⏳ Acceso no registrado (espera {cooldown_time.seconds} segundos) - Usuario: {user.name}")
        return None  

    zona_local = ZoneInfo("America/Mazatlan")
    hora_local = datetime.now(tz=zona_local)
    hora_utc = hora_local.astimezone(ZoneInfo("UTC"))
    print(hora_utc)
    access = await client.access.create(
        data={
            "userId": user_id,
            "classroomId": classroom_id,
            "listTime": hora_utc
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
            "listTime": {
                "gte": datetime.strptime(date, "%Y-%m-%d"),
                "lt": datetime.strptime(date, "%Y-%m-%d") + timedelta(days=1)
            }
        },
        include={
            "user": {
                "select": {
                    "name": True,
                    "nControl": True
                }
            },
            "classroomFK": {
                "select": {
                    "subject": True,
                    "room": True
                }
            }
        },
        order={"listTime": "asc"}

    )
    return access_records
