# Módulo: vista/central_panel/view_alarmas.py

import tkinter as tk
from tkinter import ttk
from vista.config import *


# AlarmManager se importa en PanelCentral y se pasa como argumento


class AlarmaPanel(ttk.Frame):
    """
    Panel de la pestaña Alarmas (T4).
    Interfaz para programar y visualizar el tiempo restante de las alarmas.
    """

    def __init__(self, parent_notebook, root, alarm_manager, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root

        # Lógica de alarmas pasada desde el controlador
        self.alarm_manager = alarm_manager

        self.after_alarm_id = None
        self.alarm_hours_entry = None
        self.alarm_minutes_entry = None
        self.alarm_seconds_entry = None
        self.scrollable_frame = None

        self.crear_interfaz_alarmas(self)
        self.iniciar_actualizacion_alarmas()

    # -------------------------------------------------------------
    # 🔔 VISTA Y LÓGICA DE ALARMAS
    # -------------------------------------------------------------

    def crear_interfaz_alarmas(self, parent_frame):
        """Crea la interfaz para programar y visualizar alarmas (H:M:S)."""

        frame = ttk.Frame(parent_frame, padding=10, style='TFrame')
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Programar Nuevo Temporizador (H:M:S)", font=FUENTE_NEGOCIOS).pack(pady=(0, 10))

        # --- Controles de Nueva Alarma (H:M:S) ---
        frame_input = ttk.Frame(frame, style='TFrame')
        frame_input.pack(fill='x', pady=5)

        ttk.Label(frame_input, text="Horas:").pack(side='left', padx=(0, 2))
        self.alarm_hours_entry = ttk.Entry(frame_input, width=3);
        self.alarm_hours_entry.pack(side='left', padx=(0, 10))
        self.alarm_hours_entry.insert(0, "0")

        ttk.Label(frame_input, text="Minutos:").pack(side='left', padx=(0, 2))
        self.alarm_minutes_entry = ttk.Entry(frame_input, width=3);
        self.alarm_minutes_entry.pack(side='left', padx=(0, 10))
        self.alarm_minutes_entry.insert(0, "1")

        ttk.Label(frame_input, text="Segundos:").pack(side='left', padx=(0, 2))
        self.alarm_seconds_entry = ttk.Entry(frame_input, width=3);
        self.alarm_seconds_entry.pack(side='left', padx=(0, 15))
        self.alarm_seconds_entry.insert(0, "0")

        ttk.Button(frame_input, text="➕ Crear Alarma", command=self.manejar_nueva_alarma,
                   style='Action.TButton').pack(side='left')

        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=15)

        # --- Listado de Alarmas Activas ---
        ttk.Label(frame, text="Alarmas Activas (Tiempo Restante)", font=FUENTE_NEGOCIOS).pack(pady=(0, 5))

        self.alarm_list_frame = ttk.Frame(frame)
        self.alarm_list_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(self.alarm_list_frame, borderwidth=0, background=COLOR_BLANCO)
        vscroll = ttk.Scrollbar(self.alarm_list_frame, orient="vertical", command=canvas.yview)

        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=vscroll.set)

        canvas.pack(side="left", fill="both", expand=True)
        vscroll.pack(side="right", fill="y")

    def add_alarm_row(self, parent, alarm_data):
        """Añade una fila con la info de la alarma y su botón de cancelación."""
        row_frame = ttk.Frame(parent, padding=5, style='Note.TFrame')
        row_frame.pack(fill='x', padx=5, pady=2)

        total_s = alarm_data['total_seconds']
        h = total_s // 3600
        m = (total_s % 3600) // 60
        s = total_s % 60
        total_time_str = f"{h:02d}h:{m:02d}m:{s:02d}s"

        info_text = (f"[ID{alarm_data['id']}] {alarm_data['restante']} -> {alarm_data['nombre']} "
                     f"({total_time_str} total)")
        ttk.Label(row_frame, text=info_text, font=('Consolas', 10), style='Note.TLabel').pack(side='left', fill='x',
                                                                                              expand=True)

        ttk.Button(row_frame, text="❌ Cancelar", style='Danger.TButton', width=10,
                   command=lambda id=alarm_data['id']: self.manejar_cancelar_alarma(id)).pack(side='right')

    def manejar_nueva_alarma(self):
        """Captura los datos del formulario (H:M:S) y llama al AlarmManager."""
        try:
            hours = int(self.alarm_hours_entry.get() or 0)
            minutes = int(self.alarm_minutes_entry.get() or 0)
            seconds = int(self.alarm_seconds_entry.get() or 0)

            total_seconds = (hours * 3600) + (minutes * 60) + seconds

            if total_seconds <= 0:
                print("⚠️ El tiempo de alarma debe ser un número positivo (H:M:S > 0).")
                return

            self.alarm_manager.set_alarm(total_seconds)

            # Limpiar campos
            self.alarm_hours_entry.delete(0, tk.END);
            self.alarm_hours_entry.insert(0, "0")
            self.alarm_minutes_entry.delete(0, tk.END);
            self.alarm_minutes_entry.insert(0, "1")
            self.alarm_seconds_entry.delete(0, tk.END);
            self.alarm_seconds_entry.insert(0, "0")

            self.actualizar_lista_alarmas()

        except ValueError:
            print("⚠️ Por favor, introduce números enteros válidos para el tiempo.")

    def manejar_cancelar_alarma(self, alarm_id):
        """Cancela la alarma usando su ID."""
        if self.alarm_manager.cancel_alarm(alarm_id):
            self.actualizar_lista_alarmas()

    def actualizar_lista_alarmas(self):
        """Actualiza la visualización de las alarmas activas."""
        if not self.scrollable_frame:
            self.after_alarm_id = self.after(1000, self.actualizar_lista_alarmas)
            return

        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        active_alarms = self.alarm_manager.get_active_alarms()

        if not active_alarms:
            ttk.Label(self.scrollable_frame, text="--- No hay alarmas activas ---", font=('Consolas', 10),
                      foreground=COLOR_TEXTO).pack(padx=10, pady=10)

        for alarm in active_alarms:
            self.add_alarm_row(self.scrollable_frame, alarm)

        self.after_alarm_id = self.after(1000, self.actualizar_lista_alarmas)

    def iniciar_actualizacion_alarmas(self):
        """Inicia el ciclo de actualización de la lista de alarmas."""
        self.after_alarm_id = self.after(0, self.actualizar_lista_alarmas)

    def detener_actualizacion(self):
        """Detiene el ciclo de actualización."""
        if self.after_alarm_id:
            self.after_cancel(self.after_alarm_id)
            self.after_alarm_id = None
            print("Ciclo de actualización de alarmas detenido.")