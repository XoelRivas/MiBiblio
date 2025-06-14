import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image
import urllib.request
from io import BytesIO
from database import actualizar_libro, eliminar_libro, insertar_libro, insertar_editorial, insertar_autor, insertar_genero
from tkcalendar import Calendar
from datetime import datetime
import tkinter as tk
import sqlite3
import os
from utils.rutas import recurso_absoluto, carpeta_portadas

"""
Clase que implementa un campo de entrada de fecha personalizado.
Permite al usuario seleccionar una fecha mediante un calendario emergente,
mostrando la fecha seleccionada en un campo de solo lectura.
"""
class CustomDateEntry(ctk.CTkFrame):
    """
    Inicializa un campo de entrada de fecha personalizado con un formato específico.
    """
    def __init__(self, master=None, date_format="YYYY-mm-dd", **kwargs):
        super().__init__(master)
        self.date_format = date_format
        self.selected_date = None

        self.entry = ctk.CTkEntry(self, width=150)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.configure(state="readonly")
        self.entry.bind("<Button-1>", self.open_calendar)

        self.top = None

    """
    Abre una ventana emergente con un calendario para seleccionar la fecha.
    """
    def open_calendar(self, event=None):
        if self.top is not None and self.top.winfo_exists():
            return
        
        self.top = tk.Toplevel(self)
        self.top.transient(self)
        self.top.grab_set()
        self.top.title("Seleccionar fecha")

        self.top.protocol("WM_DELETE_WINDOW", self.close_calendar)

        today = datetime.today()

        self.cal = Calendar(self.top, selectmode="day", year=today.year, month=today.month, day=today.day, date_pattern=self.date_format)
        self.cal.pack(padx=10, pady=10)

        button = tk.Button(self.top, text="Aceptar", command=self.set_selected_date)
        button.pack(pady=(0, 10))

    """
    Cierra la ventana emergente del calendario.
    """
    def close_calendar(self):
        if self.top is not None:
            self.top.destroy()
            self.top = None

    """
    Establece la fecha seleccionada en el campo de entrada y cierra el calendario.
    """
    def set_selected_date(self):
        self.selected_date = self.cal.get_date()
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, self.selected_date)
        self.entry.configure(state="readonly")
        self.close_calendar()

    """
    Devuelve la fecha seleccionada como cadena.
    """
    def get(self):
        return self.selected_date or ""

    """
    Establece una fecha específica en el campo de entrada.
    """
    def set_date(self, date):
        self.selected_date = date
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        if date:
            self.entry.insert(0, date)
        self.entry.configure(state="readonly")

