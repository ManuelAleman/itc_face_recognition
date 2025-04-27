import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.tableview import Tableview

from tkinter import ttk,Label, Frame, font
from models.classroom import get_classrooms
from models.access import get_access_by_classroom_and_date

import asyncio

class Report(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reporte de Asistencia")
        self.geometry("700x600")
        self.configure(bg="#003366")
        self.minsize(700, 600)
        self.theme = tb.Style(theme="darkly")

        self.title_font = font.Font(family="Helvetica", size=18, weight="bold")

        self.main_frame = Frame(self, bg="#003366")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.title_label = Label(
            self.main_frame,
            text="Reporte de Asistencia",
            font=self.title_font,
            fg="#FFFFFF",
            bg="#003366"
        )
        self.title_label.grid(row=0, column=0, columnspan=4, pady=(10, 20))

       
        self.classroom_combo = ttk.Combobox(self.main_frame)
        self.classroom_combo.set("Selecciona una clase")
        self.classroom_combo.grid(row=1, column=0, padx=10, pady=5)

        # Llamar a la funcion asincrona para obtener las clases
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.getClassroomFromDB())
        

        self.date_entry = tb.DateEntry(self.main_frame, width=20)
        self.date_entry.grid(row=1, column=2, padx=10, pady=5)
        # boton de generar reporte

        self.generate_table_button = ttk.Button(self.main_frame, text="Buscar registros", command=self.generate_table)
        self.generate_table_button.grid(row=1, column=3, padx=20, pady=5)
        # boton de salir


    def generate_table(self):
        # Aqui se generara el reporte
        selected_classroom = self.classroom_combo.get()
        date = self.date_entry.entry.get()

        if selected_classroom == "Selecciona una clase" or not date:
            self.table.destroy() if hasattr(self, 'table') else None
            self.save_button.destroy() if hasattr(self, 'save_button') else None
            text_empty = Label(self.main_frame, text="Por favor selecciona una clase y una fecha", fg="red", bg="#003366")
            text_empty.grid(row=2, column=0, columnspan=4, pady=(10, 20))
            return

        classroom_id = self.classroom_map[selected_classroom]
        loop = asyncio.get_event_loop()
        access_records = loop.run_until_complete(self.get_access_by_classroom_and_date(classroom_id, date))
        if not access_records:
            self.table.destroy() if hasattr(self, 'table') else None
            self.save_button.destroy() if hasattr(self, 'save_button') else None
            text_not_found = Label(self.main_frame, text="No se encontraron registros de asistencia para esta clase", fg="red", bg="#003366")
            text_not_found.grid(row=2, column=0, columnspan=4, pady=(10, 20))
            return

        col = [
            {"text": "Numero de control", "anchor": "w", "stretch": True},
            {"text": "Nombre", "anchor": "center", "stretch": True},
            {"text": "Hora de Acceso", "anchor": "e", "stretch": True}
        ]
        data = []
        for record in access_records:
            data.append((record.user.nControl, record.user.name, record.accessTime.strftime("%H:%M:%S")))
        # Crear la tabla
        self.table = Tableview(self.main_frame, coldata=col, rowdata=data)
        self.table.grid(row=2, column=0, columnspan=4, pady=(10, 20))

        # Boton de guardar
        self.save_button = ttk.Button(self.main_frame, text="Guardar Reporte", command=self.save_report)
        self.save_button.grid(row=3, column=0, columnspan=4, pady=(10, 20))

    def save_report(self):
        self.table.export_all_records()
        print("Reporte guardado como reporte.csv")





    
    async def get_access_by_classroom_and_date(self, classroom_id, date):
        access_records = await get_access_by_classroom_and_date(classroom_id, date)
        return access_records
       


    async def getClassroomFromDB(self):
      classrooms = await get_classrooms()
      self.classroom_map = {f"{classroom.subject} - {classroom.room} - {classroom.schedule.strftime('%H:%M')}": classroom.id for classroom in classrooms}
      self.classroom_combo["values"] = list(self.classroom_map.keys())
