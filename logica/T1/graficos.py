# Módulo: logica/T1/graficos.py

import matplotlib.pyplot as plt
import numpy as np

# --- Datos Históricos ---
MAX_PUNTOS = 60  # Mantener los últimos 60 puntos (segundos)
historial_cpu = []
historial_ram = []
historial_net_in = []
historial_net_out = []


def actualizar_historial_datos(net_in_kb, net_out_kb, cpu_percent, ram_percent):
    """
    Recopila los datos actuales de CPU, RAM y Red pasados como argumento a sus historiales.
    """
    # 1. Añadir CPU y gestionar la longitud
    historial_cpu.append(cpu_percent)
    if len(historial_cpu) > MAX_PUNTOS:
        historial_cpu.pop(0)

    # 2. Añadir RAM y gestionar la longitud
    historial_ram.append(ram_percent)
    if len(historial_ram) > MAX_PUNTOS:
        historial_ram.pop(0)

    # 3. Añadir Red y gestionar la longitud
    historial_net_in.append(net_in_kb)
    historial_net_out.append(net_out_kb)

    if len(historial_net_in) > MAX_PUNTOS:
        historial_net_in.pop(0)
        historial_net_out.pop(0)


def crear_grafico_recursos(figure):
    """
    Crea o actualiza un gráfico que muestre la evolución de CPU, RAM y Red.
    """
    # Limpiar la figura antes de dibujar (CRUCIAL para redibujo)
    figure.clear()

    # Configuramos el fondo de la figura para que coincida con el estilo de la aplicación
    figure.patch.set_facecolor('#f9f9f9')

    # --- Configuración General del Layout ---
    # 3 filas para CPU, RAM, Red con espaciado vertical
    gs = figure.add_gridspec(3, 1, hspace=0.6, top=0.95, bottom=0.05, left=0.1, right=0.95)

    # --- Función Helper para el estilo ---
    def configurar_ejes_historial(ax, title, color, data, y_limit=100, y_ticks=None):
        ax.set_facecolor('#f0f0f0')  # Fondo del área de dibujo
        ax.set_title(title, fontsize=9, loc='left', pad=10)
        ax.set_ylim(0, y_limit)

        if y_ticks:
            ax.set_yticks(y_ticks)

        ax.tick_params(axis='x', labelbottom=False, length=0)
        ax.tick_params(axis='y', labelsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.grid(axis='y', linestyle='--', alpha=0.5)

        # Dibujar línea y relleno
        ax.plot(data, color=color, linewidth=1.5)
        ax.fill_between(range(len(data)), data, color=color, alpha=0.3)

    # --- 1. Gráfico de CPU ---
    ax_cpu = figure.add_subplot(gs[0, 0])
    configurar_ejes_historial(
        ax_cpu, 'Uso de CPU (%) - Ultimo: {:.1f}%'.format(historial_cpu[-1] if historial_cpu else 0),
        'red', historial_cpu, 100, [0, 50, 100]
    )

    # --- 2. Gráfico de RAM ---
    ax_ram = figure.add_subplot(gs[1, 0])
    configurar_ejes_historial(
        ax_ram, 'Uso de RAM (%) - Ultimo: {:.1f}%'.format(historial_ram[-1] if historial_ram else 0),
        'cyan', historial_ram, 100, [0, 50, 100]
    )

    # --- 3. Gráfico de Red ---
    ax_net = figure.add_subplot(gs[2, 0])

    # Calcular el límite Y dinámico para la red (ajusta el gráfico al tráfico real)
    max_in = max(historial_net_in) if historial_net_in else 0
    max_out = max(historial_net_out) if historial_net_out else 0
    y_limit_net = max(max_in, max_out) * 1.2  # 20% de margen
    y_limit_net = max(y_limit_net, 10)  # Mínimo de 10 KB/s

    # Sobreescribir las líneas para mostrar IN y OUT
    ax_net.clear()  # Limpiamos para redibujar con las dos líneas
    ax_net.set_ylim(0, y_limit_net)

    # Dibujar Entrada (Recibido)
    ax_net.plot(historial_net_in, label='IN (Recibido)', color='green', linewidth=1.5)
    ax_net.fill_between(range(len(historial_net_in)), historial_net_in, color='green', alpha=0.2)

    # Dibujar Salida (Enviado)
    ax_net.plot(historial_net_out, label='OUT (Enviado)', color='yellow', linewidth=1.5)
    ax_net.fill_between(range(len(historial_net_out)), historial_net_out, color='yellow', alpha=0.2)

    # Reconfigurar los títulos y estilos después de limpiar el eje
    configurar_ejes_historial(
        ax_net,
        'Tráfico de Red (KB/s) - IN: {:.1f} KB/s | OUT: {:.1f} KB/s'.format(
            historial_net_in[-1] if historial_net_in else 0,
            historial_net_out[-1] if historial_net_out else 0
        ),
        'gray', [0] * MAX_PUNTOS,
        y_limit_net,
        [0, round(y_limit_net * 0.5, 1), round(y_limit_net * 0.9, 1)]
    )

    figure.tight_layout()