# Módulo: vista/panel_central.py

import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
from datetime import datetime
import os
import sys

# --- LÓGICA DE T1 (MONITOR DE RECURSOS) ---
from logica.T1.trafficMeter import iniciar_monitor_red
from logica.T1.graficos import crear_grafico_recursos, actualizar_historial_datos
from logica.T1.textEditor import cargar_contenido_res_notes, guardar_contenido_res_notes  # <--- AÑADIDO
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- LÓGICA DE T2 (CARRERA DE CAMELLOS) ---
from logica.T2.carreraCamellos import (
    iniciar_carrera,
    obtener_estado_carrera,
    RESULTADO_ULTIMO
)

# --- LÓGICA DE T3 (REPRODUCTOR DE MÚSICA) ---
# Bloque para manejar la dependencia de VLC
try:
    from logica.T2.musicReproductor import MusicReproductor
except ImportError:
    print("⚠️ Error al importar MusicReproductor. Usando simulador.")


    class MusicReproductor:
        def __init__(self, *args, **kwargs): pass

        def ajustar_volumen(self, valor): pass

        def cargar_y_reproducir(self, url): print(f"🎶 SIMULANDO PLAY: {url}")

        def reproducir(self): pass

        def pausar(self, *args): pass

        def detener(self): pass

# 🟢 LÓGICA DE T4 (ALARMAS)
from logica.T2.alarm import AlarmManager

# --- IMPORTACIÓN UNIVERSAL DE CONSTANTES ---
from vista.config import *


