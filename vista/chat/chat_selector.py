import tkinter as tk
from tkinter import ttk, messagebox
import threading
from vista.config import *
from logica.red.cliente import descubrir_servidores
from logica.red.selector import obtener_ip_local
from vista.chat.chat_servidor import ChatServidorPanel
from vista.chat.chat_cliente import ChatClientePanel

_DONUT_SIZE   = 72
_DONUT_RADIUS = 26
_DONUT_GROSOR = 9
_DONUT_COLOR  = COLOR_ACCION
_DONUT_TRACK  = "#d0d0d0"
_DONUT_STEP   = 9   # grados por frame
_DONUT_MS     = 25  # ms entre frames


class ChatSelectorPanel(ttk.Frame):
    """Panel inicial que permite elegir entre servidor o cliente."""

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.parent_notebook = parent_notebook
        self.panel_activo = None
        self._busqueda_cancelada = False
        self._stop_event = None
        self._donut_animating = False
        self._donut_angle = 0
        self.servidores_encontrados = []
        self._ultimo_visto = {}        # (ip, puerto) -> timestamp
        self._frames_servidores = {}   # (ip, puerto) -> ttk.Frame
        self._frame_servidores = None
        self._lbl_contador = None
        self._lbl_buscando = None
        self._canvas_donut = None
        self._btn_cancelar = None
        self.crear_selector()

    # ------------------------------------------------------------------
    # Pantalla principal
    # ------------------------------------------------------------------

    def crear_selector(self):
        self.selector_frame = ttk.Frame(self, padding=30, style='TFrame')
        self.selector_frame.pack(expand=True, fill="both")

        ttk.Label(
            self.selector_frame, text="Chat en Red",
            font=FUENTE_TITULO
        ).pack(pady=(20, 5))

        ip = obtener_ip_local()
        ttk.Label(
            self.selector_frame, text=f"IP local: {ip}",
            font=FUENTE_NOTA
        ).pack(pady=(0, 20))

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

        self.frame_cliente = ttk.Frame(self.selector_frame, style='TFrame')

    # ------------------------------------------------------------------
    # Servidor
    # ------------------------------------------------------------------

    def iniciar_servidor(self):
        self.selector_frame.destroy()
        self.panel_activo = ChatServidorPanel(self, self.root)
        self.panel_activo.pack(expand=True, fill="both")

    # ------------------------------------------------------------------
    # Busqueda de servidores — entrada
    # ------------------------------------------------------------------

    def iniciar_busqueda_cliente(self):
        self._busqueda_cancelada = False
        self.servidores_encontrados = []
        self._ultimo_visto = {}
        self._frames_servidores = {}
        self._stop_event = threading.Event()

        for widget in self.frame_cliente.winfo_children():
            widget.destroy()
        self.frame_cliente.pack(pady=20, fill="x")

        # Donut canvas
        self._canvas_donut = tk.Canvas(
            self.frame_cliente,
            width=_DONUT_SIZE, height=_DONUT_SIZE,
            bg=COLOR_FONDO, highlightthickness=0
        )
        self._canvas_donut.pack(pady=(10, 2))

        self._lbl_buscando = ttk.Label(
            self.frame_cliente, text="Buscando...",
            font=FUENTE_NOTA
        )
        self._lbl_buscando.pack()

        # Contador de servidores
        self._lbl_contador = ttk.Label(
            self.frame_cliente, text="", font=FUENTE_NOTA
        )
        self._lbl_contador.pack(pady=(6, 0))

        # Lista de servidores (se rellena en tiempo real)
        self._frame_servidores = ttk.Frame(self.frame_cliente, style='TFrame')
        self._frame_servidores.pack(pady=4, fill="x")

        # Boton cancelar
        self._btn_cancelar = ttk.Button(
            self.frame_cliente, text="Cancelar búsqueda",
            command=self.cancelar_busqueda
        )
        self._btn_cancelar.pack(pady=5)

        self._donut_angle = 0
        self._donut_animating = True
        self._animar_donut()

        hilo = threading.Thread(target=self._hilo_busqueda, daemon=True)
        hilo.start()

        self.root.after(2000, self._chequear_servidores_caidos)

    # ------------------------------------------------------------------
    # Animacion donut
    # ------------------------------------------------------------------

    def _animar_donut(self):
        if not self._donut_animating:
            return
        try:
            if not self._canvas_donut.winfo_exists():
                return
        except tk.TclError:
            return
        cx = cy = _DONUT_SIZE // 2
        r = _DONUT_RADIUS
        x0, y0 = cx - r, cy - r
        x1, y1 = cx + r, cy + r

        self._canvas_donut.delete("all")
        # Track
        self._canvas_donut.create_arc(
            x0, y0, x1, y1,
            start=0, extent=359.9,
            style=tk.ARC, outline=_DONUT_TRACK, width=_DONUT_GROSOR
        )
        # Arco animado
        self._canvas_donut.create_arc(
            x0, y0, x1, y1,
            start=self._donut_angle, extent=90,
            style=tk.ARC, outline=_DONUT_COLOR, width=_DONUT_GROSOR
        )
        self._donut_angle = (self._donut_angle + _DONUT_STEP) % 360
        self.root.after(_DONUT_MS, self._animar_donut)

    def _detener_donut(self):
        self._donut_animating = False

    # ------------------------------------------------------------------
    # Hilo de busqueda
    # ------------------------------------------------------------------

    def _hilo_busqueda(self):
        descubrir_servidores(
            timeout_sin_nuevos=10,
            callback=lambda ip, puerto: self.root.after(
                0, self._agregar_servidor, ip, puerto
            ),
            on_seen=lambda ip, puerto: self.root.after(
                0, self._actualizar_visto, ip, puerto
            ),
            stop_event=self._stop_event,
        )
        if not self._busqueda_cancelada:
            self.root.after(0, self._busqueda_finalizada)

    # ------------------------------------------------------------------
    # Callbacks de UI
    # ------------------------------------------------------------------

    _TIMEOUT_SERVIDOR = 8  # segundos sin broadcast → servidor caído

    def _agregar_servidor(self, ip, puerto):
        """Añade un servidor a la lista en tiempo real.

        Si llega 127.0.0.1 y ya hay una IP LAN con el mismo puerto, lo ignora.
        Si llega una IP LAN y ya hay 127.0.0.1 con ese puerto, reemplaza la entrada.
        """
        import time
        LOOPBACK = "127.0.0.1"

        # Buscar si ya existe una entrada con el mismo puerto
        clave_existente = next(
            (k for k in self.servidores_encontrados if k[1] == puerto),
            None
        )

        if clave_existente is not None:
            ip_existente = clave_existente[0]
            if ip == LOOPBACK:
                return  # Ya hay IP LAN → ignorar loopback
            if ip_existente == LOOPBACK:
                # Reemplazar loopback por IP LAN
                nueva_clave = (ip, puerto)
                self.servidores_encontrados.remove(clave_existente)
                self.servidores_encontrados.append(nueva_clave)
                frame_srv = self._frames_servidores.pop(clave_existente)
                self._frames_servidores[nueva_clave] = frame_srv
                self._ultimo_visto[nueva_clave] = time.time()
                del self._ultimo_visto[clave_existente]
                for w in frame_srv.winfo_children():
                    if isinstance(w, ttk.Label):
                        w.config(text=ip)
                        break
                return
            return  # Mismo puerto, IPs distintas no-loopback → ya existe

        entrada = (ip, puerto)
        self.servidores_encontrados.append(entrada)
        self._ultimo_visto[entrada] = time.time()

        frame_srv = ttk.Frame(self._frame_servidores, style='TFrame')
        frame_srv.pack(pady=2, fill="x", padx=40)
        self._frames_servidores[entrada] = frame_srv

        ttk.Label(
            frame_srv, text=ip, font=FUENTE_NORMAL
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_srv, text="Conectar",
            command=lambda e=entrada: self.pedir_clave_entrada(e),
            style='Action.TButton'
        ).pack(side="left", padx=5)

        self._actualizar_contador()

    def _actualizar_visto(self, ip, puerto):
        """Actualiza el timestamp de último broadcast recibido para un servidor."""
        import time
        # Buscar por puerto (independientemente de si es loopback o LAN)
        clave = next(
            (k for k in self.servidores_encontrados if k[1] == puerto),
            None
        )
        if clave:
            self._ultimo_visto[clave] = time.time()

    def _chequear_servidores_caidos(self):
        """Elimina de la lista los servidores que llevan más de _TIMEOUT_SERVIDOR sin broadcast."""
        import time
        if self._busqueda_cancelada:
            return

        try:
            if not self.frame_cliente.winfo_exists():
                return
        except tk.TclError:
            return

        ahora = time.time()
        caidos = [
            k for k in list(self.servidores_encontrados)
            if ahora - self._ultimo_visto.get(k, ahora) > self._TIMEOUT_SERVIDOR
        ]

        for clave in caidos:
            self.servidores_encontrados.remove(clave)
            del self._ultimo_visto[clave]
            frame = self._frames_servidores.pop(clave, None)
            if frame and frame.winfo_exists():
                frame.destroy()

        if caidos:
            self._actualizar_contador()

        self.root.after(2000, self._chequear_servidores_caidos)

    def _actualizar_contador(self):
        if not self._lbl_contador or not self._lbl_contador.winfo_exists():
            return
        n = len(self.servidores_encontrados)
        self._lbl_contador.config(
            text=f"{n} servidor{'es' if n != 1 else ''} encontrado{'s' if n != 1 else ''}"
        )

    def _busqueda_finalizada(self):
        self._detener_donut()

        try:
            if not self.frame_cliente.winfo_exists():
                return
        except tk.TclError:
            return

        # Ocultar donut y texto "Buscando..."
        if self._canvas_donut and self._canvas_donut.winfo_exists():
            self._canvas_donut.destroy()
        if self._lbl_buscando and self._lbl_buscando.winfo_exists():
            self._lbl_buscando.destroy()

        if self._btn_cancelar and self._btn_cancelar.winfo_exists():
            self._btn_cancelar.destroy()

        if not self.servidores_encontrados:
            if self._lbl_contador and self._lbl_contador.winfo_exists():
                self._lbl_contador.config(
                    text="No se encontraron servidores.", foreground="red"
                )
        else:
            if self._lbl_contador and self._lbl_contador.winfo_exists():
                n = len(self.servidores_encontrados)
                self._lbl_contador.config(
                    text=f"Búsqueda completada — {n} servidor{'es' if n != 1 else ''} encontrado{'s' if n != 1 else ''}",
                    foreground=COLOR_EXITO
                )

        frame_acciones = ttk.Frame(self.frame_cliente, style='TFrame')
        frame_acciones.pack(pady=8)

        ttk.Button(
            frame_acciones, text="Actualizar",
            command=self.iniciar_busqueda_cliente, style='Action.TButton'
        ).pack(side="left", padx=5)

        ttk.Button(
            frame_acciones, text="Volver",
            command=self.volver_selector
        ).pack(side="left", padx=5)

    # ------------------------------------------------------------------
    # Cancelar / volver
    # ------------------------------------------------------------------

    def cancelar_busqueda(self):
        self._busqueda_cancelada = True
        if self._stop_event:
            self._stop_event.set()
        self._detener_donut()
        for widget in self.frame_cliente.winfo_children():
            widget.destroy()
        self.frame_cliente.pack_forget()

    def pedir_clave_entrada(self, srv_entrada):
        ip, puerto = srv_entrada

        dialogo = tk.Toplevel(self.root)
        dialogo.title("Clave de acceso")
        dialogo.geometry("350x160")
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
        # Detener busqueda antes de destruir widgets
        self._busqueda_cancelada = True
        if self._stop_event:
            self._stop_event.set()
        self._detener_donut()

        print(f"[DEBUG SEL] Conectando a servidor: ip={ip} puerto={puerto} clave={contrasena!r}")
        self.selector_frame.destroy()
        self.panel_activo = ChatClientePanel(
            self, self.root, ip, puerto, contrasena,
            on_auth_error=self._auth_fallida
        )
        self.panel_activo.pack(expand=True, fill="both")

    def _auth_fallida(self):
        """Destruye el panel de chat y vuelve al selector con un aviso de error."""
        if self.panel_activo:
            self.panel_activo.destroy()
            self.panel_activo = None
        self.crear_selector()
        messagebox.showerror("Contraseña incorrecta", "La clave introducida no es válida.\nComprueba el formato: puerto#contraseña")

    def volver_al_selector(self):
        if self.panel_activo:
            self.panel_activo = None
        self.crear_selector()

    def volver_selector(self):
        for widget in self.frame_cliente.winfo_children():
            widget.destroy()
        self.frame_cliente.pack_forget()
