# Módulo: vista/central_panel/view_radio.py

import tkinter as tk
from tkinter import ttk
import json
from vista.config import *

# Bloque para manejar la dependencia de VLC
try:
    from logica.T2.musicReproductor import MusicReproductor
except ImportError:
    print("⚠️ Error al importar MusicReproductor. Usando simulador.")


    # CLASE SIMULADA
    class MusicReproductor:
        def __init__(self, *args, **kwargs): pass

        def ajustar_volumen(self, valor): print(f"🎶 SIMULANDO VOLUMEN: {valor}")

        def cargar_y_reproducir(self, url): print(f"🎶 SIMULANDO PLAY: {url}")

        def reproducir(self): print("🎶 SIMULANDO PLAY")

        def pausar(self, *args): print("🎶 SIMULANDO PAUSA")

        def detener(self): print("🎶 SIMULANDO DETENER")


class RadioPanel(ttk.Frame):
    """
    Panel de la pestaña Radios (T3).
    Gestiona la selección de emisoras y los controles de reproducción.
    """

    NOMBRE_FICHERO_RADIOS = "res/radios.json"

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root

        self.emisoras_cargadas = self.cargar_emisoras()
        self.radio_seleccionada = tk.StringVar(value="---")
        self.volumen_var = tk.DoubleVar(value=50.0)

        # Inicialización de la lógica del reproductor
        self.reproductor = MusicReproductor(initial_volume=self.volumen_var.get())

        self.crear_interfaz_radios(self)

    # -------------------------------------------------------------
    # 📻 VISTA Y LÓGICA DE RADIO
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

    def crear_interfaz_radios(self, parent_frame):
        """Crea la interfaz para seleccionar la emisora de radio."""

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

        # Controles de Volumen y Play/Pause
        frame_controles = ttk.Frame(frame_radio, padding=5)
        frame_controles.pack(fill="x", pady=10)

        ttk.Button(frame_controles, text="▶️ Play", command=lambda: self.controlar_reproduccion('play'),
                   style='Action.TButton').pack(side='left', padx=5)
        ttk.Button(frame_controles, text="⏸️ Pause", command=lambda: self.controlar_reproduccion('pause'),
                   style='Action.TButton').pack(side='left', padx=5)

        ttk.Label(frame_controles, textvariable=self.radio_seleccionada, font=FUENTE_NEGOCIOS).pack(side='left',
                                                                                                    padx=15)

        ttk.Label(frame_controles, text="Volumen:").pack(side='right', padx=5)
        volumen_slider = ttk.Scale(frame_controles, from_=0, to=100, orient=tk.HORIZONTAL,
                                   variable=self.volumen_var, command=self.cambiar_volumen, length=100)
        volumen_slider.pack(side='right', padx=5)

    def seleccionar_radio(self, listbox):
        """Captura la selección y llama al reproductor para iniciar la reproducción."""
        seleccion = listbox.curselection()
        if seleccion:
            indice = seleccion[0]
            emisora = self.emisoras_cargadas[indice]
            url = emisora['url_stream']

            self.radio_seleccionada.set(emisora['nombre'])
            self.url_seleccionada_label.config(text=url)
            self.reproductor.cargar_y_reproducir(url)

    def controlar_reproduccion(self, accion):
        """Llama al método de control del reproductor (play/pause)."""
        if accion == 'play':
            self.reproductor.reproducir()
        elif accion == 'pause':
            self.reproductor.pausar()

    def cambiar_volumen(self, valor):
        """Ajusta el volumen."""
        valor_entero = int(float(valor))
        self.volumen_var.set(valor_entero)
        self.reproductor.ajustar_volumen(valor_entero)

    def detener_actualizacion(self):
        """Método llamado por PanelCentral al cerrar la aplicación."""
        if self.reproductor:
            self.reproductor.detener()