"""Rutas de datos persistentes (local o volumen en la nube)."""
from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv('ERP_DATA_DIR', str(APP_DIR)))
DATA_DIR.mkdir(parents=True, exist_ok=True)

ERP_DB_PATH = DATA_DIR / 'erp.db'
UPLOADS_ROOT = DATA_DIR / 'uploads'
UPLOAD_REMITOS_DIR = UPLOADS_ROOT / 'remitos'
UPLOAD_REMITOS_DIR.mkdir(parents=True, exist_ok=True)

PROJECT_ROOT = APP_DIR.parent
BACKUP_ROOT = Path(os.getenv('ERP_BACKUP_DIR', str(PROJECT_ROOT / 'backups')))
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
