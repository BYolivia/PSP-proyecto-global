# Módulo: logica/T2/carreraCamellos.py

import threading
import time
import random
import uuid

# --- RECURSOS Y ESTADO GLOBAL PERSISTENTE ---

# Locks para simular tramos críticos y prevenir DEADLOCKS (Resource Ordering)
lock_tramo_1 = threading.Lock()
lock_tramo_2 = threading.Lock()

# Evento para controlar el inicio de la carrera
CARRERA_EN_CURSO = threading.Event()

# Variable GLOBAL y PERSISTENTE para guardar el ÚLTIMO resultado completo de la carrera.
# Se inicializa a None y se actualiza al finalizar CADA carrera.
# Estructura: {'id': 'uuid', 'activa': bool, 'meta': int, 'camellos': [...], 'ganador': str}
RESULTADO_ULTIMO = None


# --- CLASE DEL HILO CAMELLO ---

class Camello(threading.Thread):
    """Representa un camello que avanza y necesita adquirir recursos (Locks)."""

    def __init__(self, nombre, carrera_id, distancia_meta=50):
        super().__init__()
        self.nombre = nombre
        self.carrera_id = carrera_id
        self.progreso = 0
        self.distancia_meta = distancia_meta
        self.posicion_final = None
        self.estado = "Esperando"

    def run(self):
        self.estado = "Listo"
        CARRERA_EN_CURSO.wait()
        self.estado = "Corriendo"

        # Lista local para guardar el progreso para la actualización final
        progreso_local = []

        while self.progreso < self.distancia_meta:
            if not CARRERA_EN_CURSO.is_set():  # Salir si la carrera se detiene manualmente
                self.estado = "Abortado"
                break

            avance = random.randint(1, 5)
            self.progreso += avance
            if self.progreso >= self.distancia_meta:
                self.progreso = self.distancia_meta
                break

            # 1. TRAMO 1: Adquirir Lock 1
            if self.progreso >= 15 and self.progreso < 30:
                self.intentar_avanzar_tramo(lock_tramo_1, "TRAMO 1")

            # 2. TRAMO 2: Adquirir Lock 2 (Respetando la jerarquía para evitar deadlock)
            elif self.progreso >= 30 and self.progreso < 45:
                # Simulación de que necesita el Lock 1 y luego el Lock 2 (Jerarquía 1 -> 2)
                self.intentar_avanzar_tramo_jerarquico()

            time.sleep(0.1)
            progreso_local.append(self.progreso)

        if self.progreso >= self.distancia_meta:
            self.finalizar_carrera()

    def intentar_avanzar_tramo(self, lock_actual, nombre_tramo):
        """Intenta adquirir un Lock simple para un tramo crítico."""
        self.estado = f"Esperando {nombre_tramo}"
        with lock_actual:
            self.estado = f"En {nombre_tramo} 🔒"
            time.sleep(random.uniform(0.5, 1.0))
        self.estado = "Corriendo"

    def intentar_avanzar_tramo_jerarquico(self):
        """Simula la necesidad de adquirir Locks en ORDEN (1 luego 2) para prevenir interbloqueo."""
        self.estado = "Esperando TRAMO 2 (Lock 1 y 2)"

        # ⚠️ Clave de la prevención de Deadlock: Adquirir siempre en el mismo orden (Lock 1, luego Lock 2)
        with lock_tramo_1:
            with lock_tramo_2:
                self.estado = "En TRAMO 2 (Lock 1+2) 🔒🔒"
                time.sleep(random.uniform(1.0, 2.0))
        self.estado = "Corriendo"

    def finalizar_carrera(self):
        """Registra el resultado final de la carrera y lo guarda en RESULTADO_ULTIMO."""
        global RESULTADO_ULTIMO

        # Creamos una copia local del estado para que sea seguro leer desde el hilo principal
        estado_camello = {
            'nombre': self.nombre,
            'progreso': self.progreso,
            'estado': "Meta",
            'posicion': None,  # Se asigna después
            'carrera_id': self.carrera_id
        }

        # Utilizamos lock_tramo_1 para serializar la escritura en la variable global compartida
        with lock_tramo_1:
            if RESULTADO_ULTIMO and RESULTADO_ULTIMO['id'] == self.carrera_id:
                RESULTADO_ULTIMO['camellos'].append(estado_camello)

                # Asignar posición: len actual de la lista es la posición
                self.posicion_final = len(RESULTADO_ULTIMO['camellos'])
                RESULTADO_ULTIMO['camellos'][-1]['posicion'] = self.posicion_final

                if self.posicion_final == 1:
                    RESULTADO_ULTIMO['ganador'] = self.nombre

        self.estado = "Meta"
        print(f"🐫 {self.nombre} ha llegado en la posición {self.posicion_final}.")


# --- FUNCIONES DE CONTROL DE LA CARRERA ---

def iniciar_carrera(nombres_camellos):
    """Inicializa y comienza los hilos de la carrera, limpiando el resultado anterior."""
    global RESULTADO_ULTIMO

    carrera_id = str(uuid.uuid4())

    # 1. Limpiar el estado global y preparar el nuevo resultado PERSISTENTE
    RESULTADO_ULTIMO = {
        'id': carrera_id,
        'activa': True,
        'meta': 50,
        'camellos': [],  # Aquí se acumularán los resultados finales
        'ganador': 'Nadie'
    }

    CARRERA_EN_CURSO.clear()

    camellos = [Camello(nombre, carrera_id) for nombre in nombres_camellos]

    for camello in camellos:
        camello.start()

    CARRERA_EN_CURSO.set()

    return camellos


def obtener_estado_carrera(camellos):
    """
    Devuelve el estado actual de los camellos (mientras corren) O el último resultado guardado
    (si ya han terminado).
    """
    global RESULTADO_ULTIMO

    if RESULTADO_ULTIMO and not CARRERA_EN_CURSO.is_set():
        # Si la carrera ya terminó, devolvemos el resultado guardado
        return {
            'tipo': 'final',
            'datos': RESULTADO_ULTIMO
        }

    # Si la carrera está activa o no ha comenzado, devolvemos el progreso en tiempo real
    estado_tiempo_real = [
        {
            'nombre': c.nombre,
            'progreso': c.progreso,
            'estado': c.estado,
            'posicion': c.posicion_final
        } for c in camellos if c.is_alive() or c.progreso == c.distancia_meta
    ]

    # Si todos los hilos han terminado, marcamos la carrera como inactiva
    if estado_tiempo_real and all(
            e['progreso'] >= RESULTADO_ULTIMO['meta'] for e in estado_tiempo_real) and RESULTADO_ULTIMO:
        with lock_tramo_1:
            RESULTADO_ULTIMO['activa'] = False

    return {
        'tipo': 'activo',
        'datos': {
            'activa': CARRERA_EN_CURSO.is_set(),
            'camellos': estado_tiempo_real
        }
    }


def detener_carrera():
    """Detiene la señal de la carrera."""
    CARRERA_EN_CURSO.clear()