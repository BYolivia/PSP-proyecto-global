import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
from urllib.parse import quote
from tkinter import \
    messagebox  # Para usar messagebox en errores críticos si el Tkinter Loop lo permite (Aunque se recomienda devolver el error)

# --- CONSTANTES DE CONFIGURACIÓN ---
# URL base para realizar búsquedas en Wikipedia en español.
URL_BASE_BUSQUEDA = "https://es.wikipedia.org/w/index.php?search="
URL_TERMINACION = "&title=Especial:Buscar&go=Ir"
ARCHIVO_SALIDA = "res/datos_extraidos.txt"


def hacer_scraping(termino_busqueda: str):
    """
    Construye una URL de búsqueda en Wikipedia con el término proporcionado, 
    extrae el contenido del primer artículo encontrado y guarda el resultado.

    Args:
        termino_busqueda (str): El texto a buscar (ej: "Expedición 30").

    Returns:
        tuple: (bool, str, str) - Éxito (bool), mensaje de estado (str), y contenido extraído (str).
    """
    termino_busqueda = termino_busqueda.strip()

    if not termino_busqueda:
        return False, "❌ El término de búsqueda no puede estar vacío.", ""

    # 1. Construir la URL de búsqueda
    url_codificada = quote(termino_busqueda)
    url_final = URL_BASE_BUSQUEDA + url_codificada + URL_TERMINACION

    print(f"🔗 Buscando y extrayendo datos de: {url_final}")

    try:
        # 2. Realizar la solicitud HTTP
        headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/91.0.4472.124 Safari/537.36')
        }
        response = requests.get(url_final, headers=headers, timeout=15)
        response.raise_for_status()

        # 3. Parsear el contenido
        soup = BeautifulSoup(response.content, 'html.parser')

        # 4. Intentar encontrar el artículo directamente
        title_tag = soup.find('h1', id='firstHeading')
        title = title_tag.get_text().strip() if title_tag else "Sin Título"

        # Si el resultado es una lista de búsqueda (no fue a un artículo directo)
        if title.startswith('Buscar:'):
            # Intentamos extraer el enlace del primer resultado de búsqueda
            results_list = soup.find('ul', class_='mw-search-results')
            if results_list:
                first_result = results_list.find('a')
                if first_result:
                    # Construir la URL completa del primer resultado
                    new_url = "https://es.wikipedia.org" + first_result['href']
                    print(f"➡️ Redirigiendo a primer resultado: {new_url}")
                    # Llamamos a la función auxiliar con la URL del artículo
                    return hacer_scraping_articulo(new_url, termino_busqueda)

                    # Si no hay resultados o no se puede seguir el enlace:
            return False, f"❌ Wikipedia no encontró resultados de artículo para '{termino_busqueda}'.", ""

        # Si encontramos un artículo directamente, extraemos el contenido inmediatamente
        else:
            return hacer_scraping_articulo(url_final, termino_busqueda, title, soup)


    except requests.exceptions.RequestException as e:
        return False, f"❌ Error de red o HTTP al buscar: {e}", ""
    except Exception as e:
        return False, f"❌ Error desconocido en la búsqueda: {type(e).__name__}: {e}", ""


# --- FUNCIÓN AUXILIAR DE EXTRACCIÓN DE ARTÍCULO ---

def hacer_scraping_articulo(url_articulo, termino_busqueda, title=None, soup=None):
    """
    Función auxiliar para extraer el contenido de una URL de artículo específica de Wikipedia.
    """
    try:
        # Si no se pasó el objeto soup (ej. llamada desde redirección), hacemos la solicitud
        if soup is None:
            headers = {
                'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/91.0.4472.124 Safari/537.36')
            }
            response = requests.get(url_articulo, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            title_tag = soup.find('h1', id='firstHeading')
            title = title_tag.get_text().strip() if title_tag else "Sin Título"

        # 4b. Extraer el Cuerpo de Texto del artículo
        # Buscamos en el div principal y excluimos elementos de navegación/metadatos.
        content_div = soup.find('div', id='mw-content-text')

        if content_div:
            # Extraer párrafos, encabezados y listas dentro del contenido principal
            text_elements = content_div.find_all(['p', 'h2', 'h3', 'li'])
            full_text = "\n".join(element.get_text().strip() for element in text_elements if element.get_text().strip())
        else:
            full_text = "No se pudo encontrar el contenido principal del artículo."

        # Limitar la longitud del texto
        max_length = 1500
        extracted_text = full_text[:max_length]
        if len(full_text) > max_length:
            extracted_text += "\n[... Contenido truncado ...]"

        # 5. Formatear
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        output = (
            f"\n\n==========================================================\n"
            f"== 🌐 DATOS EXTRAÍDOS (Búsqueda: '{termino_busqueda}') ==\n"
            f"==========================================================\n"
            f"URL Artículo: {url_articulo}\n"
            f"TÍTULO: {title}\n"
            f"FECHA/HORA: {timestamp}\n"
            f"----------------------------------------------------------\n"
            f"CONTENIDO (Primeros {len(extracted_text)} chars):\n"
            f"----------------------------------------------------------\n"
            f"{extracted_text}\n"
        )

        # 6. Guardar en archivo
        os.makedirs('res', exist_ok=True)
        with open(ARCHIVO_SALIDA, 'a', encoding='utf-8') as f:
            f.write(output)

        print(f"✅ Extracción completada. Datos guardados en {ARCHIVO_SALIDA}")

        # 7. Devolver el resultado para su visualización en la GUI
        return True, f"✅ Extracción de '{title}' (Artículo de Wikipedia) completada.", output

    except requests.exceptions.RequestException as e:
        return False, f"❌ Error de red o HTTP al acceder al artículo: {e}", ""
    except Exception as e:
        return False, f"❌ Error desconocido en la extracción del artículo: {type(e).__name__}: {e}", ""