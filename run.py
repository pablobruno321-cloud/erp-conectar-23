#!/usr/bin/env python
"""
Script para ejecutar el ERP
"""
import os
import sys
import sqlite3
import webbrowser
from threading import Timer

# 1. Configuración de rutas del sistema
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

def auto_reparar():
    db_path = os.path.join(os.path.dirname(__file__), 'erp_app', 'erp.db')
    if not os.path.exists(db_path):
        return
    try:
        conn = sqlite3.connect(db_path, timeout=1)
        cursor = conn.cursor()
        for tabla in ['cobranzas', 'pagos']:
            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas_actuales = [row[1] for row in cursor.fetchall()]
            for col, tipo in [('pedido_id', 'INTEGER'), ('numero_comprobante', 'TEXT'), ('tipo_comprobante', 'TEXT')]:
                if col not in columnas_actuales:
                    cursor.execute(f"ALTER TABLE {tabla} ADD COLUMN {col} {tipo}")
        conn.commit()
        conn.close()
    except Exception: pass

def abrir_link(p):
    url = f"http://127.0.0.1:{p}/login"
    print(f"\n✅ SERVIDOR LISTO. Abriendo: {url}")
    webbrowser.open(url)

if __name__ == '__main__':
    print("\n🚀 INICIANDO ERP CONECTAR 23...")
    auto_reparar()

    try:
        print("\n🚀 CARGANDO SISTEMA...")
        from erp_app.app import app, init_db
        
        # Inicialización controlada de la base de datos
        init_db()
        
    except Exception as e:
        import traceback
        print("\n" + "!"*60)
        print("❌ ERROR AL INICIAR:")
        print(traceback.format_exc())
        print("!"*60)
        input("\nPresiona ENTER para salir...")
        sys.exit(1)

    print("📡 Iniciando servidor web...")

if __name__ == '__main__':
    is_production = os.getenv('FLASK_ENV') == 'production'
    port_env = int(os.environ.get('PORT', 5000))

    if not is_production:
        for p in [5000, 5001, 8081, 8082]:
            try:
                print(f"🔗 Buscando puerto libre (probando {p})...")
                Timer(2, abrir_link, [p]).start()
                app.run(debug=True, host='127.0.0.1', port=p, use_reloader=False)
                break
            except Exception as e:
                print(f"ℹ️ Puerto {p} ocupado o no disponible. Intentando el siguiente...")
                continue
    else:
        app.run(debug=False, host='0.0.0.0', port=port_env)
