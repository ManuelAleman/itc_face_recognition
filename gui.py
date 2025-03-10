import tkinter as tk
from tkinter import Label, Frame, font
from PIL import Image, ImageTk
from access_control_area.FaceRecognition import FaceRecognition
import asyncio
from config.db import db
import cv2

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial - Instituto Tecnológico de Culiacán")
        self.root.geometry("800x600")
        self.root.configure(bg="#003366")
        self.root.minsize(800, 600)

        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.status_font = font.Font(family="Arial", size=14)

        self.main_frame = Frame(self.root, bg="#003366")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_label = Label(
            self.main_frame,
            text="Instituto Tecnológico de Culiacán",
            font=self.title_font,
            fg="#FFFFFF",
            bg="#003366"
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

        self.camera_frame = Frame(self.main_frame, bg="#F0F0F0", bd=2, relief="solid")
        self.camera_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.video_label = Label(self.camera_frame, bg="#F0F0F0")
        self.video_label.pack(fill="both", expand=True, padx=10, pady=10)

        self.status_frame = Frame(self.main_frame, bg="#003366")
        self.status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(10, 0))

        self.status_label = Label(
            self.status_frame,
            text="Inicializando...",
            font=self.status_font,
            fg="#FFFFFF",
            bg="#003366"
        )
        self.status_label.pack(fill="x", pady=10)

        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.face_recognition = FaceRecognition()

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.run_until_complete(self.start_db_connection())
        print("Rostros cargados")

        self.status_label.config(text="Sistema iniciado correctamente.")
        self.update_frame()

    async def start_db_connection(self):
        await db.connect()
        await self.face_recognition.load_known_faces()

    def update_frame(self):
        ret, frame = self.face_recognition.cap.read()
        if not ret:
            self.status_label.config(text="Error: No se pudo capturar el cuadro.")
            return

        status_text = self.loop.run_until_complete(self.face_recognition.recognize_faces(frame))
        self.status_label.config(text=status_text)

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.root.after(10, self.update_frame)

    def on_close(self):
        self.face_recognition.cap.release()
        self.loop.run_until_complete(self.stop_db_connection())
        cv2.destroyAllWindows()
        self.root.destroy()

    async def stop_db_connection(self):
        await db.disconnect()

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceRecognitionApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
