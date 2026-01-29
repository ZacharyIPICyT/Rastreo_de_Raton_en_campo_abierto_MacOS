#!/bin/bash

# build_mac.sh
echo "=== Construyendo ejecutable para macOS ==="

# Verificar que estamos en macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: Este script solo funciona en macOS"
    exit 1
fi

# Instalar dependencias si es necesario
echo "Instalando/actualizando dependencias..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Crear directorio de distribución
mkdir -p dist

# Construir con PyInstaller
echo "Construyendo ejecutable..."
pyinstaller --onefile \
    --name="RasteoRatonCampo" \
    --add-data=".:." \
    --hidden-import cv2 \
    --hidden-import numpy \
    --console \
    --osx-bundle-identifier "com.rastreoraton.campo" \
    main.py

echo "Optimizando tamaño..."
strip dist/RasteoRatonCampo 2>/dev/null || true

# Verificar
echo "=== Verificación ==="
ls -lh dist/RasteoRatonCampo
file dist/RasteoRatonCampo

echo ""
echo "✅ Ejecutable creado en: dist/RasteoRatonCampo"
echo "Para ejecutar: ./dist/RasteoRatonCampo"