class PanelCentral(ttk.Frame):
    """Contiene el Notebook (subpestañas), el panel de Notas y el panel de Chat,
    y gestiona directamente la lógica de control de T1, T2, T3 y T4."""

    INTERVALO_ACTUALIZACION_MS = INTERVALO_RECURSOS_MS
    INTERVALO_CARRERA_MS = 200

    NOMBRE_FICHERO_RADIOS = "res/radios.json"

    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root

        self.after_id = None
        self.after_carrera_id = None
        self.after_alarm_id = None

        # T2
        self.camellos = []
        self.progreso_labels = {}
        self.frame_carrera_controles = None
        self.frame_progreso = None
        self.carrera_info_label = None
        self.carrera_estado_label = None

        # T1
        self.net_monitor = iniciar_monitor_red()
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = None

        # T3 (Radios)
        self.emisoras_cargadas = self.cargar_emisoras()
        self.radio_seleccionada = tk.StringVar(value="---")
        self.volumen_var = tk.DoubleVar(value=50.0)
        self.reproductor = MusicReproductor(initial_volume=self.volumen_var.get())

        # 🟢 T4 (Alarmas) - Inicialización de variables UI.
        self.alarm_manager = None
        self.alarm_list_frame = None
        self.scrollable_frame = None
        self.alarm_hours_entry = None
        self.alarm_minutes_entry = None
        self.alarm_seconds_entry = None

        # 📄 Tareas (res/notes)
        self.notes_text_editor = None  # <--- AÑADIDO

        # 2. CONFIGURACIÓN DEL LAYOUT
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_area_principal()  # <--- FUNCIÓN SIMPLIFICADA
        self.crear_panel_chat_y_alumnos()

        # Inicializar el AlarmManager solo después de que show_alarm_popup esté definido.
        self.inicializar_alarmas()

        # 3. INICIO DE CICLOS DE ACTUALIZACIÓN
        self.iniciar_actualizacion_automatica()
        self.iniciar_actualizacion_carrera()
        self.iniciar_actualizacion_alarmas()

    def inicializar_alarmas(self):
        """Inicializa AlarmManager, pasándole el método de callback show_alarm_popup."""
        self.alarm_manager = AlarmManager(self.root, self.show_alarm_popup)

    # -------------------------------------------------------------
    # 📻 LÓGICA Y VISTA DE T3 (REPRODUCTOR DE RADIOS)
    # ... (El código de cargar_emisoras, crear_interfaz_radios, seleccionar_radio, controlar_reproduccion, cambiar_volumen no tiene cambios)
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
        """
        Ajusta el volumen, asegurando que el valor sea un entero para estabilizar el Scale.
        """
        valor_entero = int(float(valor))

        self.volumen_var.set(valor_entero)
        self.reproductor.ajustar_volumen(valor_entero)

    # -------------------------------------------------------------
    # 🔔 LÓGICA Y VISTA DE T4 (ALARMAS / TEMPORIZADORES)
    # -------------------------------------------------------------

    def crear_interfaz_alarmas(self, parent_frame):
        """Crea la interfaz para programar y visualizar alarmas (H:M:S)."""

        frame = ttk.Frame(parent_frame, padding=10, style='TFrame')
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Programar Nuevo Temporizador (H:M:S)", font=FUENTE_NEGOCIOS).pack(pady=(0, 10))

        # --- Controles de Nueva Alarma (H:M:S) ---
        frame_input = ttk.Frame(frame, style='TFrame')
        frame_input.pack(fill='x', pady=5)

        # Horas
        ttk.Label(frame_input, text="Horas:").pack(side='left', padx=(0, 2))
        self.alarm_hours_entry = ttk.Entry(frame_input, width=3)
        self.alarm_hours_entry.pack(side='left', padx=(0, 10))
        self.alarm_hours_entry.insert(0, "0")

        # Minutos
        ttk.Label(frame_input, text="Minutos:").pack(side='left', padx=(0, 2))
        self.alarm_minutes_entry = ttk.Entry(frame_input, width=3)
        self.alarm_minutes_entry.pack(side='left', padx=(0, 10))
        self.alarm_minutes_entry.insert(0, "1")

        # Segundos
        ttk.Label(frame_input, text="Segundos:").pack(side='left', padx=(0, 2))
        self.alarm_seconds_entry = ttk.Entry(frame_input, width=3)
        self.alarm_seconds_entry.pack(side='left', padx=(0, 15))
        self.alarm_seconds_entry.insert(0, "0")

        ttk.Button(frame_input, text="➕ Crear Alarma", command=self.manejar_nueva_alarma,
                   style='Action.TButton').pack(side='left')

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)

        # --- Listado de Alarmas Activas ---
        ttk.Label(frame, text="Alarmas Activas (Tiempo Restante)", font=FUENTE_NEGOCIOS).pack(pady=(0, 5))

        self.alarm_list_frame = ttk.Frame(frame)
        self.alarm_list_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(self.alarm_list_frame, borderwidth=0, background=COLOR_BLANCO)
        vscroll = ttk.Scrollbar(self.alarm_list_frame, orient="vertical", command=canvas.yview)

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

    def manejar_nueva_alarma(self):
        """Captura los datos del formulario (H:M:S), los convierte a segundos y llama al AlarmManager."""
        try:
            # 1. Leer los valores (usando 'or 0' para manejar campos vacíos como 0)
            hours = int(self.alarm_hours_entry.get() or 0)
            minutes = int(self.alarm_minutes_entry.get() or 0)
            seconds = int(self.alarm_seconds_entry.get() or 0)

            # 2. Calcular el total de segundos
            total_seconds = (hours * 3600) + (minutes * 60) + seconds

            if total_seconds <= 0:
                print("⚠️ El tiempo de alarma debe ser un número positivo (H:M:S > 0).")
                return

            # 3. Llamar al AlarmManager con el total de segundos
            self.alarm_manager.set_alarm(total_seconds)

            # 4. Limpiar y preparar para la siguiente alarma (Default: 1 minuto)
            self.alarm_hours_entry.delete(0, tk.END)
            self.alarm_hours_entry.insert(0, "0")
            self.alarm_minutes_entry.delete(0, tk.END)
            self.alarm_minutes_entry.insert(0, "1")
            self.alarm_seconds_entry.delete(0, tk.END)
            self.alarm_seconds_entry.insert(0, "0")

            self.actualizar_lista_alarmas()

        except ValueError:
            print("⚠️ Por favor, introduce números enteros válidos para el tiempo.")
        except AttributeError:
            print("⚠️ Error: AlarmManager no inicializado.")

    def manejar_cancelar_alarma(self, alarm_id):
        """Cancela la alarma usando su ID."""
        if self.alarm_manager.cancel_alarm(alarm_id):
            self.actualizar_lista_alarmas()

    def actualizar_lista_alarmas(self):
        """Actualiza la visualización de las alarmas activas con botones de cancelación individuales."""
        if not self.scrollable_frame:
            self.after_alarm_id = self.after(1000, self.actualizar_lista_alarmas)
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        active_alarms = self.alarm_manager.get_active_alarms()

        if not active_alarms:
            ttk.Label(self.scrollable_frame, text="--- No hay alarmas activas ---", font=('Consolas', 10),
                      foreground=COLOR_TEXTO).pack(padx=10, pady=10)

        for alarm in active_alarms:
            self.add_alarm_row(self.scrollable_frame, alarm)

        self.after_alarm_id = self.after(1000, self.actualizar_lista_alarmas)

    def add_alarm_row(self, parent, alarm_data):
        """Añade una fila con la info de la alarma y su botón de cancelación."""
        row_frame = ttk.Frame(parent, padding=5, style='Note.TFrame')
        row_frame.pack(fill='x', padx=5, pady=2)

        # Convertir total_seconds a formato Hh:Mm:Ss para la visualización del tiempo total
        total_s = alarm_data['total_seconds']
        h = total_s // 3600
        m = (total_s % 3600) // 60
        s = total_s % 60
        total_time_str = f"{h:02d}h:{m:02d}m:{s:02d}s"

        # Info de la alarma
        info_text = (f"[ID{alarm_data['id']}] {alarm_data['restante']} -> {alarm_data['nombre']} "
                     f"({total_time_str} total)")
        ttk.Label(row_frame, text=info_text, font=('Consolas', 10), style='Note.TLabel').pack(side='left', fill='x',
                                                                                              expand=True)

        # Botón de Cancelación Individual
        ttk.Button(row_frame, text="❌ Cancelar", style='Danger.TButton', width=10,
                   command=lambda id=alarm_data['id']: self.manejar_cancelar_alarma(id)).pack(side='right')

    def iniciar_actualizacion_alarmas(self):
        """Inicia el ciclo de actualización de la lista de alarmas."""
        if self.alarm_manager:
            self.after_alarm_id = self.after(0, self.actualizar_lista_alarmas)

    def detener_actualizacion_alarmas(self):
        """Detiene el ciclo de actualización de la lista de alarmas."""
        if hasattr(self, 'after_alarm_id') and self.after_alarm_id:
            self.after_cancel(self.after_alarm_id)
            self.after_alarm_id = None
            print("Ciclo de actualización de alarmas detenido.")

    # -------------------------------------------------------------
    # 🔔 POPUP DE ALARMA (Notificación)
    # -------------------------------------------------------------

    def show_alarm_popup(self, alarm_name, alarm_id):
        """Muestra una ventana Toplevel sin barra de título ni botón de cierre."""

        # 1. Crear la ventana popup
        popup = tk.Toplevel(self.root)
        popup.title("🚨 ¡ALARMA!")
        popup.geometry("350x150")
        popup.resizable(False, False)

        # ✅ Eliminar la barra de título y los botones (incluido el de cierre 'X')
        popup.overrideredirect(True)

        # Hacer que el popup sea modal (siempre encima)
        popup.transient(self.root)
        popup.grab_set()

        # 2. Centrar la ventana
        self.root.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')

        # 3. Función para cerrar y detener la música
        def close_and_stop(event=None):
            """Función para cerrar el popup y detener el sonido."""
            self.alarm_manager.stop_alarm_sound()
            self.alarm_manager.cancel_alarm(alarm_id)
            popup.destroy()
            self.actualizar_lista_alarmas()

        # 4. Contenido
        frame = ttk.Frame(popup, padding=20, relief='solid', borderwidth=2)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="¡El Temporizador ha Terminado!", font=FUENTE_TITULO, foreground=COLOR_ACCION).pack(
            pady=5)
        ttk.Label(frame, text=f"Hora de Disparo: {alarm_name}", font=FUENTE_NEGOCIOS).pack(pady=5)
        ttk.Label(frame, text="Haz clic para cerrar.", font=('Arial', 9, 'italic'), foreground=COLOR_TEXTO).pack(pady=0)

        # 5. Configurar el cierre
        # La forma de cerrar es mediante un clic en la ventana.
        popup.bind("<Button-1>", close_and_stop)
        frame.bind("<Button-1>", close_and_stop)

        # 6. Esperar a que se cierre para continuar la ejecución del hilo principal de Tkinter
        self.root.wait_window(popup)

    # -------------------------------------------------------------
    # 📄 LÓGICA Y VISTA DE TAREAS (Editor de Notas)
    # -------------------------------------------------------------

    def crear_interfaz_tareas(self, parent_frame):
        """Crea el editor de texto simple para el archivo res/notes dentro de la pestaña Tareas."""

        frame = ttk.Frame(parent_frame, padding=15, style='TFrame')
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Editor de Notas ", font=FUENTE_TITULO).pack(pady=(0, 10), anchor="w")
        ttk.Label(frame, text="Use este panel para tomar notas rápidas sobre la ejecución de tareas.",
                  font=FUENTE_NEGOCIOS).pack(pady=(0, 15), anchor="w")

        # 1. Widget de texto
        self.notes_text_editor = tk.Text(
            frame,
            height=20,
            wrap="word",
            bg=COLOR_BLANCO,
            relief="solid",
            borderwidth=1,
            font=FUENTE_MONO
        )
        self.notes_text_editor.pack(fill="both", expand=True, pady=(0, 10))

        # 2. Botones de Cargar y Guardar
        frame_botones = ttk.Frame(frame)
        frame_botones.pack(fill="x", pady=(5, 0))

        ttk.Button(frame_botones, text="Guardar Cambios", command=self.guardar_res_notes, style='Action.TButton').pack(
            side=tk.RIGHT)
        ttk.Button(frame_botones, text="Cargar Archivo", command=self.cargar_res_notes, style='Action.TButton').pack(
            side=tk.LEFT)

        self.cargar_res_notes(initial_load=True)  # Carga inicial al crear la interfaz

    def cargar_res_notes(self, initial_load=False):
        """Carga el contenido de res/notes al editor de texto."""
        if not self.notes_text_editor: return

        contenido = cargar_contenido_res_notes()

        self.notes_text_editor.delete("1.0", tk.END)

        if "Error al cargar:" in contenido:
            self.notes_text_editor.insert(tk.END, contenido)
        else:
            if initial_load and not contenido.strip():
                self.notes_text_editor.insert(tk.END, "# Escriba aquí sus notas (res/notes)")
            else:
                self.notes_text_editor.insert(tk.END, contenido)

        if initial_load:
            print("Cargado 'res/notes' en la pestaña Tareas.")

    def guardar_res_notes(self):
        """Guarda el contenido del editor de texto en res/notes."""
        if not self.notes_text_editor: return

        contenido = self.notes_text_editor.get("1.0", tk.END)

        success, message = guardar_contenido_res_notes(contenido)

        if success:
            messagebox.showinfo("✅ Guardado", "Notas guardadas exitosamente.")
            print(message)
        else:
            messagebox.showerror("❌ Error al Guardar", message)
            print(f"FALLO AL GUARDAR: {message}")

    # -------------------------------------------------------------
    # 📦 ESTRUCTURA PRINCIPAL DEL PANEL
    # -------------------------------------------------------------

    def crear_area_principal(self):
        """Crea el contenedor de las subpestañas."""
        frame_izquierdo = ttk.Frame(self, style='TFrame')
        frame_izquierdo.grid(row=0, column=0, sticky="nsew")

        frame_izquierdo.grid_rowconfigure(0, weight=1)
        frame_izquierdo.grid_columnconfigure(0, weight=1)

        self.crear_notebook_pestañas(frame_izquierdo)

    def crear_notebook_pestañas(self, parent_frame):
        """Crea las pestañas internas para las tareas (T1, Carrera, Radios, Tareas, Alarmas, etc.)."""
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

            elif sub_tab_text == "Tareas":
                self.crear_interfaz_tareas(frame)  # <--- Llamada a la nueva interfaz

            elif sub_tab_text == "Alarmas":
                self.crear_interfaz_alarmas(frame)

                # -------------------------------------------------------------

    # 🐪 LÓGICA DE T2 (CARRERA DE CAMELLOS)
    # ... (El código de carreraCamellos no cambia)
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
        """Detiene el ciclo de actualización periódica y los hilos/tareas."""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
            print("Ciclo de actualización de gráficos detenido.")

        if self.net_monitor:
            self.net_monitor.stop()
            self.net_monitor.join()
            print("Hilo de TrafficMeter detenido.")

        self.detener_actualizacion_carrera()
        self.detener_actualizacion_alarmas()

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

        # --- FILA 8: Reproductor Música (T3) ---
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