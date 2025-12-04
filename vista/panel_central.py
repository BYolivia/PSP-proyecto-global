# Módulo: vista/panel_central.py

import random
import tkinter as tk
from tkinter import ttk
import json
import os
import sys  # Necesario para el bloque opcional de VLC

# --- LÓGICA DE T1 (MONITOR DE RECURSOS) ---
from logica.T1.trafficMeter import iniciar_monitor_red
from logica.T1.graficos import crear_grafico_recursos, actualizar_historial_datos
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- LÓGICA DE T2 (CARRERA DE CAMELLOS) ---
from logica.T2.carreraCamellos import (
    iniciar_carrera,
    obtener_estado_carrera,
    RESULTADO_ULTIMO
)

# --- LÓGICA DE T3 (REPRODUCTOR DE MÚSICA) ---
# Se necesita el bloque opcional aquí, ya que el import 'vlc' está en este módulo
try:
    from logica.T2.musicReproductor import MusicReproductor
except ImportError:
    # Bloque OPCIONAL si falla el import de MusicReproductor por problemas de VLC en el entorno
    print("⚠️ Error al importar MusicReproductor. Asegúrate de tener 'python-vlc' instalado y VLC en tu sistema.")


    class MusicReproductor:
        def __init__(self, *args, **kwargs): pass

        def ajustar_volumen(self, valor): print(f"Volumen (Simulado): {valor}")

        def cargar_y_reproducir(self, url): print(f"Reproduciendo (Simulado): {url}")

        def reproducir(self): print("Reproducir (Simulado)")

        def pausar(self): print("Pausar (Simulado)")

        def detener(self): print("Detener (Simulado)")

# --- IMPORTACIÓN UNIVERSAL DE CONSTANTES ---
from vista.config import *


