import requests
import re

"""
Extrae el ISBN principal de un documento de Open Library.
Busca primero en el campo 'isbn' y, si no existe, intenta extraerlo del campo 'ia'.

Args:
    doc (dict): Documento de Open Library.

Returns:
    str or None: ISBN encontrado o None si no existe.
"""
def extraer_isbn(doc):
    if "isbn" in doc and isinstance(doc["isbn"], list):
        return doc["isbn"][0]
    
    ia_list = doc.get("ia", [])
    for item in ia_list:
        if item.startswith("isbn"):
            return item.replace("isbn_", "")

    return None

"""
Busca libros en Open Library por título, autor o ISBN.
Si la consulta es un ISBN válido, busca por ISBN; si no, realiza una búsqueda general.

Args:
    query (str): Texto de búsqueda (título, autor o ISBN).
    max_resultados (int): Número máximo de resultados a devolver.

Returns:
    list: Lista de diccionarios con información de cada libro encontrado.
"""
def buscar_libros_por_titulo_autor_isbn(query, max_resultados=20):
    url = "https://openlibrary.org/search.json"

    query_limpia = query.replace("-", "").strip()
    es_isbn = re.fullmatch(r"\d{10}|\d{13}", query_limpia)

    if es_isbn:
        params = {"isbn": query_limpia}
    else:
        params = {"q": query, "limit": max_resultados}

    try:
        respuesta = requests.get(url, params=params)
        respuesta.raise_for_status()
        datos = respuesta.json()

        resultados = []
        # Procesa los documentos devueltos por la API
        for doc in datos.get("docs", [])[:max_resultados]:
            isbn = extraer_isbn(doc)
            
            autores = doc.get("author_name", []),
            libro = {
                "titulo": doc.get("title"),
                "autores": autores,
                "autor": ", ".join([a for a in doc.get("author_name", []) if isinstance(a, str)]),
                "anho": doc.get("first_publish_year"),
                "isbn": isbn,
                "id_openlibrary": doc.get("key"),
                "cover_id": doc.get("cover_i")
            }

            resultados.append(libro)

        return resultados
    
    except requests.RequestException as e:
        print(f"Error al conectarse con Open Library: {e}")
        return []