"""
Clase que representa una ventana para crear o editar la información de un libro.
Permite gestionar todos los campos relevantes, incluyendo autores, géneros,
portada, fechas y otros datos, así como guardar, actualizar o eliminar el libro.
"""
class VentanaEditarLibro(ctk.CTkToplevel):
    """
    Inicializa la ventana para editar o crear un libro.
    Carga los datos del libro si existen y prepara los widgets.
    """
    def __init__(self, master, libro, callback=None, modo_edicion=False):
        super().__init__(master)

        self.libro = libro
        self.callback = callback
        self.title("Editar Libro")
        self.geometry("900x700")
        self.resizable(False, False)
        self.campos = {}
        self.entradas_autor = []
        self.entradas_genero = []
        self.imagen_sin_portada = ctk.CTkImage(light_image=Image.open(recurso_absoluto("mi_biblio_app/portadas/sin_portada.png")), size=(120, 180))
        self.modo_edicion = modo_edicion
        
        self.iconbitmap(recurso_absoluto("mi_biblio_app/imagenes/icono.ico"))

        self.crear_widgets()

        self.portada_label.bind("<Button-1>", self.seleccionar_portada_personalizada)

    """
    Crea y organiza todos los widgets de la ventana, incluyendo campos de entrada,
    botones y el área para la portada del libro.
    """
    def crear_widgets(self):
        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=0)

        self.formulario_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.formulario_frame.grid(row=0, column=0, sticky="n", padx=10)

        self.portada_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.portada_frame.grid(row=0, column=1, sticky="ne", padx=20)
        self.portada_frame.grid_rowconfigure(0, weight=1)
        self.portada_frame.grid_columnconfigure(0, weight=1)

        self.config_campos = [
            ("titulo", "Título", "entry"),
            ("autor", "Autor", "multi_entry_autor"),
            ("serie", "Serie", "entry"),
            ("volumen", "Volumen", "entry"),
            ("fecha_publicacion", "Fecha publicación", "calendar"),
            ("fecha_edicion", "Fecha edición", "calendar"),
            ("editorial", "Editorial", "entry"),
            ("isbn", "ISBN", "entry"),
            ("resumen", "Resumen", "textbox"),
            ("genero", "Género", "multi_entry_genero"),
            ("paginas", "Páginas", "entry"),
            ("estado", "Estado", "optionmenu", ["-", "Leyendo", "Leído", "Pendiente", "Abandonado"]),
            ("fecha_comenzado", "Fecha comenzado", "calendar"),
            ("fecha_terminado", "Fecha terminado", "calendar"),
            ("tipo", "Tipo", "optionmenu", ["Físico", "Ebook", "Audio"]),
            ("adquisicion", "Adquisición", "optionmenu", ["Comprado", "Biblioteca", "Gratis", "Prestado", "Regalo"]),
            ("resena_personal", "Reseña personal", "textbox"),
            ("calificacion", "Calificación", "optionmenu", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]),
        ]

        fila = 0

        for config in self.config_campos:
            clave, etiqueta, tipo_widget = config[0], config[1], config[2]
            ctk.CTkLabel(self.formulario_frame, text=etiqueta).grid(row=fila, column=0, sticky="w", pady=5)

            if tipo_widget == "entry":
                widget = ctk.CTkEntry(self.formulario_frame, width=400)
                widget.grid(row=fila, column=1, pady=5, padx=10, sticky="w")
                self.campos[clave] = widget
            elif tipo_widget == "calendar":
                widget = CustomDateEntry(self.formulario_frame)
                widget.grid(row=fila, column=1, pady=5, padx=10, sticky="w")
                self.campos[clave] = widget
            elif tipo_widget == "textbox":
                widget = ctk.CTkTextbox(self.formulario_frame, width=400)
                widget.grid(row=fila, column=1, pady=5, padx=10, sticky="w")
                self.campos[clave] = widget
            elif tipo_widget == "optionmenu":
                opciones = config[3]
                widget = ctk.CTkOptionMenu(self.formulario_frame, values=opciones)
                widget.grid(row=fila, column=1, pady=5, padx=10, sticky="w")
                self.campos[clave] = widget
            elif tipo_widget == "multi_entry_autor":
                self.entradas_autor = []
                self.frame_autores = ctk.CTkFrame(self.formulario_frame, fg_color="#C0C0C0", corner_radius=10, border_width=1, border_color="#444444")
                self.frame_autores.grid(row=fila, column=1, pady=5, padx=10, sticky="w", columnspan=2)

                self.frame_autores_contenido = ctk.CTkFrame(self.frame_autores, fg_color="transparent")
                self.frame_autores_contenido.pack(padx=10, pady=10, fill="both", expand=True)

                self.anadir_entrada_autor()
                self.boton_anadir_autor = ctk.CTkButton(self.formulario_frame, text="+", width=30, command=self.anadir_entrada_autor)
                self.boton_anadir_autor.grid(row=fila, column=2, padx=(20, 0), sticky="w")

                self.boton_quitar_autor = ctk.CTkButton(self.formulario_frame, text="-", width=30, command=self.quitar_entrada_autor)
                self.boton_quitar_autor.grid(row=fila, column=3, padx=(5, 0), sticky="w")
                self.boton_quitar_autor.grid_remove()
                
            elif tipo_widget == "multi_entry_genero":
                self.entradas_genero = []
                self.frame_generos = ctk.CTkFrame(self.formulario_frame, fg_color="#C0C0C0", corner_radius=10, border_width=1, border_color="#444444")
                self.frame_generos.grid(row=fila, column=1, pady=5, padx=10, sticky="w", columnspan=2)

                self.frame_generos_contenido = ctk.CTkFrame(self.frame_generos, fg_color="transparent")
                self.frame_generos_contenido.pack(padx=10, pady=10, fill="both", expand=True)

                self.anadir_entrada_genero()
                self.boton_anadir_genero = ctk.CTkButton(self.formulario_frame, text="+", width=30, command=self.anadir_entrada_genero)
                self.boton_anadir_genero.grid(row=fila, column=2, padx=(20, 0), sticky="w")

                self.boton_quitar_genero = ctk.CTkButton(self.formulario_frame, text="-", width=30, command=self.quitar_entrada_genero)
                self.boton_quitar_genero.grid(row=fila, column=3, padx=(5, 0), sticky="w")
                self.boton_quitar_genero.grid_remove()
            else:
                continue

            fila += 1

        self.portada_label = ctk.CTkLabel(self.portada_frame, image=self.imagen_sin_portada, text="")
        self.portada_label.grid(row=0, column=0, padx=10, pady=10)
        self.portada_label.bind("<Enter>", lambda e: self.portada_label.configure(cursor="hand2"))
        self.portada_label.bind("<Leave>", lambda e: self.portada_label.configure(cursor=""))

        ctk.CTkButton(self, text="Guardar cambios", command=self.guardar_cambios).pack(side="left", padx=20, pady=(0, 20))
        if self.modo_edicion:
            ctk.CTkButton(self, text="Eliminar libro", fg_color="red", hover_color="#8B0000", command=self.eliminar_libro).pack(side="left", padx=10, pady=(0, 20))
        ctk.CTkButton(self, text="Cancelar", command=self.destroy).pack(side="left", padx=10, pady=(0, 20))

        self.mostrar_datos()

    """
    Muestra un cuadro de diálogo personalizado para confirmar una acción.
    Devuelve True si el usuario confirma, False en caso contrario.
    """
    def dialogo_confirmacion(self, titulo, mensaje):
        respuesta = {"valor": None}

        def confirmar():
            respuesta["valor"] = True
            ventana.destroy()

        def cancelar():
            respuesta["valor"] = False
            ventana.destroy()

        ventana = ctk.CTkToplevel(self)
        ventana.title(titulo)
        ventana.geometry("300x150")
        ventana.resizable(False, False)
        ventana.transient(self)
        ventana.grab_set()

        label = ctk.CTkLabel(ventana, text=mensaje, wraplength=250)
        label.pack(pady=20)

        boton_frame = ctk.CTkFrame(ventana, fg_color="transparent")
        boton_frame.pack(pady=10)

        boton_si = ctk.CTkButton(boton_frame, text="Sí", command=confirmar)
        boton_si.pack(side="left", padx=10)

        boton_no = ctk.CTkButton(boton_frame, text="No", command=cancelar)
        boton_no.pack(side="left", padx=10)

        self.wait_window(ventana)
        return respuesta["valor"]

    """
    Permite al usuario seleccionar una imagen de portada personalizada para el libro.
    La imagen seleccionada se guarda y se muestra en la interfaz.
    """
    def seleccionar_portada_personalizada(self, event=None):
        respuesta = self.dialogo_confirmacion("Cambiar portada", "¿Desea añadir una portada?")
        if not respuesta:
            return

        ruta_imagen = filedialog.askopenfilename(
            title="Seleccionar imagen de portada",
            filetypes=[
                ("Imágenes PNG", "*.png"),
                ("Imágenes JPG", "*.jpg"),
                ("Imágenes JPEG", "*.jpeg"),
                ("Todos los formatos de imagen", "*.png *.jpg *.jpeg")
            ],
            parent=self
        )

        if ruta_imagen:
            try:
                carpeta_imagenes = carpeta_portadas()
                if self.libro and self.libro.get("id"):
                    nombre_archivo = f"portada_{self.libro.get('id')}.png"
                else:
                    nombre_archivo = "portada_temporal.png"
                destino = os.path.join(carpeta_imagenes, nombre_archivo)
                imagen = Image.open(ruta_imagen)
                imagen = imagen.resize((120, 180))
                imagen.save(destino)

                portada_nueva = ctk.CTkImage(light_image=imagen, size=(120, 180))
                self.portada_label.configure(image=portada_nueva)
                self.imagen_personalizada = nombre_archivo

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar la imagen seleccionada.\n{e}", parent=self)

    """
    Añade un nuevo campo de entrada para introducir un autor adicional.
    Muestra el botón para eliminar autores si hay más de uno.
    """
    def anadir_entrada_autor(self):
        row = len(self.entradas_autor)
        entry = ctk.CTkEntry(self.frame_autores_contenido, width=400)
        entry.grid(row=row, column=0, pady=5, sticky="w")
        self.entradas_autor.append(entry)
        if len(self.entradas_autor) > 1:
            self.boton_quitar_autor.grid()

    """
    Añade un nuevo campo de entrada para introducir un género adicional.
    Muestra el botón para eliminar géneros si hay más de uno.
    """
    def anadir_entrada_genero(self):
        row = len(self.entradas_genero)
        entry = ctk.CTkEntry(self.frame_generos_contenido, width=400)
        entry.grid(row=row, column=0, pady=5, sticky="w")
        self.entradas_genero.append(entry)
        if len(self.entradas_genero) > 1:
            self.boton_quitar_genero.grid()

    """
    Elimina el último campo de entrada de autor si hay más de uno.
    Oculta el botón de eliminar si solo queda un campo.
    """
    def quitar_entrada_autor(self):
        if len(self.entradas_autor) > 1:
            entry = self.entradas_autor.pop()
            entry.destroy()
        if len(self.entradas_autor) == 1:
            self.boton_quitar_autor.grid_remove()

    """
    Elimina el último campo de entrada de género si hay más de uno.
    Oculta el botón de eliminar si solo queda un campo.
    """
    def quitar_entrada_genero(self):
        if len(self.entradas_genero) > 1:
            entry = self.entradas_genero.pop()
            entry.destroy()
        if len(self.entradas_genero) == 1:
            self.boton_quitar_genero.grid_remove()

    """
    Muestra los datos del libro en los campos correspondientes de la interfaz.
    Carga la portada si está disponible.
    """
    def mostrar_datos(self):
        if self.libro is None:
            self.portada_label.configure(image=self.imagen_sin_portada, text="")
            return
        
        autores = (self.libro.get("autor") or "").split(", ")
        if not self.entradas_autor:
            self.anadir_entrada_autor()

        for i, autor in enumerate(autores):
            if i < len(self.entradas_autor):
                self.entradas_autor[i].insert(0, autor)
            else:
                self.anadir_entrada_autor()
                self.entradas_autor[-1].insert(0, autor)

        generos = (self.libro.get("genero") or "").split(", ")
        if not self.entradas_genero:
            self.anadir_entrada_genero()

        for i, genero in enumerate(generos):
            if i < len(self.entradas_genero):
                self.entradas_genero[i].insert(0, genero)
            else:
                self.anadir_entrada_genero()
                self.entradas_genero[-1].insert(0, genero)

        for clave, _, tipo_widget, *resto in self.config_campos:
            if tipo_widget in ["multi_entry_autor", "multi_entry_genero"]:
                continue
            valor = self.libro.get(clave)
            widget = self.campos[clave]

            if valor is None:
                valor = ""

            if tipo_widget == "entry":
                widget.insert(0, str(valor))
            elif tipo_widget == "calendar":
                try:
                    widget.set_date(valor)
                except Exception:
                    pass
            elif tipo_widget == "textbox":
                widget.insert("1.0", str(valor))
            elif tipo_widget == "optionmenu":
                if valor in widget.cget("values"):
                    widget.set(valor)
                else:
                    widget.set(widget.cget("values")[0])

        cover_id = self.libro.get("cover_id")
        imagen_cargada = False

        if cover_id:
            for ext in [".jpg", ".png", ".jpeg"]:
                ruta = os.path.join(carpeta_portadas(), cover_id if cover_id.endswith(ext) else cover_id + ext)
                if os.path.exists(ruta):
                    try:
                        imagen_local = Image.open(ruta)
                        portada = ctk.CTkImage(light_image=imagen_local, size=(120, 180))
                        self.portada_label.configure(image=portada, text="")
                        imagen_cargada = True
                        break
                    except Exception as e:
                        print(f"Error cargando portada desde {ruta}: {e}")

        if not imagen_cargada:
            self.portada_label.configure(image=self.imagen_sin_portada, text="")

    """
    Descarga y muestra una imagen de portada desde una URL.
    """
    def cargar_portada(self, url):
        try:
            with urllib.request.urlopen(url) as u:
                raw_data = u.read()
            im = Image.open(BytesIO(raw_data)).resize((120, 180))
            self.portada = ctk.CTkImage(light_image=im, size=(120, 180))
            self.after(0, lambda: self.portada_label.configure(image=self.portada, text=""))
        except Exception as e:
            print("Error cargando portada:", e)
            self.after(0, lambda: self.portada_label.configure(text="Error al cargar portada"))

    """
    Recoge los datos introducidos por el usuario y los guarda en la base de datos.
    Si es un libro nuevo, lo inserta; si es existente, lo actualiza.
    """
    def guardar_cambios(self):
        datos_actualizados = {}

        for clave, _, tipo_widget, *_ in self.config_campos:
            if tipo_widget in ["multi_entry_autor", "multi_entry_genero"]:
                continue
            widget = self.campos[clave]
            if tipo_widget == "entry":
                datos_actualizados[clave] = widget.get()
            elif tipo_widget == "textbox":
                datos_actualizados[clave] = widget.get("1.0", "end").strip()
            elif tipo_widget == "optionmenu":
                datos_actualizados[clave] = widget.get()
            elif tipo_widget == "calendar":
                valor = widget.get()
                datos_actualizados[clave] =valor[:4] if valor else ""

        autores = [entry.get().strip() for entry in self.entradas_autor if entry.get().strip()]
        generos = [entry.get().strip() for entry in self.entradas_genero if entry.get().strip()]
        datos_actualizados["cover_id"] = self.libro.get("cover_id") if self.libro else None

        if hasattr(self, "imagen_personalizada"):
            datos_actualizados["cover_id"] = self.imagen_personalizada

        try:
            conn = sqlite3.connect(recurso_absoluto("mi_biblio_app/miBiblio.db"))
            cursor = conn.cursor()

            id_editorial = None
            if "editorial" in datos_actualizados and datos_actualizados["editorial"]:
                id_editorial = insertar_editorial(datos_actualizados["editorial"], conn=conn, cursor=cursor)

            ids_autores = [insertar_autor(nombre, conn=conn, cursor=cursor) for nombre in autores]
            ids_generos = [insertar_genero(nombre, conn=conn, cursor=cursor) for nombre in generos]

            if self.libro:
                actualizar_libro(datos_actualizados, self.libro["id"], id_editorial, ids_autores, ids_generos, conn, cursor)
                messagebox.showinfo("Éxito", "Libro actualizado correctamente.", parent=self)
            else:
                id_libro = insertar_libro(datos_actualizados, id_editorial, conn=conn, cursor=cursor)

                if hasattr(self, "imagen_personalizada") and self.imagen_personalizada == "portada_temporal.png":
                    carpeta = carpeta_portadas()
                    origen = os.path.join(carpeta, "portada_temporal.png")
                    destino = os.path.join(carpeta, f"portada_{id_libro}.png")
                    if os.path.exists(origen):
                        os.rename(origen, destino)
                        datos_actualizados["cover_id"] = f"portada_{id_libro}.png"
                        cursor.execute("UPDATE libros SET cover_id = ? WHERE id = ?", (datos_actualizados["cover_id"], id_libro))
                        conn.commit()
                    self.imagen_personalizada = datos_actualizados["cover_id"]

                for id_autor in ids_autores:
                    cursor.execute("INSERT OR IGNORE INTO libros_autores (id_libro, id_autor) VALUES (?, ?)", (id_libro, id_autor))
                for id_genero in ids_generos:
                    cursor.execute("INSERT OR IGNORE INTO libros_generos (id_libro, id_genero) VALUES (?, ?)", (id_libro, id_genero))

                conn.commit()
                messagebox.showinfo("Éxito", "Libro creado correctamente.", parent=self)

            conn.close()
            self.destroy()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el libro.\n{e}", parent=self)

    """
    Elimina el libro actual de la base de datos tras confirmación del usuario.
    También elimina la imagen de portada asociada si existe.
    """
    def eliminar_libro(self):
        confirm = messagebox.askyesno(
            "Eliminar", 
            "¿Estás seguro de que quieres eliminar este libro?",
            parent=self
        )
        if confirm:
            try:
                cover_id = self.libro.get("cover_id")
                if cover_id:
                    posibles_extensiones = [".png", ".jpg", ".jpeg"]
                    for ext in posibles_extensiones:
                        ruta_portada = os.path.join(carpeta_portadas(), cover_id if cover_id.endswith(ext) else cover_id + ext)
                        if os.path.exists(ruta_portada):
                            os.remove(ruta_portada)
                            break

                eliminar_libro(self.libro["id"])

                messagebox.showinfo(
                    "Eliminado", 
                    "Libro eliminado correctamente.",
                    parent=self
                )
                self.destroy()
                if self.callback:
                    self.callback()
            except Exception as e:
                messagebox.showerror(
                    "Error", 
                    f"No se pudo eliminar el libro.\n{e}",
                    parent=self
                )