#!/bin/sh
set -e

echo "Esperando a la base de datos en $DATABASE_URL..."

if command -v pg_isready >/dev/null 2>&1; then
  if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -q; do
      echo "DB no lista, reintentando..."
      sleep 2
    done
  else
    python - <<'PY'
import os, time, sys
import psycopg2
url = os.environ.get("DATABASE_URL")
print(f"🔍 DATABASE_URL original: {url}")
if not url:
    print("⚠️  DATABASE_URL no está configurada")
    sys.exit(0)
# Convertir URL de SQLAlchemy a formato psycopg2
# postgresql+psycopg2://... -> postgresql://...
original_url = url
if url.startswith("postgresql+psycopg2://"):
    url = url.replace("postgresql+psycopg2://", "postgresql://")
    print(f"🔄 URL convertida de SQLAlchemy a psycopg2")
print(f"🔍 URL para psycopg2: {url}")
for i in range(30):
    try:
        import psycopg2
        print(f"🔌 Intento {i+1}/30 de conexión a la BD...")
        conn = psycopg2.connect(url)
        conn.close()
        print("✅ Conexión a DB exitosa")
        sys.exit(0)
    except Exception as e:
        print(f"⚠️  Intento {i+1}/30 falló: {e}")
        time.sleep(2)
print("⚠️  WARNING: No se pudo conectar a la DB después de 30 intentos. Continuando de todas formas...", file=sys.stderr)
sys.exit(0)
PY
  fi
fi

if [ -d "migrations" ]; then
  echo "Ejecutando migraciones Alembic..."
  flask db upgrade || { echo "⚠️  WARNING: Fallo flask db upgrade, continuando..."; }
else
  echo "Sin 'migrations', creando tablas con create_all()..."
  python - <<'PY'
import os
print(f"🔍 DATABASE_URL para create_all: {os.environ.get('DATABASE_URL')}")
print(f"🔍 FLASK_ENV: {os.environ.get('FLASK_ENV')}")
from app import create_app
from app.api.extensions import db
print("📦 Creando app Flask...")
app = create_app()
print(f"🔍 Config de la app - SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
try:
    with app.app_context():
        print("🔨 Ejecutando db.create_all()...")
        db.create_all()
        print("✅ Tablas creadas con create_all().")
except Exception as e:
    print(f"⚠️  WARNING: No se pudieron crear tablas: {e}")
    import traceback
    traceback.print_exc()
PY
fi

echo "Levantando Gunicorn en :8000 con recarga automática..."
if [ "${NEW_RELIC_DEBUG_KEY:-false}" = "true" ]; then
  python - <<'PY'
import os
key = os.environ.get("NEW_RELIC_LICENSE_KEY", "")
print(f"🔎 NEW_RELIC_LICENSE_KEY len={len(key)} start='{key[:4]}' end='{key[-4:]}'")
PY
fi
if [ "${NEW_RELIC_VALIDATE:-false}" = "true" ]; then
  echo "Validando configuración de New Relic..."
  newrelic-admin validate-config "${NEW_RELIC_CONFIG_FILE:-/app/newrelic.ini}" || echo "⚠️  WARNING: newrelic-admin validate-config falló"
fi
exec newrelic-admin run-program gunicorn -b 0.0.0.0:8000 --reload "app:create_app()"
