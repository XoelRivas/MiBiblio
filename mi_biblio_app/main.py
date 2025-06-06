from ui.ventana_principal import VentanaPrincipal
from database import crear_tablas
import tkinter as tk
import os

if __name__ == "__main__":
    if not os.path.exists("mi_biblio_app/miBiblio.db"):
        crear_tablas()

    app = VentanaPrincipal()
    app.mainloop()