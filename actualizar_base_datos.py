#!/usr/bin/env python
"""
Script para actualizar la base de datos y agregar las columnas faltantes
"""
import sqlite3
import os

def actualizar_base_datos():
    """Agregar las columnas faltantes a las tablas cobranzas y pagos"""
    
    # Ruta a la base de datos
    db_path = os.path.join(os.path.dirname(__file__), 'erp_app', 'erp.db')
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada. Inicia la aplicación primero para crearla.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Verificando columnas existentes...")
        
        # Verificar columnas en cobranzas
        cursor.execute("PRAGMA table_info(cobranzas)")
        cobranzas_cols = [row[1] for row in cursor.fetchall()]
        print(f"Columnas en cobranzas: {cobranzas_cols}")
        
        # Verificar columnas en pagos
        cursor.execute("PRAGMA table_info(pagos)")
        pagos_cols = [row[1] for row in cursor.fetchall()]
        print(f"Columnas en pagos: {pagos_cols}")
        
        # Agregar columnas faltantes en cobranzas
        columnas_cobranzas = [
            ('pedido_id', 'INTEGER'),
            ('numero_comprobante', 'TEXT'),
            ('tipo_comprobante', 'TEXT')
        ]
        
        for col_name, col_type in columnas_cobranzas:
            if col_name not in cobranzas_cols:
                print(f"➕ Agregando columna {col_name} a cobranzas...")
                cursor.execute(f"ALTER TABLE cobranzas ADD COLUMN {col_name} {col_type}")
        
        # Agregar columnas faltantes en pagos
        columnas_pagos = [
            ('pedido_id', 'INTEGER'),
            ('numero_comprobante', 'TEXT'),
            ('tipo_comprobante', 'TEXT')
        ]
        
        for col_name, col_type in columnas_pagos:
            if col_name not in pagos_cols:
                print(f"➕ Agregando columna {col_name} a pagos...")
                cursor.execute(f"ALTER TABLE pagos ADD COLUMN {col_name} {col_type}")
        
        conn.commit()
        conn.close()
        
        print("✅ Base de datos actualizada exitosamente!")
        print("📋 Resumen de cambios:")
        print("   - Tabla cobranzas: pedido_id, numero_comprobante, tipo_comprobante")
        print("   - Tabla pagos: pedido_id, numero_comprobante, tipo_comprobante")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar la base de datos: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("ACTUALIZADOR DE BASE DE DATOS")
    print("="*60)
    
    if actualizar_base_datos():
        print("\n🎉 ¡Listo! Ahora puedes usar el sistema sin errores.")
        print("   - Inicia la aplicación: python erp_app/app.py")
        print("   - Ve a la sección de cobranzas o pagos")
        print("   - Todo debería funcionar correctamente")
    else:
        print("\n⚠️  Hubo un problema. Verifica que la base de datos exista.")