import face_recognition
from config.db import db
from models.user import get_user_by_face_id


async def verify_access(image_path: str):
    await db.connect()

    image_to_validate = face_recognition.load_image_file(image_path)
    encodings_to_validate = face_recognition.face_encodings(image_to_validate)

    if len(encodings_to_validate) > 0:
        encoding_to_validate = encodings_to_validate[0]
        
        user = await get_user_by_face_id(encoding_to_validate.tolist())

        if user:
            if user.faceEncoding:
                stored_face_encoding = user.faceEncoding

                results = face_recognition.compare_faces([stored_face_encoding], encoding_to_validate)

                if results[0]:
                    print(f"Acceso autorizado para el usuario: {user.name} de la carrera de {user.carreer}.")
                else:
                    print("Acceso denegado: Las caras no coinciden.")
            else:
                print("Acceso denegado: No se encontró ninguna imagen registrada para el usuario.")
        else:
            print("Acceso denegado: No se encontró un usuario con ese `faceId`.")
    else:
        print("Acceso denegado: No se detectó ninguna cara en la imagen proporcionada.")

    await db.disconnect()
