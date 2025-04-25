from config.db import db
from datetime import datetime

async def create_classroom(subject: str, room: str, teacher: str, schedule):
    client = db.get_client()
    fecha_base = datetime(2025, 4, 24)
    schedule_dt = datetime.combine(fecha_base.date(), datetime.strptime(schedule, "%H:%M").time())
    classroom = await client.classroom.create(
        data={
            'subject': subject,
            'room': room,
            'schedule': schedule_dt,
            'teacherId': teacher,
        }
    )
    return classroom

async def get_classrooms():
    client = db.get_client()
    classrooms = await client.classroom.find_many()
    return classrooms