class PanelCentral(ttk.Frame):
    """Contiene el Notebook (subpestañas), el panel de Notas y el panel de Chat,
    y gestiona directamente la lógica de control de T1, T2 y T3."""

    INTERVALO_ACTUALIZACION_MS = INTERVALO_RECURSOS_MS
    INTERVALO_CARRERA_MS = 200

    # ✅ CORRECCIÓN DE RUTA
    NOMBRE_FICHERO_RADIOS = "res/radios.json"

    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root

        self.after_id = None
        self.after_carrera_id = None
        self.camellos = []
        self.progreso_labels = {}
        self.frame_carrera_controles = None
        self.frame_progreso = None
        self.carrera_info_label = None
        self.carrera_estado_label = None

        # 1. INICIALIZACIÓN DE VARIABLES (T1)
        self.net_monitor = iniciar_monitor_red()
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = None

        # 2. INICIALIZACIÓN DE VARIABLES Y LÓGICA DE RADIO (T3)
        self.emisoras_cargadas = self.cargar_emisoras()
        self.radio_seleccionada = tk.StringVar(value="---")
        self.volumen_var = tk.DoubleVar(value=50.0)
        self.reproductor = MusicReproductor(initial_volume=self.volumen_var.get())

        # 3. CONFIGURACIÓN DEL LAYOUT
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_area_principal_y_notas()
        self.crear_panel_chat_y_alumnos()

        # 4. INICIO DE CICLOS DE ACTUALIZACIÓN
        self.iniciar_actualizacion_automatica()
        self.iniciar_actualizacion_carrera()

    # -------------------------------------------------------------
    # 📻 LÓGICA Y VISTA DE T3 (REPRODUCTOR DE RADIOS)
    # -------------------------------------------------------------

    def cargar_emisoras(self):
        """Carga la lista de emisoras desde el archivo radios.json."""
        try:
            # ✅ La ruta ahora apunta correctamente al subdirectorio 'res'
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

    def seleccionar_radio(self, listbox):
        """Captura la selección y llama al reproductor para iniciar la reproducción."""
        seleccion = listbox.curselection()
        if seleccion:
            indice = seleccion[0]
            emisora = self.emisoras_cargadas[indice]
            url = emisora['url_stream']

            # 1. Actualizar la interfaz
            self.radio_seleccionada.set(emisora['nombre'])
            self.url_seleccionada_label.config(text=url)

            # 2. Llamar a la lógica del reproductor
            self.reproductor.cargar_y_reproducir(url)

    def controlar_reproduccion(self, accion):
        """Llama al método de control del reproductor (play/pause)."""
        if accion == 'play':
            self.reproductor.reproducir()
        elif accion == 'pause':
            self.reproductor.pausar()

    def cambiar_volumen(self, valor):
        """
        Llama al método de control de volumen del reproductor,
        asegurando que el valor sea un entero para evitar saltos del Scale.
        """
        # ✅ CORRECCIÓN DE LA BARRA DE VOLUMEN
        # 1. Convertir el valor de punto flotante a entero
        valor_entero = int(float(valor))

        # 2. Actualizar la variable de control con el valor entero.
        self.volumen_var.set(valor_entero)

        # 3. Llamar a la lógica del reproductor.
        self.reproductor.ajustar_volumen(valor_entero)

    # -------------------------------------------------------------
    # 📦 ESTRUCTURA PRINCIPAL DEL PANEL
    # -------------------------------------------------------------

    def crear_area_principal_y_notas(self):
        """Crea el contenedor de las subpestañas y el panel de notas."""
        frame_izquierdo = ttk.Frame(self, style='TFrame')
        frame_izquierdo.grid(row=0, column=0, sticky="nsew")

        frame_izquierdo.grid_rowconfigure(0, weight=4)
        frame_izquierdo.grid_rowconfigure(1, weight=1)
        frame_izquierdo.grid_columnconfigure(0, weight=1)

        self.crear_notebook_pestañas(frame_izquierdo)

        panel_notas = ttk.Frame(frame_izquierdo, style='Note.TFrame')
        panel_notas.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        ttk.Label(panel_notas, text="Panel para notas informativas y mensajes sobre la ejecución de los hilos.",
                  style='Note.TLabel', anchor="nw", justify=tk.LEFT, padding=10, font=FUENTE_NOTA).pack(
            expand=True, fill="both")

    def crear_notebook_pestañas(self, parent_frame):
        """Crea las pestañas internas para las tareas (T1, Carrera, Radios)."""
        sub_notebook = ttk.Notebook(parent_frame)
        sub_notebook.grid(row=0, column=0, sticky="nsew")

        sub_tabs = ["Recursos", "Resultados", "Radios", "Navegador", "Correos", "Tareas", "Alarmas", "Enlaces"]
        self.tabs = {}

        for i, sub_tab_text in enumerate(sub_tabs):
            frame = ttk.Frame(sub_notebook, style='TFrame')
            sub_notebook.add(frame, text=sub_tab_text)
            self.tabs[sub_tab_text] = frame

            if sub_tab_text == "Recursos":
                self.grafico_frame = ttk.Frame(frame, style='TFrame')
                self.grafico_frame.pack(expand=True, fill="both", padx=10, pady=10)

                self.canvas = FigureCanvasTkAgg(self.figure, master=self.grafico_frame)
                self.canvas_widget = self.canvas.get_tk_widget()
                self.canvas_widget.pack(expand=True, fill="both")

            elif sub_tab_text == "Resultados":
                self.crear_interfaz_carrera(frame)

            elif sub_tab_text == "Radios":
                self.crear_interfaz_radios(frame)

    # -------------------------------------------------------------
    # 🐪 LÓGICA DE T2 (CARRERA DE CAMELLOS)
    # -------------------------------------------------------------

    def crear_interfaz_carrera(self, parent_frame):
        """Crea los controles y la visualización de la Carrera de Camellos."""
        frame_controles = ttk.Frame(parent_frame, style='TFrame', padding=10)
        frame_controles.pack(fill="x")
        self.frame_carrera_controles = frame_controles

        ttk.Label(frame_controles, text="Resultado de Carrera de Camellos (T2 Sincronización)",
                  style='TLabel', font=FUENTE_NEGOCIOS).pack(side="left", padx=5)

        self.carrera_estado_label = ttk.Label(frame_controles, text="Estado.", style='TLabel', font=FUENTE_NEGOCIOS)
        self.carrera_estado_label.pack(side="right", padx=10)

        self.frame_progreso = ttk.Frame(parent_frame, style='TFrame', padding=10)
        self.frame_progreso.pack(fill="both", expand=True)

        ttk.Label(self.frame_progreso,
                  text="Presiona el botón 'App2 (T2-Carrera 🏁)' en el panel lateral para iniciar la simulación de hilos.",
                  style='TLabel').pack(pady=20)

    def manejar_inicio_carrera(self):
        """Inicia una nueva carrera de camellos con un número aleatorio de participantes."""
        if self.camellos and any(c.is_alive() for c in self.camellos):
            self.carrera_estado_label.config(text="⚠️ Ya hay una carrera en curso.")
            return

        print("Iniciando Carrera de Camellos con número variable de participantes...")

        num_camellos = random.randint(10, 20)
        nombres = [f"Camello {i + 1}" for i in range(num_camellos)]

        for widget in self.frame_progreso.winfo_children():
            widget.destroy()
        self.progreso_labels = {}

        self.camellos = iniciar_carrera(nombres)

        self.carrera_estado_label.config(text=f"¡Carrera en marcha! 💨 ({num_camellos} participantes)")

        self.crear_visualizacion_carrera(nombres)
        self.iniciar_actualizacion_carrera()

    def crear_visualizacion_carrera(self, nombres):
        """Prepara el layout de la carrera."""
        for widget in self.frame_progreso.winfo_children():
            widget.destroy()

        for i, nombre in enumerate(nombres):
            ttk.Label(self.frame_progreso, text=f"{nombre}: ", style='TLabel', font=FUENTE_NEGOCIOS).grid(row=i,
                                                                                                          column=0,
                                                                                                          sticky="w")

            label_progreso = ttk.Label(self.frame_progreso, text="[Esperando...]", style='TLabel',
                                       foreground=COLOR_TEXTO)
            label_progreso.grid(row=i, column=1, sticky="w", padx=10)
            self.progreso_labels[nombre] = label_progreso

            label_posicion = ttk.Label(self.frame_progreso, text="", style='TLabel')
            label_posicion.grid(row=i, column=2, sticky="w")
            self.progreso_labels[f'{nombre}_pos'] = label_posicion

        self.carrera_info_label = ttk.Label(self.frame_progreso, text="", style='TLabel', font=FUENTE_NEGOCIOS)
        self.carrera_info_label.grid(row=len(nombres), column=0, columnspan=3, sticky="w", pady=(10, 0))

    def mostrar_progreso_activo(self, datos_activos):
        """Actualiza la visualización de la carrera mientras los hilos están corriendo."""

        if not datos_activos['camellos']:
            return

        nombres_activos = [c['nombre'] for c in datos_activos['camellos']]
        if not self.progreso_labels or any(n not in self.progreso_labels for n in nombres_activos):
            self.crear_visualizacion_carrera(nombres_activos)

        for estado in datos_activos['camellos']:
            nombre = estado['nombre']
            progreso = estado['progreso']
            etiqueta_progreso = self.progreso_labels.get(nombre)
            etiqueta_posicion = self.progreso_labels.get(f'{nombre}_pos')

            if etiqueta_progreso:
                barra = "█" * (progreso // 2)
                texto_progreso = f"[{barra}{' ' * (25 - len(barra))}] ({progreso}/50) Estado: {estado['estado']}"
                etiqueta_progreso.config(text=texto_progreso)

            if etiqueta_posicion and estado['posicion']:
                etiqueta_posicion.config(text=f"POS: {estado['posicion']} 🏆", foreground=COLOR_ACCION)

        self.carrera_estado_label.config(text="Carrera en curso...")
        self.carrera_info_label.config(text="")

    def mostrar_resultado_final(self, resultado_final):
        """Muestra el resultado final persistente de la carrera."""

        nombres_finales = [c['nombre'] for c in resultado_final['camellos']]
        if not self.progreso_labels or any(n not in self.progreso_labels for n in nombres_finales):
            self.crear_visualizacion_carrera(nombres_finales)

        camellos_ordenados = sorted(resultado_final['camellos'], key=lambda x: x['posicion'])

        for estado in camellos_ordenados:
            nombre = estado['nombre']
            etiqueta_progreso = self.progreso_labels.get(nombre)
            etiqueta_posicion = self.progreso_labels.get(f'{nombre}_pos')

            if etiqueta_progreso:
                barra = "█" * (estado['progreso'] // 2)
                texto_progreso = f"[{barra}{' ' * (25 - len(barra))}] (50/50) Estado: Meta"
                etiqueta_progreso.config(text=texto_progreso)

            if etiqueta_posicion:
                etiqueta_posicion.config(text=f"POS: {estado['posicion']} {'🏆' if estado['posicion'] == 1 else ''}",
                                         foreground=COLOR_ACCION)

        self.carrera_estado_label.config(text="✅ Carrera Terminada.")
        self.carrera_info_label.config(text=f"¡El ganador es: {resultado_final['ganador']}!",
                                       font=FUENTE_TITULO, foreground=COLOR_EXITO)

    def actualizar_carrera(self):
        """Ciclo de actualización visual: lee el estado activo o el resultado final persistente."""

        estado = obtener_estado_carrera(self.camellos)

        if estado['tipo'] == 'final':
            self.mostrar_resultado_final(estado['datos'])
            self.detener_actualizacion_carrera()
            return

        elif estado['tipo'] == 'activo':
            self.mostrar_progreso_activo(estado['datos'])

        self.after_carrera_id = self.after(self.INTERVALO_CARRERA_MS, self.actualizar_carrera)

    def iniciar_actualizacion_carrera(self):
        """Inicia el ciclo de actualización visual (o carga el resultado guardado al inicio)."""
        self.detener_actualizacion_carrera()

        if RESULTADO_ULTIMO and not RESULTADO_ULTIMO.get('activa', True) and self.frame_progreso:
            self.mostrar_resultado_final(RESULTADO_ULTIMO)
        else:
            self.carrera_estado_label.config(text="Carrera lista para empezar.")
            self.after_carrera_id = self.after(0, self.actualizar_carrera)

    def detener_actualizacion_carrera(self):
        """Detiene el ciclo de actualización visual de la carrera."""
        if self.after_carrera_id:
            self.after_cancel(self.after_carrera_id)
            self.after_carrera_id = None
            print("Ciclo de actualización de carrera detenido.")

    # -------------------------------------------------------------
    # 📈 LÓGICA DE T1 (MONITOR DE RECURSOS)
    # -------------------------------------------------------------

    def actualizar_recursos(self):
        """Obtiene los datos del sistema (incluyendo Red) y dibuja/redibuja el gráfico."""
        try:
            net_in, net_out = self.net_monitor.get_io_data_kb()
            actualizar_historial_datos(net_in, net_out)

            if self.canvas:
                crear_grafico_recursos(self.figure)
                self.canvas.draw()

        except Exception as e:
            error_msg = f"Error al generar el gráfico de recursos: {e}"
            print(error_msg)
            if self.canvas_widget and self.canvas_widget.winfo_exists():
                self.canvas_widget.pack_forget()
            error_label = ttk.Label(self.grafico_frame, text=error_msg, foreground='red', style='TLabel')
            error_label.pack(pady=20)
            self.detener_actualizacion_automatica()

        self.after_id = self.after(self.INTERVALO_ACTUALIZACION_MS, self.actualizar_recursos)

    def iniciar_actualizacion_automatica(self):
        """Inicia el ciclo de actualización del gráfico de recursos."""
        print("Iniciando actualización automática de recursos.")
        self.after_id = self.after(0, self.actualizar_recursos)

    def detener_actualizacion_automatica(self):
        """Detiene el ciclo de actualización periódica y el hilo de red (T1) y T3."""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
            print("Ciclo de actualización de gráficos detenido.")

        if self.net_monitor:
            self.net_monitor.stop()
            self.net_monitor.join()
            print("Hilo de TrafficMeter detenido.")

        self.detener_actualizacion_carrera()

        # Detener el reproductor al cerrar la aplicación
        if self.reproductor:
            self.reproductor.detener()

    # -------------------------------------------------------------
    # 💬 PANEL CHAT, ALUMNOS Y APPS (PANEL LATERAL)
    # -------------------------------------------------------------

    def crear_panel_chat_y_alumnos(self, ):
        """Crea el panel de chat y lista de Alumnos (columna derecha), incluyendo el reproductor."""
        panel_chat = ttk.Frame(self, style='TFrame', padding="10")
        panel_chat.grid(row=0, column=1, sticky="nsew")

        panel_chat.grid_rowconfigure(5, weight=1)
        panel_chat.grid_columnconfigure(0, weight=1)

        # --- FILA 0: Título ---
        ttk.Label(panel_chat, text="Chat", foreground=COLOR_ACCION, font=FUENTE_TITULO, style='TLabel').grid(row=0,
                                                                                                             column=0,
                                                                                                             pady=(0,
                                                                                                                   10),
                                                                                                             sticky="w")

        # --- FILAS 1-3: Chat Input ---
        ttk.Label(panel_chat, text="Mensaje", style='TLabel').grid(row=1, column=0, sticky="w")
        chat_text = tk.Text(panel_chat, height=6, width=30, bg=COLOR_BLANCO, relief="solid", borderwidth=1,
                            font=('Arial', 10))
        chat_text.grid(row=2, column=0, sticky="ew", pady=(0, 5))
        ttk.Button(panel_chat, text="Enviar", style='Action.TButton').grid(row=3, column=0, pady=(0, 15), sticky="e")

        # --- FILAS 4-7: Alumnos (Se expanden) ---
        for i in range(1, 4):
            frame_alumno = ttk.Frame(panel_chat, style='Alumno.TFrame', padding=8)
            frame_alumno.grid(row=3 + i, column=0, sticky="ew", pady=5)
            frame_alumno.grid_columnconfigure(0, weight=1)

            ttk.Label(frame_alumno, text=f"Alumno {i}", font=('Arial', 11, 'bold'), style='Alumno.TLabel').grid(row=0,
                                                                                                                column=0,
                                                                                                                sticky="w")
            ttk.Label(frame_alumno, text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.", wraplength=250,
                      justify=tk.LEFT, style='Alumno.TLabel').grid(row=1, column=0, sticky="w")
            ttk.Button(frame_alumno, text="↻", width=3, style='Action.TButton').grid(row=0, column=1, rowspan=2, padx=5,
                                                                                     sticky="ne")

        # --- FILA 8: Reproductor Música ---
        musica_frame = ttk.LabelFrame(panel_chat, text="Reproductor Música", padding=10, style='TFrame')
        musica_frame.grid(row=8, column=0, sticky="ew", pady=(15, 0))

        # 8a: Emisora Actual
        ttk.Label(musica_frame, text="Actual: ", style='TLabel').grid(row=0, column=0, sticky="w")
        ttk.Label(musica_frame, textvariable=self.radio_seleccionada, font=('Arial', 10, 'bold'), style='TLabel').grid(
            row=0, column=1, columnspan=2, sticky="w")

        # 8b: Controles de Reproducción (Play/Pause)
        frame_controles_musica = ttk.Frame(musica_frame, style='TFrame')
        frame_controles_musica.grid(row=1, column=0, columnspan=3, pady=(5, 5))

        ttk.Button(frame_controles_musica, text="▶️ Iniciar", command=lambda: self.controlar_reproduccion('play'),
                   style='Action.TButton', width=8).pack(side="left", padx=5)
        ttk.Button(frame_controles_musica, text="⏸️ Pausar", command=lambda: self.controlar_reproduccion('pause'),
                   style='Action.TButton', width=8).pack(side="left", padx=5)

        # 8c: Control de Volumen (Scale/Deslizable)
        ttk.Label(musica_frame, text="Volumen:", style='TLabel').grid(row=2, column=0, sticky="w")

        volumen_scale = ttk.Scale(musica_frame, from_=0, to=100, orient="horizontal",
                                  variable=self.volumen_var, command=self.cambiar_volumen)
        volumen_scale.grid(row=2, column=1, sticky="ew", padx=(0, 5))

        ttk.Label(musica_frame, textvariable=self.volumen_var, style='TLabel').grid(row=2, column=2, sticky="w")

        musica_frame.grid_columnconfigure(1, weight=1)

        panel_chat.grid_rowconfigure(8, weight=0)