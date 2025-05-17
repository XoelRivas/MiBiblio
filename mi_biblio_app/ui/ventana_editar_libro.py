import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import urllib.request
from io import BytesIO
from database import actualizar_libro, eliminar_libro
import threading

class VentanaEditarLibro(ctk.CTkToplevel):
    def __init__(self, master, libro, callback=None):
        super().__init__(master)

        self.libro = libro
        self.callback = callback
        self.title("Editar Libro")
        self.geometry("800x800")
        self.resizable(False, False)
        self.campos = {}

        self.crear_widgets()
        self.mostrar_datos()

    def crear_widgets(self):
        frame = ctk.CTkScrollableFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        campos_a_mostrar = [
            "titulo", "fecha_publicacion", "fecha_edicion", "paginas", "isbn", "serie", "volumen",
            "fecha_comenzado", "fecha_terminado", "estado", "resumen", "resena_personal", "calificacion",
            "tipo", "adquisicion", "editorial"
        ]

        for i, campo in enumerate(campos_a_mostrar):
            label = ctk.CTkLabel(frame, text=campo.replace("_", " ").capitalize())
            label.grid(row=i, column=0, sticky="w", pady=5)

            entry = ctk.CTkEntry(frame, width=400)
            entry.grid(row=i, column=1, pady=5, padx=10, sticky="ew")
            self.campos[campo] = entry

        self.portada_label = ctk.CTkLabel(frame, text="Cargando portada...")
        self.portada_label.grid(row=0, column=2, rowspan=6, padx=20)

        btn_guardar = ctk.CTkButton(self, text="Guardar cambios", command=self.guardar_cambios)
        btn_guardar.pack(side="left", padx=10)

        btn_eliminar = ctk.CTkButton(self, text="Eliminar libro", fg_color="red", hover_color="#8B0000", command=self.eliminar_libro)
        btn_eliminar.pack(side="left", padx=10)

        btn_cancelar = ctk.CTkButton(self, text="Cancelar", command=self.destroy)
        btn_cancelar.pack(side="left", padx=10)

    def mostrar_datos(self):
        for campo, entry in self.campos.items():
            valor = self.libro.get(campo) or ""
            entry.insert(0, str(valor))

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
            portada = ctk.CTkImage(light_image=im, size=(120, 180))
            self.after(0, lambda: self.portada_label.configure(image=portada, text=""))
        except Exception as e:
            print("Error cargando portada:", e)
            self.after(0, lambda: self.portada_label.configure(text="Error al cargar portada"))

    def guardar_cambios(self):
        datos_actualizados = {campo: campo_widget.get() for campo, campo_widget in self.campos.items()}
        datos_actualizados["cover_id"] = self.libro.get("cover_id")

        try:
            actualizar_libro(datos_actualizados, self.libro["id"])
            messagebox.showinfo("Éxito", "Libro actualizado correctamente.")
            self.destroy()
            self.callback()
        except Exception as e:
            messagebox.showerror("Error", f"No se puedo actualizar el libro.\n{e}")

    def eliminar_libro(self):
        confirm = messagebox.askyesno("Eliminar", "¿Estás seguro de que quieres elimnar este libro?")
        if confirm:
            try:
                eliminar_libro(self.libro["id"])
                messagebox.showinfo("Eliminado", "Libro eliminado correctamente.")
                self.destroy()
                self.callback()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo elimnar el libro.\n{e}")