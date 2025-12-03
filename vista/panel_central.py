# Módulo: vista/panel_central.py

import tkinter as tk
from tkinter import ttk


from logica.T1.trafficMeter import iniciar_monitor_red
from logica.T1.graficos import crear_grafico_recursos, actualizar_historial_datos
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class PanelCentral(ttk.Frame):
    """Contiene el Notebook (subpestañas de T1), el panel de Notas y el panel de Chat."""

    # Reducimos el intervalo de actualización a 1000ms (1 segundo) para gráficos fluidos
    INTERVALO_ACTUALIZACION_MS = 1000

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.after_id = None  # ID para controlar el timer de tk.after

        # 1. INICIALIZACIÓN DE VARIABLES
        self.net_monitor = iniciar_monitor_red()  # <-- INICIAR EL HILO DE RED

        # Objeto Figure de Matplotlib (debe crearse antes de crear_sub_pestañas_t1)
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = None  # Se inicializará en crear_sub_pestañas_t1

        # 2. CONFIGURACIÓN DEL LAYOUT
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_area_principal_y_notas()
        self.crear_panel_chat_y_alumnos()

        # La actualización se inicia al final de __init__
        self.iniciar_actualizacion_automatica()

    def crear_area_principal_y_notas(self):
        """Crea el contenedor de las subpestañas de T1 y el panel de notas (inferior izquierda)."""
        frame_izquierdo = ttk.Frame(self, style='TFrame')
        frame_izquierdo.grid(row=0, column=0, sticky="nsew")

        frame_izquierdo.grid_rowconfigure(0, weight=4)
        frame_izquierdo.grid_rowconfigure(1, weight=1)
        frame_izquierdo.grid_columnconfigure(0, weight=1)

        # 1. El Notebook de T1 (Sub-pestañas)
        self.crear_sub_pestañas_t1(frame_izquierdo)

        # 2. El Panel de Notas
        panel_notas = ttk.Frame(frame_izquierdo, style='Note.TFrame')
        panel_notas.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        ttk.Label(panel_notas, text="Panel para notas informativas y mensajes sobre la ejecución de los hilos.",
            style='Note.TLabel', anchor="nw", justify=tk.LEFT, padding=10, font=('Arial', 9, 'italic')).pack(
            expand=True, fill="both")

    def crear_sub_pestañas_t1(self, parent_frame):
        """Crea las pestañas internas para la tarea T1 y las empaqueta en la rejilla."""
        sub_notebook = ttk.Notebook(parent_frame)
        sub_notebook.grid(row=0, column=0, sticky="nsew")

        sub_tabs = ["Recursos", "Resultados", "Navegador", "Correos", "Tareas", "Alarmas", "Enlaces"]
        self.tabs = {}

        for i, sub_tab_text in enumerate(sub_tabs):
            frame = ttk.Frame(sub_notebook, style='TFrame')
            sub_notebook.add(frame, text=sub_tab_text)
            self.tabs[sub_tab_text] = frame

            # LÓGICA DE LA PESTAÑA DE RECURSOS
            if sub_tab_text == "Recursos":
                self.grafico_frame = ttk.Frame(frame, style='TFrame')
                self.grafico_frame.pack(expand=True, fill="both", padx=10, pady=10)

                # Inicialización del Canvas de Matplotlib
                self.canvas = FigureCanvasTkAgg(self.figure, master=self.grafico_frame)
                self.canvas_widget = self.canvas.get_tk_widget()
                self.canvas_widget.pack(expand=True, fill="both")

                # La actualización automática iniciada en __init__ se encarga de esto
                sub_notebook.select(i)

            # Contenido de otras pestañas
            elif sub_tab_text == "Navegador":
                contenido_area = tk.Text(frame, wrap="word", padx=15, pady=15, bg='white', relief="groove",
                    borderwidth=1, font=('Consolas', 10), foreground="#555555")
                contenido_area.insert(tk.END,
                    ">>> ÁREA DE CONTENIDO / VISOR DE NAVEGADOR (Para mostrar resultados o web scraping)\n\n""Este es el espacio dedicado a la visualización de datos o interfaces específicas de cada tarea.")
                contenido_area.pack(expand=True, fill="both", padx=5, pady=5)

    def actualizar_grafico_recursos(self):
        """
        Obtiene los datos del sistema (incluyendo Red) y dibuja/redibuja el gráfico.
        """
        try:
            # 1. Obtener datos de red del hilo (en KB/s)
            net_in, net_out = self.net_monitor.get_io_data_kb()

            # 2. Actualizar el historial global (CPU y RAM se obtienen dentro de esta función)
            actualizar_historial_datos(net_in, net_out)

            # 3. Redibujar el gráfico
            crear_grafico_recursos(self.figure)
            self.canvas.draw()

        except Exception as e:
            error_msg = f"Error al generar el gráfico de recursos: {e}"
            print(error_msg)
            # Manejo de errores visual en la pestaña (limpiar y mostrar error)
            if self.canvas_widget.winfo_exists():
                self.canvas_widget.pack_forget()

            error_label = ttk.Label(self.grafico_frame, text=error_msg, foreground='red', style='TLabel')
            error_label.pack(pady=20)

            # Detener la actualización para evitar bucle de error
            self.detener_actualizacion_automatica()

        # 4. Programar la siguiente llamada (solo si no hay error crítico que detenga la actualización)
        self.after_id = self.after(self.INTERVALO_ACTUALIZACION_MS, self.actualizar_grafico_recursos)

    # --- Control del Ciclo de Vida ---

    def iniciar_actualizacion_automatica(self):
        """Inicia el ciclo de actualización del gráfico de recursos."""
        print("Iniciando actualización automática de recursos.")
        # Programar la primera llamada inmediatamente
        self.after_id = self.after(0, self.actualizar_grafico_recursos)

    def detener_actualizacion_automatica(self):
        """Detiene el ciclo de actualización periódica y el hilo de red."""
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
            print("Ciclo de actualización de gráficos detenido.")

        # Detener el monitor de red al cerrar la aplicación
        if self.net_monitor:
            self.net_monitor.stop()
            self.net_monitor.join()  # Esperar a que el hilo termine
            print("Hilo de TrafficMeter detenido.")

    def crear_panel_chat_y_alumnos(self, ):
        """Crea el panel de chat, lista de Alumnos y Reproductor de Música (columna derecha)."""
        panel_chat = ttk.Frame(self, style='TFrame', padding="10")
        panel_chat.grid(row=0, column=1, sticky="nsew")

        panel_chat.grid_rowconfigure(5, weight=1)
        panel_chat.grid_rowconfigure(7, weight=0)
        panel_chat.grid_columnconfigure(0, weight=1)

        # 1. Título "Chat"
        ttk.Label(panel_chat, text="Chat", foreground="#0078d4", font=("Arial", 18, "bold"), style='TLabel').grid(row=0,
            column=0,
            pady=(
                0,
                10),
            sticky="w")

        # 2. Área de Mensaje
        ttk.Label(panel_chat, text="Mensaje", style='TLabel').grid(row=1, column=0, sticky="w")

        chat_text = tk.Text(panel_chat, height=6, width=30, bg='#fff8e1', relief="solid", borderwidth=1,
            font=('Arial', 10))
        chat_text.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        ttk.Button(panel_chat, text="Enviar", style='Action.TButton').grid(row=3, column=0, pady=(0, 15), sticky="e")

        # 3. Lista de Alumnos (Simulación)
        for i in range(1, 4):
            frame_alumno = ttk.Frame(panel_chat, style='Alumno.TFrame', padding=8)
            frame_alumno.grid(row=3 + i, column=0, sticky="ew", pady=5)
            frame_alumno.grid_columnconfigure(0, weight=1)

            ttk.Label(frame_alumno, text=f"Alumno {i}", font=("Arial", 11, "bold"), style='Alumno.TLabel').grid(row=0,
                                                                                                                column=0,
                                                                                                                sticky="w")

            ttk.Label(frame_alumno, text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.", wraplength=250,
                justify=tk.LEFT, style='Alumno.TLabel').grid(row=1, column=0, sticky="w")

            ttk.Button(frame_alumno, text="↻", width=3, style='Action.TButton').grid(row=0, column=1, rowspan=2, padx=5,
                sticky="ne")

        # 4. Reproductor de Música (Simulado)
        musica_frame = ttk.LabelFrame(panel_chat, text="Reproductor Música", padding=10, style='TFrame')
        musica_frame.grid(row=8, column=0, sticky="ew", pady=(15, 0))
        ttk.Label(musica_frame, text="[ Botones de Play/Stop y Control de Volumen ]", anchor="center",
            style='TLabel').pack(fill="x", padx=5, pady=5)