"""
Punto de entrada para AWS Elastic Beanstalk.
Este archivo es requerido por Elastic Beanstalk y debe llamarse 'application.py'.
"""
import os
import sys
from app import create_app
from app.api.extensions import db

# Determinar el entorno basado en variables de entorno
config_name = os.getenv('FLASK_ENV', 'production')

# Crear la aplicación Flask
application = create_app(config_name)

# Elastic Beanstalk espera que la variable se llame 'application'
app = application

# Crear las tablas de la base de datos si no existen
with application.app_context():
    try:
        # Intentar conectarse a la base de datos
        db.engine.connect()
        print("✓ Conexión a base de datos exitosa")

        # Crear las tablas
        db.create_all()
        print("✓ Tablas de base de datos creadas/verificadas correctamente")

        # Verificar que las tablas existen
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✓ Tablas disponibles: {tables}")

    except Exception as e:
        print(f"⚠ Error al configurar base de datos: {e}", file=sys.stderr)
        print(f"⚠ Tipo de error: {type(e).__name__}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Para desarrollo local - AP
    port = int(os.getenv('PORT', 8000))
    application.run(host='0.0.0.0', port=port)

