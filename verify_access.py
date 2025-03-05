import cv2
import face_recognition
import datetime
from config.db import db
from models.user import get_all_users_encodings
from models.access import create_access, get_last_access_from_user

ACCESS_INTERVAL = 30

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
                
                now = datetime.datetime.now(datetime.timezone.utc)
                last_access = await get_last_access_from_user(user.id)
                
                if last_access:
                    last_access_time = last_access.timestamp.astimezone(datetime.timezone.utc) 
                    time_diff = (now - last_access_time).total_seconds()

                    print(f"Current Time: {now}")
                    print(f"Last Access Time: {last_access_time}")
                    print(f"Time Difference: {time_diff} seconds")

                    if time_diff > ACCESS_INTERVAL:
                        await create_access(user_id=user.id)
                        print("ultimo acceso", last_access_time)
                        print(f"✅ Acceso autorizado para {user.name} ({user.carreer}).")
                    else:
                        print(f"⏳ Espera {ACCESS_INTERVAL} segundos entre accesos.")

                else:
                    
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
