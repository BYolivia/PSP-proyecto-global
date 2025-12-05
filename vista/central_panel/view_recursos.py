# Módulo: vista/central_panel/view_recursos.py

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # <-- ¡IMPORTACIÓN NECESARIA!
from logica.T1.graficos import crear_grafico_recursos, actualizar_historial_datos
from vista.config import *  # Asumiendo que las constantes de estilo/fondo están aquí


class RecursosPanel(ttk.Frame):
    """
    Panel de la pestaña Recursos (T1).
    Muestra el gráfico de Matplotlib con el consumo de recursos de red.
    """

    # NOTA: Los parámetros 'canvas' y 'canvas_widget' ya no son necesarios
    # en el constructor, pero los mantenemos para no romper el flujo de PanelCentral.
    def __init__(self, parent_notebook, figure, canvas, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.figure = figure
        # Aseguramos que el frame se expanda para llenar la pestaña
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = None  # Lo crearemos aquí
        self.canvas_widget = None  # Lo crearemos aquí
        self.grafico_frame = None

        self.crear_interfaz_recursos(self)

        # Estado inicial del gráfico
        crear_grafico_recursos(self.figure)

        # Después de la creación, nos aseguramos de que PanelCentral obtenga las referencias
        # que espera si las necesita.

    def crear_interfaz_recursos(self, parent_frame):
        """Prepara el Frame para contener el gráfico de Matplotlib."""

        # 1. Crear el Frame que contendrá el Canvas (contenedor interno)
        self.grafico_frame = ttk.Frame(parent_frame, style='TFrame')
        self.grafico_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.grafico_frame.grid_rowconfigure(0, weight=1)
        self.grafico_frame.grid_columnconfigure(0, weight=1)

        # 2. 🎯 CREAR Y UBICAR EL CANVAS DENTRO DEL FRAME (SOLUCIÓN DEL PROBLEMA)
        # El canvas debe crearse AQUÍ y usar 'self.grafico_frame' como master
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.grafico_frame)
        self.canvas_widget = self.canvas.get_tk_widget()

        # Usamos .grid() para llenar el frame_contenedor
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

        # -------------------------------------------------------------

    # 📞 MÉTODOS DE CONEXIÓN (Llamados por PanelCentral)
    # -------------------------------------------------------------

    def actualizar_datos(self, net_in, net_out):
        """Recibe los datos del monitor de red y actualiza el historial."""
        actualizar_historial_datos(net_in, net_out)

    def dibujar_grafico(self):
        """Llama a la función de redibujo del gráfico."""
        if self.figure:
            crear_grafico_recursos(self.figure)