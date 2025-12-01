# Módulo: vista/panel_central.py

import tkinter as tk
from tkinter import ttk
from logica.T1.geterSystemRecource import obtener_datos_cpu_ram
from logica.T1.graficos import crear_grafico_recursos
from logica.controlador import accion_placeholder


class PanelCentral(ttk.Frame):
    """Contiene el Notebook (subpestañas de T1), el panel de Notas y el panel de Chat."""

    # Definimos el intervalo de actualización en milisegundos (5000 ms = 5 segundos)
    INTERVALO_ACTUALIZACION_MS = 5000

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.after_id = None  # ID para controlar el timer de tk.after

        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_area_principal_y_notas()
        self.crear_panel_chat_y_alumnos()

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

                # Llamada inicial, la auto-actualización tomará el control
                self.actualizar_grafico_recursos()

                sub_notebook.select(i)

            # Contenido de otras pestañas
            elif sub_tab_text == "Navegador":
                contenido_area = tk.Text(frame, wrap="word", padx=15, pady=15, bg='white', relief="groove",
                                         borderwidth=1, font=('Consolas', 10), foreground="#555555")
                contenido_area.insert(tk.END,
                                      ">>> ÁREA DE CONTENIDO / VISOR DE NAVEGADOR (Para mostrar resultados o web scraping)\n\n""Este es el espacio dedicado a la visualización de datos o interfaces específicas de cada tarea.")
                contenido_area.pack(expand=True, fill="both", padx=5, pady=5)

    def actualizar_grafico_recursos(self):
        """Obtiene los datos del sistema y dibuja/redibuja el gráfico."""
        try:
            datos_sistema = obtener_datos_cpu_ram()
            crear_grafico_recursos(self.grafico_frame, datos_sistema)
        except Exception as e:
            error_msg = f"Error al generar el gráfico de recursos: {e}"
            print(error_msg)
            for widget in self.grafico_frame.winfo_children():
                widget.destroy()
            ttk.Label(self.grafico_frame, text=error_msg, foreground='red', style='TLabel').pack(pady=20)

    def iniciar_actualizacion_automatica(self):
        """
        Programa la actualización periódica del gráfico de recursos usando tk.after,
        y almacena el ID para poder cancelarlo.
        """
        # 1. Ejecuta la actualización
        self.actualizar_grafico_recursos()

        # 2. Programa la siguiente llamada y almacena el ID
        self.after_id = self.after(self.INTERVALO_ACTUALIZACION_MS, self.iniciar_actualizacion_automatica)

    def detener_actualizacion_automatica(self):
        """Detiene el ciclo de actualización periódica del gráfico."""
        if self.after_id:
            self.after_cancel(self.after_id)
            print("Ciclo de actualización de gráficos detenido.")

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