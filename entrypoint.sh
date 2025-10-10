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
if not url:
    sys.exit(0)
for _ in range(30):
    try:
        import psycopg2
        conn = psycopg2.connect(url)
        conn.close()
        sys.exit(0)
    except Exception:
        time.sleep(2)
print("No se pudo conectar a la DB.", file=sys.stderr)
sys.exit(1)
PY
  fi
fi

if [ -d "migrations" ]; then
  echo "Ejecutando migraciones Alembic..."
  flask db upgrade || { echo "Fallo flask db upgrade"; exit 1; }
else
  echo "Sin 'migrations', creando tablas con create_all()..."
  python - <<'PY'
from app import create_app
from app.api.extensions import db
app = create_app()
with app.app_context():
    db.create_all()
    print("Tablas creadas con create_all().")
PY
fi

echo "Levantando Gunicorn en :8000 con recarga automática..."
exec gunicorn -b 0.0.0.0:8000 --reload "app:create_app()"
