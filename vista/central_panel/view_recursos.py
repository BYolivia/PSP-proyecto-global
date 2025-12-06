# Módulo: vista/central_panel/view_recursos.py

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from logica.T1.graficos import crear_grafico_recursos, actualizar_historial_datos
from vista.config import *


class RecursosPanel(ttk.Frame):
    """
    Panel de la pestaña Recursos (T1).
    Muestra el gráfico de Matplotlib con el consumo de recursos de red.
    """

    def __init__(self, parent_notebook, figure, canvas, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.figure = figure
        # Asegura que el frame del panel se expande
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas = None
        self.canvas_widget = None
        self.grafico_frame = None

        self.crear_interfaz_recursos(self)

        # Estado inicial del gráfico (limpia y configura la figura)
        crear_grafico_recursos(self.figure)

        # ✅ DIBUJO INICIAL: Asegura que el gráfico vacío se muestre inmediatamente.
        if self.canvas:
            self.canvas.draw()

    def crear_interfaz_recursos(self, parent_frame):
        """Prepara el Frame para contener el gráfico de Matplotlib."""
        self.grafico_frame = ttk.Frame(parent_frame, style='TFrame')
        # Ubicar el frame contenedor del gráfico
        self.grafico_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        # Asegura que el contenido del gráfico_frame se expande
        self.grafico_frame.grid_rowconfigure(0, weight=1)
        self.grafico_frame.grid_columnconfigure(0, weight=1)

        # CREAR Y UBICAR EL CANVAS
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.grafico_frame)
        self.canvas_widget = self.canvas.get_tk_widget()

        # ✅ CRÍTICO: El widget del canvas debe expandirse para llenar el gráfico_frame
        self.canvas_widget.grid(row=0, column=0, sticky="nsew")

    # 📞 MÉTODOS DE CONEXIÓN (Llamados por PanelCentral)
    # -------------------------------------------------------------

    def actualizar_datos(self, net_in, net_out, cpu_percent, ram_percent):
        """Recibe los datos del monitor y actualiza el historial de datos en la lógica."""
        # Recibe los 4 datos validados por la prueba de terminal
        actualizar_historial_datos(net_in, net_out, cpu_percent, ram_percent)

    def dibujar_grafico(self):
        """Llama a la función de redibujo del gráfico y fuerza la actualización del canvas."""
        if self.figure:
            # 1. Modifica la figura usando los datos del historial
            crear_grafico_recursos(self.figure)

            # 2. ✅ FORZAR EL REDIBUJADO DE TKINTER
            if self.canvas:
                self.canvas.draw()