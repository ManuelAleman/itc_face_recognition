from models.user import create_user
from models.images import create_image
import pandas as pd
import os
async def add_new_user():
    image_path = "/Users/manuelaleman/Desktop/face_recognition/dataset/Carlos Daniel Beltran Medina.jpg"
    
    user = await create_user(
        nControl="18161083",
        name="Carlos Daniel Beltran Medina", 
        email="beltranmed.carlos03@gmail.com", 
        role="Estudiante", 
        career="Sistemas", 
    )
    print(f"User added successfully : {user.nControl} - {user.name} - {user.email} - {user.career}")

    await create_image(user_id=user.id, image_path=image_path)


async def add_users_from_dataset():
    data = pd.read_excel("/Users/manuelaleman/Desktop/face_recognition/Datos_Investigacion.xlsx")
    image_folder_path = "/Users/manuelaleman/Desktop/face_recognition/imagenes"
    
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
                    if img_file.endswith(".jpg"):
                        image_path = os.path.join(user_folder, img_file)
                        await create_image(user_id=user.id, image_path=image_path)
                
            except Exception as e:
                print(f"Error occurred while adding user {row.nControl}: {e}")
        else:
            print(f"No folder found for user {row.name}.")
    
    print("All users and images added successfully.")
