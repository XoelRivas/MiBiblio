import sqlite3


def crear_tablas():
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS autores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        apellido TEXT NOT NULL,
        UNIQUE(nombre, apellido)
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS generos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS editoriales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS libros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        id_editorial INTEGER,
        fecha_publicacion TEXT,
        fecha_edicion TEXT,
        paginas INTEGER,
        isbn TEXT UNIQUE,
        serie TEXT,
        volumen INTEGER,
        fecha_comenzado TEXT,
        fecha_terminado TEXT,
        estado TEXT,
        resumen TEXT,
        resena_personal TEXT,
        calificacion INTEGER,
        tipo TEXT,
        adquisicion TEXT,
        FOREIGN KEY (id_editorial) REFERENCES editoriales(id)
    );
    """
    )

    try:
        cursor.execute("ALTER TABLE libros ADD COLUMN cover_id INTEGER")
    except sqlite3.OperationalError:
        pass

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS libros_autores (
        id_libro INTEGER,
        id_autor INTEGER,
        PRIMARY KEY (id_libro, id_autor),
        FOREIGN KEY (id_libro) REFERENCES libros(id),
        FOREIGN KEY (id_autor) REFERENCES autores(id)
    );    
"""
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS libros_generos (
        id_libro INTEGER,
        id_genero INTEGER,
        PRIMARY KEY (id_libro, id_genero),
        FOREIGN KEY (id_libro) REFERENCES libros(id),
        FOREIGN KEY (id_genero) REFERENCES generos(id)
    );    
"""
    )

    conn.commit()
    conn.close()

def actualizar_libro(libro, id_libro):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    id_editorial = insertar_editorial(libro.get("editorial")) if libro.get("editorial") else None

    cursor.execute("""
        UPDATE libros SET
            titulo = ?,
            id_editorial = ?,
            fecha_publicacion = ?,
            fecha_edicion = ?,
            paginas = ?,
            isbn = ?,
            serie = ?,
            volumen = ?,
            fecha_comenzado = ?,
            fecha_terminado = ?,
            estado = ?,
            resumen = ?,
            resena_personal = ?,
            calificacion = ?,
            tipo = ?,
            adquision = ?,
            cover_id = ?
        WHERE id = ?
    """, (
        libro.get("titulo"),
        id_editorial,
        libro.get("fecha_publicacion"),
        libro.get("fecha_edicion"),
        libro.get("paginas"),
        libro.get("isbn"),
        libro.get("serie"),
        libro.get("volumen"),
        libro.get("fecha_comenzado"),
        libro.get("fecha_terminado"),
        libro.get("estado"),
        libro.get("resumen"),
        libro.get("resena_personal"),
        libro.get("calificacion"),
        libro.get("tipo"),
        libro.get("adquision"),
        libro.get("cover_id"),
        id_libro
    ))

    conn.commit()
    conn.close()

def eliminar_libro(id_libro):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM libros_autores WHERE id_libro = ?", (id_libro,))
    cursor.execute("DELETE FROM libros_generos WHERE id_libro = ?", (id_libro,))
    cursor.execute("DELETE FROM libros WHERE id = ?", (id_libro,))

    conn.commit()
    conn.close()

def insertar_editorial(nombre):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO editoriales (nombre) VALUES (?)", (nombre,))
    conn.commit()

    cursor.execute("SELECT id FROM editoriales WHERE nombre = ?", (nombre,))
    id_editorial = cursor.fetchone()[0]

    conn.close()
    return id_editorial

def insertar_autor(nombre_completo):
    partes = nombre_completo.strip().split()
    if len(partes) == 1:
        nombre, apellido = partes[0], ""
    else:
        nombre = " ".join(partes[:-1])
        apellido = partes[-1]

    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO autores (nombre, apellido) VALUES (?, ?)",
        (nombre, apellido)
    )
    conn.commit()

    cursor.execute(
        "SELECT id FROM autores WHERE nombre = ? AND apellido = ?",
        (nombre, apellido)
    )
    id_autor = cursor.fetchone()[0]

    conn.close()
    return id_autor

def insertar_libro(libro, id_editorial=None):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO libros (
            titulo, id_editorial, fecha_publicacion, isbn, cover_id
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        libro.get("titulo"),
        id_editorial,
        libro.get("anho"),
        libro.get("isbn"),
        libro.get("cover_id")
    ))
    conn.commit()

    id_libro = cursor.lastrowid

    if not id_libro:
        cursor.execute(
            "SELECT id FROM libros WHERE titulo = ? AND isbn IS ?",
            (libro.get("titulo"), libro.get("isbn"))
        )
        resultado = cursor.fetchone()
        id_libro = resultado[0] if resultado else None

    conn.close()
    return id_libro

def relacionar_libro_autor(id_libro, id_autor):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO libros_autores (id_libro, id_autor)
        VALUES (?, ?)
    """, (id_libro, id_autor))
    conn.commit()
    conn.close()

def obtener_libros_guardados():
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT l.titulo, l.fecha_publicacion, l.isbn,
           GROUP_CONCAT(a.nombre || ' ' || a.apellido, ', ') AS autor,
           l.cover_id
        FROM libros l
        LEFT JOIN libros_autores la ON l.id = la.id_libro
        LEFT JOIN autores a ON la.id_autor = a.id
        GROUP BY l.id
        ORDER BY l.titulo ASC
    """)

    libros = [dict(fila) for fila in cursor.fetchall()]

    conn.close()
    return libros

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada con éxito.")
