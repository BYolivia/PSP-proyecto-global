
# 🚀 ProyectoGlobal: Aplicaciones Multi-Funcionales

## Indice ##
- [📄 Descripción del Proyecto](#-descripción-del-proyecto)
- [🛠️ Requisitos e Instalación](#-requisitos-e-instalación)
- [✅ Funcionalidades Implementadas (Evaluaciones Anteriores)](#-funcionalidades-implementadas-evaluaciones-anteriores)
  - [T1. Multiprocesos](#t1-multiprocesos)
  - [T2. Multihilos (Concurrencia)](#t2-multihilos-concurrencia)
- [📅 Hoja de Ruta (Próximas Evaluaciones)](#-hoja-de-ruta-próximas-evaluaciones)
  - [T3. Sockets (Comunicación de Red Básica)](#t3-sockets-comunicación-de-red-básica)
  - [T4. Servicios en Red (Aplicaciones Avanzadas)](#t4-servicios-en-red-aplicaciones-avanzadas)
  - [T5. Seguridad](#t5-seguridad)
## 📄 Descripción del Proyecto

**ProyectoGlobal** es una aplicación de escritorio desarrollada en Python que integra diversas funcionalidades clave relacionadas con el **multiproceso**, la **concurrencia (multihilo)** y la **interacción de sistemas (sockets/redes)**.

La aplicación sirve como un panel de control que permite al usuario gestionar procesos, visualizar recursos del sistema, ejecutar tareas de automatización, y acceder a mini-juegos y herramientas de scraping/reproducción multimedia.

---

## 🛠️ Requisitos e Instalación

Para ejecutar la aplicación, debes tener **Python 3** instalado. A continuación se detallan los paquetes necesarios y su comando de instalación.

### 📦 Dependencias de Python

Se recomienda instalar las dependencias en un **entorno virtual** (`venv`).

| **Paquete**              | **Instalación**                       | **Uso principal**                          |
| ------------------------ | ------------------------------------- | ------------------------------------------ |
| **tkinter**              | `sudo apt install python3-tk` (Linux) | Interfaz gráfica (GUI)                     |
| **matplotlib**           | `pip install matplotlib`              | Gráficas de recursos del sistema           |
| **psutil**               | `pip install psutil`                  | Monitorización del sistema (CPU, RAM, red) |
| **python-vlc**           | `pip install python-vlc`              | Reproducción de audio/música               |
| **beautifulsoup4** (bs4) | `pip install bs4`                     | Extracción de datos (Scraping)             |
| **requests**             | `pip install requests`                | Solicitudes HTTP (para Scraping)           |

### ⚙️ Como Ejecutar

Una vez instaladas las dependencias, ejecuta la aplicación desde el directorio principal del proyecto (el directorio que contiene la carpeta `ProyectoGlobal`):

Bash


> [!NOTE]
> Asegúrate de ejecutar este comando desde la carpeta del proyecto tras haber instalado las dependencias.


Bash `python3 __main__.py`

o si es ejecutado desde el IDE pyCharm puede darle al boton de play <svg width="1em" height="1em" viewBox="0 0 16 16" fill="green" style="vertical-align: middle;">
  <path d="M11.596 8.697l-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.803.803 0 0 1 0 1.393z"/>
</svg> para ejecutar el proyecto habiendo seleccionado el archivo \_\_main\_\_.py


---

## ✅ Funcionalidades Implementadas (Evaluaciones Anteriores)

### T1. Multiprocesos

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

---

## 📅 Hoja de Ruta (Próximas Evaluaciones)

### T3. Sockets (Comunicación de Red Básica)

1. Implementación de un **Chat** simple.
    
2. Desarrollo de un **Servidor TCP** básico.
    
3. Desarrollo de un **Servidor UDP** básico.
    
4. Manejo de **Streams** de datos.
    
5. Uso de **Asyncio** para operaciones concurrentes en red.
    

### T4. Servicios en Red (Aplicaciones Avanzadas)

1. **Cliente de Correo Electrónico** (usando POP3 y/o IMAP).
    
2. Implementación del protocolo **SMTP**.
    
3. **Cliente FTP** para transferencia de ficheros.
    
4. **Cliente HTTP** para peticiones web.
    
5. **Servidor de música / radio online**.
    
6. Juegos multijugador: **Adivina número** (cliente único/múltiple) y **Piedra, Papel o Tijera**.
    
7. Consumo de una **API REST** externa.
    
8. Implementación de **Servicios API REST** propios.
    
9. Desarrollo de **Microservicios**.
    

### T5. Seguridad

1. Manejo de **Autenticación y Roles** de usuario.
    
2. Implementación de **Logs** de actividad.
    
3. Cálculo y verificación de **HASH** aplicado a ficheros.
    
4. Técnicas de **Cifrado**.
    
    - Algoritmos **DES** y **AES**.
        
    - Cifrado Simétrico y **RSA** (Cifrado Asimétrico).
        
5. Implementación de **Firma Digital**.
    
6. Configuración y uso de **SSL/TLS**.