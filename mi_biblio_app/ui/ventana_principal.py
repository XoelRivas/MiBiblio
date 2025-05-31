import customtkinter as ctk
from PIL import Image
from ui.ventana_anhadir_libro import VentanaAnhadirLibro
from database import obtener_libros_guardados
import urllib.request
from io import BytesIO
import threading
from ui.ventana_editar_libro import VentanaEditarLibro

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
        self.frame_libros.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        #Botón añadir
        icono_mas = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/plus.png"), size=(20, 20))
        self.boton_anhadir = ctk.CTkButton(
            self, 
            image=icono_mas, text="", 
            command=self.accion_anhadir, 
            width=50, height=50,
            corner_radius=15)
        self.boton_anhadir.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

        self.imagen_sin_portada = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/sin_portada.png"), size=(100, 150))

        self.mostrar_libros_guardados()

    def mostrar_libros_guardados(self):
        color_normal = "#3B8ED0"
        color_hover = "#36719F"

        for widget in self.frame_libros.winfo_children():
            widget.destroy()

        libros = obtener_libros_guardados()
        if not libros:
            label = ctk.CTkLabel(self.frame_libros, text="No hay libros guardados.")
            label.pack(pady=10)
            return
        
        for libro in libros:
            texto = f"{libro['titulo']}\n{libro['autor']} ({libro['fecha_publicacion']})"

            item_frame = ctk.CTkFrame(self.frame_libros, fg_color=color_normal, height=170)
            item_frame.pack(fill="x", padx=10, pady=5)
            item_frame.grid_propagate(False)

            def on_enter(e, frame=item_frame):
                frame.configure(fg_color=color_hover)
                frame.configure(cursor="hand2")

            def on_leave(e, frame=item_frame):
                frame.configure(fg_color=color_normal)
                frame.configure(cursor="")

            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_rowconfigure(0, weight=1)
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)

            texto_label = ctk.CTkLabel(item_frame, text=texto, anchor="w", justify="left")
            texto_label.grid(row=0, column=0, sticky="nsw", padx=(10, 0))
            texto_label.bind("<Enter>", on_enter)
            texto_label.bind("<Leave>", on_leave)

            imagen_label = ctk.CTkLabel(item_frame, text="")
            imagen_label.grid(row=0, column=1, sticky="nse", padx=10)
            imagen_label.bind("<Enter>", on_enter)
            imagen_label.bind("<Leave>", on_leave)

            if libro.get("cover_id"):
                try:
                    url = f"https://covers.openlibrary.org/b/id/{libro['cover_id']}-M.jpg"
                    self.cargar_portada_async(url, imagen_label)
                except Exception as e:
                    print("Error cargando portada:", e)
                    imagen_label.configure(image=self.imagen_sin_portada)
            else:
                imagen_label.configure(image=self.imagen_sin_portada)

            item_frame.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))
            texto_label.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))
            imagen_label.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))

    def cargar_portada_async(self, url, label):
        def task():
            try:
                with urllib.request.urlopen(url) as u:
                    raw_data = u.read()
                im = Image.open(BytesIO(raw_data)).resize((100, 150))
                imagen = ctk.CTkImage(light_image=im, size=(100, 150))
                self.after(0, lambda: label.configure(image=imagen))
            except Exception as e:
                print("Error cargando portada:", e)

        threading.Thread(target=task, daemon=True).start()

    def accion_anhadir(self):
        ventana = VentanaAnhadirLibro(self, callback=self.mostrar_libros_guardados)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()

    def accion_buscar(self):
        print(f"Buscando: {self.entry_busqueda.get()}")

    def accion_editar_libro(self, libro):
        ventana = VentanaEditarLibro(self, libro, callback=self.mostrar_libros_guardados)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()
