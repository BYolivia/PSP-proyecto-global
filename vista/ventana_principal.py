# Módulo: ventana_principal.py

import tkinter as tk
from tkinter import ttk
from vista.panel_lateral import PanelLateral
from vista.panel_central import PanelCentral
from logica.T2.getLocalTime import obtener_hora_local
from logica.T2.getWeather import obtener_datos_clima

# --- IMPORTACIÓN DE CONSTANTES DESDE vista/config.py ---
from vista.config import *


class VentanaPrincipal(tk.Tk):
    """Ventana principal de la aplicación con panel lateral y central, reloj y clima."""

    def __init__(self):
        super().__init__()
        self.title("Proyecto Integrado - PSP")
        self.geometry("1200x800")

        self.label_reloj = None
        self.reloj_after_id = None
        self.label_clima = None
        self.clima_after_id = None

        style = ttk.Style()
        style.theme_use('clam')

        # Usando la constante importada
        self.config(bg=COLOR_FONDO)
        self.configurar_estilos(style)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.crear_paneles_principales()
        self.crear_barra_inferior()

        self.iniciar_actualizacion_reloj()
        self.iniciar_actualizacion_clima()

    def configurar_estilos(self, s: ttk.Style):
        """Define estilos visuales personalizados sin dependencias externas usando constantes de config."""

        # Los colores se importan, ya no se definen aquí

        s.configure('TFrame', background=COLOR_FONDO)
        s.configure('TLabel', background=COLOR_FONDO, foreground=COLOR_TEXTO, font=FUENTE_NORMAL)

        s.configure('Action.TButton',
                    background=COLOR_ACCION,
                    foreground=COLOR_BLANCO,
                    font=FUENTE_NEGOCIOS,  # Usando FUENTE_NEGOCIOS
                    relief='flat',
                    padding=[10, 5])

        # Mapeo de colores de estado de botón (usando las constantes de hover/pressed)
        s.map('Action.TButton',
              background=[('active', COLOR_ACCION_HOVER),
                          ('pressed', COLOR_ACCION_PRESSED)])

        s.configure('Note.TFrame', background=COLOR_EXITO, borderwidth=0, relief="solid")
        s.configure('Note.TLabel', background=COLOR_EXITO, foreground=COLOR_BLANCO, font=FUENTE_NOTA)

        s.configure('Chat.TFrame', background=COLOR_ADVERTENCIA)
        s.configure('Chat.TLabel', background=COLOR_ADVERTENCIA)

        s.configure('Alumno.TFrame', background=COLOR_BLANCO, borderwidth=1, relief='solid')
        s.configure('Alumno.TLabel', background=COLOR_BLANCO, foreground=COLOR_TEXTO, font=FUENTE_NORMAL)

        s.configure('TNotebook.Tab', padding=[10, 5], font=FUENTE_NEGOCIOS)
        s.map('TNotebook.Tab', background=[('selected', COLOR_FONDO)], foreground=[('selected', COLOR_ACCION)])

    def crear_paneles_principales(self):
        """Ensambla el panel lateral y el panel central en la rejilla, asegurando el ancho del lateral."""

        self.panel_central = PanelCentral(self, self)
        self.panel_central.grid(row=0, column=1, sticky="nswe", padx=(5, 10), pady=10)

        # Usando la constante importada
        self.panel_lateral = PanelLateral(self, central_panel=self.panel_central, width=ANCHO_PANEL_LATERAL)
        self.panel_lateral.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)

        self.panel_lateral.grid_propagate(False)

    # --- LÓGICA DE ACTUALIZACIÓN DE RELOJ ---
    def actualizar_reloj(self):
        """Obtiene la hora local y actualiza la etiqueta del reloj."""
        try:
            hora_actual = obtener_hora_local()
            if self.label_reloj:
                self.label_reloj.config(text=f"Día y Hora: {hora_actual}")
        except Exception as e:
            if self.label_reloj:
                self.label_reloj.config(text="Error al obtener la hora")
            print(f"Error en el reloj: {e}")
            self.detener_actualizacion_reloj()
            return

        # Usando la constante importada
        self.reloj_after_id = self.after(INTERVALO_RELOJ_MS, self.actualizar_reloj)

    def iniciar_actualizacion_reloj(self):
        """Inicia el ciclo de actualización del reloj."""
        print("Iniciando actualización automática del reloj.")
        self.reloj_after_id = self.after(0, self.actualizar_reloj)

    def detener_actualizacion_reloj(self):
        """Detiene el ciclo de actualización del reloj."""
        if self.reloj_after_id:
            self.after_cancel(self.reloj_after_id)
            self.reloj_after_id = None
            print("Ciclo de actualización del reloj detenido.")

    # --- LÓGICA DE ACTUALIZACIÓN DE CLIMA ---
    def actualizar_clima(self):
        """Obtiene la temperatura local y actualiza la etiqueta en la barra inferior."""
        try:
            datos_clima = obtener_datos_clima()
            if self.label_clima:
                self.label_clima.config(text=f"Temperatura: {datos_clima}")
        except Exception as e:
            if self.label_clima:
                self.label_clima.config(text="Error al obtener el clima")
            print(f"Error en la actualización del clima: {e}")
            self.detener_actualizacion_clima()
            return

        # Usando la constante importada
        self.clima_after_id = self.after(INTERVALO_CLIMA_MS, self.actualizar_clima)

    def iniciar_actualizacion_clima(self):
        """Inicia el ciclo de actualización del clima."""
        print("Iniciando actualización automática del clima.")
        self.clima_after_id = self.after(0, self.actualizar_clima)

    def detener_actualizacion_clima(self):
        """Detiene el ciclo de actualización del clima."""
        if self.clima_after_id:
            self.after_cancel(self.clima_after_id)
            self.clima_after_id = None
            print("Ciclo de actualización del clima detenido.")

    # --- FUNCIÓN DE CIERRE ---
    def on_closing(self):
        """Se ejecuta cuando se presiona el botón 'X'. Detiene todos los ciclos y cierra la ventana."""
        self.detener_actualizacion_reloj()
        self.detener_actualizacion_clima()

        if self.panel_central:
            self.panel_central.detener_actualizacion_automatica()

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

        # Marco de Temperatura
        frame_temp = ttk.Frame(frame_inferior, style='TFrame')
        frame_temp.grid(row=0, column=1)

        self.label_clima = ttk.Label(frame_temp, text="Temperatura: --", style='TLabel')
        self.label_clima.pack(side="left")

        # Marco de Fecha y Hora
        frame_fecha = ttk.Frame(frame_inferior, style='TFrame')
        frame_fecha.grid(row=0, column=2, sticky="e")

        self.label_reloj = ttk.Label(frame_fecha, text="Día y Hora: --/--/--", style='TLabel')
        self.label_reloj.pack(side="left")