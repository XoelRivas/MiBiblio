import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import urllib.request
from io import BytesIO
from database import actualizar_libro, eliminar_libro
import threading
from tkcalendar import Calendar
from datetime import datetime
import tkinter as tk

class CustomDateEntry(ctk.CTkFrame):
    def __init__(self, master=None, date_format="YYYY-mm-dd", **kwargs):
        super().__init__(master)
        self.date_format = date_format
        self.selected_date = None

        self.entry = ctk.CTkEntry(self, width=150)
        self.entry.pack(side="left", fill="x", expand=True)
        self.entry.configure(state="readonly")
        self.entry.bind("<Button-1>", self.open_calendar)

        self.top = None

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

    def close_calendar(self):
        if self.top is not None:
            self.top.destroy()
            self.top = None

    def set_selected_date(self):
        self.selected_date = self.cal.get_date()
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, self.selected_date)
        self.entry.configure(state="readonly")
        self.close_calendar()

    def get(self):
        return self.selected_date or ""

    def set_date(self, date):
        self.selected_date = date
        self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        if date:
            self.entry.insert(0, date)
        self.entry.configure(state="readonly")

class VentanaEditarLibro(ctk.CTkToplevel):
    def __init__(self, master, libro, callback=None):
        super().__init__(master)

        self.libro = libro
        self.callback = callback
        self.title("Editar Libro")
        self.geometry("900x800")
        self.resizable(False, False)
        self.campos = {}
        self.entradas_autor = []
        self.entradas_genero = []
        self.imagen_sin_portada = ctk.CTkImage(light_image=Image.open("mi_biblio_app/imagenes/sin_portada.png"), size=(120, 180))
        

        self.crear_widgets()

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
            ("estado", "Estado", "optionmenu", ["Leyendo", "Leído", "Pendiente", "Abandonado"]),
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

        self.portada_label = ctk.CTkLabel(self.portada_frame, text="Cargando portada...")
        self.portada_label.grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkButton(self, text="Guardar cambios", command=self.guardar_cambios).pack(side="left", padx=20, pady=(0, 20))
        ctk.CTkButton(self, text="Eliminar libro", fg_color="red", hover_color="#8B0000", command=self.eliminar_libro).pack(side="left", padx=10, pady=(0, 20))
        ctk.CTkButton(self, text="Cancelar", command=self.destroy).pack(side="left", padx=10, pady=(0, 20))

        self.mostrar_datos()

    def anadir_entrada_autor(self):
        row = len(self.entradas_autor)
        entry = ctk.CTkEntry(self.frame_autores_contenido, width=400)
        entry.grid(row=row, column=0, pady=5, sticky="w")
        self.entradas_autor.append(entry)
        if len(self.entradas_autor) > 1:
            self.boton_quitar_autor.grid()

    def anadir_entrada_genero(self):
        row = len(self.entradas_genero)
        entry = ctk.CTkEntry(self.frame_generos_contenido, width=400)
        entry.grid(row=row, column=0, pady=5, sticky="w")
        self.entradas_genero.append(entry)
        if len(self.entradas_genero) > 1:
            self.boton_quitar_genero.grid()

    def quitar_entrada_autor(self):
        if len(self.entradas_autor) > 1:
            entry = self.entradas_autor.pop()
            entry.destroy()
        if len(self.entradas_autor) == 1:
            self.boton_quitar_autor.grid_remove()

    def quitar_entrada_genero(self):
        if len(self.entradas_genero) > 1:
            entry = self.entradas_genero.pop()
            entry.destroy()
        if len(self.entradas_genero) == 1:
            self.boton_quitar_genero.grid_remove()

    def mostrar_datos(self):
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

        if self.libro.get("cover_id"):
            url = f"https://covers.openlibrary.org/b/id/{self.libro['cover_id']}-L.jpg"
            threading.Thread(target=self.cargar_portada, args=(url,), daemon=True).start()
        else:
            self.portada_label.configure(image=self.imagen_sin_portada, text="")

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
                datos_actualizados[clave] = widget.get()

        datos_actualizados["autor"] = ", ".join(entry.get().strip() for entry in self.entradas_autor if entry.get().strip())
        datos_actualizados["genero"] = ", ".join(entry.get().strip() for entry in self.entradas_genero if entry.get().strip())
        datos_actualizados["cover_id"] = self.libro.get("cover_id")

        try:
            actualizar_libro(datos_actualizados, self.libro["id"])
            messagebox.showinfo("Éxito", "Libro actualizado correctamente.", parent=self)
            self.destroy()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"No se puedo actualizar el libro.\n{e}", parent=self)

    def eliminar_libro(self):
        confirm = messagebox.askyesno(
            "Eliminar", 
            "¿Estás seguro de que quieres eliminar este libro?",
            parent=self
            )
        if confirm:
            try:
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
                    f"No se pudo elimnar el libro.\n{e}",
                    parent=self
                    )