# Módulo: logica/T2/musicReproductor.py

import vlc
import threading
import os
import sys


# --- BLOQUE DE CÓDIGO OPCIONAL PARA SOLUCIÓN DE ERRORES DE RUTA DE VLC ---
# Si al ejecutar el programa obtienes un error de "ImportError: DLL load failed"
# o similar con 'vlc', DESCOMENTA el siguiente bloque y AJUSTA la ruta de vlc_path.
# Esto ayuda a que Python encuentre las librerías principales de VLC.
#
# if sys.platform.startswith('win'):
#     # RUTA DE EJEMPLO PARA WINDOWS (AJUSTA según tu instalación)
#     vlc_path = r"C:\Program Files\VideoLAN\VLC"
#     if vlc_path not in os.environ.get('PATH', ''):
#         os.environ['PATH'] += os.pathsep + vlc_path
# -------------------------------------------------------------------------

class MusicReproductor:
    """
    Gestiona la reproducción de streams de radio usando la librería python-vlc.
    """

    def __init__(self, initial_volume=50.0):
        """Inicializa la instancia de VLC y el reproductor."""

        # Instancia de VLC y objeto Reproductor
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.current_media = None

        # 🔑 Variables de estado/control
        self._current_url = None  # Guarda la última URL cargada
        self._is_playing = False  # Indica si se está reproduciendo activamente (no pausado)

        # Configurar volumen inicial
        self.set_volumen(initial_volume)  # 🔑 Renombrado a set_volumen
        print(f"🎵 [VLC] Reproductor inicializado. Volumen: {self.get_volumen()}")

    # -------------------------------------------------------------
    # 🔑 MÉTODOS REQUERIDOS POR LA VISTA
    # -------------------------------------------------------------

    def get_volumen(self):
        """
        [REQUERIDO] Devuelve el nivel de volumen actual (0-100).
        Este método es esencial para inicializar el slider de la interfaz.
        """
        # VLC proporciona el volumen actual directamente
        return self.player.audio_get_volume()

    def set_volumen(self, valor_porcentual):
        """
        [REQUERIDO - Antes ajustar_volumen] Ajusta el volumen del reproductor (0 a 100).
        """
        volumen_int = int(max(0, min(100, valor_porcentual)))
        self.player.audio_set_volume(volumen_int)

    def esta_reproduciendo(self):
        """
        [REQUERIDO] Devuelve True si el reproductor está en estado Playing o Paused
        y nosotros lo consideramos 'activo'.
        Usaremos el estado interno _is_playing para indicar el estado activo/pausado.
        """
        return self._is_playing

    def continuar(self):
        """
        [REQUERIDO] Reanuda la reproducción si está pausada, o inicia el stream si está detenido.
        Devuelve True si la reproducción se inició/continuó.
        """
        # Si está pausado, reanuda
        if self.player.get_state() == vlc.State.Paused:
            self.player.play()
            self._is_playing = True
            print("▶️ [VLC] Reproducción reanudada.")
            return True

        # Si está detenido y hay un medio cargado, intenta reproducir
        elif self.player.get_state() == vlc.State.Stopped and self.current_media:
            self.player.play()
            self._is_playing = True
            print("▶️ [VLC] Reproducción iniciada desde stream cargado.")
            return True

        # Si no hay medio cargado, no puede continuar
        elif not self.current_media:
            print("ℹ️ [VLC] No hay stream cargado para continuar.")
            return False

        # Si ya está reproduciendo, lo ignoramos
        return True

    # -------------------------------------------------------------
    # MÉTODOS DE CONTROL DE VLC
    # -------------------------------------------------------------

    def cargar_y_reproducir(self, url_stream):
        """
        Carga una nueva URL de stream y comienza la reproducción.
        """
        if not url_stream:
            print("❌ [VLC] URL del stream vacía.")
            return False, "URL del stream vacía."

        print(f"🔄 [VLC] Intentando cargar y reproducir: {url_stream}")

        # Detener la reproducción anterior
        self.player.stop()

        self.current_media = self.instance.media_new(url_stream)
        self.player.set_media(self.current_media)
        self._current_url = url_stream

        # Iniciar reproducción
        self.player.play()
        self._is_playing = True

        # Esperar un poco para confirmar el estado de reproducción
        # En entornos reales, se usaría un callback de evento para esto.
        import time
        time.sleep(0.1)

        if self.player.get_state() in [vlc.State.Playing, vlc.State.Opening]:
            print("✅ [VLC] Reproducción iniciada.")
            return True, url_stream
        else:
            print(f"❌ [VLC] Fallo al iniciar la reproducción. Estado: {self.player.get_state()}")
            self._is_playing = False
            return False, "Fallo al iniciar el stream (Revisa la URL)."

    def pausar(self):
        """
        Pausa la reproducción.
        """
        if self.player.get_state() == vlc.State.Playing:
            self.player.pause()
            self._is_playing = False
            print("⏸️ [VLC] Reproducción pausada.")
            return True
        else:
            print("ℹ️ [VLC] No se puede pausar, el reproductor no está en estado de reproducción.")
            return False

    def detener(self):
        """
        Detiene la reproducción y el estado activo.
        """
        if self.player:
            self.player.stop()
            self._is_playing = False
            print("⏹️ [VLC] Reproductor detenido.")
            return True
        return False