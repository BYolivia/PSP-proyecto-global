# Módulo: vista/panel_lateral.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from logica.controlador import accion_placeholder
from logica.T1.backup import accion_backup_t1
from logica.T1.runVScode import abrir_vscode
# NO necesitamos importar cargar/guardar notas aquí, ya que la lógica se mueve al Panel Central
# from logica.T1.textEditor import cargar_contenido_res_notes, guardar_contenido_res_notes
from logica.T1.openBrowser import navegar_a_url

# --- IMPORTACIÓN DE CONSTANTES DESDE vista/config.py ---
from vista.config import *


class PanelLateral(ttk.Frame):
    """Contiene el menú de botones y entradas para las tareas."""

    # Usamos la constante importada
    ANCHO_CARACTERES_FIJO = ANCHO_CARACTERES_PANEL_LATERAL

    def __init__(self, parent, central_panel=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        # La referencia al PanelCentral es esencial para iniciar la carrera y acceder a sus métodos
        self.central_panel = central_panel

        self.configurar_estilos_locales(parent)

        # 1. Entrada superior (amarilla)
        self.entrada_superior = ttk.Entry(self, width=self.ANCHO_CARACTERES_FIJO, style='Yellow.TEntry')
        self.entrada_superior.pack(fill="x", pady=10, padx=5, ipady=3)
        self.entrada_superior.bind('<Return>', self.manejar_navegacion)

        # 2. Área de Extracción/Navegación
        acciones_extraccion = [
            ("Actualizar Recursos", self.manejar_extraccion_datos),
            ("Navegar", self.manejar_navegacion),
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
        # Ahora este marco se expandirá para ocupar todo el espacio restante.
        tk.Frame(self, height=1).pack(expand=True, fill="both")

        # 6. Panel de Notas - ELIMINADO: Se moverá a la pestaña Tareas del Panel Central.
        # self.crear_editor_res_notes() # <--- LÍNEA ELIMINADA

    # --- MÉTODOS DE LÓGICA / CONTROL ---

    def manejar_inicio_carrera_t2(self):
        """
        Llama al método 'manejar_inicio_carrera' del Panel Central.
        """
        if self.central_panel:
            print("Botón App2 presionado. Iniciando Carrera de Camellos en Panel Central...")
            # Llamada a la función expuesta por PanelCentral
            self.central_panel.manejar_inicio_carrera()

            # Opcional: Cambiar automáticamente a la pestaña Resultados
            if "Resultados" in self.central_panel.tabs:
                notebook = self.central_panel.tabs["Resultados"].winfo_toplevel().winfo_children()[0]
                if isinstance(notebook, ttk.Notebook):
                    # Asume que el Notebook es el primer widget hijo del frame principal
                    notebook.select(self.central_panel.tabs["Resultados"])
        else:
            messagebox.showerror("Error", "El Panel Central no está inicializado.")

    def manejar_navegacion(self, event=None):
        """
        Obtiene el texto de la entrada superior y llama a la función de navegación.
        """
        url = self.entrada_superior.get()
        if navegar_a_url(url):
            self.entrada_superior.delete(0, tk.END)

    # --- MÉTODOS DE NOTAS ELIMINADOS (Se moverán a PanelCentral) ---
    # def crear_editor_res_notes(self): ...
    # def cargar_res_notes(self, initial_load=False): ...
    # def guardar_res_notes(self): ...

    def manejar_extraccion_datos(self):
        """
        Llama a la lógica de actualización del gráfico de recursos en el panel central (actualización manual).
        """
        if self.central_panel:
            print("Activando actualización del gráfico de Recursos (Manual)...")
            self.central_panel.actualizar_recursos()
        else:
            messagebox.showerror("Error", "El Panel Central no está inicializado.")

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
            ttk.Button(frame_botones, text=texto_boton, command=comando, style='Green.TButton').pack(fill="x", pady=5)