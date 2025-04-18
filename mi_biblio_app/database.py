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


if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada con éxito.")
