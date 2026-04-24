#!/usr/bin/env python
"""
Script simple para completar referencias de cobranzas y pagos
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

import pandas as pd
from app import app
from models import db, Cliente, Proveedor, Cobranza, Pago

def completar_referencias_simple():
    """Completar referencias de cobranzas y pagos"""
    
    with app.app_context():
        print("COMPLETANDO REFERENCIAS...")
        
        # Cargar datos de Excel
        df_cobranzas = pd.read_excel('04 - Cobranzas.xlsx')
        df_pagos = pd.read_excel('05 - Pagos.xlsx')
        
        # Mapear clientes y proveedores
        clientes_db = {c.nombre: c.id for c in Cliente.query.all()}
        proveedores_db = {p.nombre: p.id for p in Proveedor.query.all()}
        
        print(f"Cobranzas Excel: {len(df_cobranzas)}")
        print(f"Pagos Excel: {len(df_pagos)}")
        
        # Completar cobranzas
        cobranzas_actualizadas = 0
        for _, row in df_cobranzas.iterrows():
            cliente_nombre = row['Cliente']
            importe = row['Importe']
            comentarios = row.get('Comentarios', '')
            forma = row['Forma']
            
            if cliente_nombre in clientes_db:
                cliente_id = clientes_db[cliente_nombre]
                cobranza = Cobranza.query.filter_by(cliente_id=cliente_id, monto=float(importe)).first()
                
                if cobranza:
                    cobranza.referencia = str(comentarios) if pd.notna(comentarios) else ''
                    cobranza.metodo = forma if pd.notna(forma) else ''
                    cobranza.tipo_comprobante = 'Recibo'
                    cobranza.numero_comprobante = f"COB-{cobranzas_actualizadas + 1:03d}"
                    cobranzas_actualizadas += 1
        
        # Completar pagos
        pagos_actualizados = 0
        for _, row in df_pagos.iterrows():
            proveedor_nombre = row['Proveedores']
            cliente_nombre = row.get('Cliente', '')
            importe = row['Importe']
            comentarios = row.get('Comentarios', '')
            forma = row['Forma']
            
            if proveedor_nombre in proveedores_db:
                proveedor_id = proveedores_db[proveedor_nombre]
                pago = Pago.query.filter_by(proveedor_id=proveedor_id, monto=float(importe)).first()
                
                if pago:
                    pago.referencia = str(comentarios) if pd.notna(comentarios) else ''
                    pago.metodo = forma if pd.notna(forma) else ''
                    pago.tipo_comprobante = 'Recibo'
                    pago.numero_comprobante = f"PAGO-{pagos_actualizados + 1:03d}"
                    
                    # Asignar cliente si está en el Excel
                    if cliente_nombre and cliente_nombre in clientes_db:
                        pago.cliente_id = clientes_db[cliente_nombre]
                    
                    pagos_actualizados += 1
        
        db.session.commit()
        print(f"✅ COMPLETADO: {cobranzas_actualizadas} cobranzas, {pagos_actualizados} pagos")

if __name__ == '__main__':
    completar_referencias_simple()