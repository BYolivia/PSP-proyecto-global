import platform


_os = None

def getPlataforma():
    global _os
    if _os==None:
        _os = _obtener_datos_sistema()
    return _os


def accion_placeholder(nombre_accion):
    """
    Función placeholder temporal para acciones que aún no tienen implementación.
    Simplemente imprime un mensaje en la consola.
    """
    print(f"Acción pendiente de implementación: {nombre_accion}")

def _obtener_datos_sistema():
    """
    Función placeholder para la tarea T1.3 (recursos del sistema).
    Esta función se llenará con la lógica para obtener datos de CPU/RAM.
    """
    print("Iniciando la recopilación de datos del sistema...")
    # Lógica a añadir aquí en el futuro (usando psutil, por ejemplo)
    tmpVar = platform.system().lower()
    if tmpVar.__contains__("windows"):
        print("Sistema operativo detectado: Windows")
        return {'WINDOWS'}
    elif tmpVar.__contains__("darwin"):
        print("Sistema operativo detectado: MacOS")
        return {'MACOS'}
    else:
        print("Sistema operativo detectado: Linux/Unix")
        return {'LINUX'}