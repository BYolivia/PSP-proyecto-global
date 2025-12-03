# Módulo: logica/T1/openBrowser.py

import webbrowser

def navegar_a_url(url: str):
    """
    Abre la URL proporcionada en el navegador web predeterminado del sistema.
    Utiliza el método .open(new=1) para solicitar una nueva ventana.
    """
    url = url.strip()

    if not url:
        print("Error de Navegación: URL vacía.")
        return False

    # Restauramos la verificación de esquema para la estabilidad de la URI
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    try:
        # Se usa new=1 para solicitar una nueva ventana.
        # El comportamiento final depende del SO y del navegador por defecto del usuario.
        webbrowser.open(url, new=1)
        print(f"Lanzando navegador externo (solicitando nueva ventana) con URL: {url}")
        return True
    except Exception as e:
        print(f"Error crítico al intentar abrir el navegador para {url}: {e}")
        return False