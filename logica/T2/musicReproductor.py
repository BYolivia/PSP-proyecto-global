# Módulo: logica/T2/musicReproductor.py

import vlc
import os


class MusicReproductor:
    """
    Clase para gestionar la reproducción de audio utilizando la librería python-vlc.
    Se asegura de que el objeto 'player' de VLC sea liberado y recreado correctamente
    para poder manejar múltiples eventos de alarma o cambiar de stream de radio sin fallos.
    """

    def __init__(self, initial_volume=50):
        # 1. Crear la instancia de VLC, que debe ser única por aplicación.
        self.instance = vlc.Instance()

        # 2. Creamos el player inicial.
        self.player = self.instance.media_player_new()

        self.volumen = initial_volume
        self.ajustar_volumen(initial_volume)
        print(f"🎵 [VLC] Reproductor inicializado. Volumen: {self.volumen}")

    def ajustar_volumen(self, valor):
        """Ajusta el volumen del reproductor."""
        self.volumen = int(valor)
        if self.player:
            self.player.audio_set_volume(self.volumen)

    def cargar_y_reproducir(self, url):
        """
        Carga el archivo o stream y lo reproduce.

        **Corrección:** Recrea self.player si fue liberado (release) por el método detener().
        """
        print(f"🔄 [VLC] Intentando cargar y reproducir: {url}")

        # 1. Recrear el reproductor si fue liberado.
        if not self.player:
            self.player = self.instance.media_player_new()
            self.ajustar_volumen(self.volumen)  # Restaurar volumen

        # 2. Detener la reproducción actual de forma segura antes de cargar una nueva media.
        # Esto previene el AttributeError, ya que self.player ahora está garantizado que no es None.
        if self.player:
            self.player.stop()

        # 3. Cargar y reproducir la nueva media.
        media = self.instance.media_new(url)
        self.player.set_media(media)

        if self.player.play() == 0:
            print("✅ [VLC] Reproducción iniciada.")
        else:
            print("❌ [VLC] Error al intentar iniciar la reproducción.")

    def detener(self):
        """
        Detiene la reproducción, libera los recursos del player y lo establece a None.
        Esto es crucial para que el sistema de audio no se quede bloqueado por VLC.
        """
        if self.player:
            self.player.stop()
            self.player.release()
            self.player = None  # <--- Obliga a recrear el player en la próxima llamada a cargar_y_reproducir
            print("⏹️ [VLC] Reproductor detenido y recursos liberados.")

    def pausar(self):
        """Pausa la reproducción."""
        if self.player and self.player.is_playing():
            self.player.pause()

    def reproducir(self):
        """Reanuda la reproducción."""
        if self.player:
            self.player.play()