import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import urllib.request
from io import BytesIO
from database import actualizar_libro, eliminar_libro
import threading
from tkcalendar import DateEntry

class VentanaEditarLibro(ctk.CTkToplevel):
    def __init__(self, master, libro, callback=None):
        super().__init__(master)

        self.libro = libro
        self.callback = callback
        self.title("Editar Libro")
        self.geometry("750x800")
        self.resizable(True, True)
        self.campos = {}

        self.crear_widgets()
        self.mostrar_datos()

    def crear_widgets(self):
        self.frame = ctk.CTkScrollableFrame(self)
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.config_campos = [
            ("titulo", "Título", "entry"),
            ("autor", "Autor", "entry"),
            ("serie", "Serie", "entry"),
            ("volumen", "Volumen", "entry"),
            ("fecha_publicacion", "Fecha publicación", "calendar"),
            ("fecha_edicion", "Fecha edición", "calendar"),
            ("editorial", "Editorial", "entry"),
            ("isbn", "ISBN", "entry"),
            ("resumen", "Resumen", "textbox"),
            ("genero", "Género", "entry"),
            ("paginas", "Páginas", "entry"),
            ("estado", "Estado", "optionmenu", ["Leyendo", "Pendiente", "Terminado"]),
            ("fecha_comenzado", "Fecha comenzado", "calendar"),
            ("fecha_terminado", "Fecha terminado", "calendar"),
            ("tipo", "Tipo", "optionmenu", ["Físico", "Ebook", "Audio"]),
            ("adquisicion", "Adquisición", "optionmenu", ["Comprado", "Biblioteca", "Gratis", "Prestado", "Regalo"]),
            ("resena_personal", "Reseña personal", "textbox"),
            ("calificacion", "Calificación", "optionmenu", ["⭐", "⭐⭐", "⭐⭐⭐", "⭐⭐⭐⭐", "⭐⭐⭐⭐⭐"]),
        ]

        for i, config in enumerate(self.config_campos):
            clave, etiqueta, tipo_widget = config[0], config[1], config[2]
            ctk.CTkLabel(self.frame, text=etiqueta).grid(row=i, column=0, sticky="w", pady=5)

            if tipo_widget == "entry":
                widget = ctk.CTkEntry(self.frame, width=400)
            elif tipo_widget == "calendar":
                widget = DateEntry(self.frame, width=19, background="darkblue", foreground="white", borderwidth=2, date_pattern="yyyy-mm-dd", state="readonly")
            elif tipo_widget == "textbox":
                widget = ctk.CTkTextbox(self.frame, width=400)
            elif tipo_widget == "optionmenu":
                opciones = config[3]
                widget = ctk.CTkOptionMenu(self.frame, values=opciones)
            else:
                continue

            widget.grid(row=i, column=1, pady=5, padx=10, sticky="w")
            self.campos[clave] = widget

        self.portada_label = ctk.CTkLabel(self.frame, text="Cargando portada...")
        self.portada_label.grid(row=0, column=2, rowspan=6, padx=20)

        ctk.CTkButton(self, text="Guardar cambios", command=self.guardar_cambios).pack(side="left", padx=20, pady=(0, 20))
        ctk.CTkButton(self, text="Eliminar libro", fg_color="red", hover_color="#8B0000", command=self.eliminar_libro).pack(side="left", padx=10, pady=(0, 20))
        ctk.CTkButton(self, text="Cancelar", command=self.destroy).pack(side="left", padx=10, pady=(0, 20))

    def mostrar_datos(self):
        for clave, _, tipo_widget, *resto in self.config_campos:
            valor = self.libro.get(clave)
            widget = self.campos[clave]

            if valor is None:
                valor = ""

            if tipo_widget == "entry":
                if valor != "":
                    widget.insert(0, str(valor))
            elif tipo_widget == "calendar":
                try:
                    widget.set_date(valor)
                except Exception:
                    pass
            elif tipo_widget == "textbox":
                if valor != "":
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
            self.portada_label.configure(text="Sin portada")

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
            widget = self.campos[clave]
            if tipo_widget == "entry":
                datos_actualizados[clave] = widget.get()
            elif tipo_widget == "textbox":
                datos_actualizados[clave] = widget.get("1.0", "end").strip()
            elif tipo_widget == "optionmenu":
                datos_actualizados[clave] = widget.get()

        datos_actualizados["cover_id"] = self.libro.get("cover_id")

        try:
            actualizar_libro(datos_actualizados, self.libro["id"])
            messagebox.showinfo("Éxito", "Libro actualizado correctamente.")
            self.destroy()
            if self.callback:
                self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"No se puedo actualizar el libro.\n{e}")

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