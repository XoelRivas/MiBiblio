import requests

def extraer_isbn(doc):
    if "isbn" in doc and isinstance(doc["isbn"], list):
        return doc["isbn"][0]
    
    ia_list = doc.get("ia", [])
    for item in ia_list:
        if item.startswith("isbn"):
            return item.replace("isbn_", "")

    return None

def buscar_libros_por_titulo(titulo, max_resultados=10):
    url = "https://openlibrary.org/search.json"
    params = {
        "title": titulo,
        "limit": max_resultados
    }

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