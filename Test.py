import asyncio
import os
from .config.db import db
from models.user import create_user
from models.images import create_image
import pandas as pd
async def main():
    await db.connect()
    
    
    await add_users_from_dataset()

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
                    if img_file.lower().endswith(".jpg"):
                        image_path = os.path.join(user_folder, img_file)
                        await create_image(user_id=user.nControl, image_path=image_path)
                
            except Exception as e:
                print(f"Error occurred while adding user {row.nControl}: {e}")
        else:
            print(f"No folder found for user {row.name}.")
    
    print("All users and images added successfully.")

if __name__ == "__main__":
    asyncio.run(main())

