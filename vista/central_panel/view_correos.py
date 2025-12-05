# Módulo: vista/central_panel/view_correos.py

import tkinter as tk
from tkinter import ttk
from vista.config import *


class CorreosPanel(ttk.Frame):
    """
    Panel de la pestaña Correos.
    Placeholder para la gestión de correos electrónicos y notificaciones.
    """

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.crear_interfaz_correos(self)

    # -------------------------------------------------------------
    # 📧 VISTA PLACEHOLDER
    # -------------------------------------------------------------

    def crear_interfaz_correos(self, parent_frame):
        """Crea un mensaje placeholder para la pestaña de Correos."""
        frame = ttk.Frame(parent_frame, padding=20, style='TFrame')
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Gestor de Correos Electrónicos 📧",
                  font=FUENTE_TITULO).pack(pady=(10, 20))

        ttk.Label(frame, text="🛠️ ESTA FUNCIÓN ESTÁ EN DESARROLLO 🛠️",
                  font=FUENTE_NEGOCIOS, foreground=COLOR_ACCION).pack(pady=10)

        ttk.Label(frame,
                  text="Aquí se integrará la visualización y gestión de emails o un sistema de notificaciones por correo.",
                  wraplength=500, justify=tk.CENTER).pack(pady=5)