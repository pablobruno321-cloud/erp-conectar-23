#!/usr/bin/env python3
"""
Copia los datos de erp.db (SQLite local) a PostgreSQL (Neon / Render).
Uso:
  set DATABASE_URL=postgresql://usuario:pass@host/db?sslmode=require
  python scripts/migrar_a_postgres.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
except ImportError:
    pass

import pandas as pd
from sqlalchemy import create_engine, inspect, text

SQLITE_PATH = ROOT / 'erp_app' / 'erp.db'
PG_URL = os.getenv('DATABASE_URL', '').strip()
if PG_URL.startswith('postgres://'):
    PG_URL = PG_URL.replace('postgres://', 'postgresql://', 1)

if not PG_URL:
    print('ERROR: configure DATABASE_URL con la connection string de Neon.')
    sys.exit(1)
if not SQLITE_PATH.is_file():
    print(f'ERROR: no se encontró {SQLITE_PATH}')
    sys.exit(1)

# Orden por dependencias (foreign keys)
TABLAS = [
    'erps', 'usuarios', 'frutas', 'variedades', 'clasificaciones', 'envases',
    'marcas', 'kilogramos', 'formas_cobro', 'config_margen',
    'clientes', 'proveedores', 'proveedores_contactos', 'proveedores_logisticos',
    'productos', 'cotizaciones',
    'pedidos', 'items_pedido',
    'cobranzas', 'cobranzas_lineas', 'cobranzas_imputaciones',
]

sqlite_engine = create_engine(f'sqlite:///{SQLITE_PATH}')
pg_engine = create_engine(PG_URL)

print('Creando tablas en PostgreSQL...')
from erp_app.app import app, db  # noqa: E402

with app.app_context():
    app.config['SQLALCHEMY_DATABASE_URI'] = PG_URL
    db.create_all()

insp = inspect(pg_engine)
existentes = set(insp.get_table_names())

print('Copiando datos...')
with pg_engine.begin() as conn:
    for tabla in reversed(TABLAS):
        if tabla in existentes:
            conn.execute(text(f'TRUNCATE TABLE {tabla} RESTART IDENTITY CASCADE'))
    for tabla in TABLAS:
        if tabla not in existentes:
            print(f'  omitida (no existe en PG): {tabla}')
            continue
        try:
            df = pd.read_sql(f'SELECT * FROM {tabla}', sqlite_engine)
        except Exception as e:
            print(f'  omitida {tabla}: {e}')
            continue
        if df.empty:
            print(f'  {tabla}: vacía')
            continue
        df.to_sql(tabla, conn, if_exists='append', index=False, method='multi', chunksize=500)
        print(f'  {tabla}: {len(df)} filas')

print('Listo. Probá login en Render con tu usuario de siempre.')
