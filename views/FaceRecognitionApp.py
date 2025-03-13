import tkinter as tk
from tkinter import Label, Frame, font
from PIL import Image, ImageTk
import asyncio
import cv2
from models.FaceRecognition import FaceRecognition
from config.db import db

class FaceRecognitionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reconocimiento Facial - Instituto Tecnológico de Culiacán")
        self.root.geometry("1000x600")
        self.root.configure(bg="#003366")
        self.root.minsize(1000, 600)

        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.status_font = font.Font(family="Arial", size=14, weight="bold")
        self.user_info_font = font.Font(family="Arial", size=12)

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

        self.right_panel_frame = Frame(self.main_frame, bg="#F0F0F0", bd=2, relief="solid", width=300)
        self.right_panel_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.user_nControl_label = Label(self.right_panel_frame, text="ID: N/A", font=self.user_info_font, fg="#003366", bg="#e0e0e0", relief="solid", padx=10, pady=5)
        self.user_nControl_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.user_career_label = Label(self.right_panel_frame, text="Carrera: N/A", font=self.user_info_font, fg="#003366", bg="#e0e0e0", relief="solid", padx=10, pady=5)
        self.user_career_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.user_name_label = Label(self.right_panel_frame, text="Nombre: No reconocido", font=self.user_info_font, fg="#003366", bg="#e0e0e0", relief="solid", padx=10, pady=5)
        self.user_name_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")

        self.user_email_label = Label(self.right_panel_frame, text="Correo: N/A", font=self.user_info_font, fg="#003366", bg="#e0e0e0", relief="solid", padx=10, pady=5)
        self.user_email_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")

        self.status_label = Label(
            self.main_frame,
            text="Inicializando...",
            font=self.status_font,
            fg="#FFFFFF",
            bg="#003366"
        )
        self.status_label.grid(row=2, column=0, columnspan=2, pady=10)

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

        status_text, user_info = self.loop.run_until_complete(self.face_recognition.recognize_faces(frame))
        self.status_label.config(text=status_text)

        if "Verificando usuario" in status_text or not user_info:
            self.right_panel_frame.grid_remove()
            self.face_recognition.last_user_info = None
        elif user_info:
            self.right_panel_frame.grid()
            self.user_nControl_label.config(text=f"nControl: {user_info.nControl}")
            self.user_career_label.config(text=f"Carrera: {user_info.career}")
            self.user_name_label.config(text=f"Nombre: {user_info.name}")
            self.user_email_label.config(text=f"Correo: {user_info.email}")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.root.after(10, self.update_frame)


