import sqlite3

"""
Crea todas las tablas necesarias en la base de datos si no existen.
Incluye tablas para autores, géneros, editoriales, libros y las tablas de relación.
"""
def crear_tablas():
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    # Tabla de autores
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

    # Tabla de géneros literarios
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS generos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """
    )

    # Tabla de editoriales
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS editoriales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """
    )

    # Tabla de libros
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

    # Añadir columna cover_id a la tabla libros si no existe
    try:
        cursor.execute("ALTER TABLE libros ADD COLUMN cover_id TEXT")
    except sqlite3.OperationalError:
        pass

    # Tabla de relación entre libros y autores
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS libros_autores (
        id_libro INTEGER,
        id_autor INTEGER,
        PRIMARY KEY (id_libro, id_autor),
        FOREIGN KEY (id_libro) REFERENCES libros(id) ON DELETE CASCADE,
        FOREIGN KEY (id_autor) REFERENCES autores(id) ON DELETE CASCADE
    );    
"""
    )

    # Tabla de relación entre libros y géneros
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS libros_generos (
        id_libro INTEGER,
        id_genero INTEGER,
        PRIMARY KEY (id_libro, id_genero),
        FOREIGN KEY (id_libro) REFERENCES libros(id) ON DELETE CASCADE,
        FOREIGN KEY (id_genero) REFERENCES generos(id) ON DELETE CASCADE
    );    
"""
    )

    conn.commit()
    conn.close()

"""
Actualiza los datos de un libro existente, así como sus relaciones con autores y géneros.
Si no se pasan conexión y cursor, los crea y los cierra internamente.
"""
def actualizar_libro(libro, id_libro, id_editorial=None, ids_autores=None, ids_generos=None, conn=None, cursor=None):
    cerrar = False
    if conn is None or cursor is None:
        conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
        cursor = conn.cursor()
        cerrar = True

    # Actualiza los campos principales del libro
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
            adquisicion = ?,
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
        libro.get("adquisicion"),
        libro.get("cover_id"),
        id_libro
    ))

    # Actualiza las relaciones con autores y géneros
    cursor.execute("DELETE FROM libros_autores WHERE id_libro = ?", (id_libro,))
    if ids_autores:
        for id_autor in ids_autores:
            cursor.execute("INSERT OR IGNORE INTO libros_autores (id_libro, id_autor) VALUES (?, ?)", (id_libro, id_autor))

    # Actualiza las relaciones con géneros
    cursor.execute("DELETE FROM libros_generos WHERE id_libro = ?", (id_libro,))
    if ids_generos:
        for id_genero in ids_generos:
            cursor.execute("INSERT OR IGNORE INTO libros_generos (id_libro, id_genero) VALUES (?, ?)", (id_libro, id_genero))

    conn.commit()
    if cerrar:
        conn.close()

