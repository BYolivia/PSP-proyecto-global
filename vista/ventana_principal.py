# Módulo: vista/ventana_principal.py

import tkinter as tk
from tkinter import ttk
from vista.panel_lateral import PanelLateral
from vista.panel_central import PanelCentral
# Asegúrate de que estas funciones de lógica existen y funcionan sin error.
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
        self.panel_central = None
        self.panel_lateral = None # 🔑 Añadir inicialización a None

        style = ttk.Style()
        style.theme_use('clam')

        self.config(bg=COLOR_FONDO)
        self.configurar_estilos(style)

        # Configuración del protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Configuración de la cuadrícula
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # Fila de la barra inferior
        self.grid_columnconfigure(0, weight=0)  # Columna del panel lateral (ancho fijo)
        self.grid_columnconfigure(1, weight=1)  # Columna del panel central

        self.crear_paneles_principales()
        self.crear_barra_inferior()

        # Inicio de los ciclos de actualización
        self.iniciar_actualizacion_reloj()
        self.iniciar_actualizacion_clima()

        # 🔑 CORRECCIÓN CRÍTICA: Iniciar el bucle de actualización del Panel Central (T1)
        self.iniciar_actualizacion_graficos()

    def configurar_estilos(self, s: ttk.Style):
        """Define estilos visuales personalizados."""

        s.configure('TFrame', background=COLOR_FONDO)
        s.configure('TLabel', background=COLOR_FONDO, foreground=COLOR_TEXTO, font=FUENTE_NORMAL)

        s.configure('Action.TButton',
                    background=COLOR_ACCION,
                    foreground=COLOR_BLANCO,
                    font=FUENTE_NEGOCIOS,
                    relief='flat',
                    padding=[10, 5])

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

    # 🔑 MÉTODO CORREGIDO
    def crear_paneles_principales(self):
        """Ensambla el panel lateral y el panel central, resolviendo la dependencia circular."""

        # 1. Crear Panel Lateral: Inicialmente no necesita el PanelCentral, solo necesita saber que existirá.
        # PanelLateral espera: PanelLateral(parent, root, panel_central_ref, ...)
        # Usamos None para 'panel_central_ref' por ahora.
        self.panel_lateral = PanelLateral(self, self, None, width=ANCHO_PANEL_LATERAL)
        self.panel_lateral.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)
        self.panel_lateral.grid_propagate(False)


        # 2. Crear Panel Central: Ahora sí necesita la referencia al PanelLateral para inyectar el controlador de audio.
        # PanelCentral espera: PanelCentral(parent, root, panel_lateral)
        self.panel_central = PanelCentral(self, self, panel_lateral=self.panel_lateral)
        self.panel_central.grid(row=0, column=1, sticky="nswe", padx=(5, 10), pady=10)

        # 3. Finalizar la dependencia circular: Asignar la referencia del Panel Central al Panel Lateral.
        # El PanelLateral requiere la referencia de PanelCentral para manejar eventos (ej. Scrapping).
        self.panel_lateral.set_panel_central_reference(self.panel_central)


    # --- LÓGICA DE ACTUALIZACIÓN DE GRÁFICOS (T1) ---
    def iniciar_actualizacion_graficos(self):
        """Inicia el ciclo de actualización de recursos del PanelCentral."""
        if self.panel_central:
            print("Iniciando actualización automática de gráficos del Panel Central.")
            # Llama al método que inicializa el TrafficMeter y el self.after()
            self.panel_central.iniciar_actualizacion_automatica()
        else:
            print("Error: Panel Central no inicializado para iniciar gráficos.")

    # --- LÓGICA DE ACTUALIZACIÓN DE RELOJ ---
    def actualizar_reloj(self):
        """Obtiene la hora local y actualiza la etiqueta del reloj. CORREGIDO: No se detiene en caso de error."""
        try:
            hora_actual = obtener_hora_local()
            if self.label_reloj:
                self.label_reloj.config(text=f"Día y Hora: {hora_actual}")
        except Exception as e:
            if self.label_reloj:
                self.label_reloj.config(text="Error al obtener la hora")
            print(f"Error en el reloj: {e}")

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
        """Obtiene la temperatura local y actualiza la etiqueta en la barra inferior. CORREGIDO: No se detiene en caso de error."""
        try:
            datos_clima = obtener_datos_clima()
            if self.label_clima:
                self.label_clima.config(text=f"Temperatura: {datos_clima}")
        except Exception as e:
            if self.label_clima:
                self.label_clima.config(text="Error al obtener el clima")
            print(f"Error en la actualización del clima: {e}")

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

            # Desconectar correo si hay sesión activa
            panel_correos = self.panel_central.modulos.get("Correos")
            if panel_correos:
                panel_correos.cerrar()

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