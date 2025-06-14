import customtkinter as ctk
from ui.ventana_anhadir_libro import VentanaAnhadirLibro
from ui.ventana_editar_libro import VentanaEditarLibro
import tkinter as tk

"""
Ventana modal que permite al usuario elegir entre crear un libro desde cero
o añadir un libro existente. Llama a la ventana correspondiente según la acción.
"""
class VentanaElegirModo(ctk.CTkToplevel):
    """
    Inicializa la ventana de selección de modo.

    Args:
        master: Ventana principal o padre.
        callback: Función a ejecutar tras completar la acción en la ventana hija.
    """
    def __init__(self, master, callback=None):
        super().__init__(master)
        self.title("Seleccionar acción")
        self.geometry("300x150")
        self.resizable(False, False)
        self.callback = callback

        # Etiqueta principal de la ventana
        ctk.CTkLabel(self, text="¿Qué deseas hacer?", font=("Arial", 18)).pack(pady=20)

        # Botones para crear o añadir un libro
        btn_crear = ctk.CTkButton(self, text="Crear libro", command=self.accion_crear)
        btn_crear.pack(pady=(0, 10))
        btn_anhadir = ctk.CTkButton(self, text="Añadir libro", command=self.accion_anhadir)
        btn_anhadir.pack()

        self.lift()
        self.focus_force()
        self.grab_set()

    """
    Acción al pulsar 'Crear libro'.
    Cierra esta ventana y abre la ventana de edición en modo creación.
    """
    def accion_crear(self):
        self.destroy()
        ventana = VentanaEditarLibro(self.master, libro=None, callback=self.callback, modo_edicion=False)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()

    """
    Acción al pulsar 'Añadir libro'.
    Cierra esta ventana y abre la ventana para añadir un libro.
    """
    def accion_anhadir(self):
        self.destroy()
        ventana = VentanaAnhadirLibro(self.master, callback=self.callback)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()