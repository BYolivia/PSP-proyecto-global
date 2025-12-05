# Módulo: logica/T2/alarm.py

import tkinter as tk
from datetime import datetime
import os
import sys

try:
    from logica.T2.musicReproductor import MusicReproductor
except ImportError:
    class MusicReproductor:
        def __init__(self, *args, **kwargs): pass

        def ajustar_volumen(self, valor): pass

        def cargar_y_reproducir(self, url): print(f"🎶 SIMULANDO PLAY: {url}")

        def detener(self): print("🔇 SIMULANDO STOP")


class AlarmManager:
    """
    Gestiona la creación, seguimiento y disparo de múltiples alarmas (temporizadores).
    """

    def __init__(self, root, trigger_callback):
        self.root = root
        self.active_alarms = {}
        self.next_id = 1
        self.trigger_callback = trigger_callback

        self.alarm_sound_player = MusicReproductor()

        self.ALARM_SOUND_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'res', 'alarm.mp3')

    # === MODIFICACIÓN CLAVE: Acepta total_seconds en lugar de minutes ===
    def set_alarm(self, total_seconds):
        """
        Programa una nueva alarma para sonar después de un número de segundos.

        :param total_seconds: Número de segundos hasta que suena la alarma.
        :return: ID único de la alarma.
        """
        if total_seconds <= 0:
            raise ValueError("El tiempo de alarma debe ser positivo.")

        alarm_id = self.next_id
        self.next_id += 1

        ms_delay = total_seconds * 1000
        ms_delay_int = int(ms_delay)

        tiempo_disparo_ts = datetime.now().timestamp() + total_seconds
        tiempo_disparo_dt = datetime.fromtimestamp(tiempo_disparo_ts)

        name = f"⏰ {tiempo_disparo_dt.strftime('%H:%M:%S')}"

        alarm_data = {
            'nombre': name,
            'total_seconds': total_seconds,  # Almacenamos el tiempo total en segundos
            'tiempo_creacion': datetime.now(),
            'tiempo_disparo': tiempo_disparo_ts,
            'after_id': None,
            'sonada': False
        }

        after_id = self.root.after(ms_delay_int, lambda: self._trigger_alarm(alarm_id))

        alarm_data['after_id'] = after_id
        self.active_alarms[alarm_id] = alarm_data

        print(f"🔔 Alarma '{name}' ({alarm_id}) programada para sonar en {total_seconds} segundos.")
        return alarm_id

    def _trigger_alarm(self, alarm_id):
        # ... (código sin cambios aquí) ...
        if alarm_id in self.active_alarms:
            alarm = self.active_alarms[alarm_id]

            print(f"🚨 ¡ALARMA! La alarma '{alarm['nombre']}' ({alarm_id}) ha sonado.")

            alarm['sonada'] = True

            self.alarm_sound_player.cargar_y_reproducir(self.ALARM_SOUND_PATH)

            self.trigger_callback(alarm['nombre'], alarm_id)

    def stop_alarm_sound(self):
        self.alarm_sound_player.detener()

    def cancel_alarm(self, alarm_id):
        # ... (código sin cambios aquí) ...
        if alarm_id in self.active_alarms:
            alarm = self.active_alarms[alarm_id]

            if not alarm['sonada'] and alarm['after_id']:
                self.root.after_cancel(alarm['after_id'])
                print(f"❌ Alarma '{alarm['nombre']}' ({alarm_id}) cancelada.")

            del self.active_alarms[alarm_id]
            return True
        return False

    def get_active_alarms(self):
        """
        Retorna una lista de las alarmas activas, incluyendo el tiempo restante.
        """
        alarms_to_show = []
        current_time = datetime.now().timestamp()

        for alarm_id, alarm in list(self.active_alarms.items()):
            if not alarm['sonada']:
                time_diff = alarm['tiempo_disparo'] - current_time

                if time_diff > 0:
                    remaining_sec = int(time_diff)

                    hours = remaining_sec // 3600
                    minutes = (remaining_sec % 3600) // 60
                    seconds = remaining_sec % 60

                    remaining_str = f"{hours:02d}h:{minutes:02d}m:{seconds:02d}s"

                    alarms_to_show.append({
                        'id': alarm_id,
                        'nombre': alarm['nombre'],
                        'restante': remaining_str,
                        'total_seconds': alarm['total_seconds']  # Usar total_seconds
                    })

        return sorted(alarms_to_show, key=lambda x: x['restante'])