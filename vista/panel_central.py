import tkinter as tk
from tkinter import ttk


class PanelCentral(ttk.Frame):
    """Contiene el Notebook (subpestañas de T1), el panel de Notas y el panel de Chat."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # Columna 0: Área Principal (3/4) | Columna 1: Chat (1/4)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_area_principal_y_notas()
        self.crear_panel_chat_y_alumnos()

    def crear_area_principal_y_notas(self):
        """Crea el contenedor de las subpestañas de T1 y el panel de notas (inferior izquierda)."""
        frame_izquierdo = ttk.Frame(self, style='TFrame')
        frame_izquierdo.grid(row=0, column=0, sticky="nsew")

        # Fila 0: Subpestañas (4 partes) | Fila 1: Notas (1 parte)
        frame_izquierdo.grid_rowconfigure(0, weight=4)
        frame_izquierdo.grid_rowconfigure(1, weight=1)
        frame_izquierdo.grid_columnconfigure(0, weight=1)

        # 1. El Notebook de T1 (Sub-pestañas)
        self.crear_sub_pestañas_t1(frame_izquierdo)

        # 2. El Panel de Notas (área verde clara inferior izquierda)
        panel_notas = ttk.Frame(frame_izquierdo, style='Note.TFrame')
        panel_notas.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        ttk.Label(panel_notas, text="Panel para notas informativas y mensajes sobre la ejecución de los hilos.",style='Note.TLabel', anchor="nw", justify=tk.LEFT, padding=10,font=('Arial', 9, 'italic')).pack(expand=True, fill="both")

    def crear_sub_pestañas_t1(self, parent_frame):
        """Crea las pestañas internas para la tarea T1 y las empaqueta en la rejilla."""
        sub_notebook = ttk.Notebook(parent_frame)
        sub_notebook.grid(row=0, column=0, sticky="nsew")  # Ocupa Fila 0, Columna 0

        sub_tabs = ["Resultados", "Navegador", "Correos", "Tareas", "Alarmas", "Enlaces"]
        for i, sub_tab_text in enumerate(sub_tabs):
            frame = ttk.Frame(sub_notebook, style='TFrame')
            sub_notebook.add(frame, text=sub_tab_text)

            # Contenido del área central (simulando el panel rayado)
            if sub_tab_text == "Navegador":
                # Usamos un widget Text con fondo blanco y un borde sutil para que destaque
                contenido_area = tk.Text(frame, wrap="word", padx=15, pady=15,bg='white', relief="groove", borderwidth=1,font=('Consolas', 10), foreground="#555555")
                contenido_area.insert(tk.END,">>> ÁREA DE CONTENIDO / VISOR DE NAVEGADOR (Para mostrar resultados o web scraping)\n\n""Este es el espacio dedicado a la visualización de datos o interfaces específicas de cada tarea.")
                contenido_area.pack(expand=True, fill="both", padx=5, pady=5)
                sub_notebook.select(i)

    def crear_panel_chat_y_alumnos(self):
        """Crea el panel de chat, lista de Alumnos y Reproductor de Música (columna derecha)."""
        panel_chat = ttk.Frame(self, style='TFrame', padding="10")
        panel_chat.grid(row=0, column=1, sticky="nsew")

        # Configuración interna del panel de chat
        panel_chat.grid_rowconfigure(5, weight=1)
        panel_chat.grid_rowconfigure(7, weight=0)
        panel_chat.grid_columnconfigure(0, weight=1)

        # 1. Título "Chat"
        ttk.Label(panel_chat, text="Chat", foreground="#0078d4", font=("Arial", 18, "bold"), style='TLabel').grid(row=0,column=0,pady=(0,10),sticky="w")

        # 2. Área de Mensaje
        ttk.Label(panel_chat, text="Mensaje", style='TLabel').grid(row=1, column=0, sticky="w")

        # Área de texto para el mensaje (el recuadro amarillo)
        chat_text = tk.Text(panel_chat, height=6, width=30, bg='#fff8e1', relief="solid", borderwidth=1,font=('Arial', 10))
        chat_text.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        # Botón Enviar
        ttk.Button(panel_chat, text="Enviar", style='Action.TButton').grid(row=3, column=0, pady=(0, 15), sticky="e")

        # 3. Lista de Alumnos (Simulación)
        for i in range(1, 4):
            frame_alumno = ttk.Frame(panel_chat, style='Alumno.TFrame', padding=8)
            frame_alumno.grid(row=3 + i, column=0, sticky="ew", pady=5)
            frame_alumno.grid_columnconfigure(0, weight=1)

            ttk.Label(frame_alumno, text=f"Alumno {i}", font=("Arial", 11, "bold"), style='Alumno.TLabel').grid(row=0,column=0,sticky="w")
            ttk.Label(frame_alumno, text="Lorem ipsum dolor sit amet, consectetur adipiscing elit.",wraplength=250, justify=tk.LEFT, style='Alumno.TLabel').grid(row=1, column=0, sticky="w")

            # Botón de Recargar/Actualizar
            ttk.Button(frame_alumno, text="↻", width=3, style='Action.TButton').grid(row=0, column=1, rowspan=2, padx=5,sticky="ne")

        # 4. Reproductor de Música (Simulado)
        musica_frame = ttk.LabelFrame(panel_chat, text="Reproductor Música", padding=10, style='TFrame')
        musica_frame.grid(row=8, column=0, sticky="ew", pady=(15, 0))
        ttk.Label(musica_frame, text="[ Botones de Play/Stop y Control de Volumen ]", anchor="center",style='TLabel').pack(fill="x", padx=5, pady=5)