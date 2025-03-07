from models.user import create_user
from models.images import create_image
async def add_new_user():
    image_path = "/Users/manuelaleman/Desktop/face_recognition/dataset/Carlos_Beltran/Carlos_Daniel_Beltran_Medina.png"
    
    user = await create_user(
        nControl="21170259",
        name="Carlos Daniel Beltran Medina", 
        email="beltranmed.carlos03@gmail.com", 
        role="Estudiante", 
        career="Sistemas", 
        image_path=image_path
    )

    print(f"User added successfully : {user.nControl} - {user.name} - {user.email} - {user.career}")

    await create_image(user_id=user.id, image_path=image_path)