import cv2
import face_recognition
import datetime
from config.db import db
from models.user import get_all_users_encodings
from models.access import create_access, get_last_access_from_user

ACCESS_INTERVAL = 30
EYE_AR_THRESH = 0.2  
PROCESS_INTERVAL = 5  
FRAME_RESIZE_SCALE = 0.5  

def eye_aspect_ratio(eye_points):
    A = euclidean_distance(eye_points[1], eye_points[5])
    B = euclidean_distance(eye_points[2], eye_points[4])
    C = euclidean_distance(eye_points[0], eye_points[3])
    ear = (A + B) / (2.0 * C)
    return ear

def euclidean_distance(point1, point2):
    return ((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2) ** 0.5

def detect_blink(face_landmarks):
    left_eye = face_landmarks['left_eye']
    right_eye = face_landmarks['right_eye']
    left_eye_ratio = eye_aspect_ratio(left_eye)
    right_eye_ratio = eye_aspect_ratio(right_eye)

    if left_eye_ratio < EYE_AR_THRESH or right_eye_ratio < EYE_AR_THRESH:
        return True
    return False

async def verify_access_camera():
    await db.connect()
    
    video_capture = cv2.VideoCapture(0)
    print("Presiona 'q' para salir.")
    
    users = await get_all_users_encodings()
    known_encodings = [user.faceEncoding for user in users]
    known_users = {tuple(user.faceEncoding): user for user in users}
    
    face_detected = False
    frame_counter = 0  
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error al acceder a la cámara.")
            break
        
    
        small_frame = cv2.resize(frame, None, fx=FRAME_RESIZE_SCALE, fy=FRAME_RESIZE_SCALE)
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        frame_counter += 1
        if frame_counter % PROCESS_INTERVAL == 0:  
            encodings_to_validate = face_recognition.face_encodings(rgb_frame)
            face_landmarks_list = face_recognition.face_landmarks(rgb_frame)
            
            if encodings_to_validate:
                if not face_detected:
                    print("👤 Rostro detectado. Procesando...")
                    face_detected = True
                
                encoding_to_validate = encodings_to_validate[0]
                matches = face_recognition.compare_faces(known_encodings, encoding_to_validate)
                
                if True in matches:
                    matched_idx = matches.index(True)
                    user = known_users[tuple(known_encodings[matched_idx])]
                    
                
                    liveness_detected = False
                    for face_landmarks in face_landmarks_list:
                        if detect_blink(face_landmarks):
                            liveness_detected = True
                            break
                    
                    if not liveness_detected:
                        continue
                    
                    now = datetime.datetime.now(datetime.timezone.utc)
                    last_access = await get_last_access_from_user(user.id)
                    
                    if last_access:
                        last_access_time = last_access.timestamp.astimezone(datetime.timezone.utc)
                        time_diff = (now - last_access_time).total_seconds()
                        if time_diff > ACCESS_INTERVAL:
                            await create_access(user_id=user.id)
                            print(f"✅ Acceso autorizado para {user.name} ({user.career}).")
                        else:
                            print(f"⏳ Espera {ACCESS_INTERVAL} segundos entre accesos.")
                    else:
                        await create_access(user_id=user.id)
                        print(f"✅ Acceso autorizado para {user.name} ({user.career}).")
                else:
                    print("🚫 Acceso denegado: Usuario no reconocido.")
            else:
                if face_detected:
                    print("🔍 Rostro perdido. Esperando detección...")
                    face_detected = False
        
        # Mostrar el video en una ventana
        cv2.imshow('Verificación de acceso', small_frame)  # Mostrar el frame reducido para fluidez
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()
    await db.disconnect()
