import cv2
import face_recognition
import numpy as np
import time
import os
import dlib
from scipy.spatial import distance as dist
from models.images import get_images
from models.access import create_access, log_unauthorized_access
from models.user import get_user_info  
from controllers.ArduinoController import ArduinoController


class FaceRecognition:
    def __init__(self,classroom_id):
        self.classroom_id = classroom_id
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise Exception("No se pudo abrir la cámara.")
        
        self.cap.set(3, 640)
        self.cap.set(4, 480)
        
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_face_ids = []
        
        self.verification_time = 3
        self.access_cooldown = 5
        
        self.unauthorized_attempts = 0  
        self.last_alert_time = 0  
        self.alert_cooldown_time = 5  

        self.last_user_info = None  
        self.arduino = ArduinoController()

        self.alert_folder = "img/unauthorized_attempts"
        if not os.path.exists(self.alert_folder):
            os.makedirs(self.alert_folder)

        self.verification_start_time = None
        self.cooldown_start_time = None
        self.cooldown_status = None

        # Detección de parpadeo
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")
        self.eye_blink_detected = False

    def eye_aspect_ratio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        return (A + B) / (2.0 * C)

    async def load_known_faces(self):
        images = await get_images()
        if images:
            self.known_face_encodings = [img.faceEncoding for img in images]
            self.known_face_names = [img.user.name for img in images]
            self.known_face_ids = [img.userId for img in images]
            print(f"Se cargaron {len(self.known_face_encodings)} imágenes conocidas.")
        else:
            print("No se encontraron imágenes conocidas.")

    async def recognize_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detección de parpadeo
        rects = self.detector(gray, 0)
        for rect in rects:
            shape = self.predictor(gray, rect)
            shape_np = np.zeros((68, 2), dtype="int")
            for i in range(0, 68):
                shape_np[i] = (shape.part(i).x, shape.part(i).y)
            left_eye = shape_np[42:48]
            right_eye = shape_np[36:42]
            left_ear = self.eye_aspect_ratio(left_eye)
            right_ear = self.eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
            EAR_THRESHOLD = 0.21
            if ear < EAR_THRESHOLD:
                self.eye_blink_detected = True
        
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations) if face_locations else []
        current_time = time.perf_counter()

        if self.cooldown_start_time is not None and (current_time - self.cooldown_start_time < self.access_cooldown):
            return self.cooldown_status, self.last_user_info
        if not face_locations:
            self.verification_start_time = None
            return "Esperando...", self.last_user_info

        if self.verification_start_time is None:
            self.verification_start_time = current_time

        time_elapsed = current_time - self.verification_start_time

        if time_elapsed < self.verification_time:
            countdown = int(self.verification_time - time_elapsed)
            return f"🔄 Verificando usuario... {countdown} segundos restantes", self.last_user_info

        # Verifica si hubo parpadeo
        if not self.eye_blink_detected:
            self.cooldown_status = "❌ Acceso denegado (no se detectó parpadeo)"
            await self.arduino.send_display_message("Parpadeo no detectado")
            self.cooldown_start_time = current_time
            await self.trigger_alert(frame)
            self.unauthorized_attempts += 1
            await self.arduino.unauthorize_access()
            self.verification_start_time = None
            return self.cooldown_status, None
        
        valid_face_found = False
        user_info = self.last_user_info

        for face_encoding in face_encodings:
            if not self.known_face_encodings:
                return "No se han cargado rostros conocidos", None

            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else None
            THRESHOLD = 0.5

            if best_match_index is not None and matches[best_match_index] and face_distances[best_match_index] < THRESHOLD:
                valid_face_found = True
                user_id = self.known_face_ids[best_match_index]
                user_name = self.known_face_names[best_match_index]

                if user_info is None or user_info.id != user_id:
                    user_info = await get_user_info(user_id)

                await create_access(user_id,classroom_id=self.classroom_id)
                self.cooldown_status = f"✅ Acceso concedido a: {user_name}"
                await self.arduino.send_display_message({user_name})
                self.cooldown_start_time = current_time
                self.last_user_info = user_info
                await self.arduino.authorize_access()
                break

        if not valid_face_found:
            self.cooldown_status = "❌ Acceso no autorizado"
            await self.arduino.send_display_message("Acceso denegado")
            self.cooldown_start_time = current_time
            await self.trigger_alert(frame)
            self.unauthorized_attempts += 1
            await self.arduino.unauthorize_access()

        self.verification_start_time = None
        self.eye_blink_detected = False
        return self.cooldown_status, user_info

    async def trigger_alert(self, frame):
        current_time = time.perf_counter()
        if current_time - self.last_alert_time < self.alert_cooldown_time:
            return
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = os.path.join(self.alert_folder, f"unauthorized_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        
        await log_unauthorized_access(filename)

        print(f"🚨 Alerta activada: Imagen guardada como {filename}")
        self.last_alert_time = current_time
