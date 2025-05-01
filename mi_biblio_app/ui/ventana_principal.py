import customtkinter as ctk
from PIL import Image
from ui.ventana_anhadir_libro import VentanaAnhadirLibro



class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("Mi Biblioteca")
        self.geometry("900x600")
        self.minsize(800, 500)

        self.grid_columnconfigure(0, weight=0) #Título
        self.grid_columnconfigure(1, weight=1) #Buscador
        self.grid_columnconfigure(2, weight=0) #Lupa
        self.grid_rowconfigure(1, weight=1) #Botón +

        self.crear_widgets()

    def crear_widgets(self):
        self.label_titulo = ctk.CTkLabel(self, text="📚 MiBiblio 📚", font=("Arial", 24))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.entry_busqueda = ctk.CTkEntry(self, placeholder_text="Buscar libros...")
        self.entry_busqueda.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

        icono_lupa = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/lupa.png"), size=(30, 30))
        self.boton_buscar = ctk.CTkButton(self, image=icono_lupa, text="", width=50, height=50, corner_radius=15, command=self.accion_buscar)
        self.boton_buscar.grid(row=0, column=2, padx=10, pady=20)

        icono_mas = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/plus.png"), size=(20, 20))
        self.boton_anhadir = ctk.CTkButton(
            self, 
            image=icono_mas, text="", 
            command=self.accion_anhadir, 
            width=50, height=50,
            corner_radius=15)
        self.boton_anhadir.grid(row=1, column=2, sticky="se", padx=10, pady=10)

    def accion_anhadir(self):
        VentanaAnhadirLibro(self)

    def accion_buscar(self):
        print(f"Buscando: {self.entry_busqueda.get()}")
