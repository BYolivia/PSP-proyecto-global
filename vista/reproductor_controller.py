# Módulo: vista/reproductor_controller.py

import tkinter as tk
from tkinter import ttk
# ⚠️ Asegúrate de que esta ruta es correcta: 'vista/config' o 'config'
from vista.config import *


class ReproductorController(ttk.Frame):
    """
    Controlador de la interfaz de reproducción de música (Panel Lateral).
    Delega todas las acciones de audio a la instancia MusicReproductor.
    """

    def __init__(self, parent, root, music_reproductor_instance=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root
        self.reproductor = music_reproductor_instance # Instancia de MusicReproductor (Lógica T2)

        # Variables de control de UI
        # Intentar obtener el volumen inicial de la lógica, si está disponible
        initial_volume = self.reproductor.get_volumen() if self.reproductor and hasattr(self.reproductor,
                                                                                        'get_volumen') else 50
        self.volumen_var = tk.DoubleVar(value=initial_volume)

        # Estado inicial del botón Play/Pause
        self.play_pause_text = tk.StringVar(value="▶️")
        if self.reproductor and hasattr(self.reproductor, 'esta_reproduciendo') and self.reproductor.esta_reproduciendo():
            self.play_pause_text.set("⏸️")

        # Configuración de Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_controles()

    def crear_controles(self):
        """Crea el marco con el slider de volumen y los botones de control."""

        main_frame = ttk.Frame(self, padding=10, style='TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew")

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # --- Título ---
        ttk.Label(main_frame, text="🎵 Control de Música", font=FUENTE_NEGOCIOS).grid(
            row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        # --- Slider de Volumen ---
        ttk.Label(main_frame, text="Volumen:", font=FUENTE_NORMAL).grid(
            row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")

        self.slider_volumen = ttk.Scale(
            main_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volumen_var,
            command=self.manejar_ajuste_volumen
        )
        self.slider_volumen.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(5, 10))

        # --- Botones de Control ---

        self.boton_play_pause = ttk.Button(
            main_frame,
            textvariable=self.play_pause_text,
            style='Action.TButton',
            command=self.manejar_play_pause
        )
        self.boton_play_pause.grid(row=3, column=0, sticky="ew", padx=(0, 5), pady=5)

        self.boton_stop = ttk.Button(main_frame, text="⏹️", style='Action.TButton', command=self.manejar_stop)
        self.boton_stop.grid(row=3, column=1, sticky="ew", padx=(5, 0), pady=5)

    def manejar_play_pause(self):
        """Alterna entre reproducir y pausar llamando al reproductor de la lógica."""
        if not self.reproductor: return
        if self.reproductor.esta_reproduciendo():
            self.reproductor.pausar()
            self.play_pause_text.set("▶️")
        else:
            # Llama a continuar, que intenta reanudar o iniciar el último medio
            if self.reproductor.continuar():
                self.play_pause_text.set("⏸️")
            else:
                self.play_pause_text.set("▶️")

    def manejar_stop(self):
        """Detiene completamente la reproducción."""
        if not self.reproductor: return
        self.reproductor.detener()
        self.play_pause_text.set("▶️")

    def manejar_ajuste_volumen(self, valor):
        """Ajusta el volumen del reproductor basado en el slider."""
        if not self.reproductor: return
        volumen = int(float(valor))
        # 🔑 Delega el ajuste de volumen a la lógica (MusicReproductor.set_volumen)
        self.reproductor.set_volumen(volumen)

        # -------------------------------------------------------------

    # 📡 FUNCIÓN EXPORTADA PARA RECIBIR EL STREAM DEL view_radio
    # -------------------------------------------------------------

    def cargar_stream(self, url_stream):
        """
        Recibe la URL de la radio seleccionada y la pasa a la lógica para su reproducción.
        """
        if not self.reproductor:
            print("Error: Instancia de reproductor no asignada.")
            return

        # 🔑 Llama a la lógica para detener lo anterior, cargar y reproducir el nuevo stream
        success, message = self.reproductor.cargar_y_reproducir(url_stream)

        # Actualiza la UI basada en el resultado de la carga
        if success:
            self.play_pause_text.set("⏸️")
        else:
            self.play_pause_text.set("▶️")
            print(f"⚠️ Fallo en la carga del stream: {message}")