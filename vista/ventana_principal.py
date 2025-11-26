import tkinter as tk
from tkinter import ttk
from vista.panel_lateral import PanelLateral
from vista.panel_central import PanelCentral


class VentanaPrincipal(tk.Tk):
    """Clase principal de la aplicación que monta la interfaz con estilos nativos mejorados."""

    def __init__(self):
        super().__init__()
        self.title("Proyecto Integrado - PSP (Estilo Moderno Nativo)")
        self.geometry("1200x800")

        # 1. Usar el tema 'clam' para un aspecto más plano y moderno
        style = ttk.Style()
        style.theme_use('clam')

        self.config(bg="#f9f9f9")  # Fondo global muy claro

        self.configurar_estilos(style)

        # Configuración de la rejilla principal de la ventana
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)  # Panel lateral es de ancho fijo
        self.grid_columnconfigure(1, weight=1)  # Panel central se expande

        self.crear_paneles_principales()
        self.crear_barra_inferior()

    def configurar_estilos(self, s: ttk.Style):
        """Define estilos visuales personalizados sin dependencias externas."""

        # Paleta de Colores
        COLOR_FONDO = "#f9f9f9"
        COLOR_ACCION = "#0078d4"  # Azul principal
        COLOR_EXITO = "#4CAF50"  # Verde para éxito/notas
        COLOR_ADVERTENCIA = "#ffc107"  # Amarillo para chat
        COLOR_TEXTO = "#333333"

        # TFrame y TLabel base (fondo claro)
        s.configure('TFrame', background=COLOR_FONDO)
        s.configure('TLabel', background=COLOR_FONDO, foreground=COLOR_TEXTO, font=('Arial', 9))

        # Botones de Acción (Simulando el color azul/verde de tu diseño)
        s.configure('Action.TButton', background=COLOR_ACCION, foreground='white', font=('Arial', 10, 'bold'),
                    relief='flat', padding=[10, 5])
        s.map('Action.TButton', background=[('active', '#005a9e'), ('pressed', '#003c6e')])

        # Estilo para el área de notas (simulando el recuadro verde claro)
        s.configure('Note.TFrame', background=COLOR_EXITO, borderwidth=0, relief="solid")
        s.configure('Note.TLabel', background=COLOR_EXITO, foreground='white', font=('Arial', 9, 'italic'))

        # Estilo para el área de chat/entrada (simulando el recuadro amarillo)
        s.configure('Chat.TFrame', background=COLOR_ADVERTENCIA)
        s.configure('Chat.TLabel', background=COLOR_ADVERTENCIA)

        # Estilo para los recuadros de Alumnos (fondo blanco con borde)
        s.configure('Alumno.TFrame', background='white', borderwidth=1, relief='solid')
        s.configure('Alumno.TLabel', background='white', foreground=COLOR_TEXTO)

        # Configuración de las pestañas (Notebook interno - subpestañas)
        s.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10, 'bold'))
        s.map('TNotebook.Tab', background=[('selected', COLOR_FONDO)], foreground=[('selected', COLOR_ACCION)])

    def crear_paneles_principales(self):
        """Ensambla el panel lateral y el panel central en la rejilla."""

        # Panel Lateral (columna 0)
        self.panel_lateral = PanelLateral(self)
        self.panel_lateral.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)

        # Panel Central (columna 1)
        self.panel_central = PanelCentral(self)
        self.panel_central.grid(row=0, column=1, sticky="nswe", padx=(5, 10), pady=10)

    def crear_barra_inferior(self):
        """Crea la barra de estado o información inferior."""
        frame_inferior = ttk.Frame(self, relief="flat", padding=[10, 5, 10, 5], style='TFrame', borderwidth=0)
        frame_inferior.grid(row=1, column=0, columnspan=2, sticky="ew")
        frame_inferior.grid_columnconfigure(0, weight=1)
        frame_inferior.grid_columnconfigure(1, weight=1)
        frame_inferior.grid_columnconfigure(2, weight=1)

        # Elementos de la barra inferior (más discretos)

        # Correos sin leer
        frame_correo = ttk.Frame(frame_inferior, style='TFrame')
        frame_correo.grid(row=0, column=0, sticky="w")
        ttk.Label(frame_correo, text="Correos sin leer: 0", style='TLabel').pack(side="left")
        ttk.Button(frame_correo, text="↻", width=3, style='Action.TButton').pack(side="left", padx=5)

        # Temperatura local
        frame_temp = ttk.Frame(frame_inferior, style='TFrame')
        frame_temp.grid(row=0, column=1)
        ttk.Button(frame_temp, text="↻", width=3, style='Action.TButton').pack(side="left", padx=5)
        ttk.Label(frame_temp, text="Temperatura local: --", style='TLabel').pack(side="left")

        # Fecha y Hora
        frame_fecha = ttk.Frame(frame_inferior, style='TFrame')
        frame_fecha.grid(row=0, column=2, sticky="e")
        ttk.Label(frame_fecha, text="Fecha Día y Hora: --/--/--", style='TLabel').pack(side="left")