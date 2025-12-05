# Módulo: logica/T1/trafficMeter.py

import psutil
import time
import threading

# Constante de conversión: 1 KB = 1024 bytes
KB = 1024


class NetIOMonitor(threading.Thread):
    """
    Hilo que monitorea y almacena el tráfico de red (bytes por segundo)
    convirtiéndolo a Kilobytes por segundo (KB/s), además de CPU y RAM.
    """

    def __init__(self, intervalo=1):
        super().__init__()
        self._stop_event = threading.Event()
        self.intervalo = intervalo

        # Almacenamiento seguro para los últimos datos de tráfico
        self.lock = threading.Lock()
        self.data_in_kb = 0.0  # Tráfico de entrada en KB/s (Recibido)
        self.data_out_kb = 0.0  # Tráfico de salida en KB/s (Enviado)
        self.cpu_percent = 0.0  # Nuevo
        self.ram_percent = 0.0  # Nuevo

        # Almacena el contador anterior para calcular la diferencia (tasa)
        self.last_counters = psutil.net_io_counters()

        # Necesario para inicializar la medición de CPU/RAM al inicio
        psutil.cpu_percent(interval=None)

    def run(self):
        """Método principal del hilo."""
        try:
            while not self._stop_event.is_set():
                # Esperar el intervalo antes de la lectura para calcular la tasa
                time.sleep(self.intervalo)
                self._actualizar_datos()
        except Exception as e:
            print(f"Error fatal en el hilo NetIOMonitor: {e}")
            self._stop_event.set()

    def stop(self):
        """Detiene el hilo de forma segura."""
        self._stop_event.set()

    def _actualizar_datos(self):
        """Calcula el tráfico de red en KB/s y mide CPU/RAM."""

        current_counters = psutil.net_io_counters()

        # Medición de CPU y RAM (usando interval=0.0 ya que el sleep garantiza el intervalo)
        current_cpu = psutil.cpu_percent(interval=0.0)
        current_ram = psutil.virtual_memory().percent

        # Calcular la diferencia de bytes recibidos y enviados desde la última lectura
        bytes_recv_diff = current_counters.bytes_recv - self.last_counters.bytes_recv
        bytes_sent_diff = current_counters.bytes_sent - self.last_counters.bytes_sent

        # Calcular la tasa (bytes/segundo) y convertir a KB/s
        rate_in_kb_s = (bytes_recv_diff / self.intervalo) / KB
        rate_out_kb_s = (bytes_sent_diff / self.intervalo) / KB

        # Actualizar el contador anterior
        self.last_counters = current_counters

        # Guardar los resultados de forma segura
        with self.lock:
            self.data_in_kb = rate_in_kb_s
            self.data_out_kb = rate_out_kb_s
            self.cpu_percent = current_cpu
            self.ram_percent = current_ram

    def get_io_data_kb(self):
        """Devuelve el tráfico de E/S, CPU y RAM actual."""
        with self.lock:
            # Devuelve los 4 valores
            return self.data_in_kb, self.data_out_kb, self.cpu_percent, self.ram_percent


# --- FUNCIÓN DE INICIO ---
def iniciar_monitor_red():
    """Inicializa y comienza el monitor de red."""
    monitor = NetIOMonitor(intervalo=1)  # 1 segundo de intervalo
    monitor.start()
    return monitor