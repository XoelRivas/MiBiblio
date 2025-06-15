from ui.ventana_principal import VentanaPrincipal
from database import crear_tablas
import tkinter as tk
import os
from utils.rutas import recurso_absoluto

# Punto de entrada principal de la aplicación.
if __name__ == "__main__":
    # Comprueba si la base de datos existe; si no, la crea inicializando las tablas necesarias.
    if not os.path.exists(recurso_absoluto("mi_biblio_app/miBiblio.db")):
        crear_tablas()

     # Crea la ventana principal de la aplicación y lanza el bucle principal de la interfaz gráfica.
    app = VentanaPrincipal()
    app.mainloop()