import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import urllib.request
from io import BytesIO
from database import actualizar_libro, eliminar_libro

class VentanaEditarLibro(ctk.CTkToplevel):
    def __init__(self, master, libro, callback=None):
        super().__init__(master)

        self.libro = libro
        self.callback = callback
        self.title("Editar Libro")
        self.geometry("600x700")
        self.resizable(False, False)

        self.grid_columnconfigure(1, weight=1)

        self.crear_widgets()

    def crear_widgets(self):
        fila = 0

        if self.libro.get("cover_id"):
            try:
                url = f"https://covers.openlibrary.org/b/id/{self.libro['cover_id']}-L.jpg"
                with urllib.request.urlopen(url) as u:
                    raw_data = u.read()
                im = Image.open(BytesIO(raw_data)).resize((150, 220))
                imagen = ctk.CTkImage(light_image=im, size=(150, 220))
                portada = ctk.CTkLabel(self, image=imagen, text="")
                portada.grid(row=fila, column=0, columnspan=2, pady=10)
            except:
                pass

        fila += 1
        self.entries = {}

        campos = [
            ("titulo", "Título"),
            ("fecha_publicacion", "Fecha publicación"),
            ("fecha_edicion", "Fecha edición"),
            ("paginas", "Páginas"),
            ("isbn", "ISBN"),
            ("serie", "Serie"),
            ("volumen", "Volumen"),
            ("fecha_comenzado", "Fecha comenzado"),
            ("fecha_terminado", "Fecha terminado"),
            ("estado", "Estado"),
            ("calificacion", "Calificación"),
            ("tipo", "Tipo"),
            ("adquisicion", "Adquisición"),
            ("editorial", "Editorial")
        ]

        self.textos_largos = {}
        for clave, etiqueta in [("resumen", "Resumen"), ("resena_personal", "Reseña personal")]:
            lbl = ctk.CTkLabel(self, text=etiqueta + ":")
            lbl.grid(row=fila, column=0, padx=10, pady=5, sticky="ne")
            texto = ctk.CTkTextbox(self, height=80)
            texto.insert("1.0", self.libro.get(clave, ""))
            texto.grid(row=fila, column=1, padx=10, pady=5, sticky="ew")
            self.textos_largos[clave] = texto
            fila += 1

        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.grid(row=fila, column=0, columnspan=2, pady=20)

        btn_guardar = ctk.CTkButton(frame_botones, text="Guardar cambios", command=self.guardar_cambios)
        btn_guardar.pack(side="left", padx=10)

        btn_eliminar = ctk.CTkButton(frame_botones, text="Eliminar libro", fg_color="red", hover_color="#8B0000", command=self.eliminar_libro)
        btn_eliminar.pack(side="left", padx=10)

        btn_cancelar = ctk.CTkButton(frame_botones, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side="left", padx=10)

    def guardar_cambios(self):
        for clave, entry in self.entries.items():
            self.libro[clave] = entry.get().strip()

        for clave, texto in self.textos_largos.items():
            self.libro[clave] = texto.get("1.0", "end").strip()

        actualizar_libro(self.libro)

        if self.callback:
            self.destroy()

    def eliminar_libro(self):
        confirm = messagebox.askyesno("Eliminar", "¿Estás seguro de que quieres elimnar este libro?")
        if confirm:
            eliminar_libro(self.libro["id"])
            if self.callback:
                self.callback()
            self.destroy()