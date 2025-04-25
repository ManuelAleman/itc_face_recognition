import asyncio
import os
from config.db import db
from models.user import create_user, get_user_by_name
from models.classroom import create_classroom
from models.images import create_image
import pandas as pd
async def main():
    await db.connect()
    
    await add_users_from_dataset()
    await add_classroom_from_dataset()

    await db.disconnect()


async def add_users_from_dataset():
    data = pd.read_excel("Datos_Investigacion.xlsx")
    image_folder_path = "img/users"
    
    for row in data.itertuples(index=False):
        user_name = row.name.lower()
        user_folder = None
        for subfolder in os.listdir(image_folder_path):
            if user_name in subfolder.lower():
                user_folder = os.path.join(image_folder_path, subfolder)
                break

        if user_folder:
            try:
                user = await create_user(
                    nControl=str(row.nControl),
                    name=row.name, 
                    email=row.email, 
                    role=row.role, 
                    career=row.career,
                )
                
                for img_file in os.listdir(user_folder):
                    if img_file.lower().endswith(("jpg", "jpeg", "png")):
                        image_path = os.path.join(user_folder, img_file)
                        await create_image(user_id=user.nControl, image_path=image_path)
                
            except Exception as e:
                print(f"Error occurred while adding user {row.nControl}: {e}")
        else:
            print(f"No folder found for user {row.name}.")
    
    print("All users and images added successfully.")

async def add_classroom_from_dataset():
    data = pd.read_excel("Datos_Salones.xlsx")
    for row in data.itertuples(index=False):
        try:
            teacher = await get_user_by_name(row.teacher)
            if not teacher:
                print(f"Teacher {row.teacher} not found in the database.")
                continue
            await create_classroom(
                subject=row.subject,
                room=row.room,
                teacher=teacher.nControl,
                schedule=row.schedule.strftime("%H:%M"),
            )
        except Exception as e:
            print(f"Error occurred while adding classroom {row.subject}: {e}")
    print("All classrooms added successfully.")

if __name__ == "__main__":
    asyncio.run(main())

