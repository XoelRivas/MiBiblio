import customtkinter as ctk
from PIL import Image
from ui.ventana_anhadir_libro import VentanaAnhadirLibro
from ui.ventana_elegir_modo import VentanaElegirModo
from database import obtener_libros_guardados, buscar_libros_por_titulo_o_autor
from io import BytesIO
from ui.ventana_editar_libro import VentanaEditarLibro
from tkinter import messagebox
import os

"""
Ventana principal de la aplicación MiBiblio.
Permite visualizar, buscar, añadir y editar libros de la biblioteca.
"""
class VentanaPrincipal(ctk.CTk):
    """
    Inicializa la ventana principal, configura la interfaz y carga los libros guardados.
    """
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.title("MiBiblio")
        self.geometry("900x600")
        self.minsize(800, 500)
    
        self.iconbitmap("mi_biblio_app/imagenes/icono.ico")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.fuente = ("Arial", 20)

        # Carga los libros guardados desde la base de datos
        self.libros = obtener_libros_guardados()

        self.crear_widgets()


    """
    Crea y coloca todos los widgets principales de la interfaz:
    título, barra de búsqueda, botón de búsqueda, lista de libros y botón de añadir.
    """
    def crear_widgets(self):
        self.label_titulo = ctk.CTkLabel(self, text="📚 MiBiblio 📚", font=("Arial", 30))
        self.label_titulo.grid(row=0, column=0, padx=20, pady=20, sticky="w")

        self.entry_busqueda = ctk.CTkEntry(self, placeholder_text="Buscar libros por título o autor...")
        self.entry_busqueda.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

        icono_lupa = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/lupa.png"), size=(30, 30))
        self.boton_buscar = ctk.CTkButton(self, image=icono_lupa, text="", width=50, height=50, corner_radius=15, command=self.accion_buscar)
        self.boton_buscar.grid(row=0, column=2, padx=10, pady=20)

        self.frame_libros = ctk.CTkScrollableFrame(self)
        self.frame_libros.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        icono_mas = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/plus.png"), size=(20, 20))
        self.boton_anhadir = ctk.CTkButton(
            self, 
            image=icono_mas, text="", 
            command=self.accion_anhadir, 
            width=50, height=50,
            corner_radius=15)
        self.boton_anhadir.place(relx=1.0, rely=1.0, x=-20, y=-20, anchor="se")

        self.imagen_sin_portada = ctk.CTkImage(light_image=Image.open("mi_biblio_app/portadas/sin_portada.png"), size=(100, 150))

        self.mostrar_libros(self.libros)


    """
    Muestra la lista de libros en el frame principal.
    Cada libro se representa con un frame que incluye título, autor, año y portada.
    Si no hay libros, muestra un mensaje indicativo.
    """
    def mostrar_libros(self, libros):
        # Limpia el frame antes de mostrar los libros
        for widget in self.frame_libros.winfo_children():
            widget.destroy()

        if not libros:
            label = ctk.CTkLabel(self.frame_libros, text="Tú biblioteca está vacía.", font=self.fuente)
            label.pack(pady=10)
            return
        
        for libro in libros:
            # Elimina duplicados en autores y géneros por si la consulta SQL los devuelve repetidos
            autores = libro["autor"].split(", ") if libro.get("autor") else []
            libro["autor"] = ", ".join(sorted(set(autores), key=autores.index))

            generos = libro["genero"].split(", ") if libro.get("genero") else []
            libro["genero"] = ", ".join(sorted(set(generos), key=generos.index))

            # Muestra solo el año de publicación si está disponible
            fecha_publicacion = libro['fecha_publicacion'] if libro['fecha_publicacion'] else "Sin fecha de publicación"
            texto = f"{libro['titulo'].upper()}\n{libro['autor']} ({fecha_publicacion})"

            estado = libro.get("estado", "-")

            # Diccionario de colores según el estado del libro
            colores = {
                "-": ("#3B8ED0", "#36719F"),
                "Leído": ("#4CAF50", "#388E3C"),
                "Leyendo": ("#FF9800", "#F57C00"),
                "Pendiente": ("#9C27B0", "#7B1FA2"),
                "Abandonado": ("#F44336", "#D32F2F"),
            }

            color_normal, color_hover = colores.get(estado, ("#3B8ED0", "#36719F"))

            # Frame individual para cada libro
            item_frame = ctk.CTkFrame(self.frame_libros, fg_color=color_normal, height=190)
            item_frame.pack(fill="x", padx=10, pady=5)
            item_frame.grid_propagate(False)

            # Funciones para el efecto hover en el frame del libro
            def make_hover_callbacks(frame, normal_color, hover):
                def on_enter(e, f=frame, hc=hover):
                    f.configure(fg_color=hc)
                    f.configure(cursor="hand2")

                def on_leave(e, f=item_frame, nc=normal_color):
                    f.configure(fg_color=nc)
                    f.configure(cursor="")
                return on_enter, on_leave

            on_enter, on_leave = make_hover_callbacks(item_frame, color_normal, color_hover)
            item_frame.grid_columnconfigure(0, weight=1)
            item_frame.grid_rowconfigure(0, weight=1)
            item_frame.bind("<Enter>", on_enter)
            item_frame.bind("<Leave>", on_leave)

            texto_label = ctk.CTkLabel(item_frame, text=texto, anchor="w", justify="left", font=self.fuente)
            texto_label.grid(row=0, column=0, sticky="nsw", padx=(10, 0))
            texto_label.bind("<Enter>", on_enter)
            texto_label.bind("<Leave>", on_leave)

            imagen_label = ctk.CTkLabel(item_frame, text="")
            imagen_label.grid(row=0, column=1, sticky="nse", padx=10)
            imagen_label.bind("<Enter>", on_enter)
            imagen_label.bind("<Leave>", on_leave)

            # Lógica para mostrar la portada del libro:
            # Si cover_id es un nombre de archivo con extensión, lo usa directamente.
            # Si es solo un id, prueba con varias extensiones.
            cover_id = libro.get("cover_id")
            if cover_id:
                if cover_id.endswith((".jpg", ".png", ".jpeg")):
                    ruta = os.path.join("mi_biblio_app", "portadas", cover_id)
                    if os.path.exists(ruta):
                        try:
                            imagen_local = Image.open(ruta).resize((100, 150))
                            imagen = ctk.CTkImage(light_image=imagen_local, size=(100, 150))
                            imagen_label.configure(image=imagen)
                        except Exception as e:
                            print("Error cargando portada local:", e)
                            imagen_label.configure(image=self.imagen_sin_portada)
                    else:
                        imagen_label.configure(image=self.imagen_sin_portada)
                else:
                    ruta_base = os.path.join("mi_biblio_app", "portadas", cover_id)
                    for ext in [".jpg", ".png", ".jpeg"]:
                        ruta = ruta_base + ext
                        if os.path.exists(ruta):
                            try:
                                imagen_local = Image.open(ruta).resize((100, 150))
                                imagen = ctk.CTkImage(light_image=imagen_local, size=(100, 150))
                                imagen_label.configure(image=imagen)
                                break
                            except Exception as e:
                                print("Error cargando portada local:", e)
                                imagen_label.configure(image=self.imagen_sin_portada)
                    else:
                        imagen_label.configure(image=self.imagen_sin_portada)
            else:
                imagen_label.configure(image=self.imagen_sin_portada)

            # Asocia la acción de editar libro al hacer clic en cualquier parte del frame
            item_frame.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))
            texto_label.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))
            imagen_label.bind("<Button-1>", lambda e, l=libro: self.accion_editar_libro(l))


    """
    Abre la ventana para elegir el modo de añadir un libro (nuevo o desde la API).
    """
    def accion_anhadir(self):
        ventana = VentanaElegirModo(self, callback=self.mostrar_libros_guardados)

    """
    Realiza la búsqueda de libros por título o autor.
    Si el campo de búsqueda está vacío, muestra todos los libros guardados.
    """
    def accion_buscar(self):
        texto = self.entry_busqueda.get().strip().lower()
        if not texto:
            self.mostrar_libros_guardados()
            return
        
        try:
            libros = buscar_libros_por_titulo_o_autor(texto)
            if libros:
                self.mostrar_libros(libros)
            else:
                messagebox.showinfo("Sin resultados", "No se encontraron libros que coincidan.")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al buscar libros.\n{e}")


    """
    Abre la ventana de edición para el libro seleccionado.
    """
    def accion_editar_libro(self, libro):
        ventana = VentanaEditarLibro(self, libro, callback=self.mostrar_libros_guardados, modo_edicion=True)
        ventana.lift()
        ventana.focus_force()
        ventana.grab_set()


    """
    Recarga la lista de libros guardados desde la base de datos y los muestra en pantalla.
    """
    def mostrar_libros_guardados(self):
        self.libros = obtener_libros_guardados()
        self.mostrar_libros(self.libros)