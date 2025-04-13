import sqlite3

def crear_tablas():
    conn = sqlite3.connect("mi_biblio_app/miBiblio.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS autores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS generos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS editoriales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS libros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor_id INTEGER,
        genero_id INTEGER,
        editorial_id INTEGER,
        fecha_publicacion TEXT,
        fecha_edicion TEXT,
        paginas INTEGER,
        isbn TEXT,
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
        FOREIGN KEY (autor_id) REFERENCES autores(id),
        FOREIGN KEY (genero_id) REFERENCES generos(id),
        FOREIGN KEY (editorial_id) REFERENCES editoriales(id)
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    crear_tablas()
    print("Base de datos creada con éxito.")