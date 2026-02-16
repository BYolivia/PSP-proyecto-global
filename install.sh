#!/bin/bash

# Script para instalación automática de dependencias y verificación de entorno virtual

# Función para instalar dependencias del sistema
install_system_dependencies() {
    echo "🔍 Verificando dependencias del sistema..."

    MISSING=()

    # Verificar tkinter
    if ! python3 -c "import tkinter" 2>/dev/null; then
        MISSING+=("python3-tk")
    else
        echo "✅ tkinter disponible"
    fi

    # Verificar VLC
    if ! command -v vlc &>/dev/null; then
        MISSING+=("vlc")
    else
        echo "✅ vlc disponible"
    fi

    if [ ${#MISSING[@]} -gt 0 ]; then
        echo "📦 Instalando paquetes del sistema: ${MISSING[*]}"
        if command -v apt &>/dev/null; then
            sudo apt update && sudo apt install -y "${MISSING[@]}"
        elif command -v dnf &>/dev/null; then
            sudo dnf install -y "${MISSING[@]}"
        elif command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm "${MISSING[@]}"
        else
            echo "❌ Gestor de paquetes no soportado. Instala manualmente: ${MISSING[*]}"
            return 1
        fi
        echo "✅ Dependencias del sistema instaladas"
    else
        echo "✅ Todas las dependencias del sistema están disponibles"
    fi
}

# Función para comprobar y activar entorno virtual
check_virtual_env() {
    echo "🔍 Verificando entorno virtual..."
    
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "✅ Entorno virtual activado: $VIRTUAL_ENV"
        return 0
    fi
    
    echo "❌ No se detectó un entorno virtual activado"
    
    # Buscar directorio venv en el proyecto
    if [ -d "venv" ]; then
        echo "📁 Se encontró directorio 'venv'. Activando..."
        source venv/bin/activate
        if [[ "$VIRTUAL_ENV" != "" ]]; then
            echo "✅ Entorno virtual activado correctamente"
            return 0
        else
            echo "❌ Error al activar el entorno virtual"
            return 1
        fi
    else
        echo "❌ No se encontró directorio 'venv'. Creando entorno virtual..."
        python3 -m venv venv
        source venv/bin/activate
        echo "✅ Entorno virtual creado y activado"
        return 0
    fi
}

# Función para instalar dependencias
install_dependencies() {
    echo "📦 Actualizando pip..."
    python -m pip install --upgrade pip
    
    # Verificar si existe requirements.txt
    if [ -f "requirements.txt" ]; then
        echo "📋 Instalando dependencias desde requirements.txt..."
        pip install -r requirements.txt
        echo "✅ Dependencias instaladas correctamente"
    else
        echo "⚠️  No se encontró requirements.txt"
        echo "ℹ️  Crea un requirements.txt con: pip freeze > requirements.txt"
    fi
}

# Función para verificar instalación
verify_installation() {
    echo "🔍 Verificando instalación..."
    python -c "import sys; print(f'✅ Python {sys.version.split()[0]} funcionando correctamente')"
    
    echo "📋 Paquetes instalados:"
    pip list
}

# Función principal
main() {
    echo "🚀 Iniciando script de instalación..."
    echo ""

    # Comprobar entorno virtual
    if ! check_virtual_env; then
        echo "❌ Error en la configuración del entorno virtual"
        exit 1
    fi
    
    echo ""

    # Instalar dependencias del sistema (tkinter, vlc)
    if ! install_system_dependencies; then
        echo "❌ Error instalando dependencias del sistema"
        exit 1
    fi

    echo ""

    # Instalar dependencias de Python
    install_dependencies
    
    echo ""
    
    # Verificar instalación
    verify_installation
    
    echo ""
    echo "🎉 Instalación completada con éxito!"
    echo "💡 Para activar el entorno virtual manualmente: source venv/bin/activate"
    echo "💡 Para ejecutar el proyecto: python __main__.py"
}

# Ejecutar función principal
main