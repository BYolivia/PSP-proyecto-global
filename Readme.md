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

Necesitas tener **Python 3** y **VLC** instalados en el sistema.

```bash
# Dependencia del sistema (Linux)
sudo apt install python3-tk vlc
```

### 🔽 Clonar el repositorio

```bash
git clone https://github.com/BYolivia/PSP-proyecto-global.git
cd PSP-proyecto-global
```

### 📦 Crear el entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ▶️ Ejecutar la aplicación

```bash
python -m ProyectoGlobal
```

### ⏹️ Salir del entorno virtual

```bash
deactivate
```

> [!NOTE]
> La próxima vez que abras el proyecto solo necesitas activar el entorno (`source venv/bin/activate`) y ejecutarlo.


---

## ✅ Funcionalidades Implementadas (Evaluaciones Anteriores)

### T1. Multiprocesos

[Video de la demostracion](https://youtu.be/37-wJIXNZAg)

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





