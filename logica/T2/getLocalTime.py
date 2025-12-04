# Módulo: logica/T2/getLocalTime.py

from datetime import datetime


def obtener_hora_local():
    """
    Devuelve la fecha y hora actual del sistema en un formato legible.
    Ej: "Jueves, 04 de Diciembre de 2025 | 12:07:05 AM"
    """
    now = datetime.now()

    # Formato de ejemplo:
    # %A: Día de la semana completo (ej: Jueves)
    # %d: Día del mes (ej: 04)
    # %B: Mes completo (ej: Diciembre)
    # %Y: Año (ej: 2025)
    # %H: Hora (24h) o %I: Hora (12h)
    # %p: AM/PM

    # Usaremos una simple y clara: DD/MM/YYYY HH:MM:SS
    formato_completo = now.strftime("%d/%m/%Y %H:%M:%S")

    return formato_completo