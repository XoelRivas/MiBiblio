import customtkinter as ctk
from PIL import Image
from api import buscar_libros_por_titulo
from database import insertar_editorial, insertar_autor, insertar_libro, relacionar_libro_autor

class VentanaAnhadirLibro(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)

        self.title("Añadir Libro")
        self.geometry("700x500")
        self.resizable(False, False)

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.crear_widgets()

    def crear_widgets(self):
        self.label_titulo = ctk.CTkLabel(self, text="Añadir libro", font=("Arial", 20))
        self.label_titulo.grid(row=0, column=0, sticky="w", padx=20, pady=20)

        self.entry_busqueda = ctk.CTkEntry(self, placeholder_text="Buscar por título, autor o ISBN")
        self.entry_busqueda.grid(row=0, column=1, sticky="ew", padx=10)

        icono_lupa = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/lupa.png"), size=(30, 30))
        self.boton_buscar = ctk.CTkButton(self, image=icono_lupa, text="", width=50, height=50, corner_radius=15, command=self.buscar_libro)
        self.boton_buscar.grid(row=0, column=2, sticky="e", padx=20)

        self.frame_resultados = ctk.CTkFrame(self)
        self.frame_resultados.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

    def buscar_libro(self):
        titulo = self.entry_busqueda.get().strip()
        if not titulo:
            return
        
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        resultados = buscar_libros_por_titulo(titulo)

        if not resultados:
            label = ctk.CTkLabel(self.frame_resultados, text="No se encontraron libros.")
            label.pack(pady=5)
            return
        
        for libro in resultados:
            texto = f"{libro['titulo']} - {libro['autor']} ({libro['anho']})"
            boton = ctk.CTkButton(
                self.frame_resultados, text=texto,
                command=lambda l=libro: self.seleccionar_libro(l),
                anchor="w"
            )
            boton.pack(fill="x", pady=2, padx=5)

    def seleccionar_libro(self, libro):
        id_editorial = None
        id_libro = insertar_libro(libro, id_editorial)

        if libro.get("autor"):
            for autor in libro["autor"].split(","):
                id_autor = insertar_autor(autor.strip())
                relacionar_libro_autor(id_libro, id_autor)

        ctk.CTkLabel(self.frame_resultados, text="✅ Libro guardado correctamente.").pack(pady=10)