import tkinter as tk
from tkinter import ttk
from tkinter import Label, Frame, font
from models.user import create_user
from models.images import create_image
from config.db import db
import asyncio
import cv2
import os

class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Admin Panel")
        self.geometry("1000x600")
        self.resizable(False, False)

        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")
        self.title_label = tk.Label(self, text="Ingresar nuevo Usuario", font=self.title_font)
        self.title_label.pack(pady=20)

        self.form_frame = Frame(self)
        self.form_frame.columnconfigure(0, weight=1)

        # Numero de control
        self.ncontrol_label = tk.Label(self.form_frame, text="Numero de control:")
        self.ncontrol_label.grid(row=0, column=0)
        self.ncontrol_entry = tk.Entry(self.form_frame)
        self.ncontrol_entry.grid(row=0, column=1)

        # Nombre
        self.name_label = tk.Label(self.form_frame, text="Nombre:")
        self.name_label.grid(row=1, column=0)
        self.name_entry = tk.Entry(self.form_frame)
        self.name_entry.grid(row=1, column=1)

        # Correo
        self.email_label = tk.Label(self.form_frame, text="Correo:")
        self.email_label.grid(row=2, column=0)
        self.email_entry = tk.Entry(self.form_frame)
        self.email_entry.grid(row=2, column=1)

        # Rol
        self.role_label = tk.Label(self.form_frame, text="Rol:")
        self.role_label.grid(row=3, column=0)
        self.role_combo = ttk.Combobox(self.form_frame, values=["Estudiante", "Docente", "Administrativo", "Otro"])
        self.role_combo.grid(row=3, column=1)

        self.role_combo.bind("<<ComboboxSelected>>", self.show_c)

        btn_capturar = ttk.Button(self.form_frame, text="Abrir Cámara", command=self.capturar_imagen)
        btn_capturar.grid(row=5, column=0, columnspan=2, pady=10)
        
        btn_guardar = ttk.Button(self.form_frame, text="Guardar", command=self.guardar_usuario_sync)
        btn_guardar.grid(row=6, column=0, columnspan=2, pady=10)
        self.status_label = tk.Label(self.form_frame, text="Captura 3 imágenes antes de guardar.", font=("Arial", 12))
        self.status_label.grid(row=7, column=0, columnspan=2)

        self.form_frame.pack(pady=20)

    def capturar_imagen(self):
        self.imagenes_temporales = []
        
        if len(self.imagenes_temporales) >= 3:
            self.status_label.config(text="¡Máximo de 3 imágenes alcanzado!", fg="red")
            return

        cap = cv2.VideoCapture(0)  # Abre la cámara
        if not cap.isOpened():
            self.status_label.config(text="Error al abrir la cámara.", fg="red")
            return

        self.status_label.config(text="Presiona 'ESPACIO' para tomar foto, 'ESC' para salir.", fg="blue")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            cv2.imshow("Captura de imagen", frame)

            key = cv2.waitKey(1)
            if key == 32:  # Tecla ESPACIO para capturar imagen
                self.imagenes_temporales.append(frame)
                self.status_label.config(text=f"Imagen {len(self.imagenes_temporales)} capturada", fg="green")
                if len(self.imagenes_temporales) >= 3:
                    self.status_label.config(text="Imagenes tomadas exitosamente", fg="red")
                    break
            elif key == 27:  # Tecla ESC para salir
                self.status_label.config(text="Captura de imagen cancelada.", fg="red")
                break

        cap.release()
        cv2.destroyAllWindows()

    def guardar_usuario_sync(self):
        # Usamos asyncio.create_task para ejecutar la función asincrónica
        asyncio.create_task(self.guardar_usuario())

    async def guardar_usuario(self):
        nControl = self.ncontrol_entry.get()
        name = self.name_entry.get()
        career = self.career_entry.get() if hasattr(self, 'career_entry') else None
        email = self.email_entry.get()
        role = self.role_combo.get()

        if not nControl or not name or not email or not role:
            self.status_label.config(text="¡Todos los campos son requeridos!", fg="red")
            return

        if len(self.imagenes_temporales) < 3:
            self.status_label.config(text="¡Necesitas capturar 3 imágenes!", fg="red")
            return

        if not os.path.exists("imagenes"):
            os.mkdir("imagenes")

        if not os.path.exists(f"imagenes/{name}"):
            os.mkdir(f"imagenes/{name}")

        for i, img in enumerate(self.imagenes_temporales):
            cv2.imwrite(f"imagenes/{name}/{i}.jpg", img)

        # Guardar en la base de datos
        await create_user(nControl, name, email, role, career)
        await create_image(nControl, f"imagenes/{name}/0.jpg")
        await create_image(nControl, f"imagenes/{name}/1.jpg")
        await create_image(nControl, f"imagenes/{name}/2.jpg")

        self.status_label.config(text="¡Usuario guardado exitosamente!", fg="green")

    def show_c(self, event):
        if(self.role_combo.get() == "Estudiante"):
            self.career_label = tk.Label(self.form_frame, text="Carrera:")
            self.career_label.grid(row=4, column=0)
            self.career_entry = ttk.Combobox(self.form_frame, values=[
                "Ingenieria Ambiental", "Ingenieria Bioquimica", "Ingenieria Electrica", "Ingenieria Electronica",
                "Ingenieria en Energias Renovables", "Ingenieria en Gestion Empresarial", "Ingenieria Industrial",
                "Ingenieria Mecanica", "Ingenieria Mecatronica", "Ingenieria en Sistemas Computacionales", "Ingenieria en TIC"])
            self.career_entry.grid(row=4, column=1)
        else:
            self.career_label.grid_forget()
            self.career_entry.grid_forget()

    def logout(self):
        self.destroy()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(db.connect())
    
    app = AdminPanel()
    app.mainloop()

    # Cerrar la conexión al final
    loop.run_until_complete(db.disconnect())