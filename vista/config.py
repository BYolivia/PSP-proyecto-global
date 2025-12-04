# Módulo: vista/config.py

# --- CONSTANTES GENERALES ---

# Dimensiones y Tiempos
ANCHO_PANEL_LATERAL = 300
INTERVALO_RELOJ_MS = 1000
INTERVALO_CLIMA_MS = 60000
INTERVALO_RECURSOS_MS = 1000
ANCHO_CARACTERES_PANEL_LATERAL = 35

# --- CONSTANTES DE ESTILO (Colores) ---

COLOR_FONDO = "#f9f9f9"        # Fondo principal
COLOR_ACCION = "#0078d4"       # Azul para botones de acción/texto principal
COLOR_ACCION_HOVER = "#005a9e" # Azul oscuro para estado activo/hover
COLOR_ACCION_PRESSED = "#003c6e"# Azul muy oscuro para estado presionado
COLOR_EXITO = "#4CAF50"        # Verde para mensajes de éxito/notas
COLOR_ADVERTENCIA = "#ffc107"   # Amarillo para advertencias/chat
COLOR_TEXTO = "#333333"        # Texto oscuro principal
COLOR_BLANCO = "white"         # Fondo de áreas de contenido, texto en botones

# --- CONSTANTES DE FUENTE ---

# Familia de fuente principal
FUENTE_FAMILIA = 'Arial'

# Tamaños y Estilos
FUENTE_NORMAL = (FUENTE_FAMILIA, 9)
FUENTE_NEGOCIOS = (FUENTE_FAMILIA, 10, 'bold') # Para botones y pestañas
FUENTE_TITULO = (FUENTE_FAMILIA, 18, 'bold')  # Para títulos grandes (ej: Chat)
FUENTE_NOTA = (FUENTE_FAMILIA, 9, 'italic')   # Para notas y texto de estado
FUENTE_MONO = ('Consolas', 10)                 # Fuente monoespaciada para código/logs