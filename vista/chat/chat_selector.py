import tkinter as tk
from tkinter import ttk
import threading
from vista.config import *
from logica.red.cliente import descubrir_servidores
from logica.red.selector import obtener_ip_local
from vista.chat.chat_servidor import ChatServidorPanel
from vista.chat.chat_cliente import ChatClientePanel


class ChatSelectorPanel(ttk.Frame):
    """Panel inicial que permite elegir entre servidor o cliente."""

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.parent_notebook = parent_notebook
        self.panel_activo = None
        self._busqueda_cancelada = False
        self.crear_selector()

    def crear_selector(self):
        """Crea la pantalla de seleccion de rol."""
        self.selector_frame = ttk.Frame(self, padding=30, style='TFrame')
        self.selector_frame.pack(expand=True, fill="both")

        # Titulo
        ttk.Label(
            self.selector_frame, text="Chat en Red",
            font=FUENTE_TITULO
        ).pack(pady=(20, 5))

        ip = obtener_ip_local()
        ttk.Label(
            self.selector_frame, text=f"IP local: {ip}",
            font=FUENTE_NOTA
        ).pack(pady=(0, 20))

        # Botones de rol
        frame_botones = ttk.Frame(self.selector_frame, style='TFrame')
        frame_botones.pack(pady=10)

        ttk.Button(
            frame_botones, text="Crear Servidor",
            command=self.iniciar_servidor, style='Action.TButton'
        ).pack(side="left", padx=10)

        ttk.Button(
            frame_botones, text="Conectar como Cliente",
            command=self.iniciar_busqueda_cliente, style='Action.TButton'
        ).pack(side="left", padx=10)

        # Frame para resultado de busqueda (cliente)
        self.frame_cliente = ttk.Frame(self.selector_frame, style='TFrame')
        self.estado_label = None
        self.servidores_encontrados = []

    def iniciar_servidor(self):
        """Reemplaza el selector por el panel de chat servidor."""
        self.selector_frame.destroy()
        self.panel_activo = ChatServidorPanel(self, self.root)
        self.panel_activo.pack(expand=True, fill="both")

    def iniciar_busqueda_cliente(self):
        """Muestra progreso y busca servidores."""
        self._busqueda_cancelada = False

        # Limpiar frame cliente previo
        for widget in self.frame_cliente.winfo_children():
            widget.destroy()
        self.frame_cliente.pack(pady=20, fill="x")

        self.estado_label = ttk.Label(
            self.frame_cliente, text="Buscando servidores...",
            font=FUENTE_NEGOCIOS
        )
        self.estado_label.pack()

        self.progress = ttk.Progressbar(self.frame_cliente, mode='indeterminate')
        self.progress.pack(fill="x", padx=40, pady=5)
        self.progress.start(15)

        ttk.Button(
            self.frame_cliente, text="Cancelar busqueda",
            command=self.cancelar_busqueda
        ).pack(pady=5)

        hilo = threading.Thread(target=self.buscar_servidores, daemon=True)
        hilo.start()

    def cancelar_busqueda(self):
        """Cancela la busqueda de servidores."""
        self._busqueda_cancelada = True
        self.progress.stop()
        for widget in self.frame_cliente.winfo_children():
            widget.destroy()
        self.frame_cliente.pack_forget()

    def buscar_servidores(self):
        print("[DEBUG SEL] Iniciando busqueda de servidores...")
        servidores = descubrir_servidores(timeout=5)
        print(f"[DEBUG SEL] Busqueda completada: {servidores}")
        if not self._busqueda_cancelada:
            self.root.after(0, self.mostrar_resultado_busqueda, servidores)

    def mostrar_resultado_busqueda(self, servidores):
        self.progress.stop()
        for widget in self.frame_cliente.winfo_children():
            widget.destroy()

        if not servidores:
            ttk.Label(
                self.frame_cliente, text="No se encontraron servidores.",
                font=FUENTE_NEGOCIOS, foreground="red"
            ).pack()

            frame_opciones = ttk.Frame(self.frame_cliente, style='TFrame')
            frame_opciones.pack(pady=10)
            ttk.Button(
                frame_opciones, text="Reintentar",
                command=self.iniciar_busqueda_cliente, style='Action.TButton'
            ).pack(side="left", padx=5)
            ttk.Button(
                frame_opciones, text="Volver",
                command=self.volver_selector
            ).pack(side="left", padx=5)
            return

        self.servidores_encontrados = servidores

        ttk.Label(
            self.frame_cliente,
            text=f"{len(servidores)} servidor(es) encontrado(s):",
            font=FUENTE_NEGOCIOS
        ).pack()

        for i, (ip, puerto) in enumerate(servidores):
            frame_srv = ttk.Frame(self.frame_cliente, style='TFrame')
            frame_srv.pack(pady=2)
            ttk.Label(frame_srv, text=f"{ip}", font=FUENTE_NORMAL).pack(side="left", padx=5)
            ttk.Button(
                frame_srv, text="Conectar",
                command=lambda idx=i: self.pedir_clave(idx), style='Action.TButton'
            ).pack(side="left", padx=5)

    def pedir_clave(self, indice):
        """Muestra un dialogo para introducir la contrasena."""
        ip, puerto = self.servidores_encontrados[indice]

        dialogo = tk.Toplevel(self.root)
        dialogo.title("Clave de acceso")
        dialogo.geometry("350x120")
        dialogo.resizable(False, False)
        dialogo.transient(self.root)
        dialogo.grab_set()

        frame = ttk.Frame(dialogo, padding=15)
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text=f"Conectar a {ip}", font=FUENTE_NEGOCIOS).pack()
        ttk.Label(frame, text="Clave (puerto#contraseña):", font=FUENTE_NORMAL).pack(pady=(5, 0))

        entrada = ttk.Entry(frame, font=FUENTE_NORMAL)
        entrada.pack(fill="x", pady=5)
        entrada.focus_set()

        def conectar(event=None):
            contrasena = entrada.get().strip()
            if contrasena:
                dialogo.destroy()
                self.conectar_a_servidor(ip, puerto, contrasena)

        entrada.bind('<Return>', conectar)
        ttk.Button(frame, text="Conectar", command=conectar, style='Action.TButton').pack()

    def conectar_a_servidor(self, ip, puerto, contrasena):
        """Reemplaza el selector por el panel de chat cliente."""
        print(f"[DEBUG SEL] Conectando a servidor: ip={ip} puerto={puerto} clave={contrasena!r}")
        self.selector_frame.destroy()
        self.panel_activo = ChatClientePanel(self, self.root, ip, puerto, contrasena)
        self.panel_activo.pack(expand=True, fill="both")

    def volver_al_selector(self):
        """Destruye el panel activo y recrea el selector."""
        if self.panel_activo:
            self.panel_activo = None
        self.crear_selector()

    def volver_selector(self):
        """Limpia el frame de cliente para volver al estado inicial."""
        for widget in self.frame_cliente.winfo_children():
            widget.destroy()
        self.frame_cliente.pack_forget()
