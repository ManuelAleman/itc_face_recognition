import tkinter as tk
from tkinter import ttk,Label, Frame, font
from models.classroom import get_classrooms
from views.FaceRecognitionApp import FaceRecognitionApp
import asyncio

class SelectClass(tk.Tk):

  def __init__(self):
    super().__init__()
    self.title("Seleccionar Clase")
    self.geometry("400x300")
    self.configure(bg="#003366")
    self.minsize(400, 300)

    self.title_font = font.Font(family="Helvetica", size=18, weight="bold")

    self.main_frame = Frame(self, bg="#003366")
    self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    self.title_label = Label(
        self.main_frame,
        text="Seleccionar Clase",
        font=self.title_font,
        fg="#FFFFFF",
        bg="#003366"
    )
    self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

    # Combobox for selecting classroom
    self.classroom_combo = ttk.Combobox(self.main_frame)
    self.classroom_combo.set("Selecciona una clase")
    self.classroom_combo.grid(row=1, column=0, padx=10, pady=5)

    # Button to confirm selection
    self.confirm_button = tk.Button(self.main_frame, text="Confirmar")
    self.confirm_button.grid(row=1, column=1, padx=10, pady=5)

    # Traer clases de la base de datos
    loop = asyncio.get_event_loop()
    loop.run_until_complete(self.getClassroomFromDB())

    self.confirm_button.bind("<Button-1>", self.confirm_selection)

  def confirm_selection(self, event):
    selected_classroom = self.classroom_combo.get()
    if selected_classroom != "Selecciona una clase":
        new_window = tk.Toplevel(self)
        FaceRecognitionApp(new_window, self.classroom_map[selected_classroom])
    else:
        print("Por favor, selecciona una clase válida.")
    
  async def getClassroomFromDB(self):
    classrooms = await get_classrooms()
    classroom_list = []
    # Guardar ids de las clases
    self.classroom_map = {}
    for classroom in classrooms:
      schedule = classroom.schedule.strftime("%H:%M")
      name = f"{classroom.subject} - {classroom.room} - {schedule}"
      classroom_list.append(name)
      self.classroom_map[name] = classroom.id
    self.classroom_combo['values'] = classroom_list


