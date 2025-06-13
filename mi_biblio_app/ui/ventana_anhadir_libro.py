import customtkinter as ctk
from PIL import Image
from api import buscar_libros_por_titulo_autor_isbn
from database import insertar_autor, insertar_libro, relacionar_libro_autor
from io import BytesIO
import urllib.request
import threading
import time
from tkinter import messagebox
import os

class VentanaAnhadirLibro(ctk.CTkToplevel):
    def __init__(self, master, callback=None):
        super().__init__(master)
        self.callback = callback

        self.title("Añadir Libro")
        self.geometry("700x500")
        self.resizable(False, False)

        self.iconbitmap("mi_biblio_app/imagenes/icono.ico")

        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.crear_widgets()

    def crear_widgets(self):
        self.label_titulo = ctk.CTkLabel(self, text="📚 Añadir libro 📚", font=("Arial", 20))
        self.label_titulo.grid(row=0, column=0, sticky="w", padx=20, pady=20)

        self.entry_busqueda = ctk.CTkEntry(self, placeholder_text="Buscar por título, autor o ISBN...")
        self.entry_busqueda.grid(row=0, column=1, sticky="ew", padx=10)

        icono_lupa = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/lupa.png"), size=(30, 30))
        self.boton_buscar = ctk.CTkButton(self, image=icono_lupa, text="", width=50, height=50, corner_radius=15, command=self.buscar_libro)
        self.boton_buscar.grid(row=0, column=2, sticky="e", padx=20)

        self.frame_resultados = ctk.CTkScrollableFrame(self)
        self.frame_resultados.grid(row=1, column=0, columnspan=3, padx=20, pady=10, sticky="nsew")

    def buscar_libro(self):
        titulo = self.entry_busqueda.get().strip()
        if not titulo:
            return
        
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        self.label_cargando = ctk.CTkLabel(self.frame_resultados, text="Buscando.")
        self.label_cargando.pack(pady=10)
        
        self.buscando = True
        threading.Thread(target=self.animar_texto_cargando, daemon=True).start()
        threading.Thread(target=self.ejecutar_busqueda, args=(titulo,), daemon=True).start()

    def ejecutar_busqueda(self, titulo):
        resultados = buscar_libros_por_titulo_autor_isbn(titulo)
        self.buscando = False
        self.after(0, self.mostrar_resultados, resultados)

    def mostrar_resultados(self, resultados):
        self.label_cargando.destroy()

        if not resultados:
            label = ctk.CTkLabel(self.frame_resultados, text="No se encontraron libros.")
            label.pack(pady=5)
            return
        
        for libro in resultados:
            self.mostrar_resultado(libro)

    def animar_texto_cargando(self):
        puntos = ["Buscando.", "Buscando..", "Buscando..."]
        etapa = 0
        while self.buscando:
            texto = puntos[etapa % 3]
            self.after(0, lambda t=texto: self.label_cargando.configure(text=t))
            etapa += 1
            time.sleep(0.5)

    def mostrar_resultado(self, libro):
        color_normal = "#3B8ED0"
        color_hover = "#36719F"
        texto = f"{libro['titulo'].upper()} - {libro['autor']} ({libro['anho']})"

        item_frame = ctk.CTkFrame(self.frame_resultados, fg_color=color_normal, height=190)
        item_frame.pack(fill="x", padx=10, pady=5)
        item_frame.grid_propagate(False)

        item_frame.grid_columnconfigure(0, weight=1)
        item_frame.grid_rowconfigure(0, weight=1)

        def on_enter(e): item_frame.configure(fg_color=color_hover, cursor="hand2")
        def on_leave(e): item_frame.configure(fg_color=color_normal, cursor="")

        item_frame.bind("<Enter>", on_enter)
        item_frame.bind("<Leave>", on_leave)

        texto_label = ctk.CTkLabel(item_frame, text=texto, anchor="w", justify="left", wraplength=400)
        texto_label.grid(row=0, column=0, sticky="nsw", padx=(10, 0))
        texto_label.bind("<Enter>", on_enter)
        texto_label.bind("<Leave>", on_leave)

        imagen_label = ctk.CTkLabel(item_frame, text="")
        imagen_label.grid(row=0, column=1, sticky="nse", padx=10)
        imagen_label.bind("<Enter>", on_enter)
        imagen_label.bind("<Leave>", on_leave)

        item_frame.bind("<Button-1>", lambda e, l=libro: self.seleccionar_libro(l))
        texto_label.bind("<Button-1>", lambda e, l=libro: self.seleccionar_libro(l))
        imagen_label.bind("<Button-1>", lambda e, l=libro: self.seleccionar_libro(l))

        if libro.get("cover_id"):
            def cargar_portada():
                try:
                    url = f"https://covers.openlibrary.org/b/id/{libro['cover_id']}-M.jpg"
                    with urllib.request.urlopen(url) as u:
                        raw_data = u.read()
                    im = Image.open(BytesIO(raw_data)).resize((100, 150))
                except Exception as e:
                    print("Error cargando portada:", e)
                    im = Image.open("mi_biblio_app/portadas/sin_portada.png").resize((100, 150))

                portada = ctk.CTkImage(light_image=im, size=(100, 150))
                self.after(0, lambda: imagen_label.configure(image=portada))
            threading.Thread(target=cargar_portada, daemon=True).start()
        else:
            im = Image.open("mi_biblio_app/portadas/sin_portada.png").resize((100, 150))
            portada = ctk.CTkImage(light_image=im, size=(100, 150))
            imagen_label.configure(image=portada)
        

    def seleccionar_libro(self, libro):
        id_editorial = None

        portada_path = None
        if libro.get("cover_id"):
            try:
                url = f"https://covers.openlibrary.org/b/id/{libro['cover_id']}-L.jpg"
                with urllib.request.urlopen(url) as u:
                    raw_data = u.read()
                im = Image.open(BytesIO(raw_data))
                portada_dir = "mi_biblio_app/portadas"
                os.makedirs(portada_dir, exist_ok=True)
                portada_path = os.path.join(portada_dir, f"{libro['cover_id']}.jpg")
                im.save(portada_path)
            except Exception as e:
                print(f"Error descargando la portada: {e}")
                portada_path = None

        libro["portada"] = portada_path

        if libro.get("anho"):
            libro["fecha_publicacion"] = str(libro["anho"])
        else:
            libro["fecha_publicacion"] = ""

        id_libro = insertar_libro(libro, id_editorial)

        if libro.get("autor"):
            for autor in libro["autor"].split(","):
                id_autor = insertar_autor(autor.strip())
                relacionar_libro_autor(id_libro, id_autor)

        messagebox.showinfo("Libro añadido", "Libro añadido a la biblioteca.", parent=self)

        if self.callback:
            self.callback()
    