out-null
cls

# SCRIPT: backup_script.ps1

# --- CONFIGURACIÓN DE RUTAS ---
# La carpeta de ORIGEN es la carpeta 'Pictures' (Imágenes) del usuario
$SourceFolder = Join-Path $env:USERPROFILE "Pictures"

# La carpeta base de DESTINO es 'BACKUPS' dentro del directorio raíz del usuario
$DestinationBasePath = Join-Path $env:USERPROFILE "BACKUPS"
# ------------------------------

# 1. Verificar que la carpeta de origen exista
if (-not (Test-Path $SourceFolder)) {
    Write-Error "ERROR: La carpeta de origen '$SourceFolder' (Imágenes) no existe."
    exit 1 # Código de error
}

# 2. Generar el nombre de la carpeta con la fecha y hora (Formato: backup-AAAA-MM-DD_HH-MM-SS)
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$BackupFolderName = "backup-$Timestamp"

# 3. Crear la ruta final de destino
$FinalDestinationPath = Join-Path $DestinationBasePath $BackupFolderName

# 4. Crear la carpeta base 'BACKUPS' si no existe y luego la carpeta de la copia
try {
    # New-Item -ItemType Directory -Path $FinalDestinationPath -Force:
    # Crea la estructura completa ($DestinationBasePath/backup-...)
    Write-Host "Creando carpeta de destino: $FinalDestinationPath"
    $null = New-Item -ItemType Directory -Path $FinalDestinationPath -Force
} catch {
    Write-Error "ERROR: No se pudo crear la carpeta de destino: $($_.Exception.Message)"
    exit 1
}

# 5. Ejecutar la copia recursiva (Copiando el *contenido* de la carpeta de Imágenes)
Write-Host "Iniciando copia de seguridad de '$SourceFolder' a '$FinalDestinationPath'..."
try {
    # Copia todo el contenido de $SourceFolder (el asterisco es importante)
    Copy-Item -Path "$SourceFolder\*" -Destination $FinalDestinationPath -Recurse -Force

    # 6. Mensaje de finalización
    Write-Host ""
    Write-Host "✅ Copia de seguridad completada con éxito."
    Write-Host "   Origen: $SourceFolder"
    Write-Host "   Destino: $FinalDestinationPath"

} catch {
    Write-Error "ERROR: La copia de seguridad falló durante la copia de archivos: $($_.Exception.Message)"
    exit 1
}

exit 0 # Código de éxito