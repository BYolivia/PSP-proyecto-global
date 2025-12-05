# Módulo: vista/central_panel/view_scrapping.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from vista.config import *
from datetime import datetime


class NavegadorPanel(ttk.Frame):
    """
    Panel de visualización de contenido web (Scraping).
    Contiene un widget Text para mostrar los resultados de las extracciones.
    """

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.web_text_viewer = None
        self.crear_interfaz_navegador(self)

    # -------------------------------------------------------------
    # 🌐 VISTA DE NAVEGADOR
    # -------------------------------------------------------------

    def crear_interfaz_navegador(self, parent_frame):
        """Crea el área donde se mostrará el resultado del scraping."""

        frame = ttk.Frame(parent_frame, padding=15, style='TFrame')
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Visualizador de Contenido Web (Scraping)", font=FUENTE_TITULO).pack(pady=(0, 10),
                                                                                                   anchor="w")
        ttk.Label(frame, text="El resultado de la extracción de datos se carga aquí.",
                  font=FUENTE_NEGOCIOS).pack(pady=(0, 15), anchor="w")

        self.web_text_viewer = tk.Text(
            frame,
            height=20,
            wrap="word",
            bg=COLOR_BLANCO,
            relief="solid",
            borderwidth=1,
            font=FUENTE_MONO
        )
        self.web_text_viewer.pack(fill="both", expand=True, pady=(0, 10))

    # -------------------------------------------------------------
    # 📞 MÉTODO DE CONEXIÓN
    # -------------------------------------------------------------

    def cargar_contenido_web(self, titulo, contenido):
        """Carga el contenido extraído (scraping) al widget de texto."""
        if not self.web_text_viewer:
            messagebox.showerror("Error", "El visualizador web no está inicializado.")
            return

        self.web_text_viewer.delete("1.0", tk.END)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        header = f"--- RESULTADO DE EXTRACCIÓN: {titulo.upper()} ({timestamp}) ---\n\n"
        self.web_text_viewer.insert(tk.END, header)
        self.web_text_viewer.insert(tk.END, contenido)
        self.web_text_viewer.see("1.0")