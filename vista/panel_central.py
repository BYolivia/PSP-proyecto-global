# Módulo: vista/panel_central.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# --- LÓGICA DE CONTROL UNIVERSAL ---
from logica.T1.trafficMeter import iniciar_monitor_red
from logica.T2.alarm import AlarmManager

# --- MÓDULOS DE PESTAÑAS (Importación de las Vistas Modulares) ---
from vista.central_panel.view_recursos import RecursosPanel
from vista.central_panel.view_carrera import CarreraPanel
from vista.central_panel.view_radio import RadioPanel
from vista.central_panel.view_alarmas import AlarmaPanel
from vista.central_panel.view_notas import NotasPanel
from vista.central_panel.view_scrapping import NavegadorPanel
from vista.central_panel.view_chat import ChatPanel
from vista.central_panel.view_correos import CorreosPanel
from vista.central_panel.view_enlaces import EnlacesPanel

# --- IMPORTACIÓN UNIVERSAL DE CONSTANTES ---
from vista.config import *


class PanelCentral(ttk.Frame):
    """
    Controlador central del Panel.
    Gestiona el layout principal, inicializa la lógica universal y coordina
    las instancias de las clases modulares de cada pestaña (view_*).
    """

    INTERVALO_ACTUALIZACION_MS = INTERVALO_RECURSOS_MS

    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root

        # --- Variables de Estado y Lógica Central ---
        self.after_id = None
        self.net_monitor = None

        # Lógica de Matplotlib (T1)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = None
        self.canvas_widget = None
        self.grafico_frame = None

        # Lógica de Alarmas
        self.alarm_manager = AlarmManager(self.root, self.show_alarm_popup)

        # Contenedores para módulos y pestañas
        self.tabs = {}
        self.modulos = {}

        # Configuración de Layout Principal
        # 🎯 CORRECCIÓN 1: Se elimina la columna 1. La columna 0 ocupa todo el espacio.
        self.grid_columnconfigure(0, weight=1)  # La Columna de Pestañas ahora es la única y principal
        self.grid_rowconfigure(0, weight=1)

        self.crear_area_principal()
        # ❌ Se elimina la llamada a self.crear_panel_chat_y_alumnos()

    # 📦 ESTRUCTURA PRINCIPAL Y CREACIÓN DE PESTAÑAS
    # -------------------------------------------------------------

    def crear_area_principal(self):
        """Crea el contenedor de las subpestañas (Notebook), columna izquierda (0)."""
        frame_izquierdo = ttk.Frame(self, style='TFrame')
        frame_izquierdo.grid(row=0, column=0, sticky="nsew")  # Ocupa toda la ventana

        frame_izquierdo.grid_rowconfigure(0, weight=1)
        frame_izquierdo.grid_columnconfigure(0, weight=1)

        self.crear_notebook_pestanas(frame_izquierdo)

    def crear_notebook_pestanas(self, parent_frame):
        """Crea las pestañas e inicializa los módulos modulares en cada Frame."""
        sub_notebook = ttk.Notebook(parent_frame)
        sub_notebook.grid(row=0, column=0, sticky="nsew")

        # Lista completa de pestañas
        sub_tabs = ["Recursos", "Carrera", "Radios", "Navegador", "Correos", "Tareas", "Alarmas", "Enlaces", "Chat"]

        # Mapeo de la pestaña a la clase modular
        CLASES_MODULARES = {
            "Recursos": RecursosPanel,
            "Carrera": CarreraPanel,
            "Radios": RadioPanel,
            "Navegador": NavegadorPanel,
            "Correos": CorreosPanel,
            "Tareas": NotasPanel,
            "Alarmas": AlarmaPanel,
            "Enlaces": EnlacesPanel,
            "Chat": ChatPanel,
        }

        for sub_tab_text in sub_tabs:
            frame = ttk.Frame(sub_notebook, style='TFrame')
            sub_notebook.add(frame, text=sub_tab_text)
            self.tabs[sub_tab_text] = frame

            # Asegurar que el Frame de la pestaña se expande
            frame.grid_rowconfigure(0, weight=1)
            frame.grid_columnconfigure(0, weight=1)

            ClasePanel = CLASES_MODULARES.get(sub_tab_text)
            vista_instancia = None

            if ClasePanel:
                # --- Lógica de Inicialización específica ---
                if sub_tab_text == "Recursos":
                    vista_instancia = RecursosPanel(frame, self.figure, self.canvas)
                    self.modulos[sub_tab_text] = vista_instancia

                    self.canvas = vista_instancia.canvas
                    self.canvas_widget = vista_instancia.canvas_widget
                    self.grafico_frame = vista_instancia.grafico_frame

                elif sub_tab_text == "Alarmas":
                    vista_instancia = AlarmaPanel(frame, self.root, self.alarm_manager)
                    self.modulos[sub_tab_text] = vista_instancia

                else:
                    vista_instancia = ClasePanel(frame, self.root)
                    self.modulos[sub_tab_text] = vista_instancia

                # Ubicar la instancia de la vista modular dentro de su Frame padre (CRÍTICO)
                vista_instancia.grid(row=0, column=0, sticky="nsew")

    # -------------------------------------------------------------
    # 📞 MÉTODOS DE CONEXIÓN (Llamados desde panel_lateral.py)
    # -------------------------------------------------------------

    def manejar_inicio_carrera(self):
        """Inicia la carrera de camellos llamando al módulo de Carrera (T2)."""
        if 'Carrera' in self.modulos:
            self.modulos['Carrera'].manejar_inicio_carrera()
        else:
            messagebox.showerror("Error", "Módulo de Carrera no inicializado.")

    def cargar_contenido_web(self, titulo, contenido):
        """Muestra el resultado del scraping llamando al módulo Navegador."""
        if 'Navegador' in self.modulos:
            self.modulos['Navegador'].cargar_contenido_web(titulo, contenido)
        else:
            messagebox.showerror("Error", "El módulo Navegador (Scrapping) no está inicializado.")

    # -------------------------------------------------------------
    # 🔔 POPUP DE ALARMA Y LÓGICA T1
    # -------------------------------------------------------------

    def show_alarm_popup(self, alarm_name, alarm_id):
        """Muestra una ventana emergente cuando una alarma salta."""
        popup = tk.Toplevel(self.root)
        popup.title("🚨 ¡ALARMA!")

        # --- Código de configuración del popup omitido por brevedad ---
        popup.geometry("350x150")
        popup.resizable(False, False)
        popup.overrideredirect(True)
        popup.transient(self.root)
        popup.grab_set()

        self.root.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')

        def close_and_stop(event=None):
            self.alarm_manager.stop_alarm_sound()
            self.alarm_manager.cancel_alarm(alarm_id)
            popup.destroy()
            if 'Alarmas' in self.modulos:
                self.modulos['Alarmas'].actualizar_lista_alarmas()

        frame = ttk.Frame(popup, padding=20, relief='solid', borderwidth=2)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="¡El Temporizador ha Terminado!", font=FUENTE_TITULO, foreground=COLOR_ACCION).pack(
            pady=5)
        ttk.Label(frame, text=f"Hora de Disparo: {alarm_name}", font=FUENTE_NEGOCIOS).pack(pady=5)
        ttk.Label(frame, text="Haz clic para cerrar.", font=('Arial', 9, 'italic'), foreground=COLOR_TEXTO).pack(pady=0)

        popup.bind("<Button-1>", close_and_stop)
        frame.bind("<Button-1>", close_and_stop)
        self.root.wait_window(popup)

    # -------------------------------------------------------------
    # 📈 LÓGICA DE T1 (MONITOR DE RECURSOS)
    # -------------------------------------------------------------

    def actualizar_recursos(self):
        """Obtiene los datos del sistema y delega el dibujo al módulo RecursosPanel."""
        try:
            if self.net_monitor is None:
                raise Exception("TrafficMeter no inicializado.")

            net_in, net_out, cpu_percent, ram_percent = self.net_monitor.get_io_data_kb()

            if 'Recursos' in self.modulos:
                self.modulos['Recursos'].actualizar_datos(net_in, net_out, cpu_percent, ram_percent)
                self.modulos['Recursos'].dibujar_grafico()

                if self.canvas:
                    self.canvas.draw()

        except Exception as e:
            print(f"Error en la actualización de recursos T1: {e}")
            pass

        self.after_id = self.after(self.INTERVALO_ACTUALIZACION_MS, self.actualizar_recursos)

    def iniciar_actualizacion_automatica(self):
        """
        Inicia el ciclo de actualización del gráfico de recursos.
        Inicializa TrafficMeter si no se hizo en __init__.
        """
        if self.net_monitor is None:
            print("Inicializando TrafficMeter antes de actualizar recursos.")
            try:
                self.net_monitor = iniciar_monitor_red()
            except Exception as e:
                messagebox.showerror("Error de Hilo", f"No se pudo iniciar TrafficMeter. ¿Falta 'psutil'? Detalle: {e}")
                print("No se pudo iniciar TrafficMeter. La actualización automática no comenzará.")
                return

        print("Iniciando actualización automática de recursos.")
        self.after_id = self.after(0, self.actualizar_recursos)

    def detener_actualizacion_automatica(self):
        """Detiene el ciclo de actualización periódica y los hilos/tareas de los módulos."""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
            print("Ciclo de actualización de gráficos detenido.")

        if self.net_monitor:
            self.net_monitor.stop()
            self.net_monitor.join()
            print("Hilo de TrafficMeter detenido.")

        # Llama a los métodos de detención de los módulos (si existen)
        for nombre, modulo in self.modulos.items():
            if hasattr(modulo, 'detener_actualizacion'):
                modulo.detener_actualizacion()

