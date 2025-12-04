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
        self.is_playing = False

        # Configurar volumen inicial
        self.ajustar_volumen(initial_volume)
        print(f"🎵 [VLC] Reproductor inicializado. Volumen: {self.player.audio_get_volume()}")

    def ajustar_volumen(self, valor_porcentual):
        """
        Ajusta el volumen del reproductor (0 a 100).
        """
        volumen_int = int(max(0, min(100, valor_porcentual)))
        self.player.audio_set_volume(volumen_int)
        # No imprimimos el volumen aquí para evitar saturar la consola con cada movimiento del Scale

    def cargar_y_reproducir(self, url_stream):
        """
        Carga una nueva URL de stream y comienza la reproducción.
        """
        if not url_stream:
            print("❌ [VLC] URL del stream vacía.")
            return

        print(f"🔄 [VLC] Intentando cargar y reproducir: {url_stream}")

        self.player.stop()

        self.current_media = self.instance.media_new(url_stream)
        self.player.set_media(self.current_media)

        self.player.play()
        self.is_playing = True
        print("✅ [VLC] Reproducción iniciada.")

    def reproducir(self):
        """
        Reanuda la reproducción si está pausada.
        """
        if self.player.get_state() == vlc.State.Paused:
            self.player.play()
            self.is_playing = True
            print("▶️ [VLC] Reproducción reanudada.")
        else:
            print("ℹ️ [VLC] Ya está reproduciéndose o esperando un stream.")

    def pausar(self):
        """
        Pausa la reproducción.
        """
        if self.player.get_state() == vlc.State.Playing:
            self.player.pause()
            self.is_playing = False
            print("⏸️ [VLC] Reproducción pausada.")
        else:
            print("ℹ️ [VLC] No se puede pausar, el reproductor no está en estado de reproducción.")

    def detener(self):
        """
        Detiene la reproducción y libera los recursos. Crucial al cerrar la aplicación.
        """
        if self.player:
            self.player.stop()
            # Limpiar referencias para asegurar que VLC se libere correctamente
            del self.player
            del self.instance
            print("⏹️ [VLC] Reproductor detenido y recursos liberados.")