import tkinter as tk
from tkinter import ttk, Frame, font, messagebox
from models.user import create_user, delete_user
from models.images import create_image, delete_image
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
        self.form_frame.pack(pady=20)

        
        self.ncontrol_label = tk.Label(self.form_frame, text="Número de control:")
        self.ncontrol_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.ncontrol_entry = tk.Entry(self.form_frame)
        self.ncontrol_entry.grid(row=0, column=1, padx=10, pady=5)

        
        self.name_label = tk.Label(self.form_frame, text="Nombre:")
        self.name_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.name_entry = tk.Entry(self.form_frame)
        self.name_entry.grid(row=1, column=1, padx=10, pady=5)

        
        self.email_label = tk.Label(self.form_frame, text="Correo:")
        self.email_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")
        self.email_entry = tk.Entry(self.form_frame)
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        
        self.role_label = tk.Label(self.form_frame, text="Rol:")
        self.role_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")
        self.role_combo = ttk.Combobox(self.form_frame, values=["Estudiante", "Docente", "Administrativo", "Otro"])
        self.role_combo.set("Estudiante")
        self.role_combo.grid(row=3, column=1, padx=10, pady=5)
        self.role_combo.bind("<<ComboboxSelected>>", self.show_c)

        
        self.career_label = tk.Label(self.form_frame, text="Carrera:")
        self.career_label.grid(row=4, column=0, padx=10, pady=5, sticky="e")
        self.career_entry = ttk.Combobox(self.form_frame, values=[
            "Ingenieria Ambiental", "Ingenieria Bioquimica", "Ingenieria Electrica", "Ingenieria Electronica",
            "Ingenieria en Energias Renovables", "Ingenieria en Gestion Empresarial", "Ingenieria Industrial",
            "Ingenieria Mecanica", "Ingenieria Mecatronica", "Ingenieria en Sistemas Computacionales", "Ingenieria en TIC"])
        self.career_entry.grid(row=4, column=1, padx=10, pady=5)

        
        self.button_frame = Frame(self)
        self.button_frame.pack(pady=20)

        self.btn_capturar = ttk.Button(self.button_frame, text="Abrir Cámara", command=self.capturar_imagen)
        self.btn_capturar.grid(row=0, column=0, padx=10)

        self.btn_limpiar = ttk.Button(self.button_frame, text="Limpiar", command=self.limpiar_formulario)
        self.btn_limpiar.grid(row=0, column=1, padx=10)

        self.btn_guardar = ttk.Button(self.button_frame, text="Guardar", command=self.guardar_usuario_sync)
        self.btn_guardar.grid(row=0, column=2, padx=10)

        
        self.status_label = tk.Label(self, text="Captura 3 imágenes antes de guardar.", font=("Arial", 12))
        self.status_label.pack(pady=10)

    def capturar_imagen(self):
        self.imagenes_temporales = []
        
        if len(self.imagenes_temporales) >= 3:
            self.status_label.config(text="¡Máximo de 3 imágenes alcanzado!", fg="red")
            return

        cap = cv2.VideoCapture(0) 
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
            if key == 32:  
                self.imagenes_temporales.append(frame)
                self.status_label.config(text=f"Imagen {len(self.imagenes_temporales)} capturada", fg="green")
                if len(self.imagenes_temporales) >= 3:
                    self.status_label.config(text="Imagenes tomadas exitosamente", fg="green")
                    break
            elif key == 27: 
                self.status_label.config(text="Captura de imagen cancelada.", fg="red")
                break

        cap.release()
        cv2.destroyAllWindows()

    def limpiar_formulario(self):
        
        self.ncontrol_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.role_combo.set("Estudiante")
        self.career_entry.set("")

    def guardar_usuario_sync(self):
        if not self.validar_campos():
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return
        asyncio.run(self.guardar_usuario_async())
        
    def validar_campos(self):
        
        return all([
            self.ncontrol_entry.get(),
            self.name_entry.get(),
            self.email_entry.get(),
            self.role_combo.get(),
        ])
    async def guardar_usuario_async(self):
        nControl = self.ncontrol_entry.get()
        name = self.name_entry.get()
        career = self.career_entry.get() if hasattr(self, 'career_entry') else None
        email = self.email_entry.get()
        role = self.role_combo.get()

        if len(self.imagenes_temporales) < 3:
            self.status_label.config(text="¡Necesitas capturar 3 imágenes!", fg="red")
            return

        if not os.path.exists("img"):
            os.mkdir("img")

        if not os.path.exists(f"img/users/{name}"):
            os.mkdir(f"img/users/{name}")

        for i, img in enumerate(self.imagenes_temporales):
            cv2.imwrite(f"img/users/{name}/{i}.jpg", img)

        try:
            
            await create_user(nControl, name, email, role, career)
            self.status_label.config(text="¡Usuario guardado exitosamente!", fg="green")
            
            
            try: 
                await create_image(nControl, f"img/users/{name}/0.jpg")
                await create_image(nControl, f"img/users/{name}/1.jpg")
                await create_image(nControl, f"img/users/{name}/2.jpg")
            except Exception as e:
                await delete_image(nControl)
                await delete_user(nControl)
                for i in range(3):
                    os.remove(f"img/users/{name}/{i}.jpg")
                os.rmdir(f"img/users/{name}")
                self.status_label.config(text="¡Error al guardar las imágenes!", fg="red")
                print(f"Error al guardar las imágenes: {e}")
                return 
        except Exception as e:
            
            print(f"Error al guardar el usuario: {e}")
            for i in range(3):
                os.remove(f"img/users/{name}/{i}.jpg")
            os.rmdir(f"img/users/{name}")
            self.status_label.config(text="¡Error al guardar el usuario!", fg="red")
            return

        messagebox.showinfo("Éxito", "Usuario guardado correctamente.")
        self.limpiar_formulario()

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

