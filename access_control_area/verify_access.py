import cv2
import face_recognition
import numpy as np
import logging
import time
from models.images import get_images
from models.access import create_access

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

async def start_camera():
    images = await get_images()
    known_face_encodings = [img.faceEncoding for img in images]
    known_face_names = [img.user.name for img in images]
    known_face_ids = [img.user.id for img in images]

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logging.error("No se pudo acceder a la cámara.")
        return

    cap.set(3, 640)
    cap.set(4, 480)

    verification_time = 3  
    user_verification_time = {} 
    access_granted_time = None 
    access_cooldown = 5  

    while True:
        ret, frame = cap.read()
        if not ret:
            logging.error("No se pudo capturar el cuadro.")
            break

        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations) if face_locations else []

        face_names = []
        detected_user_id = None

        
        if access_granted_time is None or (time.time() - access_granted_time) >= access_cooldown:
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances) if matches else None

                name = "Verificando..."
                status_text = "Verificando..."

                if best_match_index is not None and matches[best_match_index]:
                    user_id = known_face_ids[best_match_index]
                    user_name = known_face_names[best_match_index]
                    detected_user_id = user_id

                    
                    if user_id not in user_verification_time:
                        user_verification_time[user_id] = time.time()

                    
                    if time.time() - user_verification_time[user_id] >= verification_time:
                        await create_access(user_id)
                        logging.info(f"✅ Acceso concedido a: {user_name} (ID: {user_id})")
                        name = user_name
                        status_text = "Acceso concedido"
                        user_verification_time.pop(user_id) 
                        access_granted_time = time.time()  
                    else:
                        status_text = "Verificando..."
                else:
                    user_verification_time = {k: v for k, v in user_verification_time.items() if v + verification_time > time.time()}

                face_names.append((face_location, name, status_text))

       
        for (face_location, name, status_text) in face_names:
            if face_location:
                top, right, bottom, left = face_location
                top, right, bottom, left = top * 2, right * 2, bottom * 2, left * 2
                color = (0, 255, 0) if name != "Verificando..." else (0, 255, 255)

                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                cv2.putText(frame, status_text, (left, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.imshow('Reconocimiento Facial', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    logging.info("Cámara apagada.")
