import subprocess
import platform


def abrir_vscode():
    """
    Intenta abrir Visual Studio Code utilizando el comando 'code'.
    """
    comando = 'code'

    # Notificación en consola para el desarrollador
    print(f"[*] Intentando ejecutar el comando: '{comando}'...")

    try:
        # Ejecutamos el comando de forma asíncrona (Popen) para evitar que
        # la interfaz de Tkinter se bloquee mientras se abre VS Code.
        subprocess.Popen([comando])
        print("[+] Visual Studio Code lanzado exitosamente.")

    except FileNotFoundError:
        # Esto ocurre si el comando 'code' no está en el PATH
        mensaje_error = (
            "===================================================\n"
            f"ERROR: El comando '{comando}' no se encontró en el PATH del sistema.\n"
            "Asegúrate de que Visual Studio Code esté instalado y de que el comando 'code' "
            "esté configurado para ser accesible desde la terminal.\n"
            "==================================================="
        )
        print(mensaje_error)
    except Exception as e:
        # Captura cualquier otro error (ej. permisos)
        print(f"[-] Ocurrió un error inesperado al intentar abrir VS Code: {e}")

