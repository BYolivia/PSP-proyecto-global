# Módulo: logica/T1/geterSystemRecource.py

import psutil


def obtener_datos_cpu_ram():
    """
    Función que utiliza psutil para recopilar información de CPU, RAM y procesos.
    :return: Diccionario con métricas.
    """

    # --- 1. MEDICIÓN DE CPU (CORRECCIÓN CLAVE) ---
    # La primera llamada 'primea' el cálculo de psutil.
    psutil.cpu_percent(interval=None)

    # La segunda llamada devuelve el porcentaje real calculado desde la primera.
    # Aquí obtenemos el total y los núcleos en la misma llamada para consistencia.
    cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)
    cpu_percent_total = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
    # Alternativamente, psutil.cpu_percent(interval=None) - pero calculando la media es más seguro.


    # --- 2. RESTO DE DATOS (Sin cambios) ---
    mem = psutil.virtual_memory()
    num_procesos = len(psutil.pids())
    cpu_freq = psutil.cpu_freq()

    datos = {
        'cpu_total': round(cpu_percent_total, 1),
        'cpu_cores': [round(p, 1) for p in cpu_percent_per_core],
        'ram_total_gb': round(mem.total / (1024 ** 3), 2),
        'ram_uso_gb': round(mem.used / (1024 ** 3), 2),
        'ram_percent': mem.percent,
        # Nota: 'num_hilos' es técnicamente el número de PIDs (procesos), no hilos
        'num_hilos': num_procesos,
        'cpu_freq_mhz': cpu_freq.current if cpu_freq else 0
    }

    return datos