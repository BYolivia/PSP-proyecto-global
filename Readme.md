# ProyectoGlobal: Aplicaciones Multi-Funcionales

## Indice

- [Descripción del Proyecto](#descripción-del-proyecto)
- [Requisitos e Instalación](#requisitos-e-instalación)
- [Funcionalidades Implementadas](#funcionalidades-implementadas)
  - [T1. Multiprocesos](#t1-multiprocesos)
  - [T2. Multihilos (Concurrencia)](#t2-multihilos-concurrencia)
  - [T3. Sockets (Comunicación de Red Básica)](#t3-sockets-comunicación-de-red-básica)
  - [T4. Servicios en Red (Aplicaciones Avanzadas)](#t4-servicios-en-red-aplicaciones-avanzadas)
- [Hoja de Ruta (Próximas Evaluaciones)](#hoja-de-ruta-próximas-evaluaciones)
  - [T5. Seguridad](#t5-seguridad)

---

## Descripción del Proyecto

**ProyectoGlobal** es una aplicación de escritorio desarrollada en Python que integra diversas funcionalidades relacionadas con el **multiproceso**, la **concurrencia (multihilo)**, la **comunicación en red mediante sockets** y los **servicios de red**.

La aplicación sirve como un panel de control que permite al usuario gestionar procesos, visualizar recursos del sistema, ejecutar tareas de automatización, chatear en red local, gestionar correos electrónicos, y acceder a mini-juegos, scraping y reproducción multimedia.

---

## Requisitos e Instalación

Necesitas tener **Python 3** y **VLC** instalados en el sistema.

```bash
# Dependencia del sistema (Linux)
sudo apt install python3-tk vlc
```

### Clonar el repositorio

```bash
git clone https://github.com/BYolivia/PSP-proyecto-global.git
cd PSP-proyecto-global
```

### Crear el entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Ejecutar la aplicación

```bash
python -m ProyectoGlobal
```

### Salir del entorno virtual

```bash
deactivate
```

> [!NOTE]
> La próxima vez que abras el proyecto solo necesitas activar el entorno (`source venv/bin/activate`) y ejecutarlo.

---

## Funcionalidades Implementadas

### T1. Multiprocesos

[Video de la demostración](https://youtu.be/37-wJIXNZAg)

| **Estado** | **Característica**                                                                                               |
|------------|------------------------------------------------------------------------------------------------------------------|
| **Done**   | Lanzamiento de **aplicaciones externas** con parámetros (ej. navegadores con URL).                               |
| **Done**   | Implementación de **Copias de seguridad** mediante la ejecución de scripts Powershell (`.ps1`).                  |
| **Done**   | Visualización de **recursos del sistema** (memoria, procesador, hilos) usando gráficas `matplotlib`.             |
| **Done**   | **Editor de texto** básico (estilo Notepad).                                                                     |
| **Done**   | Hilo concurrente para contar el **tráfico de red** (entrada/salida en KB) utilizando `psutil.net_io_counters()`. |
| **Done**   | Apertura directa de **VS Code** desde la interfaz del programa.                                                  |

### T2. Multihilos (Concurrencia)

| **Estado** | **Característica**                                                                                                    |
|------------|-----------------------------------------------------------------------------------------------------------------------|
| **Done**   | Visualización de **Fecha y Hora** del sistema.                                                                        |
| **Done**   | Obtención y visualización de la **Temperatura local**.                                                                |
| **Done**   | Sistema de **Alarma** programable (aviso visual y sonoro).                                                            |
| **Done**   | Funcionalidad de **Scraping** para extracción de datos web.                                                           |
| **Done**   | **Mini-juego** (Carrera de camellos / Buscaminas) aplicando resolución de sincronización (para evitar interbloqueos). |
| **Done**   | **Música de fondo** (reproducción de mp3 o midi) utilizando `python-vlc`.                                             |

### T3. Sockets (Comunicación de Red Básica)

| **Estado** | **Característica**                                                                                                                  |
|------------|-------------------------------------------------------------------------------------------------------------------------------------|
| **Done**   | **Chat TCP** multijugador: el servidor acepta múltiples clientes simultáneos y retransmite los mensajes a todos (broadcast interno). |
| **Done**   | **Servidor TCP** con autenticación mediante clave generada aleatoriamente (puerto + contraseña alfabética).                          |
| **Done**   | **Descubrimiento automático por UDP**: el servidor emite broadcasts UDP para que los clientes encuentren la sesión sin configuración manual. |
| **Done**   | **Gestión de streams**: recepción y envío de datos en bloques vía `recv`/`sendall` en hilos dedicados por cliente.                  |
| **Done**   | **Interfaz gráfica del chat** con selector de rol (servidor / cliente), lista de servidores descubiertos y campo de mensajes.        |

### T4. Servicios en Red (Aplicaciones Avanzadas)

| **Estado** | **Característica**                                                                                                         |
|------------|----------------------------------------------------------------------------------------------------------------------------|
| **Done**   | **Cliente de Correo IMAP** con lectura de bandeja de entrada (últimos 100 correos), soporte de flags de leído/no leído.    |
| **Done**   | **Cliente SMTP** para envío de correos, compatible con los modos **SSL**, **STARTTLS** y sin cifrado.                      |
| **Done**   | Soporte completo de **SSL/TLS** en las conexiones IMAP y SMTP.                                                             |
| **Done**   | **Persistencia de credenciales** en archivo `.env` (servidor, puertos IMAP/SMTP, usuario, contraseña y modo de seguridad). |
| **Done**   | **Interfaz estilo Gmail**: lista de correos, vista de detalle, botón de respuesta y navegación hacia atrás.                |
| **Done**   | **Servidor de radio online** con reproducción de streams mediante `python-vlc`.                                            |

---

## Hoja de Ruta (Próximas Evaluaciones)

### T5. Seguridad

1. Manejo de **Autenticación y Roles** de usuario.

2. Implementación de **Logs** de actividad.

3. Cálculo y verificación de **HASH** aplicado a ficheros.

4. Técnicas de **Cifrado**.

    - Algoritmos **DES** y **AES**.

    - Cifrado Simétrico y **RSA** (Cifrado Asimétrico).

5. Implementación de **Firma Digital**.

6. Configuración y uso de **SSL/TLS**.
