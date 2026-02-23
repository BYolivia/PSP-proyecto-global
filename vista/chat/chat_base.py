import tkinter as tk
from tkinter import ttk
from datetime import datetime
from vista.config import *


class ChatBase(ttk.Frame):
    """Base comun para las vistas de chat servidor y cliente."""

    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.root = root
        self.chat_history = None
        self.chat_input_entry = None
        self._btn_enviar = None
        self.socket = None

    def crear_interfaz_chat(self, parent_frame, titulo="Chat", boton_accion_texto=None, boton_accion_callback=None):
        """Crea la interfaz grafica del chat: titulo, historial, entrada y boton."""
        self._chat_frame = ttk.Frame(parent_frame, padding=15, style='TFrame')
        self._chat_frame.pack(expand=True, fill="both")

        self._chat_frame.grid_rowconfigure(1, weight=1)
        self._chat_frame.grid_columnconfigure(0, weight=1)

        # Titulo y boton de accion
        frame_titulo = ttk.Frame(self._chat_frame, style='TFrame')
        frame_titulo.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        frame_titulo.grid_columnconfigure(0, weight=1)

        self.info_label = ttk.Label(frame_titulo, text=titulo, font=FUENTE_TITULO)
        self.info_label.grid(row=0, column=0, sticky="w")

        if boton_accion_texto and boton_accion_callback:
            ttk.Button(
                frame_titulo, text=boton_accion_texto,
                command=boton_accion_callback
            ).grid(row=0, column=1, sticky="e", padx=(10, 0))

        # Historial de mensajes
        self.chat_history = tk.Text(
            self._chat_frame, wrap="word",
            bg=COLOR_BLANCO, fg=COLOR_TEXTO,
            relief="flat", borderwidth=1,
            font=('Arial', 10)
        )
        self.chat_history.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.chat_history.config(state=tk.DISABLED)

        # Entrada y boton
        frame_input = ttk.Frame(self._chat_frame, style='TFrame')
        frame_input.grid(row=2, column=0, columnspan=2, sticky="ew")
        frame_input.grid_columnconfigure(0, weight=1)

        self.chat_input_entry = ttk.Entry(frame_input, font=('Arial', 11))
        self.chat_input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.chat_input_entry.bind('<Return>', self.enviar_mensaje)

        self._btn_enviar = ttk.Button(
            frame_input, text="Enviar",
            command=self.enviar_mensaje, style='Action.TButton'
        )
        self._btn_enviar.grid(row=0, column=1, sticky="e")

    def agregar_mensaje(self, remitente, texto):
        """Agrega un mensaje al historial."""
        self.chat_history.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.chat_history.insert(tk.END, f"[{timestamp}] {remitente.upper()}: {texto.strip()}\n")
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def agregar_mensaje_sistema(self, texto):
        """Agrega un mensaje del sistema."""
        self.agregar_mensaje("SISTEMA", f"--- {texto} ---")

    def enviar_mensaje(self, event=None):
        """Debe ser implementado por las subclases."""
        raise NotImplementedError

    def bloquear_entrada(self):
        """Deshabilita el campo de texto y el boton de enviar."""
        if self.chat_input_entry:
            self.chat_input_entry.config(state=tk.DISABLED)
        if self._btn_enviar:
            self._btn_enviar.config(state=tk.DISABLED)

    def cerrar_conexion(self):
        """Cierra el socket si esta activo."""
        if self.socket:
            try:
                self.socket.close()
            except OSError:
                pass
            self.socket = None