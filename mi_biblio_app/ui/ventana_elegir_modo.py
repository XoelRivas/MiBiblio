import customtkinter as ctk
from ui.ventana_anhadir_libro import VentanaAnhadirLibro
from ui.ventana_editar_libro import VentanaEditarLibro
import tkinter as tk

class VentanaElegirModo(ctk.CTkToplevel):
    def __init__(self, master, callback=None):
        super().__init__(master)
        self.title("Seleccionar acción")
        self.geometry("300x150")
        self.resizable(False, False)
        self.callback = callback

        ctk.CTkLabel(self, text="¿Qué deseas hacer?", font=("Arial", 18)).pack(pady=20)

        btn_crear = ctk.CTkButton(self, text="Crear libro", command=self.accion_crear)
        btn_crear.pack(pady=(0, 10))

        btn_anhadir = ctk.CTkButton(self, text="Añadir libro", command=self.accion_anhadir)
        btn_anhadir.pack()

        self.lift()
        self.focus_force()
        self.grab_set()

    def accion_crear(self):
        self.destroy()
        ventana = VentanaEditarLibro(self.master, libro=None, callback=self.callback, modo_edicion=False)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()

    def accion_anhadir(self):
        self.destroy()
        ventana = VentanaAnhadirLibro(self.master, callback=self.callback)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()