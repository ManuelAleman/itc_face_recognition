import cv2
import face_recognition
import numpy as np
import logging
from models.images import get_images
from models.access import create_access

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

def liveness_check(face_location, prev_locations):
    """Verifica si la persona se ha movido lo suficiente entre cuadros."""
    if not prev_locations:
        return True
    return any(abs(prev[0] - face_location[0]) > 5 or abs(prev[1] - face_location[1]) > 5 for prev in prev_locations)

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

    prev_face_locations = []
    verification_counts = {}
    granted_access = set()

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

        for face_encoding, face_location in zip(face_encodings, face_locations):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances) if matches else None

            name = "Desconocido"
            liveness = liveness_check(face_location, prev_face_locations)

            if best_match_index is not None and matches[best_match_index]:
                user_id = known_face_ids[best_match_index]
                user_name = known_face_names[best_match_index]

                name = user_name  

                if liveness:
                    verification_counts[user_id] = verification_counts.get(user_id, 0) + 1

                    if verification_counts[user_id] >= 3:  
                        if user_id not in granted_access:
                            granted_access.add(user_id)
                            await create_access(user_id)
                            logging.info(f"✅ Acceso concedido a: {user_name} (ID: {user_id})")

            face_names.append((face_location, name, liveness))

        prev_face_locations = face_locations

        for (top, right, bottom, left), name, liveness in face_names:
            top, right, bottom, left = top * 2, right * 2, bottom * 2, left * 2  
            color = (0, 255, 0) if liveness else (0, 0, 255)  

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow('Reconocimiento Facial', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    logging.info("Cámara apagada.")
