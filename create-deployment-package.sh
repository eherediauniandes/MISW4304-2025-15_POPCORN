#!/bin/bash

# Script para crear el paquete de deployment para AWS Elastic Beanstalk
# Autor: DevOps Team
# Fecha: 2025-10-11

set -e

echo "🚀 Creando paquete de deployment para AWS Elastic Beanstalk..."
echo ""

# Nombre del archivo ZIP
ZIP_NAME="popcorn-app-$(date +%Y%m%d-%H%M%S).zip"

# Verificar que los archivos necesarios existen
echo "✓ Verificando archivos necesarios..."

if [ ! -f "application.py" ]; then
    echo "❌ Error: application.py no encontrado"
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt no encontrado"
    exit 1
fi

if [ ! -d ".ebextensions" ]; then
    echo "❌ Error: carpeta .ebextensions no encontrada"
    exit 1
fi

if [ ! -d "app" ]; then
    echo "❌ Error: carpeta app no encontrada"
    exit 1
fi

echo "✓ Todos los archivos necesarios están presentes"
echo ""

# Limpiar archivos temporales y cache
echo "🧹 Limpiando archivos temporales..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.log" -delete 2>/dev/null || true
find . -type f -name ".DS_Store" -delete 2>/dev/null || true

echo "✓ Limpieza completada"
echo ""

# Crear el archivo ZIP
echo "📦 Creando archivo ZIP: $ZIP_NAME"
echo ""

zip -r "$ZIP_NAME" \
  application.py \
  requirements.txt \
  setup.cfg \
  app/ \
  .ebextensions/ \
  -x "*.pyc" \
  -x "*__pycache__*" \
  -x "*.pyo" \
  -x "*.log" \
  -x ".DS_Store" \
  -x "app/__pycache__/*" \
  -x "app/*/__pycache__/*" \
  -x "app/*/*/__pycache__/*"

echo ""
echo "✅ Paquete creado exitosamente: $ZIP_NAME"
echo ""

# Mostrar información del archivo
FILE_SIZE=$(du -h "$ZIP_NAME" | cut -f1)
echo "📊 Información del paquete:"
echo "   - Nombre: $ZIP_NAME"
echo "   - Tamaño: $FILE_SIZE"
echo ""

# Listar contenido del ZIP
echo "📋 Contenido del paquete:"
unzip -l "$ZIP_NAME" | head -20
echo "   ..."
echo ""

# Verificar que application.py está en la raíz
if unzip -l "$ZIP_NAME" | grep -q "^.*application.py$"; then
    echo "✅ application.py está en la raíz del ZIP (correcto)"
else
    echo "❌ ADVERTENCIA: application.py NO está en la raíz del ZIP"
    exit 1
fi

# Verificar que .ebextensions está incluida
if unzip -l "$ZIP_NAME" | grep -q ".ebextensions/"; then
    echo "✅ .ebextensions está incluida (correcto)"
else
    echo "❌ ADVERTENCIA: .ebextensions NO está incluida"
    exit 1
fi

echo ""
echo "🎉 ¡Paquete listo para deployment!"
echo ""
echo "📝 Próximos pasos:"
echo "   1. Ir a AWS Elastic Beanstalk Console"
echo "   2. Crear una nueva aplicación o actualizar una existente"
echo "   3. Subir el archivo: $ZIP_NAME"
echo "   4. Configurar las variables de entorno (ver DEPLOYMENT.md)"
echo "   5. Deploy!"
echo ""

