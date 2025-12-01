# Módulo: logica/T1/graficos.py

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

COLOR_PRINCIPAL = '#0078d4'
COLOR_RAM = '#4CAF50'


def crear_grafico_recursos(parent_frame: tk.Frame, datos: dict):
    """
    Genera un gráfico de matplotlib que muestra el uso de CPU y RAM,
    e integra este gráfico en un Frame de Tkinter.
    """

    # Limpiamos el frame padre para redibujar
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 1. Crear la figura (2 subplots)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4))
    fig.patch.set_facecolor('white')

    # --- GRÁFICO 1: USO DE CPU (Gráfico de Barras) ---
    core_labels = [f'Núcleo {i + 1}' for i in range(len(datos['cpu_cores']))]
    ax1.bar(core_labels, datos['cpu_cores'], color=COLOR_PRINCIPAL)
    ax1.axhline(datos['cpu_total'], color='red', linestyle='--', linewidth=1, label=f'Total: {datos["cpu_total"]}%')

    ax1.set_title(f'Uso de CPU por Núcleo (Total: {datos["cpu_total"]}%)', fontsize=10)
    ax1.set_ylabel('Uso (%)')
    ax1.set_ylim(0, 100)
    ax1.tick_params(axis='x', rotation=45)
    ax1.legend(loc='upper right')

    # --- GRÁFICO 2: USO DE RAM (Gráfico Circular/Pie) ---
    labels = ['Usada', 'Libre']
    sizes = [datos['ram_percent'], 100 - datos['ram_percent']]
    colors = [COLOR_RAM, '#d3d3d3']
    explode = (0.1, 0)

    ax2.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=False, startangle=90)
    ax2.axis('equal')

    ram_title = f'RAM Total: {datos["ram_total_gb"]} GB\nUso: {datos["ram_uso_gb"]} GB'
    ax2.set_title(ram_title, fontsize=10)

    # 3. Integración en Tkinter
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas_widget = canvas.get_tk_widget()
    fig.tight_layout(pad=3.0)
    canvas_widget.pack(fill=tk.BOTH, expand=True)

    return canvas_widget