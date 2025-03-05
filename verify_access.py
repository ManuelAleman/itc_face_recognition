import cv2
import face_recognition
from config.db import db
from models.user import get_all_users_encodings
from models.access import create_access

async def verify_access_camera():
    await db.connect()
    
    video_capture = cv2.VideoCapture(0)
    print("Presiona 'q' para salir.")
    
    users = await get_all_users_encodings()
    known_encodings = [user.faceEncoding for user in users]
    known_users = {tuple(user.faceEncoding): user for user in users}
    
    face_detected = False
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Error al acceder a la cámara.")
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        encodings_to_validate = face_recognition.face_encodings(rgb_frame)
        
        if encodings_to_validate:
            if not face_detected:
                print("👤 Rostro detectado. Procesando...")
                face_detected = True
            
            encoding_to_validate = encodings_to_validate[0]
            matches = face_recognition.compare_faces(known_encodings, encoding_to_validate)
            
            if True in matches:
                matched_idx = matches.index(True)
                user = known_users[tuple(known_encodings[matched_idx])]
                await create_access(user_id=user.id)
                print(f"✅ Acceso autorizado para {user.name} ({user.carreer}).")
            else:
                print("🚫 Acceso denegado: Usuario no reconocido.")
        else:
            if face_detected:
                print("🔍 Rostro perdido. Esperando detección...")
                face_detected = False
        
        cv2.imshow('Verificación de acceso', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    video_capture.release()
    cv2.destroyAllWindows()
    await db.disconnect()
