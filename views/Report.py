import tkinter as tk
from tkinter import ttk,Label, Frame, font
from models.classroom import get_classrooms
from models.access import get_access_by_classroom_and_date
import asyncio

class Report(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Reporte de Asistencia")
        self.geometry("800x600")
        self.configure(bg="#003366")
        self.minsize(800, 600)

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
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

       
        self.classroom_combo = ttk.Combobox(self.main_frame)
        self.classroom_combo.set("Selecciona una clase")
        self.classroom_combo.grid(row=1, column=0, padx=10, pady=5)

        # Llamar a la funcion asincrona para obtener las clases
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.getClassroomFromDB())
        # seleccionar el dia de la clase
        self.day_combo = ttk.Combobox(self.main_frame)
        self.day_combo.set("Dia")
        dias = list(range(1, 32))
        self.day_combo['values'] = dias
        self.day_combo.grid(row=1, column=1, padx=10, pady=5)
        # seleccionar el mes de la clase
        self.month_combo = ttk.Combobox(self.main_frame)
        self.month_combo.set("Mes")
        meses = list(range(1, 13))
        self.month_combo['values'] = meses
        self.month_combo.grid(row=1, column=2, padx=10, pady=5)
        # seleccionar el año de la clase
        self.year_combo = ttk.Combobox(self.main_frame)
        self.year_combo.set("Año")
        anios = list(range(2023, 2030))
        self.year_combo['values'] = anios
        self.year_combo.grid(row=1, column=3, padx=10, pady=5)
        # boton de generar reporte
        self.generate_report_button = ttk.Button(self.main_frame, text="Generar Reporte", command=self.generate_report)
        self.generate_report_button.grid(row=2, column=0, columnspan=4, pady=(10, 20))
        # boton de salir


    def generate_report(self):
        # Aqui se generara el reporte
        selected_classroom = self.classroom_combo.get()
        selected_day = self.day_combo.get()
        selected_month = self.month_combo.get()
        selected_year = self.year_combo.get()

        if not selected_classroom or not selected_day or not selected_month or not selected_year:
            print("Por favor selecciona todos los campos")
            return

        classroom_id = self.classroom_map[selected_classroom]
        # Buscar la lista de asistencia en la base de datos
        date = f"{selected_year}-{selected_month}-{selected_day}"
        access_records = asyncio.run(self.get_access_by_classroom_and_date(classroom_id, date))
        if not access_records:
            print("No se encontraron registros de asistencia para esta clase")
            return
        # Aqui se generara el reporte
        # Por ahora solo se imprimira en la consola
        print(f"Registros de asistencia para la clase {classroom_id} del {selected_day}/{selected_month}/{selected_year}:")
        for record in access_records:
            print(record)
            print(f"Usuario: {record.userId} - Fecha: {record.listTime}")

    
    async def get_access_by_classroom_and_date(self, classroom_id, date):
        access_records = await get_access_by_classroom_and_date(classroom_id, date)
        return access_records
       


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
