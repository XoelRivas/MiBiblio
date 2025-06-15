import os
import sys

def recurso_absoluto(rel_path):
    """
    Devuelve la ruta absoluta correcta, compatible con PyInstaller (EXE) y desarrollo normal.
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, rel_path)

def carpeta_portadas():
    """
    Devuelve la ruta absoluta a la carpeta 'portadas' junto al ejecutable o script.
    Crea la carpeta si no existe.
    """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    carpeta = os.path.join(base_path, "portadas")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta