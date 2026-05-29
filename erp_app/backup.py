"""
Backups de producción: SQLite (restauración completa) + Excel (legible / auditoría).
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from .backup_excel import crear_backup_excel

from .paths import ERP_DB_PATH, BACKUP_ROOT

SQLITE_DIR = BACKUP_ROOT / 'sqlite'
EXCEL_DIR = BACKUP_ROOT / 'excel'
ERP_DB = ERP_DB_PATH

MAX_BACKUPS_POR_TIPO = 60


def _timestamp() -> str:
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def _rotar_antiguos(carpeta: Path, patron: str, maximo: int = MAX_BACKUPS_POR_TIPO) -> None:
    if not carpeta.is_dir():
        return
    archivos = sorted(carpeta.glob(patron), key=lambda p: p.stat().st_mtime, reverse=True)
    for viejo in archivos[maximo:]:
        try:
            viejo.unlink()
        except OSError:
            pass


def backup_sqlite(dest_dir: Path | None = None) -> Path:
    """Backup 1: copia consistente de erp.db (restauración total)."""
    if not ERP_DB.is_file():
        raise FileNotFoundError(f'No se encontró la base de datos: {ERP_DB}')

    dest_dir = dest_dir or SQLITE_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f'erp_{_timestamp()}.db'

    src = sqlite3.connect(str(ERP_DB))
    try:
        dst = sqlite3.connect(str(dest))
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()

    _rotar_antiguos(dest_dir, 'erp_*.db')
    return dest


def backup_excel(dest_dir: Path | None = None) -> Path:
    """Backup 2: export Excel por tablas (lectura / respaldo paralelo)."""
    dest_dir = dest_dir or EXCEL_DIR
    dest_dir.mkdir(parents=True, exist_ok=True)
    ok, resultado = crear_backup_excel(dest_dir=dest_dir)
    if not ok:
        raise RuntimeError(resultado)
    _rotar_antiguos(dest_dir, 'backup_*.xlsx')
    return Path(resultado)


def ejecutar_backups_produccion() -> dict:
    """Ejecuta los 2 backups y devuelve rutas generadas."""
    sqlite_path = backup_sqlite()
    excel_path = backup_excel()
    return {
        'ok': True,
        'timestamp': _timestamp(),
        'sqlite': str(sqlite_path),
        'excel': str(excel_path),
    }


def listar_backups_recientes(limite: int = 10) -> dict:
    """Lista últimos backups SQLite y Excel."""
    def _lista(carpeta: Path, patron: str):
        if not carpeta.is_dir():
            return []
        files = sorted(carpeta.glob(patron), key=lambda p: p.stat().st_mtime, reverse=True)
        out = []
        for f in files[:limite]:
            st = f.stat()
            out.append({
                'nombre': f.name,
                'ruta': str(f),
                'tamano_kb': round(st.st_size / 1024, 1),
                'fecha': datetime.fromtimestamp(st.st_mtime).strftime('%d/%m/%Y %H:%M'),
            })
        return out

    return {
        'sqlite': _lista(SQLITE_DIR, 'erp_*.db'),
        'excel': _lista(EXCEL_DIR, 'backup_*.xlsx'),
        'carpeta_sqlite': str(SQLITE_DIR),
        'carpeta_excel': str(EXCEL_DIR),
    }


def backup_excel_opcional() -> None:
    """Solo Excel, para no copiar DB en cada alta (ligero)."""
    try:
        backup_excel()
    except Exception as e:
        print(f'Error en backup Excel: {e}')
