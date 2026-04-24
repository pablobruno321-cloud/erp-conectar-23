#!/usr/bin/env python
"""
Script para completar las referencias de cobranzas y pagos con los datos del Excel
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

import pandas as pd
from app import app
from models import db, Cliente, Proveedor, Cobranza, Pago

def completar_referencias():
    """Completar referencias de cobranzas y pagos con datos del Excel"""
    
    with app.app_context():
        print("="*70)
        print("COMPLETANDO REFERENCIAS CON DATOS DEL EXCEL")
        print("="*70)
        
        # Cargar datos de Excel
        print("\n1. Cargando datos de Excel...")
        
        try:
            df_cobranzas = pd.read_excel('04 - Cobranzas.xlsx')
            df_pagos = pd.read_excel('05 - Pagos.xlsx')
        except Exception as e:
            print(f"❌ Error al cargar Excel: {e}")
            return
        
        print(f"✓ Cobranzas Excel: {len(df_cobranzas)} registros")
        print(f"✓ Pagos Excel: {len(df_pagos)} registros")
        
        # Mapear clientes y proveedores
        print("\n2. Mapeando clientes y proveedores...")
        
        clientes_db = {c.nombre: c.id for c in Cliente.query.all()}
        proveedores_db = {p.nombre: p.id for p in Proveedor.query.all()}
        
        print(f"✓ Clientes en DB: {len(clientes_db)}")
        print(f"✓ Proveedores en DB: {len(proveedores_db)}")
        
        # Completar cobranzas
        print("\n3. Completando referencias de cobranzas...")
        cobranzas_actualizadas = 0
        
        for _, row in df_cobranzas.iterrows():
            cliente_nombre = row['Cliente']
            fecha_pago = row['Fecha Pago']
            forma = row['Forma']
            importe = row['Importe']
            comentarios = row.get('Comentarios', '')
            
            # Buscar cliente en DB
            if cliente_nombre not in clientes_db:
                print(f"⚠ Cliente no encontrado: {cliente_nombre}")
                continue
            
            cliente_id = clientes_db[cliente_nombre]
            
            # Buscar cobranza en DB (por cliente, fecha y monto)
            cobranza = Cobranza.query.filter_by(
                cliente_id=cliente_id,
                monto=float(importe)
            ).first()
            
            if cobranza:
                # Completar datos
                cobranza.referencia = str(comentarios) if pd.notna(comentarios) else ''
                cobranza.metodo = forma if pd.notna(forma) else ''
                
                # Determinar tipo de comprobante basado en comentarios
                if pd.notna(comentarios):
                    comentarios_str = str(comentarios).lower()
                    if 'cheque' in comentarios_str:
                        cobranza.tipo_comprobante = 'Cheque'
                    elif 'transfer' in comentarios_str or 'transf' in comentarios_str:
                        cobranza.tipo_comprobante = 'Transferencia'
                    elif 'efectivo' in comentarios_str:
                        cobranza.tipo_comprobante = 'Efectivo'
                    else:
                        cobranza.tipo_comprobante = 'Recibo'
                else:
                    cobranza.tipo_comprobante = 'Recibo'
                
                # Generar número de comprobante basado en fecha
                if pd.notna(fecha_pago):
                    fecha_str = fecha_pago.strftime('%Y%m%d')
                    cobranza.numero_comprobante = f"COB-{fecha_str}-{cobranzas_actualizadas + 1:03d}"
                
                cobranzas_actualizadas += 1
                print(f"✓ Cobranza {cobranza.id}: {cliente_nombre} - ${importe:,.0f}")
        
        # Completar pagos
        print("\n4. Completando referencias de pagos...")
        pagos_actualizados = 0
        
        for _, row in df_pagos.iterrows():
            proveedor_nombre = row['Proveedores']
            cliente_nombre = row.get('Cliente', '')
            fecha_pago = row['Fecha Pago']
            forma = row['Forma']
            importe = row['Importe']
            comentarios = row.get('Comentarios', '')
            
            # Buscar proveedor en DB
            if proveedor_nombre not in proveedores_db:
                print(f"⚠ Proveedor no encontrado: {proveedor_nombre}")
                continue
            
            proveedor_id = proveedores_db[proveedor_nombre]
            
            # Buscar pago en DB (por proveedor, fecha y monto)
            pago = Pago.query.filter_by(
                proveedor_id=proveedor_id,
                monto=float(importe)
            ).first()
            
            if pago:
                # Completar datos
                pago.referencia = str(comentarios) if pd.notna(comentarios) else ''
                pago.metodo = forma if pd.notna(forma) else ''
                
                # Determinar tipo de comprobante basado en comentarios
                if pd.notna(comentarios):
                    comentarios_str = str(comentarios).lower()
                    if 'cheque' in comentarios_str:
                        pago.tipo_comprobante = 'Cheque'
                    elif 'transfer' in comentarios_str or 'transf' in comentarios_str:
                        pago.tipo_comprobante = 'Transferencia'
                    elif 'efectivo' in comentarios_str:
                        pago.tipo_comprobante = 'Efectivo'
                    else:
                        pago.tipo_comprobante = 'Recibo'
                else:
                    pago.tipo_comprobante = 'Recibo'
                
                # Generar número de comprobante basado en fecha
                if pd.notna(fecha_pago):
                    fecha_str = fecha_pago.strftime('%Y%m%d')
                    pago.numero_comprobante = f"PAGO-{fecha_str}-{pagos_actualizados + 1:03d}"
                
                # Asignar cliente si está en el Excel
                if cliente_nombre and cliente_nombre in clientes_db:
                    pago.cliente_id = clientes_db[cliente_nombre]
                
                pagos_actualizados += 1
                print(f"✓ Pago {pago.id}: {proveedor_nombre} - ${importe:,.0f}")
        
        # Guardar cambios
        try:
            db.session.commit()
            print(f"\n✅ COMPLETADO EXITOSAMENTE!")
            print(f"   - Cobranzas actualizadas: {cobranzas_actualizadas}")
            print(f"   - Pagos actualizados: {pagos_actualizados}")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error al guardar cambios: {e}")

if __name__ == '__main__':
    completar_referencias()