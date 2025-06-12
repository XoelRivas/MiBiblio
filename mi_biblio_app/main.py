from ui.ventana_principal import VentanaPrincipal
from database import crear_tablas, get_database_path
import os

if __name__ == "__main__":
    db_path = get_database_path()

    if not os.path.exists(db_path):
        crear_tablas(db_path)

    app = VentanaPrincipal()
    app.mainloop()