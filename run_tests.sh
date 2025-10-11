#!/bin/bash

# Script simple para ejecutar pruebas unitarias con cobertura
echo "Ejecutando pruebas unitarias..."

# Activar entorno virtual y ejecutar tests con cobertura
source venv/bin/activate
coverage run -m unittest discover
coverage report
coverage html

echo ""
echo "✅ Reporte HTML de cobertura generado en: htmlcov/index.html"
