import tkinter as tk
from tkinter import ttk
import threading
from vista.chat.chat_base import ChatBase
from logica.red.cliente import conectar_servidor
from vista.config import *

PREFIJO_NOMBRE = "__NOMBRE__:"


class ChatClientePanel(ChatBase):
    """Vista de chat para el rol de cliente."""

    def __init__(self, parent, root, ip, puerto, clave, on_auth_error=None, *args, **kwargs):
        super().__init__(parent, root, *args, **kwargs)
        self.ip = ip
        self.puerto = puerto
        self.clave = clave
        self.nombre = None
        self.on_auth_error = on_auth_error
        self.crear_interfaz_chat(
            self, titulo="Chat - Cliente",
            boton_accion_texto="Desconectar",
            boton_accion_callback=self.desconectar_y_volver
        )
        self.conectar()

    def conectar(self):
        print(f"[DEBUG CLI-GUI] Iniciando conexion a {self.ip}:{self.puerto} con clave={self.clave!r}")
        self.agregar_mensaje_sistema(f"Conectando a {self.ip}:{self.puerto}...")

        def hilo_conexion():
            cliente, extra = conectar_servidor(self.ip, self.puerto, self.clave)
            if cliente:
                self.socket = cliente
                print(f"[DEBUG CLI-GUI] Conexion exitosa, extra={extra!r}")
                self.root.after(0, self.agregar_mensaje_sistema, f"Conectado a {self.ip}:{self.puerto}")
                self.recibir_mensajes(extra)
            else:
                print(f"[DEBUG CLI-GUI] Conexion fallida")
                if self.on_auth_error:
                    self.root.after(0, self.on_auth_error)
                else:
                    self.root.after(0, self.agregar_mensaje_sistema, "Error: no se pudo conectar o clave incorrecta")

        hilo = threading.Thread(target=hilo_conexion, daemon=True)
        hilo.start()

    def _procesar_mensaje(self, mensaje):
        """Procesa un mensaje recibido (nombre, chat o remoto)."""
        print(f"[DEBUG CLI-GUI] Procesando mensaje: {mensaje!r}")
        if mensaje.startswith(PREFIJO_NOMBRE):
            self.nombre = mensaje[len(PREFIJO_NOMBRE):]
            print(f"[DEBUG CLI-GUI] Nombre asignado: {self.nombre!r}")
            self.root.after(0, self.agregar_mensaje_sistema, f"Tu nombre: {self.nombre}")
            self.root.after(0, self._actualizar_titulo)
        elif ": " in mensaje:
            remitente, texto = mensaje.split(": ", 1)
            print(f"[DEBUG CLI-GUI] Mensaje de chat: {remitente!r} -> {texto!r}")
            self.root.after(0, self.agregar_mensaje, remitente, texto)
        else:
            print(f"[DEBUG CLI-GUI] Mensaje remoto sin formato: {mensaje!r}")
            self.root.after(0, self.agregar_mensaje, "REMOTO", mensaje)

    def recibir_mensajes(self, extra=""):
        # Procesar datos que llegaron junto con el "OK" de autenticacion
        if extra:
            print(f"[DEBUG CLI-GUI] Procesando datos extra del handshake: {extra!r}")
            self._procesar_mensaje(extra)

        print("[DEBUG CLI-GUI] Bucle de recepcion iniciado")
        try:
            while self.socket:
                datos = self.socket.recv(4096)
                if not datos:
                    print("[DEBUG CLI-GUI] Datos vacios recibidos (servidor cerro)")
                    self.root.after(0, self._servidor_desconectado)
                    break
                mensaje = datos.decode("utf-8")
                print(f"[DEBUG CLI-GUI] Datos crudos recibidos: {datos!r}")
                self._procesar_mensaje(mensaje)
        except (ConnectionResetError, OSError) as e:
            print(f"[DEBUG CLI-GUI] Error en recepcion: {e}")
            self.root.after(0, self._servidor_desconectado)

    def _actualizar_titulo(self):
        if self.nombre:
            self.info_label.config(text=f"Chat - {self.nombre}")

    def enviar_mensaje(self, event=None):
        mensaje = self.chat_input_entry.get().strip()
        if not mensaje or not self.socket:
            return "break" if event else None

        self.chat_input_entry.delete(0, "end")
        self.agregar_mensaje("TU", mensaje)

        try:
            print(f"[DEBUG CLI-GUI] Enviando mensaje: {mensaje!r}")
            self.socket.sendall(mensaje.encode("utf-8"))
        except OSError as e:
            print(f"[DEBUG CLI-GUI] Error al enviar: {e}")
            self.agregar_mensaje_sistema("Error al enviar mensaje")

        return "break" if event else None

    def _servidor_desconectado(self):
        """Bloquea la entrada y muestra popup cuando el servidor cierra la conexion."""
        self.cerrar_conexion()
        self.bloquear_entrada()

        dialogo = tk.Toplevel(self.root)
        dialogo.title("Servidor desconectado")
        dialogo.geometry("320x140")
        dialogo.resizable(False, False)
        dialogo.transient(self.root)
        dialogo.grab_set()

        frame = ttk.Frame(dialogo, padding=20)
        frame.pack(expand=True, fill="both")

        ttk.Label(
            frame, text="El servidor se ha cerrado.",
            font=FUENTE_NEGOCIOS
        ).pack(pady=(0, 15))

        frame_btns = ttk.Frame(frame)
        frame_btns.pack()

        def volver():
            dialogo.destroy()
            self.desconectar_y_volver()

        def ver_chat():
            dialogo.destroy()

        ttk.Button(
            frame_btns, text="Volver al inicio",
            command=volver, style='Action.TButton'
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_btns, text="Ver el chat",
            command=ver_chat
        ).pack(side="left", padx=5)

    def desconectar_y_volver(self):
        """Desconecta del servidor y vuelve al selector."""
        self.cerrar_conexion()
        parent = self.master
        self.destroy()
        if hasattr(parent, 'volver_al_selector'):
            parent.volver_al_selector()
