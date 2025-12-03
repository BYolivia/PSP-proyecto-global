# Módulo: logica/T1/textEditor.py

import os

# Definimos la ruta del archivo de notas (asumiendo que res/ está un nivel arriba)
# Esto calcula la ruta absoluta: .../ProyectoGlobal/res/notes
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # logica/T1 -> logica -> ProyectoGlobal
ARCHIVO_NOTAS_RES = os.path.join(BASE_DIR, "res", "notes")


def cargar_contenido_res_notes():
    """
    Carga el contenido del archivo 'res/notes'. Si no existe, lo crea y devuelve una cadena vacía.
    """
    try:
        if not os.path.exists(os.path.dirname(ARCHIVO_NOTAS_RES)):
            os.makedirs(os.path.dirname(ARCHIVO_NOTAS_RES), exist_ok=True)

        if not os.path.exists(ARCHIVO_NOTAS_RES):
            with open(ARCHIVO_NOTAS_RES, 'w', encoding='utf-8') as f:
                f.write("")  # Crear vacío si no existe
            return ""

        with open(ARCHIVO_NOTAS_RES, 'r', encoding='utf-8') as f:
            return f.read()

    except Exception as e:
        print(f"Error al cargar el archivo {ARCHIVO_NOTAS_RES}: {e}")
        return f"Error al cargar: {e}"


def guardar_contenido_res_notes(contenido: str):
    """
    Guarda el contenido proporcionado en el archivo 'res/notes'.
    """
    try:
        # Aseguramos que la carpeta exista antes de intentar escribir
        os.makedirs(os.path.dirname(ARCHIVO_NOTAS_RES), exist_ok=True)

        with open(ARCHIVO_NOTAS_RES, 'w', encoding='utf-8') as f:
            f.write(contenido)

        return True, f"Contenido guardado exitosamente en {ARCHIVO_NOTAS_RES}"

    except Exception as e:
        error_msg = f"Error al guardar en {ARCHIVO_NOTAS_RES}: {e}"
        print(error_msg)
        return False, error_msg