# Módulo: logica/T1/geterSystemRecource.py

import psutil


def obtener_datos_cpu_ram():
    """
    Función que utiliza psutil para recopilar información de CPU, RAM y procesos.
    :return: Diccionario con métricas.
    """

    cpu_percent_total = psutil.cpu_percent(interval=None)
    cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)

    mem = psutil.virtual_memory()

    num_procesos = len(psutil.pids())

    cpu_freq = psutil.cpu_freq()

    datos = {
        'cpu_total': cpu_percent_total,
        'cpu_cores': cpu_percent_per_core,
        'ram_total_gb': round(mem.total / (1024 ** 3), 2),
        'ram_uso_gb': round(mem.used / (1024 ** 3), 2),
        'ram_percent': mem.percent,
        'num_hilos': num_procesos,
        'cpu_freq_mhz': cpu_freq.current if cpu_freq else 0
    }

    return datos