from models.user import create_user
from models.images import create_image
async def add_new_user():
    image_path = "/Users/manuelaleman/Desktop/face_recognition/dataset/Manuel Berrelleza/Jesus Manuel Berrelleza Aleman.png"
    
    user = await create_user(
        nControl="21170263",
        name="Jesus Manuel Berrelleza Aleman", 
        email="manuelpluma230@gmail.com", 
        role="Estudiante", 
        career="Sistemas", 
        image_path=image_path
    )

    print(f"User addes successfully : {user.nControl} - {user.name} - {user.email} - {user.career}")

    await create_image(user_id=user.id, image_path=image_path)