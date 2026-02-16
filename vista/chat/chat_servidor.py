import threading
from vista.chat.chat_base import ChatBase
from logica.red.servidor import iniciar_servidor, autenticar_cliente
from logica.red.selector import obtener_ip_local

PREFIJO_NOMBRE = "__NOMBRE__:"


class ChatServidorPanel(ChatBase):
    """Vista de chat para el rol de servidor."""

    def __init__(self, parent, root, *args, **kwargs):
        super().__init__(parent, root, *args, **kwargs)
        self.servidor = None
        self.clientes = []
        self.clave_acceso = None
        self.broadcast_stop = None
        self.contador_clientes = 0
        self.crear_interfaz_chat(
            self, titulo="Chat - Servidor",
            boton_accion_texto="Cerrar Servidor",
            boton_accion_callback=self.cerrar_y_volver
        )
        self.iniciar()

    def iniciar(self):
        ip = obtener_ip_local()
        self.servidor, puerto, contrasena_alfa, self.broadcast_stop = iniciar_servidor()
        self.clave_acceso = f"{puerto}#{contrasena_alfa}"
        print(f"[DEBUG SRV-GUI] Servidor iniciado: ip={ip} puerto={puerto} clave={self.clave_acceso}")
        self.agregar_mensaje_sistema(f"Servidor iniciado en {ip}")
        self.agregar_mensaje_sistema(f"Clave de acceso: {self.clave_acceso}")
        self.agregar_mensaje_sistema("Esperando clientes...")

        hilo = threading.Thread(target=self.aceptar_clientes, daemon=True)
        hilo.start()

    def aceptar_clientes(self):
        print("[DEBUG SRV-GUI] Esperando conexiones de clientes...")
        while self.servidor:
            try:
                conn, addr = self.servidor.accept()
                print(f"[DEBUG SRV-GUI] Conexion entrante de {addr[0]}:{addr[1]}")
                datos = conn.recv(1024).decode("utf-8")
                print(f"[DEBUG SRV-GUI] Datos de autenticacion recibidos: {datos!r}")
                if autenticar_cliente(datos, self.clave_acceso):
                    conn.sendall("OK".encode("utf-8"))
                    self.contador_clientes += 1
                    nombre = f"Cliente {self.contador_clientes}"
                    conn.sendall(f"{PREFIJO_NOMBRE}{nombre}".encode("utf-8"))
                    print(f"[DEBUG SRV-GUI] Cliente autenticado como {nombre!r}, enviado OK + nombre")
                    self.clientes.append(conn)
                    self.root.after(0, self.agregar_mensaje_sistema, f"{nombre} conectado")
                    hilo = threading.Thread(target=self.recibir_de_cliente, args=(conn, nombre), daemon=True)
                    hilo.start()
                else:
                    conn.sendall("DENIED".encode("utf-8"))
                    conn.close()
                    etiqueta = f"{addr[0]}:{addr[1]}"
                    print(f"[DEBUG SRV-GUI] Cliente {etiqueta} rechazado (clave incorrecta)")
                    self.root.after(0, self.agregar_mensaje_sistema, f"Cliente {etiqueta} rechazado")
            except OSError as e:
                print(f"[DEBUG SRV-GUI] Error en accept: {e}")
                break

    def recibir_de_cliente(self, conn, nombre):
        print(f"[DEBUG SRV-GUI] Hilo de recepcion iniciado para {nombre}")
        try:
            while True:
                datos = conn.recv(4096)
                if not datos:
                    print(f"[DEBUG SRV-GUI] {nombre} envio datos vacios (desconexion)")
                    break
                mensaje = datos.decode("utf-8")
                print(f"[DEBUG SRV-GUI] Mensaje de {nombre}: {mensaje!r}")
                self.root.after(0, self.agregar_mensaje, nombre, mensaje)
                self.difundir(mensaje, nombre, conn)
        except (ConnectionResetError, OSError) as e:
            print(f"[DEBUG SRV-GUI] Error recibiendo de {nombre}: {e}")
        finally:
            if conn in self.clientes:
                self.clientes.remove(conn)
            conn.close()
            self.root.after(0, self.agregar_mensaje_sistema, f"{nombre} desconectado")

    def difundir(self, mensaje, remitente, origen):
        """Envia un mensaje a todos los clientes excepto al que lo envio."""
        datos = f"{remitente}: {mensaje}".encode("utf-8")
        for cliente in self.clientes[:]:
            if cliente is not origen:
                try:
                    cliente.sendall(datos)
                except OSError:
                    self.clientes.remove(cliente)

    def enviar_mensaje(self, event=None):
        mensaje = self.chat_input_entry.get().strip()
        if not mensaje:
            return "break" if event else None

        self.chat_input_entry.delete(0, "end")
        self.agregar_mensaje("SERVIDOR", mensaje)

        datos = f"SERVIDOR: {mensaje}".encode("utf-8")
        for cliente in self.clientes[:]:
            try:
                cliente.sendall(datos)
            except OSError:
                self.clientes.remove(cliente)

        return "break" if event else None

    def cerrar_y_volver(self):
        """Cierra el servidor y vuelve al selector."""
        self.cerrar_conexion()
        parent = self.master
        self.destroy()
        if hasattr(parent, 'volver_al_selector'):
            parent.volver_al_selector()

    def cerrar_conexion(self):
        if self.broadcast_stop:
            self.broadcast_stop.set()
        if self.servidor:
            self.servidor.close()
            self.servidor = None
        for cliente in self.clientes:
            try:
                cliente.close()
            except OSError:
                pass
        self.clientes.clear()
