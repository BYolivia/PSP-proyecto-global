# Módulo: vista/panel_lateral.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# --- Módulos de Lógica Existente ---
from logica.controlador import accion_placeholder
from logica.T1.backup import accion_backup_t1
from logica.T1.runVScode import abrir_vscode
from logica.T1.openBrowser import navegar_a_url
from logica.T2.scraping import hacer_scraping
# 🔑 NUEVA IMPORTACIÓN DE LÓGICA T2
from logica.T2.musicReproductor import MusicReproductor

# --- Módulos de Vistas ---
# 🔑 IMPORTACIÓN DE LA VENTANA SECUNDARIA DEL BUSCAMINAS
from vista.ventana_buscaMinas import VentanaBuscaMinas
from vista.reproductor_controller import ReproductorController
from vista.config import *


class PanelLateral(ttk.Frame):
    """
    Panel lateral izquierdo de la aplicación.
    Contiene la barra de entrada, botones de lógica (Extracción, Navegación, Backup)
    y los controles de música esenciales.
    """

    # Usamos la constante definida en vista/config.py
    ANCHO_CARACTERES_FIJO = ANCHO_CARACTERES_PANEL_LATERAL

    def __init__(self, parent, root, panel_central, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root
        self.panel_central = panel_central
        self.controles_musica = None
        self.entrada_superior = None

        # 🔑 REFERENCIA A LA VENTANA NO-MODAL DEL BUSCAMINAS
        self.buscaminas_window = None

        # 🔑 INSTANCIA DE LÓGICA DE MÚSICA T2
        self.music_reproductor = MusicReproductor()

        self.configurar_estilos_locales(root)

        # Configuración de Layout Principal
        self.grid_rowconfigure(99, weight=1)  # Permite que la Fila 99 se expanda
        self.grid_columnconfigure(0, weight=1)

        # Creación de Secciones
        self.crear_barra_de_entrada()  # Fila 0
        self.crear_seccion_acciones()  # Fila 1
        self.crear_seccion_aplicaciones()  # Fila 2
        self.crear_seccion_batch()  # Fila 3

        # Separador y Espacio Expandible
        ttk.Separator(self, orient='horizontal').grid(row=4, column=0, sticky="ew", pady=(10, 0))
        tk.Frame(self, height=1).grid(row=99, column=0, sticky="nsew")

        # 🔑 LLAMADA AL CONTROLADOR DE MÚSICA
        self.crear_controles_musica()  # Fila 100

    # -------------------------------------------------------------
    # 🖼️ ESTRUCTURA Y WIDGETS
    # -------------------------------------------------------------

    def crear_barra_de_entrada(self):
        """Crea la entrada superior para URL/Scraping."""
        frame_entrada = ttk.Frame(self, style='TFrame', padding="10 5 10 0")
        frame_entrada.grid(row=0, column=0, sticky="ew")

        self.entrada_superior = ttk.Entry(frame_entrada, width=self.ANCHO_CARACTERES_FIJO, style='Yellow.TEntry')
        self.entrada_superior.pack(fill="x", ipady=3)
        self.entrada_superior.bind('<Return>', self.manejar_navegacion)

    def crear_seccion_acciones(self):
        """Crea los botones de Extracción/Navegación."""
        acciones_extraccion = [
            ("Extraer Datos (Wikipedia)", self.manejar_extraccion_datos),
            ("Ir a la URL usando el navegador", self.manejar_navegacion),
            ("Buscar API Google", lambda: accion_placeholder("Buscar API Google"))
        ]
        self._crear_bloque_botones(self, titulo="Extracción/Navegación", acciones=acciones_extraccion, grid_row=1)

    def crear_seccion_aplicaciones(self):
        """Crea los botones de apertura de aplicaciones."""
        app2_comando = self.manejar_inicio_carrera_t2

        acciones_aplicaciones = [
            ("Visual Code", abrir_vscode),
            ("Carrera de Camellos 🏁", app2_comando),
            # 🔑 VINCULACIÓN DEL BOTÓN APP3 CON LA FUNCIÓN DE LANZAMIENTO
            ("Juego de Buscaminas 💣", self.manejar_app3)
        ]
        self._crear_bloque_botones(self, titulo="Aplicaciones", acciones=acciones_aplicaciones, grid_row=2)

    def crear_seccion_batch(self):
        """Crea el botón de Copias de seguridad."""
        acciones_batch = [
            ("Copias de seguridad", self.manejar_backup)
        ]
        self._crear_bloque_botones(self, titulo="Procesos batch", acciones=acciones_batch, grid_row=3)

    def crear_controles_musica(self):
        """Crea el área para alojar los controles de música/radio usando el nuevo controlador."""
        frame_musica = ttk.Frame(self, style='TFrame', padding="15 10")
        frame_musica.grid(row=100, column=0, sticky="ew")
        frame_musica.grid_columnconfigure(0, weight=1)

        # 🔑 REEMPLAZO CLAVE: Usamos ReproductorController y le pasamos la instancia de la lógica.
        self.controles_musica = ReproductorController(
            frame_musica,
            self.root,
            music_reproductor_instance=self.music_reproductor  # Pasamos la instancia de la lógica T2
        )
        self.controles_musica.grid(row=0, column=0, sticky="nsew")

        frame_musica.grid_rowconfigure(0, weight=1)

    # -------------------------------------------------------------
    # ⏯️ MÉTODOS DE LÓGICA / CONTROL
    # -------------------------------------------------------------

    def manejar_extraccion_datos(self):
        """
        Obtiene el término de búsqueda, realiza el scraping, y carga el resultado
        en el módulo Navegador del Panel Central.
        """
        termino_busqueda = self.entrada_superior.get().strip()

        if not termino_busqueda:
            messagebox.showwarning("⚠️ Entrada Vacía",
                                   "Por favor, introduce un término de búsqueda para extraer datos.")
            return

        success, message, contenido = hacer_scraping(termino_busqueda)

        if success:
            messagebox.showinfo("✅ Extracción Exitosa", message)

            if self.panel_central:
                self.panel_central.cargar_contenido_web(f"Scraping: {termino_busqueda}", contenido)
            else:
                messagebox.showerror("Error", "No se puede visualizar el resultado: Panel Central no disponible.")

        else:
            messagebox.showerror("❌ Error de Extracción", message)

    def manejar_inicio_carrera_t2(self):
        """
        Llama al método 'manejar_inicio_carrera' del Panel Central.
        """
        if self.panel_central:
            print("Botón Carrera presionado. Iniciando Carrera de Camellos en Panel Central...")
            self.panel_central.manejar_inicio_carrera()
        else:
            messagebox.showerror("Error", "El Panel Central no está inicializado.")

    # 🔑 FUNCIÓN PARA LANZAR LA VENTANA SECUNDARIA NO-MODAL
    def manejar_app3(self):
        """
        Lanza la ventana secundaria (Toplevel) del Buscaminas.
        Asegura que solo haya una instancia abierta a la vez.
        """

        # 1. Verificar si la ventana ya existe y está abierta
        if self.buscaminas_window and self.buscaminas_window.winfo_exists():
            # Si existe, la traemos al frente y le damos foco
            self.buscaminas_window.lift()
            print("❌ La ventana Buscaminas ya está abierta. Trayendo al frente.")
            return

        # 2. Crear y guardar la referencia de la nueva ventana
        try:
            # Creamos la instancia Toplevel, pasando la ventana principal (root) como parent
            self.buscaminas_window = VentanaBuscaMinas(self.root)
            print("✅ Ventana Buscaminas lanzada.")

        except Exception as e:
            messagebox.showerror("Error de Aplicación", f"No se pudo iniciar el Buscaminas: {e}")
            print(f"Error al iniciar Buscaminas: {e}")

    def manejar_navegacion(self, event=None):
        """
        Obtiene el texto de la entrada superior y llama a la función de navegación (abrir navegador externo).
        """
        url = self.entrada_superior.get()
        if navegar_a_url(url):
            self.entrada_superior.delete(0, tk.END)

    def manejar_backup(self):
        """Llama a la lógica de backup de T1 e informa al usuario del resultado."""
        print("Iniciando proceso de Copia de Seguridad...")
        success, message = accion_backup_t1()

        if success:
            messagebox.showinfo("✅ Backup Completado", message)
        else:
            messagebox.showerror("❌ Error en el Backup", message)

    # -------------------------------------------------------------
    # ⚙️ MÉTODOS HELPER
    # -------------------------------------------------------------

    def configurar_estilos_locales(self, parent):
        """Configura estilos para los widgets del panel lateral, usando constantes importadas."""
        style = ttk.Style(parent)

        style.configure('Yellow.TEntry', fieldbackground='#fff8e1', foreground=COLOR_TEXTO, padding=[5, 5],
                        relief='solid', borderwidth=1)

        style.configure('Green.TButton', background=COLOR_EXITO, foreground=COLOR_BLANCO, font=FUENTE_NEGOCIOS,
                        relief='flat', padding=[10, 5])
        style.map('Green.TButton', background=[('active', '#388E3C'), ('pressed', '#1B5E20')])

        style.configure('Action.TButton', background=COLOR_ACCION, foreground=COLOR_BLANCO, font=FUENTE_NEGOCIOS,
                        relief='flat', padding=[10, 5])
        style.map('Action.TButton', background=[('active', COLOR_ACCION_HOVER), ('pressed', COLOR_ACCION_PRESSED)])

        style.configure('SmallAction.TButton', background=COLOR_ACCION, foreground=COLOR_BLANCO,
                        font=(FUENTE_FAMILIA, 9, 'bold'),
                        relief='flat', padding=[5, 3])
        style.map('SmallAction.TButton', background=[('active', COLOR_ACCION_HOVER), ('pressed', COLOR_ACCION_PRESSED)])

    def _crear_bloque_botones(self, parent_frame, titulo, acciones, grid_row):
        """Función helper para crear secciones de etiquetas y botones usando GRID."""

        frame_seccion = ttk.Frame(parent_frame, style='TFrame', padding="10 0 10 5")
        frame_seccion.grid(row=grid_row, column=0, sticky="ew")

        if titulo:
            frame_titulo = ttk.Frame(frame_seccion, style='TFrame')
            frame_titulo.pack(fill="x", pady=(10, 0))
            ttk.Label(frame_titulo, text=titulo, font=FUENTE_NEGOCIOS).pack(anchor="w", padx=5)

        for texto_boton, comando in acciones:
            # 🔑 CORRECCIÓN FINAL: Todos los botones de acción usarán el estilo verde ('Green.TButton').
            style_to_use = 'Green.TButton'

            ttk.Button(frame_seccion, text=texto_boton, command=comando, style=style_to_use).pack(fill="x", pady=5)

    def set_panel_central_reference(self, panel_central_instance):
        """
        Asigna la referencia al PanelCentral una vez que ambos paneles han sido inicializados.
        Esto resuelve la dependencia circular.
        """
        self.panel_central = panel_central_instance
        print("✅ [PanelLateral] Referencia a Panel Central establecida.")