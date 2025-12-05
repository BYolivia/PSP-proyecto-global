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
        self.panel_central = None  # Inicializar a None para evitar errores en on_closing

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

    def crear_paneles_principales(self):
        """Ensambla el panel lateral y el panel central."""

        # Panel Central debe inicializarse primero para pasar la referencia al lateral
        # self es parent
        self.panel_central = PanelCentral(self, self)
        self.panel_central.grid(row=0, column=1, sticky="nswe", padx=(5, 10), pady=10)

        # 🎯 CORRECCIÓN CLAVE: Pasar 'self' como argumento 'root' y 'self.panel_central' como argumento posicional.
        # PanelLateral espera: PanelLateral(parent, root, panel_central, ...)
        self.panel_lateral = PanelLateral(self, self, self.panel_central, width=ANCHO_PANEL_LATERAL)
        self.panel_lateral.grid(row=0, column=0, sticky="nswe", padx=(10, 5), pady=10)

        self.panel_lateral.grid_propagate(False)

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
            # CORRECCIÓN: Eliminamos la detención para que el after continúe intentando
            # self.detener_actualizacion_reloj()
            # return

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
            # CORRECCIÓN: Eliminamos la detención para que el after continúe intentando
            # self.detener_actualizacion_clima()
            # return

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

        # Solo intenta detener el panel central si fue inicializado
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
        self.label_reloj.pack(side="left")# Módulo: vista/central_panel/view_radio.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# 🎯 Asumo que MusicReproductor está importado aquí.
from logica.T2.musicReproductor import MusicReproductor
from vista.config import *


class RadioPanel(ttk.Frame):
    """
    Panel de controles de Radio/Música.
    Gestiona la interfaz de reproducción y volumen.
    """

    def __init__(self, parent_frame_musica, root, *args, **kwargs):
        super().__init__(parent_frame_musica, *args, **kwargs)
        self.root = root

        # 🎯 Instanciar la lógica del reproductor al inicializar la vista
        self.reproductor = MusicReproductor()

        # Variables de control de UI
        self.volumen_var = tk.DoubleVar(value=self.reproductor.get_volumen()) # Inicializa al volumen actual (por defecto 50)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.crear_interfaz_radio(self)

    # -------------------------------------------------------------
    # 🖼️ INTERFAZ DE USUARIO
    # -------------------------------------------------------------

    def crear_interfaz_radio(self, parent_frame):
        """Crea los controles de reproducción y el slider de volumen."""

        main_frame = ttk.Frame(parent_frame, padding=5, style='TFrame')
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1) # Columna de botones
        main_frame.grid_columnconfigure(1, weight=1) # Columna de botones
        main_frame.grid_columnconfigure(2, weight=1) # Columna de botones
        main_frame.grid_columnconfigure(3, weight=1) # Columna de volumen

        # --- Título ---
        ttk.Label(main_frame, text="Controles de Música", font=FUENTE_NEGOCIOS).grid(
            row=0, column=0, columnspan=4, pady=(0, 10), sticky="w")


        # --- Botones de Control (Fila 1) ---

        # Botón Play/Pause
        self.boton_play_pause = ttk.Button(main_frame, text="▶️", style='Action.TButton', command=self.manejar_play_pause)
        self.boton_play_pause.grid(row=1, column=1, sticky="ew", padx=5)

        # Botón Stop
        ttk.Button(main_frame, text="⏹️", style='Action.TButton', command=self.manejar_stop).grid(
            row=1, column=2, sticky="ew", padx=5)

        # Botón de Prueba de Carga (Para probar la reproducción de una URL)
        ttk.Button(main_frame, text="📡 Cargar Stream", command=self.cargar_stream_prueba).grid(
            row=1, column=0, sticky="ew", padx=5)

        # --- Slider de Volumen (Fila 2) ---
        ttk.Label(main_frame, text="Volumen:", font=FUENTE_NORMAL).grid(
            row=2, column=0, columnspan=4, pady=(10, 0), sticky="w")

        self.slider_volumen = ttk.Scale(
            main_frame,
            from_=0,
            to=100,
            orient="horizontal",
            variable=self.volumen_var,
            command=self.manejar_ajuste_volumen
        )
        self.slider_volumen.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(5, 0))

        # Etiqueta de la estación actual (para estado)
        self.label_estado = ttk.Label(main_frame, text="Estado: Detenido", anchor="center", font=('Arial', 9))
        self.label_estado.grid(row=4, column=0, columnspan=4, pady=(5, 0), sticky="ew")

    # -------------------------------------------------------------
    # ⏯️ MANEJO DE LA LÓGICA
    # -------------------------------------------------------------

    def manejar_play_pause(self):
        """Alterna entre reproducir y pausar."""
        if self.reproductor.esta_reproduciendo():
            self.reproductor.pausar()
            self.boton_play_pause.config(text="▶️")
            self.label_estado.config(text="Estado: Pausado")
        else:
            # Si está pausado o detenido, intenta reproducir el último stream cargado.
            if self.reproductor.continuar():
                 self.boton_play_pause.config(text="⏸️")
                 self.label_estado.config(text="Estado: Reproduciendo")
            else:
                 # Si no hay stream cargado, se mantiene detenido o se puede mostrar un error.
                 messagebox.showwarning("Advertencia", "No hay stream cargado para reproducir.")


    def manejar_stop(self):
        """Detiene completamente la reproducción."""
        self.reproductor.detener()
        self.boton_play_pause.config(text="▶️")
        self.label_estado.config(text="Estado: Detenido")

    def manejar_ajuste_volumen(self, valor):
        """Ajusta el volumen del reproductor basado en el slider."""
        volumen = int(float(valor))
        self.reproductor.set_volumen(volumen)
        # Puedes añadir una pequeña etiqueta para ver el volumen si es necesario.
        print(f"Volumen ajustado a: {volumen}%")

    def cargar_stream_prueba(self):
        """
        Carga y reproduce una URL de prueba o la última guardada.
        Aquí usamos una URL de ejemplo que puede ser más estable.
        """
        # Nota: La URL de tu log falló. Usamos una de prueba conocida (Radio Paradise)
        URL_STREAM_PRUEBA = "http://stream.radioparadise.com/flac"

        success, mensaje = self.reproductor.cargar_y_reproducir(URL_STREAM_PRUEBA)

        if success:
            self.boton_play_pause.config(text="⏸️")
            self.label_estado.config(text=f"Estado: Reproduciendo {mensaje}")
        else:
            self.label_estado.config(text=f"Error: {mensaje}")
            messagebox.showerror("Error de Stream", f"No se pudo cargar el stream. Revisa la URL y la conexión.\nDetalle: {mensaje}")