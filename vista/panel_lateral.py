import tkinter as tk
from tkinter import ttk
# Importación de la lógica específica para abrir VS Code
from logica.T1.runVScode import abrir_vscode
# Importación de las acciones generales (placeholders y futuras funciones)
from logica.controlador import accion_placeholder, obtener_datos_sistema


class PanelLateral(ttk.Frame):
    """Contiene el menú de botones y entradas para las tareas de T1."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill="y", padx=5, pady=5)

        self.configurar_estilos_locales(parent)  # Asegura que los estilos funcionen

        # Entrada superior (amarilla)
        ttk.Entry(self, width=25, style='Yellow.TEntry').pack(fill="x", pady=10, padx=5, ipady=3)

        # 1. Área de Extracción/Navegación
        acciones_extraccion = [
            # T1.3 - Conectamos el botón de extracción a la función de obtención de datos del sistema
            ("Extraer datos", lambda: obtener_datos_sistema()),
            ("Navegar", lambda: accion_placeholder("Navegar")),
            ("Buscar API Google", lambda: accion_placeholder("Buscar API Google"))
        ]
        self.crear_seccion(self, titulo="", acciones=acciones_extraccion)

        # 2. Área de Aplicaciones
        acciones_aplicaciones = [
            # CONEXIÓN: Usa la función específica abrir_vscode
            ("Visual Code", abrir_vscode),
            ("App2", lambda: accion_placeholder("App2")),
            ("App3", lambda: accion_placeholder("App3"))
        ]
        self.crear_seccion(self, titulo="Aplicaciones", acciones=acciones_aplicaciones)

        # 3. Área de Procesos Batch
        acciones_batch = [
            ("Copias de seguridad", lambda: accion_placeholder("Copias de seguridad"))
        ]
        self.crear_seccion(self, titulo="Procesos batch", acciones=acciones_batch)

        # Espaciador para empujar los elementos inferiores si los hubiera
        # CORRECCIÓN: Eliminamos el argumento 'bg' problemático y permitimos la herencia de color.
        tk.Frame(self, height=1).pack(expand=True, fill="both")

    def configurar_estilos_locales(self, parent):
        """Configura estilos que deberían estar en la ventana principal, o crea placeholders."""
        style = ttk.Style(parent)
        # Estilo de la entrada amarilla
        style.configure('Yellow.TEntry',
                        fieldbackground='#fff8e1',
                        foreground='#333333',
                        padding=[5, 5],
                        relief='solid',
                        borderwidth=1)

        # Estilo de los botones (Verde)
        style.configure('Green.TButton',
                        background='#4CAF50',
                        foreground='white',
                        font=('Arial', 10, 'bold'),
                        relief='flat',
                        padding=[10, 5])
        style.map('Green.TButton', background=[('active', '#388E3C'), ('pressed', '#1B5E20')])

    def crear_seccion(self, parent_frame, titulo, acciones):
        """
        Función helper para crear secciones de etiquetas y botones.
        'acciones' es una lista de tuplas: (texto_boton, comando_a_ejecutar)
        """
        if titulo:
            ttk.Label(parent_frame, text=titulo, font=('Arial', 11, 'bold')).pack(fill="x", pady=(10, 0), padx=5)

        frame_botones = ttk.Frame(parent_frame, style='TFrame')  # Usando TFrame para el contenedor de botones
        frame_botones.pack(fill="x", pady=5, padx=5)

        for texto_boton, comando in acciones:
            # Conexión del botón:
            ttk.Button(frame_botones, text=texto_boton, command=comando, style='Green.TButton').pack(fill="x", pady=5)