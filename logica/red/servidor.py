import socket
import threading
import time
import random
import string


# Firma de la aplicacion para identificacion
APP_FIRMA = "PSYP_ProyectoGlobal_v1"

# Rango de puertos validos (evita puertos conocidos 0-1023 y registrados 1024-49151)
RANGO_PUERTOS = (49152, 65535)


def _obtener_puertos_en_uso():
    """Lee /proc/net/tcp y /proc/net/udp para obtener los puertos en uso."""
    puertos = set()
    for archivo in ("/proc/net/tcp", "/proc/net/udp", "/proc/net/tcp6", "/proc/net/udp6"):
        try:
            with open(archivo, "r") as f:
                for linea in f.readlines()[1:]:
                    partes = linea.split()
                    puerto = int(partes[1].split(":")[1], 16)
                    puertos.add(puerto)
        except (FileNotFoundError, PermissionError):
            pass
    return puertos


def _puerto_disponible(puerto, puertos_en_uso=None):
    """Comprueba si un puerto esta libre en TCP y UDP."""
    if puertos_en_uso and puerto in puertos_en_uso:
        return False
    for tipo in (socket.SOCK_STREAM, socket.SOCK_DGRAM):
        with socket.socket(socket.AF_INET, tipo) as s:
            try:
                s.bind(("0.0.0.0", puerto))
            except OSError:
                return False
    return True


def generar_puerto():
    """Genera un puerto aleatorio disponible en el rango dinamico/privado."""
    puertos_en_uso = _obtener_puertos_en_uso()
    while True:
        puerto = random.randint(*RANGO_PUERTOS)
        if _puerto_disponible(puerto, puertos_en_uso):
            return puerto


def generar_contrasena_alfabetica(longitud=6):
    """Genera una contraseña alfabetica aleatoria."""
    return "".join(random.choices(string.ascii_lowercase, k=longitud))


def iniciar_servidor():
    """Inicia el servidor en un puerto TCP aleatorio disponible.

    Retorna (servidor_socket, puerto, contrasena, broadcast_stop_event).
    """
    puerto = generar_puerto()
    contrasena = generar_contrasena_alfabetica()
    print(f"[DEBUG SRV] Puerto generado: {puerto}")
    print(f"[DEBUG SRV] Contrasena alfabetica: {contrasena}")

    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(("0.0.0.0", puerto))
    servidor.listen(5)
    print(f"[DEBUG SRV] Socket TCP escuchando en 0.0.0.0:{puerto}")

    broadcast_stop = threading.Event()
    hilo_broadcast = threading.Thread(target=_broadcast_presencia, args=(puerto, broadcast_stop), daemon=True)
    hilo_broadcast.start()
    print(f"[DEBUG SRV] Hilo broadcast iniciado en UDP:{PUERTO_BROADCAST}")

    return servidor, puerto, contrasena, broadcast_stop


# Puerto fijo para descubrimiento UDP
PUERTO_BROADCAST = 64738


def _broadcast_presencia(puerto, stop_event):
    """Envia broadcasts UDP para que los clientes descubran el servidor."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    mensaje = f"{APP_FIRMA}|{puerto}".encode("utf-8")

    while not stop_event.is_set():
        try:
            sock.sendto(mensaje, ("<broadcast>", PUERTO_BROADCAST))
            print(f"[DEBUG SRV] Broadcast enviado a <broadcast>:{PUERTO_BROADCAST}")
        except OSError as e:
            print(f"[DEBUG SRV] Error broadcast <broadcast>: {e}")
        try:
            sock.sendto(mensaje, ("127.255.255.255", PUERTO_BROADCAST))
            print(f"[DEBUG SRV] Broadcast enviado a 127.255.255.255:{PUERTO_BROADCAST}")
        except OSError as e:
            print(f"[DEBUG SRV] Error broadcast 127.255.255.255: {e}")
        stop_event.wait(2)
    sock.close()


def autenticar_cliente(datos_recibidos, contrasena):
    """Verifica que el cliente envie la contrasena correcta."""
    resultado = datos_recibidos.strip() == contrasena
    print(f"[DEBUG SRV] Autenticacion: recibido={datos_recibidos.strip()!r} esperado={contrasena!r} resultado={resultado}")
    return resultado