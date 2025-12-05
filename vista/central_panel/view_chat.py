# Módulo: vista/central_panel/view_chat.py

import tkinter as tk
from tkinter import ttk
from vista.config import *
from datetime import datetime
import random  # Para simular respuestas


class ChatPanel(ttk.Frame):
    """
    Panel de la pestaña Chat.
    Proporciona una interfaz básica para el chat (historial, entrada, envío).
    """

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.chat_history = None
        self.chat_input_entry = None
        self.crear_interfaz_chat(self)
        self.agregar_mensaje_sistema("Bienvenido al sistema de Chat. Introduce un mensaje para empezar.")

    # -------------------------------------------------------------
    # 💬 VISTA Y FUNCIONALIDAD BÁSICA DEL CHAT
    # -------------------------------------------------------------

    def crear_interfaz_chat(self, parent_frame):
        """Crea el área de historial, el campo de entrada y el botón de envío."""

        frame = ttk.Frame(parent_frame, padding=15, style='TFrame')
        frame.pack(expand=True, fill="both")

        frame.grid_rowconfigure(0, weight=1)  # Historial de Chat
        frame.grid_columnconfigure(0, weight=1)

        # 1. Área de Historial de Mensajes (Text Widget)
        self.chat_history = tk.Text(
            frame,
            height=20,
            wrap="word",
            bg=COLOR_BLANCO,
            fg=COLOR_TEXTO,
            relief="flat",
            borderwidth=1,
            font=('Arial', 10)
        )
        self.chat_history.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        self.chat_history.config(state=tk.DISABLED)  # No editable

        # 2. Frame para la entrada y el botón
        frame_input = ttk.Frame(frame, style='TFrame')
        frame_input.grid(row=1, column=0, columnspan=2, sticky="ew")

        frame_input.grid_columnconfigure(0, weight=1)

        # Campo de Entrada de Texto
        self.chat_input_entry = ttk.Entry(frame_input, font=('Arial', 11))
        self.chat_input_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.chat_input_entry.bind('<Return>', self.manejar_envio_mensaje)

        # Botón de Enviar
        ttk.Button(frame_input, text="Enviar 🚀", command=self.manejar_envio_mensaje,
                   style='Action.TButton').grid(row=0, column=1, sticky="e")

    def agregar_mensaje(self, remitente, texto):
        """Añade un mensaje al historial de chat."""

        # Habilitar temporalmente para la inserción
        self.chat_history.config(state=tk.NORMAL)

        timestamp = datetime.now().strftime('%H:%M:%S')

        # Formato del mensaje (ej. [16:55:01] TÚ: Hola mundo)
        mensaje_completo = f"[{timestamp}] {remitente.upper()}: {texto.strip()}\n"

        self.chat_history.insert(tk.END, mensaje_completo)

        # Deshabilitar de nuevo y hacer scroll al final
        self.chat_history.config(state=tk.DISABLED)
        self.chat_history.see(tk.END)

    def agregar_mensaje_sistema(self, texto):
        """Añade un mensaje específico del sistema (para inicio o errores)."""
        self.agregar_mensaje("SISTEMA", f"--- {texto} ---")

    def simular_respuesta_bot(self, mensaje_usuario):
        """
        Función placeholder para simular la respuesta de un bot/asistente.
        Aquí es donde conectarías tu lógica de LLM, socket o backend de chat real.
        """
        respuestas = [
            "Entendido. Procesando tu solicitud...",
            "Gracias por tu mensaje. El chat está en desarrollo.",
            "Respuesta automática: ¿Cómo puedo ayudarte con las tareas de T1 a T4?",
            f"El tema '{mensaje_usuario.split()[0]}' es muy interesante, pero no tengo datos al respecto.",
        ]
        respuesta = random.choice(respuestas)
        self.agregar_mensaje("ASISTENTE", respuesta)

    def manejar_envio_mensaje(self, event=None):
        """Procesa el mensaje del usuario al presionar Enter o el botón Enviar."""
        mensaje = self.chat_input_entry.get()

        if mensaje.strip():
            self.agregar_mensaje("TÚ", mensaje)
            self.chat_input_entry.delete(0, tk.END)  # Limpiar campo de entrada

            # Simular la respuesta del sistema después de un breve delay
            self.after(500, lambda: self.simular_respuesta_bot(mensaje))

        # Prevenir que el evento 'Return' propague y cause errores si se llama
        return "break" if event else None