# Módulo: logica/auxiliar/add_audio.py

import json
import os
import threading

# 🔑 RUTA CONFIRMADA: Desde la raíz del proyecto
NOMBRE_FICHERO = os.path.join("res", "radios.json")


class RadioManager:
    """
    Gestiona la lectura, escritura y adición de emisoras en el archivo radios.json.
    Utiliza un Lock para asegurar la seguridad al escribir el archivo.
    """

    def __init__(self, filename=NOMBRE_FICHERO):
        self.filename = filename
        # Bloqueo para operaciones de archivo
        self._lock = threading.Lock()
        self.emisoras_cargadas = self.cargar_emisoras()

    # -------------------------------------------------------------
    # GESTIÓN DE ARCHIVO
    # -------------------------------------------------------------

    def cargar_emisoras(self):
        """Carga las emisoras existentes desde el archivo."""
        with self._lock:
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️ Error al leer el archivo {self.filename}. Retornando lista vacía.")
                    return []
            return []

    def guardar_emisoras(self):
        """Guarda la lista de emisoras actual en memoria en formato JSON."""
        with self._lock:
            try:
                with open(self.filename, 'w', encoding='utf-8') as f:
                    json.dump(self.emisoras_cargadas, f, indent=4, ensure_ascii=False)
                print(f"\n✅ [RadioManager] Archivo '{self.filename}' guardado.")
                return True
            except Exception as e:
                print(f"\n❌ [RadioManager] Error al intentar guardar el archivo: {e}")
                return False

    # -------------------------------------------------------------
    # GESTIÓN DE DATOS EN MEMORIA
    # -------------------------------------------------------------

    def get_emisoras(self):
        """Retorna la lista de emisoras cargadas en memoria."""
        return self.emisoras_cargadas

    def add_radio(self, nombre, url, pais=None, genero=None):
        """
        Añade una nueva emisora a la lista en memoria y guarda el archivo.
        """
        if not nombre or not url:
            print("❌ El nombre y la URL son obligatorios.")
            return False

        nueva_emisora = {
            "nombre": nombre.strip(),
            "url_stream": url.strip(),
            "pais": pais.strip() if pais else None,
            "genero": genero.strip() if genero else None
        }

        self.emisoras_cargadas.append(nueva_emisora)
        print(f"✅ [RadioManager] Emisora '{nombre}' añadida a la lista en memoria.")

        # Guarda inmediatamente
        self.guardar_emisoras()

        return True