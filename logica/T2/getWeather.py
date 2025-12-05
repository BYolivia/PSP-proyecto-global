# Módulo: logica/T2/getWeather.py

import requests
import json

# --- CONFIGURACIÓN DE APIs ---
# 1. API para Geocodificación por IP (Ubicación)
IP_API_URL = "http://ip-api.com/json/"
# 2. API de Clima (Open-Meteo, gratuita y no requiere clave para datos básicos)
CLIMA_API_URL = "https://api.open-meteo.com/v1/forecast"


def _obtener_ubicacion_por_ip():
    """
    Obtiene la latitud, longitud y ciudad de la ubicación del usuario
    basándose en su dirección IP pública.
    """
    try:
        # Petición a la API de IP
        response = requests.get(IP_API_URL, timeout=5)
        response.raise_for_status()  # Lanza un error para códigos de estado HTTP 4xx/5xx
        data = response.json()

        if data.get("status") == "success":
            lat = data.get("lat")
            lon = data.get("lon")
            ciudad = data.get("city", "Ubicación Desconocida")

            print(f"🌎 [IP-API] Ubicación obtenida: {ciudad} ({lat}, {lon})")
            return lat, lon, ciudad
        else:
            print(f"❌ [IP-API] Fallo al obtener la IP. Estado: {data.get('status')}")
            return None, None, None

    except requests.exceptions.RequestException as e:
        print(f"❌ [IP-API] Error de conexión o timeout: {e}")
        return None, None, None


def _obtener_clima_por_coordenadas(lat, lon):
    """
    Obtiene la temperatura y el código de estado del tiempo usando Lat/Lon.
    Utiliza Open-Meteo.
    """
    if lat is None or lon is None:
        return None, None  # No hay coordenadas válidas

    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true",
        "temperature_unit": "celsius",
        "timezone": "auto"
    }

    try:
        response = requests.get(CLIMA_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Extracción de datos
        clima_actual = data.get("current_weather", {})
        temp = clima_actual.get("temperature")
        wmo_code = clima_actual.get("weathercode")

        print(f"🌡️ [Open-Meteo] Datos obtenidos: Temp={temp}°C, WMO={wmo_code}")
        return temp, wmo_code

    except requests.exceptions.RequestException as e:
        print(f"❌ [Open-Meteo] Error de conexión al API de clima: {e}")
        return None, None
    except Exception as e:
        print(f"❌ [Open-Meteo] Error al procesar los datos del clima: {e}")
        return None, None


def _decodificar_wmo(wmo_code):
    """
    Convierte el código WMO de Open-Meteo a una descripción amigable con emojis.
    """
    if wmo_code is None:
        return "Desconocido ❓"

    code = int(wmo_code)

    # 0: Cielo despejado, 1-3: Parcialmente nublado, 45-48: Niebla
    if code <= 3:
        return "Soleado/Parcialmente Nublado 🌤️"
    # 51-67: Llovizna y Lluvia
    elif 51 <= code <= 67:
        return "Lluvia 🌧️"
    # 71-75: Nieve
    elif 71 <= code <= 75:
        return "Nieve ❄️"
    # 80-82: Chubascos (Duchas)
    elif 80 <= code <= 82:
        return "Chubascos 🌦️"
    # 95, 96, 99: Tormenta
    elif code >= 95:
        return "Tormenta ⛈️"
    # Por defecto, Nublado o Niebla
    else:
        return "Nublado ☁️"


def obtener_datos_clima():
    """
    Función principal: obtiene la ubicación por IP y luego el clima para esa ubicación.
    Devuelve la temperatura en grados Celsius y el estado del tiempo.
    """
    # 1. Obtener ubicación
    lat, lon, ciudad = _obtener_ubicacion_por_ip()

    if lat is None or lon is None:
        return "No disponible (Fallo en Ubicación)"

    # 2. Obtener clima
    temperatura, wmo_code = _obtener_clima_por_coordenadas(lat, lon)

    if temperatura is None or wmo_code is None:
        return f"Clima no disponible en {ciudad}"

    # 3. Decodificar y formatear
    estado_tiempo = _decodificar_wmo(wmo_code)

    return f"{temperatura}°C ({estado_tiempo}) en {ciudad}"