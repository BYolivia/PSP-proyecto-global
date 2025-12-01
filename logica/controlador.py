import platform
from pathlib import Path

_os = None

_root_dir = Path(__file__).parent.parent
_scripts_dir = _root_dir / "res" / "scripts"

# --- Funciones de Configuración y Sistema ---

def get_scripts_dir():
    """Devuelve la ruta absoluta al directorio de scripts."""
    return _scripts_dir

def getPlataforma():
    """Detecta y devuelve el conjunto que identifica el SO ('WINDOWS', 'LINUX', 'MACOS')."""
    global _os
    if _os is None:
        _os = _obtener_datos_sistema()
    return _os

def _obtener_datos_sistema():
    """Lógica para detectar el sistema operativo."""
    tmpVar = platform.system().lower()

    if "windows" in tmpVar:
        print("Sistema operativo detectado: Windows")
        return {'WINDOWS'}
    elif "darwin" in tmpVar:
        print("Sistema operativo detectado: MacOS")
        return {'MACOS'}
    else:
        print("Sistema operativo detectado: Linux/Unix")
        return {'LINUX'}

# --- Función Placeholder ---

def accion_placeholder(nombre_accion):
    """
    Función placeholder temporal para acciones que aún no tienen implementación.
    """
    print(f"Acción pendiente de implementación: {nombre_accion}")

# Nota: La lógica de 'subprocess.run' se encuentra ahora en logica/T1/backup.py.