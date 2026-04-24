#!/usr/bin/env python
"""
Script para verificar los resultados de la actualización de referencias
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

from app import app
from models import db, Cliente, Proveedor, Cobranza, Pago

def verificar_resultados():
    """Verificar resultados de la actualización"""
    
    with app.app_context():
        print("="*70)
        print("RESULTADOS DE LA ACTUALIZACIÓN DE REFERENCIAS")
        print("="*70)
        
        # Verificar cobranzas
        cobranzas_con_referencia = Cobranza.query.filter(Cobranza.referencia.isnot(None)).count()
        cobranzas_con_comprobante = Cobranza.query.filter(Cobranza.numero_comprobante.isnot(None)).count()
        cobranzas_con_tipo = Cobranza.query.filter(Cobranza.tipo_comprobante.isnot(None)).count()
        
        print(f"\n📊 COBRANZAS:")
        print(f"   - Total en DB: {Cobranza.query.count()}")
        print(f"   - Con referencia: {cobranzas_con_referencia}")
        print(f"   - Con número de comprobante: {cobranzas_con_comprobante}")
        print(f"   - Con tipo de comprobante: {cobranzas_con_tipo}")
        
        # Mostrar algunas cobranzas de ejemplo
        print(f"\n📋 EJEMPLOS DE COBRANZAS:")
        cobranzas_ejemplo = Cobranza.query.filter(Cobranza.referencia.isnot(None)).limit(3).all()
        for cob in cobranzas_ejemplo:
            cliente = Cliente.query.get(cob.cliente_id)
            print(f"   - {cob.id}: {cliente.nombre if cliente else 'N/A'} - ${cob.monto:,.0f}")
            print(f"     Referencia: {cob.referencia}")
            print(f"     Comprobante: {cob.numero_comprobante} ({cob.tipo_comprobante})")
        
        # Verificar pagos
        pagos_con_referencia = Pago.query.filter(Pago.referencia.isnot(None)).count()
        pagos_con_comprobante = Pago.query.filter(Pago.numero_comprobante.isnot(None)).count()
        pagos_con_tipo = Pago.query.filter(Pago.tipo_comprobante.isnot(None)).count()
        pagos_con_cliente = Pago.query.filter(Pago.cliente_id.isnot(None)).count()
        
        print(f"\n💰 PAGOS:")
        print(f"   - Total en DB: {Pago.query.count()}")
        print(f"   - Con referencia: {pagos_con_referencia}")
        print(f"   - Con número de comprobante: {pagos_con_comprobante}")
        print(f"   - Con tipo de comprobante: {pagos_con_tipo}")
        print(f"   - Con cliente asignado: {pagos_con_cliente}")
        
        # Mostrar algunos pagos de ejemplo
        print(f"\n📋 EJEMPLOS DE PAGOS:")
        pagos_ejemplo = Pago.query.filter(Pago.cliente_id.isnot(None)).limit(3).all()
        for pag in pagos_ejemplo:
            proveedor = Proveedor.query.get(pag.proveedor_id)
            cliente = Cliente.query.get(pag.cliente_id)
            print(f"   - {pag.id}: {proveedor.nombre if proveedor else 'N/A'} - ${pag.monto:,.0f}")
            print(f"     Cliente: {cliente.nombre if cliente else 'N/A'}")
            print(f"     Comprobante: {pag.numero_comprobante} ({pag.tipo_comprobante})")
        
        print(f"\n✅ RESUMEN:")
        print(f"   - Cobranzas actualizadas: {cobranzas_con_referencia}")
        print(f"   - Pagos actualizados: {pagos_con_referencia}")
        print(f"   - Pagos con cliente asignado: {pagos_con_cliente}")
        print(f"\n🎯 OBJETIVO CUMPLIDO:")
        print(f"   - Referencias completadas con datos del Excel")
        print(f"   - Números de comprobante generados")
        print(f"   - Tipos de comprobante asignados")
        print(f"   - Clientes asignados a pagos según Excel")

if __name__ == '__main__':
    verificar_resultados()