# Módulo: vista/central_panel/view_radio.py

import tkinter as tk
from tkinter import ttk
import json
from vista.config import *

# -------------------------------------------------------------
# ❌ ELIMINAMOS EL BLOQUE try/except CON LA SIMULACIÓN DE VLC
#    Ya que esta clase no debe interactuar directamente con MusicReproductor.
# -------------------------------------------------------------


class RadioPanel(ttk.Frame):
    """
    Panel de la pestaña Radios (T3).
    Gestiona únicamente la selección de emisoras y DELEGA la reproducción
    al ReproductorController en el Panel Lateral.
    """

    NOMBRE_FICHERO_RADIOS = "res/radios.json"

    def __init__(self, parent_notebook, root, reproductor_controller_instance=None, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root

        # 🔑 REFERENCIA AL CONTROLADOR DE AUDIO DEL PANEL LATERAL
        # Este controlador tiene los métodos cargar_stream() y manejar_stop().
        self.reproductor_controller = reproductor_controller_instance

        self.emisoras_cargadas = self.cargar_emisoras()
        self.radio_seleccionada = tk.StringVar(value="---")

        # ❌ Se eliminaron: self.volumen_var y la inicialización de MusicReproductor.

        self.crear_interfaz_radios(self)

    # -------------------------------------------------------------
    # 📻 LÓGICA DE DATOS
    # -------------------------------------------------------------

    def cargar_emisoras(self):
        """Carga la lista de emisoras desde el archivo radios.json."""
        try:
            with open(self.NOMBRE_FICHERO_RADIOS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Archivo de emisoras no encontrado en: '{self.NOMBRE_FICHERO_RADIOS}'.")
            return []
        except json.JSONDecodeError:
            print(f"⚠️ Error al leer el archivo {self.NOMBRE_FICHERO_RADIOS}. Está mal formado.")
            return []

    # -------------------------------------------------------------
    # 🖼️ VISTA (SOLO SELECCIONADOR)
    # -------------------------------------------------------------

    def crear_interfaz_radios(self, parent_frame):
        """Crea la interfaz para seleccionar la emisora de radio (SIN CONTROLES DE AUDIO)."""

        frame_radio = ttk.Frame(parent_frame, padding=10, style='TFrame')
        frame_radio.pack(expand=True, fill="both")

        ttk.Label(frame_radio, text="Selección de Emisoras de Radio", font=FUENTE_TITULO).pack(pady=10)

        if not self.emisoras_cargadas:
            ttk.Label(frame_radio,
                      text=f"No se encontraron emisoras en '{self.NOMBRE_FICHERO_RADIOS}'.",
                      foreground='red').pack(pady=20)
            return

        frame_listado = ttk.Frame(frame_radio)
        frame_listado.pack(fill="both", expand=True)

        listbox = tk.Listbox(frame_listado, height=15, width=60, font=('Arial', 10),
                             bg=COLOR_BLANCO, fg=COLOR_TEXTO, selectbackground=COLOR_ACCION)
        listbox.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(frame_listado, orient="vertical", command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scrollbar.set)

        for emisora in self.emisoras_cargadas:
            nombre_display = f"{emisora['nombre']} ({emisora.get('genero', 'N/D')})"
            listbox.insert(tk.END, nombre_display)

        listbox.bind('<<ListboxSelect>>', lambda e: self.seleccionar_radio(listbox))

        ttk.Label(frame_radio, text="URL del Stream:", font=FUENTE_NEGOCIOS).pack(pady=(10, 0), anchor="w")
        self.url_seleccionada_label = ttk.Label(frame_radio, text="N/A", wraplength=400, foreground=COLOR_TEXTO)
        self.url_seleccionada_label.pack(anchor="w")

        # ❌ Se eliminaron los controles de volumen y Play/Pause/Stop.

    # -------------------------------------------------------------
    # ⏯️ DELEGACIÓN DE LA LÓGICA DE AUDIO
    # -------------------------------------------------------------

    def seleccionar_radio(self, listbox):
        """
        Captura la selección y DELEGA la reproducción al ReproductorController.
        """
        seleccion = listbox.curselection()
        if seleccion:
            indice = seleccion[0]
            emisora = self.emisoras_cargadas[indice]
            url = emisora['url_stream']

            self.radio_seleccionada.set(emisora['nombre'])
            self.url_seleccionada_label.config(text=url)

            # 🔑 DELEGACIÓN: Llamamos al controlador de audio del Panel Lateral
            if self.reproductor_controller:
                self.reproductor_controller.cargar_stream(url)
            else:
                # El error indica que falta conectar en panel_central.py
                print("❌ Error: ReproductorController no está asignado.")

    # ❌ Se eliminaron los métodos controlar_reproduccion, cambiar_volumen.

    def detener_actualizacion(self):
        """Método llamado por PanelCentral al cerrar la aplicación (solo delega la detención)."""
        # 🔑 DELEGACIÓN: El PanelCentral llama a esto al cerrar.
        if self.reproductor_controller:
            self.reproductor_controller.manejar_stop()
        else:
            # Si el controlador no existe, no hacemos nada, pero el PanelLateral debería manejar su propio cierre.
            pass