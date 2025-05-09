import customtkinter as ctk
from PIL import Image
from ui.ventana_anhadir_libro import VentanaAnhadirLibro
from database import obtener_libros_guardados
import urllib.request
from io import BytesIO



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
        #Título
        self.label_titulo = ctk.CTkLabel(self, text="📚 MiBiblio 📚", font=("Arial", 24))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        #Buscador
        self.entry_busqueda = ctk.CTkEntry(self, placeholder_text="Buscar libros...")
        self.entry_busqueda.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

        #Botón lupa
        icono_lupa = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/lupa.png"), size=(30, 30))
        self.boton_buscar = ctk.CTkButton(self, image=icono_lupa, text="", width=50, height=50, corner_radius=15, command=self.accion_buscar)
        self.boton_buscar.grid(row=0, column=2, padx=10, pady=20)

        #Frame libros
        self.frame_libros = ctk.CTkScrollableFrame(self)
        self.frame_libros.grid(row=1, column=0, columnspan=3, padx=20, pady=(0, 10), sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        #Botón añadir
        icono_mas = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/plus.png"), size=(20, 20))
        self.boton_anhadir = ctk.CTkButton(
            self, 
            image=icono_mas, text="", 
            command=self.accion_anhadir, 
            width=50, height=50,
            corner_radius=15,
            bg_color="#DBDBDB")
        self.boton_anhadir.place(relx=1.0, rely=1.0, x=-40, y=-20, anchor="se")

        self.mostrar_libros_guardados()

    def mostrar_libros_guardados(self):
        for widget in self.frame_libros.winfo_children():
            widget.destroy()

        libros = obtener_libros_guardados()
        if not libros:
            label = ctk.CTkLabel(self.frame_libros, text="No hay libros guardados.")
            label.pack(pady=10)
            return
        
        for libro in libros:
            texto = f"{libro['titulo']}\n{libro['autor']} ({libro['fecha_publicacion']})"

            imagen_portada = None
            if libro.get("cover_id"):
                try:
                    url = f"https://covers.openlibrary.org/b/id/{libro['cover_id']}-M.jpg"
                    with urllib.request.urlopen(url) as u:
                        raw_data = u.read()
                    im = Image.open(BytesIO(raw_data))
                    im = im.resize((160, 190))
                    imagen_portada = ctk.CTkImage(light_image=im)
                except Exception as e:
                    print("Error cargando portada:", e)

            item_frame = ctk.CTkFrame(self.frame_libros, fg_color="#3B8ED0", height=200)
            item_frame.pack(fill="x", padx=10, pady=5)
            item_frame.grid_propagate(False)  # Para que respete el height definido

            # Configurar la estructura de grid
            item_frame.grid_columnconfigure(0, weight=1)  # Para que el texto se expanda
            item_frame.grid_rowconfigure(0, weight=1)

            # Texto a la izquierda, centrado verticalmente
            texto_label = ctk.CTkLabel(item_frame, text=texto, anchor="w", justify="left")
            texto_label.grid(row=0, column=0, sticky="nsw", padx=(10, 0))

            # Imagen a la derecha, centrada verticalmente
            if imagen_portada:
                imagen_label = ctk.CTkLabel(item_frame, image=imagen_portada, text="")
                imagen_label.grid(row=0, column=1, sticky="nse", padx=10)

            # Vincular el frame y sus elementos al evento de clic
            item_frame.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))
            texto_label.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))
            if imagen_portada:
                imagen_label.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))



    def accion_anhadir(self):
        VentanaAnhadirLibro(self)

    def accion_buscar(self):
        print(f"Buscando: {self.entry_busqueda.get()}")

    def accion_editar_libro(self, libro):
        print("Editar libro: ", libro)
