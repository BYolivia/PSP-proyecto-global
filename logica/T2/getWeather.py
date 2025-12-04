# Módulo: logica/T2/getWeather.py

import random


def obtener_datos_clima():
    """
    Simula la obtención de la temperatura y el estado del tiempo local.
    Devuelve la temperatura en grados Celsius y un estado del tiempo.
    """
    # Simulación de datos
    temperatura = random.randint(10, 28)

    # Simulación de estado del tiempo
    estados = ["Soleado ☀️", "Nublado ☁️", "Lluvia 🌧️", "Tormenta ⛈️"]
    estado_tiempo = random.choice(estados)

    return f"{temperatura}°C ({estado_tiempo})"