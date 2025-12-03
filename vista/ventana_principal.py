# Módulo: ventana_principal.py

import tkinter as tk
from tkinter import ttk
from vista.panel_lateral import PanelLateral
from vista.panel_central import PanelCentral


class VentanaPrincipal(tk.Tk):
    """Clase principal de la aplicación que monta la interfaz con estilos nativos mejorados."""

    # Definimos el ancho deseado para el panel lateral
    ANCHO_PANEL_LATERAL = 300

    def __init__(self):
        super().__init__()
        self.title("Proyecto Integrado - PSP (Estilo Moderno Nativo)")
        self.geometry("1200x800")

        style = ttk.Style()
        style.theme_use('clam')

        self.config(bg="#f9f9f9")
        self.configurar_estilos(style)

        # Configuración del manejador de protocolo para el botón de cierre (X)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Columna 0 (Lateral) no se expande (weight=0), Columna 1 (Central) sí se expande (weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.crear_paneles_principales()
        self.crear_barra_inferior()

    def configurar_estilos(self, s: ttk.Style):
        """Define estilos visuales personalizados sin dependencias externas."""

        COLOR_FONDO = "#f9f9f9"
        COLOR_ACCION = "#0078d4"
        COLOR_EXITO = "#4CAF50"
        COLOR_ADVERTENCIA = "#ffc107"
        COLOR_TEXTO = "#333333"

        s.configure('TFrame', background=COLOR_FONDO)
        s.configure('TLabel', background=COLOR_FONDO, foreground=COLOR_TEXTO, font=('Arial', 9))

        s.configure('Action.TButton', background=COLOR_ACCION, foreground='white', font=('Arial', 10, 'bold'),
                    relief='flat', padding=[10, 5])
        s.map('Action.TButton', background=[('active', '#005a9e'), ('pressed', '#003c6e')])

        s.configure('Note.TFrame', background=COLOR_EXITO, borderwidth=0, relief="solid")
        s.configure('Note.TLabel', background=COLOR_EXITO, foreground='white', font=('Arial', 9, 'italic'))

        s.configure('Chat.TFrame', background=COLOR_ADVERTENCIA)
        s.configure('Chat.TLabel', background=COLOR_ADVERTENCIA)

        s.configure('Alumno.TFrame', background='white', borderwidth=1, relief='solid')
        s.configure('Alumno.TLabel', background='white', foreground=COLOR_TEXTO)

        s.configure('TNotebook.Tab', padding=[10, 5], font=('Arial', 10, 'bold'))
        s.map('TNotebook.Tab', background=[('selected', COLOR_FONDO)], foreground=[('selected', COLOR_ACCION)])

    def crear_paneles_principales(self):
        """Ensambla el panel lateral y el panel central en la rejilla, asegurando el ancho del lateral."""

        # Panel Central (se expande en columna 1)
        self.panel_central = PanelCentral(self)
        self.panel_central.grid(row=0, column=1, sticky="nswe", padx=(5, 10), pady=10)

        # Panel Lateral (se le aplica un ancho fijo para que no se expanda con el contenido)
        self.panel_lateral = PanelLateral(self, central_panel=self.panel_central, width=self.ANCHO_PANEL_LATERAL)
        self.panel_lateral.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)

        # Forzamos que el widget base respete el ancho definido, ignorando el tamaño del contenido (propagate=False)
        self.panel_lateral.grid_propagate(False)

    # --- FUNCIÓN DE CIERRE ---
    def on_closing(self):
        """
        Se ejecuta cuando se presiona el botón 'X'. Detiene el ciclo de actualización
        y cierra la ventana principal de forma limpia.
        """
        if self.panel_central:
            # Llamar al método de limpieza del Panel Central (ciclo tk.after)
            self.panel_central.detener_actualizacion_automatica()

        # Destruir el objeto Tkinter y terminar mainloop
        self.destroy()
        print("Aplicación cerrada limpiamente.")

    def crear_barra_inferior(self):
        """Crea la barra de estado o información inferior."""
        frame_inferior = ttk.Frame(self, relief="flat", padding=[10, 5, 10, 5], style='TFrame', borderwidth=0)
        frame_inferior.grid(row=1, column=0, columnspan=2, sticky="ew")
        frame_inferior.grid_columnconfigure(0, weight=1)
        frame_inferior.grid_columnconfigure(1, weight=1)
        frame_inferior.grid_columnconfigure(2, weight=1)

        frame_correo = ttk.Frame(frame_inferior, style='TFrame')
        frame_correo.grid(row=0, column=0, sticky="w")
        ttk.Label(frame_correo, text="Correos sin leer: 0", style='TLabel').pack(side="left")
        ttk.Button(frame_correo, text="↻", width=3, style='Action.TButton').pack(side="left", padx=5)

        frame_temp = ttk.Frame(frame_inferior, style='TFrame')
        frame_temp.grid(row=0, column=1)
        ttk.Button(frame_temp, text="↻", width=3, style='Action.TButton').pack(side="left", padx=5)
        ttk.Label(frame_temp, text="Temperatura local: --", style='TLabel').pack(side="left")

        frame_fecha = ttk.Frame(frame_inferior, style='TFrame')
        frame_fecha.grid(row=0, column=2, sticky="e")
        ttk.Label(frame_fecha, text="Fecha Día y Hora: --/--/--", style='TLabel').pack(side="left")