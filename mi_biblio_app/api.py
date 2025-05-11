import requests
import re

def extraer_isbn(doc):
    if "isbn" in doc and isinstance(doc["isbn"], list):
        return doc["isbn"][0]
    
    ia_list = doc.get("ia", [])
    for item in ia_list:
        if item.startswith("isbn"):
            return item.replace("isbn_", "")

    return None

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
        for doc in datos.get("docs", [])[:max_resultados]:
            isbn = extraer_isbn(doc)
            
            libro = {
                "titulo": doc.get("title"),
                "autor": ", ".join(doc.get("author_name", [])),
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