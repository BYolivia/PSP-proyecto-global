# Módulo: vista/central_panel/view_enlaces.py

import tkinter as tk
from tkinter import ttk
from vista.config import *


class EnlacesPanel(ttk.Frame):
    """
    Panel de la pestaña Enlaces.
    Placeholder para la gestión de accesos directos y enlaces rápidos.
    """

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.crear_interfaz_enlaces(self)

    # -------------------------------------------------------------
    # 🔗 VISTA PLACEHOLDER
    # -------------------------------------------------------------

    def crear_interfaz_enlaces(self, parent_frame):
        """Crea un mensaje placeholder para la pestaña de Enlaces."""
        frame = ttk.Frame(parent_frame, padding=20, style='TFrame')
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Gestor de Enlaces Rápidos 🔗",
                  font=FUENTE_TITULO).pack(pady=(10, 20))

        ttk.Label(frame, text="🛠️ ESTA FUNCIÓN ESTÁ EN DESARROLLO 🛠️",
                  font=FUENTE_NEGOCIOS, foreground=COLOR_ACCION).pack(pady=10)

        ttk.Label(frame,
                  text="Utilice este panel para almacenar y acceder rápidamente a URLs o recursos externos importantes para sus tareas.",
                  wraplength=500, justify=tk.CENTER).pack(pady=5)