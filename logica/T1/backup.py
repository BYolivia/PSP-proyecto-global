# Módulo: logica/T1/backup.py

import subprocess
import os  # Necesario para la verificación y, si es necesario, cambio de permisos

# Importamos las funciones necesarias del controlador
from logica.controlador import getPlataforma, get_scripts_dir

_scripts = None


# --- FUNCIONES AUXILIARES DE DETECCIÓN ---

def _systemToExtension(plataforma_set):
    """Mapea el set de plataforma a la extensión de script necesaria."""
    if 'WINDOWS' in plataforma_set:
        return 'ps1'
    else:
        # Incluye 'LINUX' y 'MACOS'
        return 'sh'


def _get_scripts():
    """Carga la lista de nombres de scripts disponibles en la carpeta 'res/scripts'."""
    global _scripts
    if _scripts is None:
        script_dir_path = get_scripts_dir()
        _scripts = [document.name for document in script_dir_path.iterdir() if document.is_file()]
    return _scripts


def _get_valid_script_path():
    """
    Busca el script de backup adecuado y devuelve su ruta absoluta.
    """
    plataforma = getPlataforma()
    extension = _systemToExtension(plataforma)
    scripts = _get_scripts()
    script_name = None

    for script in scripts:
        if script.endswith(extension):
            script_name = script
            break

    if script_name:
        return get_scripts_dir() / script_name

    return None


# --- FUNCIÓN PRINCIPAL DE ACCIÓN Y EJECUCIÓN ---

def accion_backup_t1():
    """
    Función de acción para el botón de backup.
    1. Obtiene la ruta del script a ejecutar.
    2. Ejecuta el script con subprocess.

    :return: Una tupla (bool, str) que indica éxito/fracaso y el mensaje.
    """

    script_path = _get_valid_script_path()

    # 1. VERIFICACIÓN DE EXISTENCIA DEL SCRIPT
    if script_path is None or not script_path.exists():
        return False, f"ERROR: No se encontró ningún script válido (.ps1 o .sh) en la carpeta de recursos."

    plataforma = getPlataforma()
    system = None

    if 'WINDOWS' in plataforma:
        system = "Windows"
    elif 'LINUX' in plataforma:
        # En Linux, aseguramos el permiso de ejecución antes de intentar ejecutar.
        try:
            os.chmod(script_path, 0o755)  # 0o755: rwxr-xr-x
            system = "Linux"
        except Exception as e:
            return False, f"ERROR de Permiso (Linux): No se pudo establecer el permiso de ejecución para {script_path.name}. Intente ejecutar 'chmod +x {script_path}' manualmente. Detalle: {e}"
    elif 'MACOS' in plataforma:
        system = "macOS"
    else:
        return False, f"Sistema operativo '{plataforma}' no soportado para la ejecución."

    print(f"Backup T1: Ejecutando script: {script_path.name} en {system}")

    # 2. DEFINICIÓN DEL COMANDO
    command = []
    if system == "Windows":
        command = [
            "powershell.exe",
            "-ExecutionPolicy", "Bypass",
            "-File", str(script_path)
        ]
    elif system == "Linux" or system == "macOS":
        command = [str(script_path)]

        # 3. EJECUCIÓN DEL COMANDO
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
        )

        # Copia exitosa
        return True, result.stdout

    except subprocess.CalledProcessError as e:
        error_output = e.stderr if e.stderr else e.stdout
        return False, f"El script falló (Código {e.returncode}). Mensaje del script:\n{error_output}"

    except FileNotFoundError:
        interpeter = 'powershell.exe' if system == 'Windows' else 'el intérprete de shell'
        return False, f"ERROR: El intérprete de comandos ({interpeter}) no se encontró en el PATH del sistema."
    except Exception as e:
        return False, f"Error inesperado al ejecutar el script: {e}"