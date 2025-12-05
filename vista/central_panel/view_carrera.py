# Módulo: vista/central_panel/view_carrera.py

import tkinter as tk
from tkinter import ttk
import random
from logica.T2.carreraCamellos import (
    iniciar_carrera,
    obtener_estado_carrera,
    RESULTADO_ULTIMO
)
from vista.config import *


class CarreraPanel(ttk.Frame):
    """
    Panel de la pestaña Carrera (T2).
    Controla la simulación y visualización de la carrera de camellos.
    """

    INTERVALO_CARRERA_MS = 200

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.after_carrera_id = None
        self.camellos = []
        self.progreso_labels = {}
        self.frame_progreso = None
        self.carrera_estado_label = None
        self.carrera_info_label = None

        self.crear_interfaz_carrera(self)
        self.iniciar_actualizacion_carrera() # Carga el resultado guardado al inicio

    # -------------------------------------------------------------
    # 🐪 VISTA DE CARRERA
    # -------------------------------------------------------------

    def crear_interfaz_carrera(self, parent_frame):
        """Crea los controles y la visualización de la Carrera de Camellos."""
        frame_controles = ttk.Frame(parent_frame, style='TFrame', padding=10)
        frame_controles.pack(fill="x")

        ttk.Label(frame_controles, text="Resultado de Carrera de Camellos (T2 Sincronización)",
                  style='TLabel', font=FUENTE_NEGOCIOS).pack(side="left", padx=5)

        self.carrera_estado_label = ttk.Label(frame_controles, text="Estado.", style='TLabel', font=FUENTE_NEGOCIOS)
        self.carrera_estado_label.pack(side="right", padx=10)

        self.frame_progreso = ttk.Frame(parent_frame, style='TFrame', padding=10)
        self.frame_progreso.pack(fill="both", expand=True)

        ttk.Label(self.frame_progreso,
                  text="Presiona el botón 'App2 (T2-Carrera 🏁)' en el panel lateral para iniciar la simulación de hilos.",
                  style='TLabel').pack(pady=20)

    def crear_visualizacion_carrera(self, nombres):
        """Prepara el layout de la carrera (barras de progreso)."""
        for widget in self.frame_progreso.winfo_children():
            widget.destroy()

        for i, nombre in enumerate(nombres):
            ttk.Label(self.frame_progreso, text=f"{nombre}: ", style='TLabel', font=FUENTE_NEGOCIOS).grid(row=i,
                                                                                                          column=0,
                                                                                                          sticky="w")

            label_progreso = ttk.Label(self.frame_progreso, text="[Esperando...]", style='TLabel',
                                       foreground=COLOR_TEXTO)
            label_progreso.grid(row=i, column=1, sticky="w", padx=10)
            self.progreso_labels[nombre] = label_progreso

            label_posicion = ttk.Label(self.frame_progreso, text="", style='TLabel')
            label_posicion.grid(row=i, column=2, sticky="w")
            self.progreso_labels[f'{nombre}_pos'] = label_posicion

        self.carrera_info_label = ttk.Label(self.frame_progreso, text="", style='TLabel', font=FUENTE_NEGOCIOS)
        self.carrera_info_label.grid(row=len(nombres), column=0, columnspan=3, sticky="w", pady=(10, 0))

    # -------------------------------------------------------------
    # ⚙️ CONTROL DE ESTADO DE CARRERA
    # -------------------------------------------------------------

    def manejar_inicio_carrera(self):
        """Inicia una nueva carrera de camellos con un número aleatorio de participantes."""
        if self.camellos and any(c.is_alive() for c in self.camellos):
            self.carrera_estado_label.config(text="⚠️ Ya hay una carrera en curso.")
            return

        print("Iniciando Carrera de Camellos con número variable de participantes...")

        num_camellos = random.randint(10, 20)
        nombres = [f"Camello {i + 1}" for i in range(num_camellos)]

        self.progreso_labels = {}
        self.camellos = iniciar_carrera(nombres)
        self.carrera_estado_label.config(text=f"¡Carrera en marcha! 💨 ({num_camellos} participantes)")
        self.crear_visualizacion_carrera(nombres)
        self.iniciar_actualizacion_carrera()

    def mostrar_progreso_activo(self, datos_activos):
        """Actualiza la visualización de la carrera mientras los hilos están corriendo."""
        if not datos_activos['camellos']:
            return

        for estado in datos_activos['camellos']:
            nombre = estado['nombre']
            progreso = estado['progreso']
            etiqueta_progreso = self.progreso_labels.get(nombre)
            etiqueta_posicion = self.progreso_labels.get(f'{nombre}_pos')

            if etiqueta_progreso:
                barra = "█" * (progreso // 2)
                texto_progreso = f"[{barra}{' ' * (25 - len(barra))}] ({progreso}/50) Estado: {estado['estado']}"
                etiqueta_progreso.config(text=texto_progreso)

            if etiqueta_posicion and estado['posicion']:
                etiqueta_posicion.config(text=f"POS: {estado['posicion']} 🏆", foreground=COLOR_ACCION)

        self.carrera_estado_label.config(text="Carrera en curso...")
        self.carrera_info_label.config(text="")

    def mostrar_resultado_final(self, resultado_final):
        """Muestra el resultado final persistente de la carrera."""
        nombres_finales = [c['nombre'] for c in resultado_final['camellos']]
        if not self.progreso_labels or any(n not in self.progreso_labels for n in nombres_finales):
            self.crear_visualizacion_carrera(nombres_finales)

        camellos_ordenados = sorted(resultado_final['camellos'], key=lambda x: x['posicion'])

        for estado in camellos_ordenados:
            nombre = estado['nombre']
            etiqueta_progreso = self.progreso_labels.get(nombre)
            etiqueta_posicion = self.progreso_labels.get(f'{nombre}_pos')

            if etiqueta_progreso:
                barra = "█" * (estado['progreso'] // 2)
                texto_progreso = f"[{barra}{' ' * (25 - len(barra))}] (50/50) Estado: Meta"
                etiqueta_progreso.config(text=texto_progreso)

            if etiqueta_posicion:
                etiqueta_posicion.config(text=f"POS: {estado['posicion']} {'🏆' if estado['posicion'] == 1 else ''}",
                                         foreground=COLOR_ACCION)

        self.carrera_estado_label.config(text="✅ Carrera Terminada.")
        self.carrera_info_label.config(text=f"¡El ganador es: {resultado_final['ganador']}!",
                                       font=FUENTE_TITULO, foreground=COLOR_EXITO)

    def actualizar_carrera(self):
        """Ciclo de actualización visual."""
        estado = obtener_estado_carrera(self.camellos)

        if estado['tipo'] == 'final':
            self.mostrar_resultado_final(estado['datos'])
            self.detener_actualizacion_carrera()
            return

        elif estado['tipo'] == 'activo':
            self.mostrar_progreso_activo(estado['datos'])

        self.after_carrera_id = self.after(self.INTERVALO_CARRERA_MS, self.actualizar_carrera)

    def iniciar_actualizacion_carrera(self):
        """Inicia el ciclo de actualización visual (o carga el resultado guardado al inicio)."""
        self.detener_actualizacion_carrera()

        # Si hay un resultado final guardado y no hay carrera activa, mostrarlo.
        if RESULTADO_ULTIMO and not RESULTADO_ULTIMO.get('activa', True) and self.frame_progreso:
            self.mostrar_resultado_final(RESULTADO_ULTIMO)
        else:
            self.carrera_estado_label.config(text="Carrera lista para empezar.")
            self.after_carrera_id = self.after(0, self.actualizar_carrera)

    def detener_actualizacion_carrera(self):
        """Detiene el ciclo de actualización visual de la carrera."""
        if self.after_carrera_id:
            self.after_cancel(self.after_carrera_id)
            self.after_carrera_id = None
            print("Ciclo de actualización de carrera detenido.")