"""
Elimina un libro y, si corresponde, elimina autores, géneros y editorial asociados
que hayan quedado huérfanos (sin ningún libro relacionado).
"""
def eliminar_libro(id_libro):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON") # Activa las claves foráneas

    try:
        # Obtiene los autores y géneros relacionados antes de eliminar el libro
        cursor.execute("SELECT id_autor FROM libros_autores WHERE id_libro = ?", (id_libro,))
        autores = cursor.fetchall()

        cursor.execute("SELECT id_genero FROM libros_generos WHERE id_libro = ?", (id_libro,))
        generos = cursor.fetchall()

        cursor.execute("SELECT id_editorial FROM libros WHERE id = ?", (id_libro,))
        resultado_editorial = cursor.fetchall()
        id_editorial = resultado_editorial[0][0] if resultado_editorial else None

        # Elimina el libro
        cursor.execute("DELETE FROM libros WHERE id = ?", (id_libro,))

        # Elimina autores huérfanos
        for (id_autor,) in autores:
            cursor.execute("SELECT COUNT(*) FROM libros_autores WHERE id_autor = ?", (id_autor,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM autores WHERE id = ?", (id_autor,))

        # Elimina géneros huérfanos
        for (id_genero,) in generos:
            cursor.execute("SELECT COUNT(*) FROM libros_generos WHERE id_genero = ?", (id_genero,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM generos WHERE id = ?", (id_genero,))

        # Elimina editorial huérfana
        if id_editorial is not None:
            cursor.execute("SELECT COUNT(*) FROM libros WHERE id_editorial = ?", (id_editorial,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("DELETE FROM editoriales WHERE id = ?", (id_editorial,))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

"""
Inserta una editorial si no existe y devuelve su id.
Permite reutilizar una conexión/cursor existente.
"""
def insertar_editorial(nombre, conn=None, cursor=None):
    cerrar = False
    if conn is None or cursor is None:
        conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
        cursor = conn.cursor()
        cerrar = True

    cursor.execute("INSERT OR IGNORE INTO editoriales (nombre) VALUES (?)", (nombre,))
    conn.commit()

    cursor.execute("SELECT id FROM editoriales WHERE nombre = ?", (nombre,))
    id_editorial = cursor.fetchone()[0]

    if cerrar:
        conn.close()

    return id_editorial

"""
Inserta un autor si no existe y devuelve su id.
Divide el nombre completo en nombre y apellido (el último término es el apellido).
Permite reutilizar una conexión/cursor existente.
"""
def insertar_autor(nombre_completo, conn=None, cursor=None):
    partes = nombre_completo.strip().split()
    if len(partes) == 1:
        nombre, apellido = partes[0], ""
    else:
        nombre = " ".join(partes[:-1])
        apellido = partes[-1]

    cerrar = False
    if conn is None or cursor is None:
        conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
        cursor = conn.cursor()
        cerrar = True

    cursor.execute(
        "INSERT OR IGNORE INTO autores (nombre, apellido) VALUES (?, ?)",
        (nombre, apellido)
    )
    conn.commit()

    cursor.execute(
        "SELECT id FROM autores WHERE nombre = ? AND apellido = ?",
        (nombre, apellido)
    )
    resultado = cursor.fetchone()
    id_autor = resultado[0] if resultado else None

    if cerrar:
        conn.close()
    return id_autor

"""
Inserta un libro en la base de datos y devuelve su id.
Si ya existe (por título e ISBN), recupera su id.
Permite reutilizar una conexión/cursor existente.
"""
def insertar_libro(libro, id_editorial=None, conn=None, cursor=None):
    cerrar = False
    if conn is None or cursor is None:
        conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
        cursor = conn.cursor()
        cerrar = True

    cursor.execute("""
        INSERT OR IGNORE INTO libros (
            titulo, serie, volumen, fecha_publicacion, fecha_edicion,
            id_editorial, isbn, resumen, paginas, estado, fecha_comenzado,
            fecha_terminado, tipo, adquisicion, resena_personal, calificacion, cover_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        libro.get("titulo"),
        libro.get("serie"),
        libro.get("volumen"),
        libro.get("fecha_publicacion"),
        libro.get("fecha_edicion"),
        id_editorial,
        libro.get("isbn"),
        libro.get("resumen"),
        libro.get("paginas"),
        libro.get("estado"),
        libro.get("fecha_comenzado"),
        libro.get("fecha_terminado"),
        libro.get("tipo"),
        libro.get("adquisicion"),
        libro.get("resena_personal"),
        libro.get("calificacion"),
        libro.get("cover_id")
    ))
    conn.commit()

    id_libro = cursor.lastrowid

    # Si el libro ya existía, recupera su id
    if not id_libro:
        cursor.execute(
            "SELECT id FROM libros WHERE titulo = ? AND isbn IS ?",
            (libro.get("titulo"), libro.get("isbn"))
        )
        resultado = cursor.fetchone()
        id_libro = resultado[0] if resultado else None

    if cerrar:
        conn.close()

    return id_libro

"""
Inserta un género si no existe y devuelve su id.
Permite reutilizar una conexión/cursor existente.
"""
def insertar_genero(nombre_genero, conn=None, cursor=None):
    cerrar = False
    if conn is None or cursor is None:
        conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
        cursor = conn.cursor()
        cerrar = True

    cursor.execute(
        "INSERT OR IGNORE INTO generos (nombre) VALUES (?)",
        (nombre_genero.strip(),)
    )
    conn.commit()

    cursor.execute(
        "SELECT id FROM generos WHERE nombre = ?",
        (nombre_genero.strip(),)
    )

    resultado = cursor.fetchone()
    id_genero = resultado[0] if resultado else None

    if cerrar:
        conn.close()

    return id_genero

"""
Relaciona un libro con un autor en la tabla de relación muchos a muchos.
"""
def relacionar_libro_autor(id_libro, id_autor):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO libros_autores (id_libro, id_autor)
        VALUES (?, ?)
    """, (id_libro, id_autor))
    conn.commit()
    conn.close()

"""
Relaciona un libro con un género en la tabla de relación muchos a muchos.
"""
def relacionar_libro_genero(id_libro, id_genero):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO libros_generos (id_libro, id_genero)
        VALUES (?, ?)
    """, (id_libro, id_genero))

    conn.commit()
    conn.close()

"""
Recupera todos los libros guardados en la base de datos, incluyendo información
de autores, géneros y editorial, agrupando los autores y géneros por libro.
"""
def obtener_libros_guardados():
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT l.id, l.titulo, l.fecha_publicacion, l.isbn,
               l.fecha_edicion, l.paginas, l.serie, l.volumen,
               l.fecha_comenzado, l.fecha_terminado, l.estado,
               l.resumen, l.resena_personal, l.calificacion,
               l.tipo, l.adquisicion, l.cover_id,
               e.nombre AS editorial,
               GROUP_CONCAT(a.nombre || ' ' || a.apellido, ', ') AS autor,
                GROUP_CONCAT(g.nombre, ', ') AS genero
        FROM libros l
        LEFT JOIN libros_autores la ON l.id = la.id_libro
        LEFT JOIN autores a ON la.id_autor = a.id
        LEFT JOIN libros_generos lg ON l.id = lg.id_libro
        LEFT JOIN generos g ON lg.id_genero = g.id
        LEFT JOIN editoriales e ON l.id_editorial = e.id
        GROUP BY l.id
        ORDER BY l.titulo ASC
    """)

    libros = [dict(fila) for fila in cursor.fetchall()]

    conn.close()
    return libros

"""
Busca libros cuyo título o autor coincida (parcialmente, sin distinción de mayúsculas/minúsculas)
con el texto proporcionado.
"""
def buscar_libros_por_titulo_o_autor(texto):
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
    SELECT l.id, l.titulo, l.fecha_publicacion, l.isbn,
               l.fecha_edicion, l.paginas, l.serie, l.volumen,
               l.fecha_comenzado, l.fecha_terminado, l.estado,
               l.resumen, l.resena_personal, l.calificacion,
               l.tipo, l.adquisicion, l.cover_id,
               e.nombre AS editorial,
               GROUP_CONCAT(a.nombre || ' ' || a.apellido, ', ') AS autor,
                GROUP_CONCAT(g.nombre, ', ') AS genero
        FROM libros l
        LEFT JOIN libros_autores la ON l.id = la.id_libro
        LEFT JOIN autores a ON la.id_autor = a.id
        LEFT JOIN libros_generos lg ON l.id = lg.id_libro
        LEFT JOIN generos g ON lg.id_genero = g.id
        LEFT JOIN editoriales e ON l.id_editorial = e.id
        WHERE LOWER(l.titulo) LIKE ?
            OR LOWER(a.nombre || ' ' || a.apellido) LIKE ?
        GROUP BY l.id
        ORDER BY l.titulo ASC
    """

    param = f"%{texto.lower()}%"
    cursor.execute(query, (param, param))
    
    resultados = [dict(fila) for fila in cursor.fetchall()]

    conn.close()
    return resultados
