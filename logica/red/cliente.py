import socket

from logica.red.servidor import APP_FIRMA, PUERTO_BROADCAST


def descubrir_servidores(timeout=5):
    """Escucha broadcasts UDP para encontrar servidores disponibles.

    Retorna una lista de tuplas (ip, puerto) de servidores encontrados.
    """
    print(f"[DEBUG CLI] Iniciando descubrimiento UDP en puerto {PUERTO_BROADCAST} (timeout={timeout}s)")
    servidores = []
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.settimeout(timeout)
    try:
        sock.bind(("", PUERTO_BROADCAST))
        print(f"[DEBUG CLI] Socket UDP enlazado a '':{PUERTO_BROADCAST}")
    except OSError as e:
        print(f"[DEBUG CLI] Error al enlazar UDP: {e}")
        sock.close()
        return servidores

    try:
        while True:
            datos, direccion = sock.recvfrom(1024)
            mensaje = datos.decode("utf-8")
            print(f"[DEBUG CLI] Paquete UDP recibido de {direccion}: {mensaje!r}")
            if verificar_firma(mensaje):
                partes = mensaje.split("|")
                if len(partes) == 2:
                    puerto_servidor = int(partes[1])
                    entrada = (direccion[0], puerto_servidor)
                    if entrada not in servidores:
                        servidores.append(entrada)
                        print(f"[DEBUG CLI] Servidor descubierto: {entrada[0]}:{entrada[1]}")
            else:
                print(f"[DEBUG CLI] Firma no valida, ignorado")
    except socket.timeout:
        print(f"[DEBUG CLI] Timeout alcanzado")
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