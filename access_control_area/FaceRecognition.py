import cv2
import face_recognition
import numpy as np
import time
from models.images import get_images
from models.access import create_access
from models.user import get_user_info  
import os

class FaceRecognition:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la cámara.")
        
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        self.verification_time = 3
        self.user_verification_time = {}
        self.access_granted_time = None
        self.access_cooldown = 5
        self.unauthorized_attempts = 0  
        self.unauthorized_attempts_threshold = 3  
        self.unauthorized_reset_time = 10  
        self.last_alert_time = 0  
        self.alert_cooldown_time = 5  

        self.alert_folder = "img/unauthorized_attemps"
        if not os.path.exists(self.alert_folder):
            os.makedirs(self.alert_folder)

    async def load_known_faces(self):
        images = await get_images()
        self.known_face_encodings = [img.faceEncoding for img in images]
        self.known_face_names = [img.user.name for img in images]
        self.known_face_ids = [img.user.id for img in images]

    async def recognize_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations) if face_locations else []
        
        status_text = "Espera..."
        user_info = None
        detected_face_ids = []

        if self.access_granted_time is None or (time.time() - self.access_granted_time) >= self.access_cooldown:
            for face_encoding, face_location in zip(face_encodings, face_locations):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances) if matches else None
                
                THRESHOLD = 0.5
                if best_match_index is not None and matches[best_match_index] and face_distances[best_match_index] < THRESHOLD:
                    user_id = self.known_face_ids[best_match_index]
                    user_name = self.known_face_names[best_match_index]

                    if user_info is None:
                        user_info = await get_user_info(user_id)

                    if user_id not in self.user_verification_time:
                        self.user_verification_time[user_id] = time.time()

                    time_elapsed = time.time() - self.user_verification_time[user_id]
                    time_remaining = max(0, self.verification_time - time_elapsed)

                    if time_elapsed >= self.verification_time:
                        await create_access(user_id)
                        status_text = f"✅ Acceso concedido a: {user_name}"
                        self.user_verification_time.pop(user_id)
                        self.access_granted_time = time.time()
                        self.unauthorized_attempts = 0
                    else:
                        status_text = f"🔄 Verificando usuario... Espera {int(time_remaining)} segundos"

                    detected_face_ids.append(user_id)

                else:
                    self.unauthorized_attempts += 1
                    status_text = "⛔ Usuario no autorizado"
                    
                    if self.unauthorized_attempts >= self.unauthorized_attempts_threshold:
                        status_text = "🚨 ¡ALERTA! Múltiples intentos fallidos"
                        self.trigger_alert(frame)

            for user_id in list(self.user_verification_time.keys()):
                if user_id not in detected_face_ids:
                    self.user_verification_time[user_id] = time.time()

        return status_text, user_info

    def trigger_alert(self, frame):
        current_time = time.time()
        if current_time - self.last_alert_time < self.alert_cooldown_time:
            return

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.alert_folder, f"unauthorized_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        print(f"🚨 Alerta activada: Imagen guardada como {filename}")

        self.last_alert_time = current_time
