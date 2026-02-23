# Módulo: vista/central_panel/view_correos.py

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from logica.correo import CorreoClient
from vista.config import *


class CorreosPanel(ttk.Frame):
    """
    Panel de la pestaña Correos.
    Gestión de correos electrónicos con login, bandeja de entrada y redacción.
    """

    def __init__(self, parent_notebook, root, *args, **kwargs):
        super().__init__(parent_notebook, *args, **kwargs)
        self.root = root
        self.cliente = CorreoClient()
        self.correos_cache = []
        self._autorefresh_id = None
        self._refreshing = False

        # Frames apilados (login, bandeja, redactar)
        self.frame_login = ttk.Frame(self)
        self.frame_bandeja = ttk.Frame(self)
        self.frame_redactar = ttk.Frame(self)

        for f in (self.frame_login, self.frame_bandeja, self.frame_redactar):
            f.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._crear_vista_login()
        self._crear_vista_bandeja()
        self._crear_vista_redactar()

        # Precargar config si existe
        self._precargar_config()

        # Mostrar login inicialmente
        self._mostrar_frame(self.frame_login)

    # ==================================================================
    # VISTA 1: LOGIN
    # ==================================================================

    # Mapeo de nombres visibles a claves internas y puertos por defecto
    _CIFRADO_MAP = {
        "Sin cifrar":    "none",
        "SSL/TLS":       "ssl",
        "STARTTLS":      "starttls",
        "Personalizado": "custom",
    }
    _CIFRADO_INVERSO = {v: k for k, v in _CIFRADO_MAP.items()}

    def _crear_vista_login(self):
        frame = self.frame_login
        contenedor = ttk.Frame(frame, padding=30)
        contenedor.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(contenedor, text="Iniciar Sesion - Correo",
                  font=FUENTE_TITULO).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Servidor
        ttk.Label(contenedor, text="Servidor:", font=FUENTE_NEGOCIOS).grid(
            row=1, column=0, sticky="e", padx=(0, 10), pady=5)
        self.entry_server = ttk.Entry(contenedor, width=30)
        self.entry_server.grid(row=1, column=1, pady=5)

        # Cifrado (3 opciones predefinidas + Personalizado)
        ttk.Label(contenedor, text="Cifrado:", font=FUENTE_NEGOCIOS).grid(
            row=2, column=0, sticky="e", padx=(0, 10), pady=5)
        self.var_cifrado = tk.StringVar(value="Sin cifrar")
        combo_cifrado = ttk.Combobox(contenedor, textvariable=self.var_cifrado,
                                     values=["Sin cifrar", "SSL/TLS", "STARTTLS", "Personalizado"],
                                     state="readonly", width=27)
        combo_cifrado.grid(row=2, column=1, pady=5)
        combo_cifrado.bind("<<ComboboxSelected>>", self._on_cifrado_change)

        # Puerto IMAP (oculto por defecto)
        self.lbl_imap_port = ttk.Label(contenedor, text="Puerto IMAP:", font=FUENTE_NEGOCIOS)
        self.entry_imap_port = ttk.Entry(contenedor, width=30)
        self.entry_imap_port.insert(0, "143")

        # Puerto SMTP (oculto por defecto)
        self.lbl_smtp_port = ttk.Label(contenedor, text="Puerto SMTP:", font=FUENTE_NEGOCIOS)
        self.entry_smtp_port = ttk.Entry(contenedor, width=30)
        self.entry_smtp_port.insert(0, "25")

        # Usuario
        ttk.Label(contenedor, text="Usuario:", font=FUENTE_NEGOCIOS).grid(
            row=5, column=0, sticky="e", padx=(0, 10), pady=5)
        self.entry_user = ttk.Entry(contenedor, width=30)
        self.entry_user.grid(row=5, column=1, pady=5)

        # Contraseña
        ttk.Label(contenedor, text="Contraseña:", font=FUENTE_NEGOCIOS).grid(
            row=6, column=0, sticky="e", padx=(0, 10), pady=5)
        self.entry_password = ttk.Entry(contenedor, width=30, show="*")
        self.entry_password.grid(row=6, column=1, pady=5)

        # Recordar credenciales
        self.var_recordar = tk.BooleanVar(value=False)
        ttk.Checkbutton(contenedor, text="Recordar credenciales",
                        variable=self.var_recordar).grid(
            row=7, column=0, columnspan=2, pady=10)

        # Botón conectar
        self.btn_conectar = ttk.Button(contenedor, text="Conectar",
                                       command=self._on_conectar)
        self.btn_conectar.grid(row=8, column=0, columnspan=2, pady=10)

        # Label de estado
        self.lbl_estado_login = ttk.Label(contenedor, text="", font=FUENTE_NOTA,
                                          foreground=COLOR_ACCION)
        self.lbl_estado_login.grid(row=9, column=0, columnspan=2)

    def _on_cifrado_change(self, event=None):
        """Muestra/oculta puertos y actualiza valores por defecto."""
        from logica.correo import CorreoClient
        opcion = self.var_cifrado.get()

        if opcion == "Personalizado":
            # Mostrar campos de puertos editables
            self.lbl_imap_port.grid(row=3, column=0, sticky="e", padx=(0, 10), pady=5)
            self.entry_imap_port.grid(row=3, column=1, pady=5)
            self.lbl_smtp_port.grid(row=4, column=0, sticky="e", padx=(0, 10), pady=5)
            self.entry_smtp_port.grid(row=4, column=1, pady=5)
        else:
            # Ocultar campos de puertos
            self.lbl_imap_port.grid_remove()
            self.entry_imap_port.grid_remove()
            self.lbl_smtp_port.grid_remove()
            self.entry_smtp_port.grid_remove()
            # Establecer puertos por defecto según la opción
            sec_key = self._CIFRADO_MAP.get(opcion, "none")
            puertos = CorreoClient.PUERTOS.get(sec_key, CorreoClient.PUERTOS["none"])
            self.entry_imap_port.delete(0, tk.END)
            self.entry_imap_port.insert(0, str(puertos["imap"]))
            self.entry_smtp_port.delete(0, tk.END)
            self.entry_smtp_port.insert(0, str(puertos["smtp"]))

    def _precargar_config(self):
        """Precarga credenciales desde .env si existen."""
        config = self.cliente.cargar_config()
        if config["server"]:
            self.entry_server.insert(0, config["server"])
            self.entry_imap_port.delete(0, tk.END)
            self.entry_imap_port.insert(0, config["imap_port"])
            self.entry_smtp_port.delete(0, tk.END)
            self.entry_smtp_port.insert(0, config["smtp_port"])
            self.entry_user.insert(0, config["user"])
            self.entry_password.insert(0, config["password"])
            # Restaurar modo de cifrado
            sec = config["security"]
            nombre = self._CIFRADO_INVERSO.get(sec, "Sin cifrar")
            self.var_cifrado.set(nombre)
            self._on_cifrado_change()
            self.var_recordar.set(True)

    def _get_security(self):
        """Devuelve la clave de seguridad interna según la selección del usuario."""
        opcion = self.var_cifrado.get()
        if opcion == "Personalizado":
            return "none"  # Personalizado usa puertos manuales sin cifrado extra
        return self._CIFRADO_MAP.get(opcion, "none")

    def _on_conectar(self):
        """Intenta conectar al servidor IMAP."""
        server = self.entry_server.get().strip()
        imap_port = self.entry_imap_port.get().strip()
        smtp_port = self.entry_smtp_port.get().strip()
        user = self.entry_user.get().strip()
        password = self.entry_password.get().strip()
        security = self._get_security()

        if not server or not user or not password:
            self.lbl_estado_login.config(text="Rellena todos los campos obligatorios.",
                                         foreground="red")
            return

        # Guardar si se pidió
        if self.var_recordar.get():
            self.cliente.guardar_config(server, imap_port, smtp_port, user, password, security)

        self.lbl_estado_login.config(text="Conectando...", foreground=COLOR_ACCION)
        self.btn_conectar.config(state="disabled")

        # Almacenar datos SMTP para uso posterior
        self.smtp_server = server
        self.smtp_port = smtp_port
        self.smtp_user = user
        self.smtp_password = password
        self.smtp_security = security

        def tarea():
            try:
                self.cliente.conectar(server, imap_port, user, password, security)
                correos = self.cliente.obtener_bandeja()
                self.root.after(0, lambda: self._conexion_exitosa(correos, user))
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda m=msg: self._conexion_fallida(m))

        threading.Thread(target=tarea, daemon=True).start()

    def _conexion_exitosa(self, correos, user):
        self.btn_conectar.config(state="normal")
        self.lbl_estado_login.config(text="")
        self.lbl_usuario.config(text=f"  {user}")
        self._poblar_bandeja(correos)
        self._mostrar_frame(self.frame_bandeja)
        self._iniciar_autorefresh()

    def _conexion_fallida(self, error):
        self.btn_conectar.config(state="normal")
        self.lbl_estado_login.config(text=f"Error: {error}", foreground="red")

    # ==================================================================
    # VISTA 2: BANDEJA DE ENTRADA
    # ==================================================================

    def _crear_vista_bandeja(self):
        frame = self.frame_bandeja

        # Barra superior
        barra = ttk.Frame(frame)
        barra.pack(fill="x", padx=10, pady=(10, 5))

        ttk.Label(barra, text="Usuario:", font=FUENTE_NEGOCIOS).pack(side="left")
        self.lbl_usuario = ttk.Label(barra, text="", font=FUENTE_NORMAL)
        self.lbl_usuario.pack(side="left")

        ttk.Button(barra, text="Cerrar Sesión",
                   command=self._on_logout).pack(side="right", padx=(5, 0))
        ttk.Button(barra, text="Redactar",
                   command=self._on_redactar).pack(side="right", padx=(5, 0))
        ttk.Button(barra, text="Actualizar",
                   command=self._on_actualizar).pack(side="right", padx=(5, 0))

        # Treeview bandeja
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("de", "asunto", "fecha")
        self.tree = ttk.Treeview(tree_frame, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("de", text="De")
        self.tree.heading("asunto", text="Asunto")
        self.tree.heading("fecha", text="Fecha")
        self.tree.column("de", width=200, minwidth=120)
        self.tree.column("asunto", width=300, minwidth=150)
        self.tree.column("fecha", width=180, minwidth=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("no_leido", font=(FUENTE_FAMILIA, 9, "bold"))
        self.tree.tag_configure("leido",    font=(FUENTE_FAMILIA, 9))

        self.tree.bind("<Double-1>", self._on_doble_clic_correo)

        # Área de lectura de correo
        lbl_detalle = ttk.Label(frame, text="Contenido del correo:", font=FUENTE_NEGOCIOS)
        lbl_detalle.pack(anchor="w", padx=10, pady=(5, 0))

        self.txt_lectura = tk.Text(frame, height=10, wrap="word", font=FUENTE_MONO,
                                   state="disabled", bg=COLOR_FONDO)
        self.txt_lectura.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _poblar_bandeja(self, correos):
        """Rellena el Treeview con la lista de correos preservando la selección."""
        self.correos_cache = correos
        sel_actual = self.tree.selection()
        uid_sel = sel_actual[0] if sel_actual else None

        self.tree.delete(*self.tree.get_children())
        for c in correos:
            tag = "leido" if c.get("leido", True) else "no_leido"
            self.tree.insert("", "end", iid=c["uid"],
                             values=(c["de"], c["asunto"], c["fecha"]),
                             tags=(tag,))

        if uid_sel and self.tree.exists(uid_sel):
            self.tree.selection_set(uid_sel)
            self.tree.see(uid_sel)

    def _on_doble_clic_correo(self, event):
        """Muestra el contenido del correo seleccionado y lo marca como leído."""
        sel = self.tree.selection()
        if not sel:
            return
        uid = sel[0]

        # Marcar visualmente como leído de inmediato
        self.tree.item(uid, tags=("leido",))
        for c in self.correos_cache:
            if c["uid"] == uid:
                c["leido"] = True
                break

        self.txt_lectura.config(state="normal")
        self.txt_lectura.delete("1.0", "end")
        self.txt_lectura.insert("1.0", "Cargando...")
        self.txt_lectura.config(state="disabled")

        def tarea():
            try:
                contenido = self.cliente.leer_correo(uid)
                self.cliente.marcar_leido(uid)
                self.root.after(0, lambda: self._mostrar_contenido(contenido))
            except Exception as e:
                self.root.after(0, lambda: self._mostrar_contenido(f"Error: {e}"))

        threading.Thread(target=tarea, daemon=True).start()

    def _mostrar_contenido(self, texto):
        self.txt_lectura.config(state="normal")
        self.txt_lectura.delete("1.0", "end")
        self.txt_lectura.insert("1.0", texto)
        self.txt_lectura.config(state="disabled")

    def _on_actualizar(self):
        """Refresca la bandeja de entrada."""
        def tarea():
            try:
                correos = self.cliente.obtener_bandeja()
                self.root.after(0, lambda: self._poblar_bandeja(correos))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))

        threading.Thread(target=tarea, daemon=True).start()

    def _on_logout(self):
        """Cierra sesión y vuelve al login."""
        self._detener_autorefresh()
        self.cliente.desconectar()
        self.tree.delete(*self.tree.get_children())
        self.txt_lectura.config(state="normal")
        self.txt_lectura.delete("1.0", "end")
        self.txt_lectura.config(state="disabled")
        self._mostrar_frame(self.frame_login)

    def _on_redactar(self):
        """Muestra la vista de redacción."""
        self.entry_para.delete(0, tk.END)
        self.entry_asunto_red.delete(0, tk.END)
        self.txt_cuerpo.delete("1.0", "end")
        self.lbl_estado_envio.config(text="")
        self._mostrar_frame(self.frame_redactar)

    # ==================================================================
    # VISTA 3: REDACTAR CORREO
    # ==================================================================

    def _crear_vista_redactar(self):
        frame = self.frame_redactar

        contenedor = ttk.Frame(frame, padding=15)
        contenedor.pack(fill="both", expand=True)

        ttk.Label(contenedor, text="Redactar Correo", font=FUENTE_TITULO).pack(
            anchor="w", pady=(0, 15))

        # Para
        fila_para = ttk.Frame(contenedor)
        fila_para.pack(fill="x", pady=3)
        ttk.Label(fila_para, text="Para:", font=FUENTE_NEGOCIOS, width=10).pack(side="left")
        self.entry_para = ttk.Entry(fila_para)
        self.entry_para.pack(side="left", fill="x", expand=True)

        # Asunto
        fila_asunto = ttk.Frame(contenedor)
        fila_asunto.pack(fill="x", pady=3)
        ttk.Label(fila_asunto, text="Asunto:", font=FUENTE_NEGOCIOS, width=10).pack(side="left")
        self.entry_asunto_red = ttk.Entry(fila_asunto)
        self.entry_asunto_red.pack(side="left", fill="x", expand=True)

        # Cuerpo
        ttk.Label(contenedor, text="Mensaje:", font=FUENTE_NEGOCIOS).pack(
            anchor="w", pady=(10, 3))
        self.txt_cuerpo = tk.Text(contenedor, wrap="word", font=FUENTE_MONO, height=12)
        self.txt_cuerpo.pack(fill="both", expand=True)

        # Botones
        fila_btns = ttk.Frame(contenedor)
        fila_btns.pack(fill="x", pady=(10, 0))

        self.btn_enviar = ttk.Button(fila_btns, text="Enviar", command=self._on_enviar)
        self.btn_enviar.pack(side="left", padx=(0, 10))
        ttk.Button(fila_btns, text="Cancelar",
                   command=lambda: self._mostrar_frame(self.frame_bandeja)).pack(side="left")

        self.lbl_estado_envio = ttk.Label(fila_btns, text="", font=FUENTE_NOTA)
        self.lbl_estado_envio.pack(side="left", padx=15)

    def _on_enviar(self):
        """Envía el correo redactado."""
        to = self.entry_para.get().strip()
        subject = self.entry_asunto_red.get().strip()
        body = self.txt_cuerpo.get("1.0", "end").strip()

        if not to or not subject:
            self.lbl_estado_envio.config(text="Destinatario y asunto son obligatorios.",
                                         foreground="red")
            return

        self.lbl_estado_envio.config(text="Enviando...", foreground=COLOR_ACCION)
        self.btn_enviar.config(state="disabled")

        def tarea():
            try:
                self.cliente.enviar_correo(
                    self.smtp_server, self.smtp_port,
                    self.smtp_user, self.smtp_password,
                    to, subject, body, self.smtp_security
                )
                self.root.after(0, self._envio_exitoso)
            except Exception as e:
                msg = str(e)
                self.root.after(0, lambda m=msg: self._envio_fallido(m))

        threading.Thread(target=tarea, daemon=True).start()

    def _envio_exitoso(self):
        self.btn_enviar.config(state="normal")
        self.lbl_estado_envio.config(text="Correo enviado correctamente.",
                                     foreground=COLOR_EXITO)
        self.root.after(2000, lambda: self._mostrar_frame(self.frame_bandeja))

    def _envio_fallido(self, error):
        self.btn_enviar.config(state="normal")
        self.lbl_estado_envio.config(text=f"Error: {error}", foreground="red")

    # ==================================================================
    # AUTO-REFRESCO
    # ==================================================================

    _INTERVALO_REFRESCO_MS = 1000

    def _iniciar_autorefresh(self):
        self._detener_autorefresh()
        self._autorefresh_id = self.root.after(
            self._INTERVALO_REFRESCO_MS, self._autorefresh_tick
        )

    def _autorefresh_tick(self):
        """Lanzado desde el hilo principal. Si ya hay refresco en curso, reintenta en el siguiente ciclo."""
        if self._refreshing:
            self._autorefresh_id = self.root.after(
                self._INTERVALO_REFRESCO_MS, self._autorefresh_tick
            )
            return

        self._refreshing = True

        def tarea():
            try:
                correos = self.cliente.obtener_bandeja()
                self.root.after(0, lambda: self._fin_autorefresh(correos))
            except Exception:
                self.root.after(0, lambda: self._fin_autorefresh(None))

        threading.Thread(target=tarea, daemon=True).start()

    def _fin_autorefresh(self, correos):
        """Siempre se ejecuta en el hilo principal."""
        self._refreshing = False
        if correos is not None:
            self._poblar_bandeja(correos)
        # Programar siguiente tick desde el hilo principal
        self._autorefresh_id = self.root.after(
            self._INTERVALO_REFRESCO_MS, self._autorefresh_tick
        )

    def _detener_autorefresh(self):
        if self._autorefresh_id is not None:
            self.root.after_cancel(self._autorefresh_id)
            self._autorefresh_id = None
        self._refreshing = False

    # ==================================================================
    # UTILIDADES
    # ==================================================================

    def cerrar(self):
        """Limpieza al cerrar la aplicación: para el auto-refresco y desconecta IMAP."""
        self._detener_autorefresh()
        self.cliente.desconectar()

    def _mostrar_frame(self, frame):
        """Levanta el frame indicado al frente."""
        frame.tkraise()
