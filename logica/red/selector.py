import socket
import sys
import threading

from logica.red.servidor import iniciar_servidor, autenticar_cliente, PUERTO_BROADCAST
from logica.red.cliente import conectar_servidor


def obtener_ip_local():
    """Obtiene la IP local de la maquina en la red."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"


def modo_servidor():
    servidor, puerto, contrasena_alfa, _broadcast_stop = iniciar_servidor()
    clave_acceso = f"{puerto}#{contrasena_alfa}"
    ip = obtener_ip_local()
    print(f"[SERVIDOR] IP: {ip}")
    print(f"[SERVIDOR] Escuchando en puerto {puerto}")
    print(f"[SERVIDOR] Clave de acceso: {clave_acceso}")
    print("[SERVIDOR] Esperando clientes...\n")

    try:
        while True:
            conn, addr = servidor.accept()
            datos = conn.recv(1024).decode("utf-8")
            if autenticar_cliente(datos, clave_acceso):
                conn.sendall("OK".encode("utf-8"))
                print(f"[SERVIDOR] Cliente {addr[0]}:{addr[1]} autenticado")
                hilo = threading.Thread(target=manejar_cliente, args=(conn, addr), daemon=True)
                hilo.start()
            else:
                conn.sendall("DENIED".encode("utf-8"))
                conn.close()
                print(f"[SERVIDOR] Cliente {addr[0]}:{addr[1]} rechazado (clave incorrecta)")
    except KeyboardInterrupt:
        print("\n[SERVIDOR] Cerrando...")
        servidor.close()


def manejar_cliente(conn, addr):
    etiqueta = f"{addr[0]}:{addr[1]}"
    try:
        while True:
            datos = conn.recv(4096)
            if not datos:
                break
            mensaje = datos.decode("utf-8")
            print(f"[{etiqueta}] {mensaje}")
            conn.sendall(f"Echo: {mensaje}".encode("utf-8"))
    except (ConnectionResetError, OSError):
        pass
    finally:
        print(f"[SERVIDOR] Cliente {etiqueta} desconectado")
        conn.close()


def buscar_servidores():
    """Busca servidores con reintentos. Retorna lista de servidores o None."""
    MAX_INTENTOS = 3
    TIMEOUT = 5

    for intento in range(1, MAX_INTENTOS + 1):
        print(f"\n[CLIENTE] Intento {intento}/{MAX_INTENTOS} - Escaneando red durante {TIMEOUT}s...")
        print(f"[CLIENTE] Puerto de descubrimiento (UDP): {PUERTO_BROADCAST}")
        print(f"[CLIENTE] Esperando broadcast de servidores", end="", flush=True)

        # Animacion simple mientras espera
        servidores = []
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.settimeout(1)
        sock.bind(("", PUERTO_BROADCAST))

        for segundo in range(TIMEOUT):
            try:
                datos, direccion = sock.recvfrom(1024)
                mensaje = datos.decode("utf-8")
                from logica.red.cliente import verificar_firma
                if verificar_firma(mensaje):
                    partes = mensaje.split("|")
                    if len(partes) == 2:
                        puerto_servidor = int(partes[1])
                        entrada = (direccion[0], puerto_servidor)
                        if entrada not in servidores:
                            servidores.append(entrada)
                            print(f"\n[CLIENTE] Servidor encontrado: {entrada[0]}:{entrada[1]}")
            except socket.timeout:
                print(".", end="", flush=True)
        sock.close()

        if servidores:
            print(f"\n[CLIENTE] {len(servidores)} servidor(es) encontrado(s)")
            return servidores

        print(f"\n[CLIENTE] No se encontraron servidores en el intento {intento}")

    # Tras 3 intentos fallidos, preguntar
    while True:
        opcion = input("\n[CLIENTE] No se encontraron servidores. (r)eintentar / (s)alir: ").strip().lower()
        if opcion == "r":
            return buscar_servidores()
        elif opcion == "s":
            return None
        print("[CLIENTE] Opcion no valida. Usa 'r' o 's'.")


def modo_cliente():
    ip_local = obtener_ip_local()
    print(f"[CLIENTE] IP local: {ip_local}")
    servidores = buscar_servidores()
    if not servidores:
        print("[CLIENTE] Saliendo.")
        return

    if len(servidores) == 1:
        seleccion = 0
    else:
        print("\nServidores disponibles:")
        for i, (ip, puerto) in enumerate(servidores, 1):
            print(f"  {i}. {ip}:{puerto}")
        try:
            num = int(input("\nElige servidor (numero): "))
            seleccion = num - 1
            if seleccion < 0 or seleccion >= len(servidores):
                print("[CLIENTE] Seleccion invalida.")
                return
        except ValueError:
            print("[CLIENTE] Entrada invalida.")
            return

    ip, puerto = servidores[seleccion]
    print(f"\n[CLIENTE] Conectando a {ip}:{puerto}...")
    contrasena = input("[CLIENTE] Introduce la contrasena: ")

    cliente, _ = conectar_servidor(ip, puerto, contrasena)
    if not cliente:
        print("[CLIENTE] Autenticacion fallida o conexion rechazada.")
        return

    print(f"[CLIENTE] Conectado correctamente a {ip}:{puerto}")
    print("[CLIENTE] Escribe mensajes (Ctrl+C para salir):\n")

    def recibir():
        try:
            while True:
                datos = cliente.recv(4096)
                if not datos:
                    print("\n[CLIENTE] El servidor cerro la conexion.")
                    break
                print(f"[SERVIDOR] {datos.decode('utf-8')}")
        except (ConnectionResetError, OSError):
            print("\n[CLIENTE] Conexion perdida con el servidor.")

    hilo = threading.Thread(target=recibir, daemon=True)
    hilo.start()

    try:
        while True:
            mensaje = input()
            if mensaje:
                cliente.sendall(mensaje.encode("utf-8"))
    except (KeyboardInterrupt, EOFError):
        print("\n[CLIENTE] Desconectando...")
        cliente.close()


if __name__ == "__main__":
    print("=== Selector de Red ===")
    print("1. Servidor")
    print("2. Cliente")

    opcion = input("\nElige rol (1/2): ").strip()

    if opcion == "1":
        modo_servidor()
    elif opcion == "2":
        modo_cliente()
    else:
        print("Opcion invalida.")
        sys.exit(1)