import requests

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
            libro = {
                "titulo": doc.get("title"),
                "autor": ", ".join(doc.get("author_name", [])),
                "anho": doc.get("first_publish_year"),
                "isbn": doc.get("isbn", [None])[0],
                "id_openlibrary": doc.get("key")
            }

            resultados.append(libro)

        return resultados
    
    except requests.RequestException as e:
        print(f"Error al conectarse con Open Library: {e}")
        return []