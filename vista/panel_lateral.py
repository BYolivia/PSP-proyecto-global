# Módulo: vista/panel_lateral.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from logica.controlador import accion_placeholder
from logica.T1.backup import accion_backup_t1
from logica.T1.runVScode import abrir_vscode
from logica.T1.openBrowser import navegar_a_url
from logica.T2.scraping import hacer_scraping  # <--- NUEVA IMPORTACIÓN DE SCRAPING

# --- IMPORTACIÓN DE CONSTANTES DESDE vista/config.py ---
# Asumo que este archivo existe y contiene las constantes de color/fuente
from vista.config import *

class PanelLateral(ttk.Frame):
    """Contiene el menú de botones y entradas para las tareas."""

    ANCHO_CARACTERES_FIJO = ANCHO_CARACTERES_PANEL_LATERAL

    def __init__(self, parent, central_panel=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.central_panel = central_panel

        self.configurar_estilos_locales(parent)

        # 1. Entrada superior (barra de entrada)
        self.entrada_superior = ttk.Entry(self, width=self.ANCHO_CARACTERES_FIJO, style='Yellow.TEntry')
        self.entrada_superior.pack(fill="x", pady=10, padx=5, ipady=3)
        self.entrada_superior.bind('<Return>', self.manejar_navegacion)

        # 2. Área de Extracción/Navegación
        acciones_extraccion = [
            # CAMBIO: Botón renombrado y vinculado a la nueva lógica de scraping
            ("Extraer Datos", self.manejar_extraccion_datos),
            ("Ir a la URL usando el navegador", self.manejar_navegacion),
            # El botón de Google se mantiene como placeholder, esperando la implementación
            ("Buscar API Google", lambda: accion_placeholder("Buscar API Google"))
        ]
        self.crear_seccion(self, titulo="", acciones=acciones_extraccion)

        # 3. Área de Aplicaciones
        app2_comando = self.manejar_inicio_carrera_t2

        acciones_aplicaciones = [
            ("Visual Code", abrir_vscode),
            ("App2 (Carrera 🏁)", app2_comando),
            ("App3", lambda: accion_placeholder("App3"))
        ]
        self.crear_seccion(self, titulo="Aplicaciones", acciones=acciones_aplicaciones)

        # 4. Área de Procesos Batch
        acciones_batch = [
            ("Copias de seguridad", self.manejar_backup)
        ]
        self.crear_seccion(self, titulo="Procesos batch", acciones=acciones_batch)

        # 5. Espacio expandible
        tk.Frame(self, height=1).pack(expand=True, fill="both")

    # --- MÉTODOS DE LÓGICA / CONTROL ---

    def manejar_extraccion_datos(self):
        """
        Obtiene el término de búsqueda de la entrada superior, realiza el scraping
        en Wikipedia (URL base fija), muestra el resultado y lo carga en el Panel Central.
        """
        # Obtenemos el texto introducido por el usuario (el término de búsqueda)
        termino_busqueda = self.entrada_superior.get().strip()

        if not termino_busqueda:
            messagebox.showwarning("⚠️ Entrada Vacía",
                                   "Por favor, introduce un término de búsqueda para extraer datos.")
            return

        # Llama a la lógica de scraping. Se esperan 3 valores: éxito, mensaje y contenido.
        success, message, contenido = hacer_scraping(termino_busqueda)

        if success:
            messagebox.showinfo("✅ Extracción Exitosa", message)

            # Llamada al Panel Central para visualizar el resultado del scraping
            if self.central_panel:
                self.central_panel.cargar_texto_en_tareas(termino_busqueda, contenido)
            else:
                messagebox.showerror("Error", "No se puede visualizar el resultado: Panel Central no disponible.")

        else:
            messagebox.showerror("❌ Error de Extracción", message)

    def manejar_inicio_carrera_t2(self):
        """
        Llama al método 'manejar_inicio_carrera' del Panel Central.
        """
        if self.central_panel:
            print("Botón App2 presionado. Iniciando Carrera de Camellos en Panel Central...")
            self.central_panel.manejar_inicio_carrera()

            # Opcional: Cambiar automáticamente a la pestaña Resultados
            if "Carrera" in self.central_panel.tabs:
                notebook = self.central_panel.tabs["Carrera"].winfo_toplevel().winfo_children()[0]
                if isinstance(notebook, ttk.Notebook):
                    notebook.select(self.central_panel.tabs["Carrera"])
        else:
            messagebox.showerror("Error", "El Panel Central no está inicializado.")

    def manejar_navegacion(self, event=None):
        """
        Obtiene el texto de la entrada superior y llama a la función de navegación.
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

    def configurar_estilos_locales(self, parent):
        """Configura estilos para los widgets del panel lateral, usando constantes importadas."""
        style = ttk.Style(parent)

        style.configure('Yellow.TEntry', fieldbackground='#fff8e1', foreground=COLOR_TEXTO, padding=[5, 5],
                        relief='solid', borderwidth=1)

        style.configure('Green.TButton', background=COLOR_EXITO, foreground=COLOR_BLANCO, font=FUENTE_NEGOCIOS,
                        relief='flat', padding=[10, 5])
        style.map('Green.TButton', background=[('active', '#388E3C'), ('pressed',
                                                                       '#1B5E20')])

        style.configure('Action.TButton', background=COLOR_ACCION, foreground=COLOR_BLANCO, font=FUENTE_NEGOCIOS,
                        relief='flat', padding=[10, 5])
        style.map('Action.TButton', background=[('active', COLOR_ACCION_HOVER), ('pressed', COLOR_ACCION_PRESSED)])

        style.configure('SmallAction.TButton', background=COLOR_ACCION, foreground=COLOR_BLANCO,
                        font=(FUENTE_FAMILIA, 9, 'bold'),
                        relief='flat', padding=[5, 3])
        style.map('SmallAction.TButton', background=[('active', COLOR_ACCION_HOVER), ('pressed', COLOR_ACCION_PRESSED)])

    def crear_seccion(self, parent_frame, titulo, acciones):
        """Función helper para crear secciones de etiquetas y botones."""
        if titulo:
            ttk.Label(parent_frame, text=titulo, font=FUENTE_NEGOCIOS).pack(fill="x", pady=(10, 0), padx=5)

        frame_botones = ttk.Frame(parent_frame, style='TFrame')
        frame_botones.pack(fill="x", pady=5, padx=5)

        for texto_boton, comando in acciones:
            # Usamos el estilo 'Green.TButton' para los botones de acción principal
            ttk.Button(frame_botones, text=texto_boton, command=comando, style='Green.TButton').pack(fill="x", pady=5)