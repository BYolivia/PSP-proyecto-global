#!/bin/bash
# SCRIPT: res/scripts/sript.sh

# --- CONFIGURACIÓN DE RUTAS ---
USER_HOME=~
# CAMBIO CLAVE: Usamos 'Imágenes' en lugar de 'Pictures'
SOURCE_FOLDER="$USER_HOME/Imágenes"
DESTINATION_BASE_PATH="$USER_HOME/BACKUPS"
# ------------------------------

# 1. Verificar que la carpeta de o2rigen exista
if [ ! -d "$SOURCE_FOLDER" ]; then
    echo "ERROR: La carpeta de origen '$SOURCE_FOLDER' no existe." >&2
    exit 1
fi

# 2. Generar el nombre de la carpeta con la fecha y hora (Formato: backup-AAAA-MM-DD_HH-MM-SS)
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FOLDER_NAME="backup-$TIMESTAMP"

# 3. Crear la ruta final de destino
FINAL_DESTINATION_PATH="$DESTINATION_BASE_PATH/$BACKUP_FOLDER_NAME"

# 4. Crear la carpeta base 'BACKUPS' si no existe y luego la carpeta de la copia
mkdir -p "$FINAL_DESTINATION_PATH"

if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear la carpeta de destino: $FINAL_DESTINATION_PATH" >&2
    exit 1
fi

# 5. Ejecutar la copia recursiva con rsync
echo "Iniciando copia de seguridad de '$SOURCE_FOLDER' a '$FINAL_DESTINATION_PATH'..."
# -a: modo archivo (preserva permisos, dueño, timestamps, etc.)
# -v: modo verbose (muestra progreso/qué está copiando)
# -z: comprime los datos durante la transferencia (útil si copias a red, pero no hace daño aquí)
# --exclude: ignora la carpeta de destino si por alguna razón ya existe dentro del origen (seguridad)
rsync -avz --exclude 'BACKUPS' "$SOURCE_FOLDER/" "$FINAL_DESTINATION_PATH/"

# $?: guarda el código de salida del último comando ejecutado (rsync)
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Copia de seguridad completada con éxito."
    echo "   Origen: $SOURCE_FOLDER"
    echo "   Destino: $FINAL_DESTINATION_PATH"
    exit 0
else
    echo "ERROR: La copia de seguridad falló durante rsync." >&2
    exit 1
fi