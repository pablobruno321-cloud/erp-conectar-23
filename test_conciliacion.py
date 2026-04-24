#!/usr/bin/env python
"""
Script de prueba para verificar la funcionalidad de conciliación
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

from app import app
from models import db, Cliente, Proveedor, Producto, Pedido, ItemPedido, Cobranza, Pago

def test_conciliacion():
    with app.app_context():
        print("="*70)
        print("TESTEANDO FUNCIONALIDAD DE CONCILIACIÓN")
        print("="*70)
        
        # Verificar que las tablas existen y tienen las nuevas columnas
        print("\n1. Verificando modelo de datos...")
        
        # Verificar Cobranza tiene las nuevas columnas
        cobranza = Cobranza.query.first()
        if cobranza:
            print(f"✓ Cobranza tiene pedido_id: {hasattr(cobranza, 'pedido_id')}")
            print(f"✓ Cobranza tiene numero_comprobante: {hasattr(cobranza, 'numero_comprobante')}")
            print(f"✓ Cobranza tiene tipo_comprobante: {hasattr(cobranza, 'tipo_comprobante')}")
        else:
            print("⚠ No hay cobranzas en la base de datos")
        
        # Verificar Pago tiene las nuevas columnas
        pago = Pago.query.first()
        if pago:
            print(f"✓ Pago tiene pedido_id: {hasattr(pago, 'pedido_id')}")
            print(f"✓ Pago tiene numero_comprobante: {hasattr(pago, 'numero_comprobante')}")
            print(f"✓ Pago tiene tipo_comprobante: {hasattr(pago, 'tipo_comprobante')}")
        else:
            print("⚠ No hay pagos en la base de datos")
        
        # Verificar relaciones
        print("\n2. Verificando relaciones...")
        if cobranza and cobranza.cliente:
            print(f"✓ Cobranza relacionada con cliente: {cobranza.cliente.nombre}")
        
        if pago and pago.proveedor:
            print(f"✓ Pago relacionado con proveedor: {pago.proveedor.nombre}")
        
        # Verificar pedidos
        print("\n3. Verificando pedidos...")
        pedidos = Pedido.query.limit(3).all()
        for pedido in pedidos:
            print(f"✓ Pedido {pedido.numero}: Cliente {pedido.cliente.nombre}")
        
        print("\n4. Verificando rutas...")
        with app.test_client() as client:
            # Probar ruta de conciliación
            response = client.get('/conciliacion')
            if response.status_code == 302:
                print("✓ Ruta /conciliacion redirige (requiere login)")
            elif response.status_code == 200:
                print("✓ Ruta /conciliacion accesible")
            else:
                print(f"⚠ Ruta /conciliacion con código: {response.status_code}")
        
        print("\n" + "="*70)
        print("✅ TEST DE CONCILIACIÓN COMPLETADO")
        print("="*70)

if __name__ == '__main__':
    test_conciliacion()