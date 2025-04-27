import customtkinter as ctk
from PIL import Image

class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Mi Biblioteca")
        self.geometry("900x600")
        self.minsize(800, 500)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_widgets()

    def crear_widgets(self):
        self.label_titulo = ctk.CTkLabel(self, text="📚 Bienvenido a tu Biblioteca 📚", font=("Arial", 24))
        self.label_titulo.grid(row=0, column=0, pady=20)

        icono_mas = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/plus.png"), size=(20, 20))
        self.boton_anhadir = ctk.CTkButton(
            self, 
            image=icono_mas, text="", 
            command=self.accion_anhadir, 
            width=50, height=50,
            corner_radius=15)
        self.boton_anhadir.grid(row=1, column=1, pady=10, padx=10)

    def accion_anhadir(self):
        print("Botón Añadir Libro pulsado")
