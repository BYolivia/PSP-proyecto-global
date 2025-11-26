import tkinter as tk
from tkinter import ttk


class PanelLateral(ttk.Frame):
    """Contiene el menú de botones y entradas para las tareas de T1."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.pack(fill="y", padx=5, pady=5)

        # Entrada superior (amarilla)
        ttk.Entry(self, width=25, style='Yellow.TEntry').pack(fill="x", pady=10, padx=5)

        # 1. Área de Extracción/Navegación
        self.crear_seccion(
            parent_frame=self,
            titulo="",
            botones=["Extraer datos", "Navegar", "Buscar API Google"]
        )

        # 2. Área de Aplicaciones
        self.crear_seccion(
            parent_frame=self,
            titulo="Aplicaciones",
            botones=["Visual Code", "App2", "App3"]
        )

        # 3. Área de Procesos Batch
        self.crear_seccion(
            parent_frame=self,
            titulo="Procesos batch",
            botones=["Copias de seguridad"]
        )

        # Espaciador para empujar los elementos inferiores si los hubiera
        tk.Frame(self, height=1).pack(expand=True, fill="both")

    def crear_seccion(self, parent_frame, titulo, botones):
        """Función helper para crear secciones de etiquetas y botones."""
        if titulo:
            ttk.Label(parent_frame, text=titulo).pack(fill="x", pady=(10, 0), padx=5)

        frame_botones = ttk.LabelFrame(parent_frame, text="")
        frame_botones.pack(fill="x", pady=5, padx=5)

        for texto_boton in botones:
            # Todos los botones usan el estilo 'Green.TButton' para simular el color
            ttk.Button(frame_botones, text=texto_boton, style='Green.TButton').pack(fill="x", pady=5)