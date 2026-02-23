import socket

from logica.red.servidor import APP_FIRMA, PUERTO_BROADCAST


def descubrir_servidores(timeout_sin_nuevos=10, callback=None, on_seen=None, stop_event=None):
    """Escucha broadcasts UDP para encontrar servidores disponibles.

    - callback(ip, puerto): llamado cuando se descubre un servidor nuevo.
    - on_seen(ip, puerto): llamado en cada broadcast valido (nuevos y ya conocidos).
    - timeout_sin_nuevos: segundos sin nuevos servidores antes de parar (default 10).
    - stop_event: threading.Event para cancelar la busqueda desde fuera.
    Retorna una lista de tuplas (ip, puerto).
    """
    import time
    print(f"[DEBUG CLI] Iniciando descubrimiento UDP en puerto {PUERTO_BROADCAST} (timeout_sin_nuevos={timeout_sin_nuevos}s)")
    servidores = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.settimeout(1)
    try:
        sock.bind(("", PUERTO_BROADCAST))
        print(f"[DEBUG CLI] Socket UDP enlazado a '':{PUERTO_BROADCAST}")
    except OSError as e:
        print(f"[DEBUG CLI] Error al enlazar UDP: {e}")
        sock.close()
        return servidores

    ultimo_encontrado = time.time()
    try:
        while True:
            if stop_event and stop_event.is_set():
                print(f"[DEBUG CLI] Busqueda cancelada externamente")
                break
            if time.time() - ultimo_encontrado >= timeout_sin_nuevos:
                print(f"[DEBUG CLI] {timeout_sin_nuevos}s sin nuevos servidores, finalizando")
                break
            try:
                datos, direccion = sock.recvfrom(1024)
                mensaje = datos.decode("utf-8")
                print(f"[DEBUG CLI] Paquete UDP recibido de {direccion}: {mensaje!r}")
                if verificar_firma(mensaje):
                    partes = mensaje.split("|")
                    if len(partes) == 2:
                        puerto_servidor = int(partes[1])
                        ip = direccion[0]
                        if on_seen:
                            on_seen(ip, puerto_servidor)
                        entrada = (ip, puerto_servidor)
                        if entrada not in servidores:
                            servidores.append(entrada)
                            ultimo_encontrado = time.time()
                            print(f"[DEBUG CLI] Servidor descubierto: {ip}:{puerto_servidor}")
                            if callback:
                                callback(ip, puerto_servidor)
                else:
                    print(f"[DEBUG CLI] Firma no valida, ignorado")
            except socket.timeout:
                pass
    finally:
        sock.close()

    print(f"[DEBUG CLI] Descubrimiento finalizado: {len(servidores)} servidor(es)")
    return servidores


def conectar_servidor(ip, puerto, clave_acceso):
    """Conecta al servidor y envia la clave de autenticacion.

    La clave debe tener el formato: puerto#contraseña_alfabetica
    """
    print(f"[DEBUG CLI] Conectando TCP a {ip}:{puerto}")
    print(f"[DEBUG CLI] Clave a enviar: {clave_acceso!r}")
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.settimeout(10)

    try:
        cliente.connect((ip, puerto))
        print(f"[DEBUG CLI] Conexion TCP establecida")
        cliente.sendall(clave_acceso.encode("utf-8"))
        print(f"[DEBUG CLI] Clave enviada, esperando respuesta...")
        respuesta = cliente.recv(1024).decode("utf-8")
        print(f"[DEBUG CLI] Respuesta recibida: {respuesta!r}")
    except (OSError, socket.timeout) as e:
        print(f"[DEBUG CLI] Error en conexion/autenticacion: {e}")
        cliente.close()
        return None, ""

    if respuesta.startswith("OK"):
        cliente.settimeout(None)
        extra = respuesta[2:]
        print(f"[DEBUG CLI] Autenticacion exitosa, datos extra: {extra!r}")
        return cliente, extra
    else:
        print(f"[DEBUG CLI] Autenticacion fallida: {respuesta!r}")
        cliente.close()
        return None, ""


def verificar_firma(mensaje):
    """Verifica que el mensaje recibido contenga la firma de la aplicacion."""
    return APP_FIRMA in mensaje