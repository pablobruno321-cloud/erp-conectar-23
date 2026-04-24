#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para migrar la BD y agregar nuevos campos
"""
import sqlite3

print("Conectando a erp.db...")
conn = sqlite3.connect('erp_app/erp.db')
cursor = conn.cursor()

print("Agregando campos nuevos a la tabla usuarios...")

# Agregar permisos
try:
    cursor.execute('''ALTER TABLE usuarios ADD COLUMN permisos VARCHAR(50) DEFAULT 'view' ''')
    print("✓ Campo 'permisos' agregado")
except sqlite3.OperationalError as e:
    print(f"⚠ {e}")

# Agregar idioma
try:
    cursor.execute('''ALTER TABLE usuarios ADD COLUMN idioma VARCHAR(10) DEFAULT 'es' ''')
    print("✓ Campo 'idioma' agregado")
except sqlite3.OperationalError as e:
    print(f"⚠ {e}")

conn.commit()
conn.close()
print("\n✅ Migración completada")
