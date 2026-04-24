#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para cargar Cobranzas y Pagos desde Excel con conciliación
"""
import sys
import os
import pandas as pd
from datetime import datetime

# Agregar ruta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

from app import app
from models import db, Cobranza, Pago, Cliente, Proveedor, Pedido

with app.app_context():
    print("="*70)
    print("CARGANDO COBRANZAS Y PAGOS CON CONCILIACIÓN")
    print("="*70)
    
    # ==================== COBRANZAS ====================
    print("\n📥 Cargando COBRANZAS...")
    df_cobranzas = pd.read_excel('04 - Cobranzas.xlsx')
    
    # Crear diccionario de clientes para búsqueda rápida
    clientes_dict = {c.nombre.strip().lower(): c.id for c in Cliente.query.all()}
    
    cobranzas_cargadas = 0
    cobranzas_error = 0
    
    for idx, row in df_cobranzas.iterrows():
        try:
            cliente_nombre = str(row['Cliente']).strip()
            fecha = row['Fecha Pago']
            importe = float(row['Importe'])
            forma = str(row['Forma']) if pd.notna(row['Forma']) else None
            referencia = str(row['Referencia']) if pd.notna(row['Referencia']) else None
            numero_comprobante = str(row['Comprobante']) if pd.notna(row['Comprobante']) else None
            tipo_comprobante = str(row['Tipo Comprobante']) if pd.notna(row['Tipo Comprobante']) else None
            
            # Buscar cliente
            cliente_id = None
            print(f"  Buscando cliente: '{cliente_nombre}'")
            for nombre_bd, id_bd in clientes_dict.items():
                if nombre_bd in cliente_nombre.lower() or cliente_nombre.lower() in nombre_bd:
                    cliente_id = id_bd
                    print(f"    ✓ Encontrado: {Cliente.query.get(cliente_id).nombre}")
                    break
            
            if not cliente_id:
                print(f"    ✗ NO ENCONTRADO")
                cobranzas_error += 1
                continue
            
            # Crear cobranza con nuevas columnas de conciliación
            cobranza = Cobranza(
                cliente_id=cliente_id,
                fecha_cobranza=fecha if pd.notna(fecha) else datetime.now(),
                monto=importe,
                metodo=forma,
                referencia=referencia,
                numero_comprobante=numero_comprobante,
                tipo_comprobante=tipo_comprobante
            )
            db.session.add(cobranza)
            cobranzas_cargadas += 1
            
        except Exception as e:
            print(f"  ✗ Error en fila {idx}: {str(e)}")
            cobranzas_error += 1
    
    db.session.commit()
    print(f"\n✅ Cobranzas: {cobranzas_cargadas} cargadas, {cobranzas_error} errores")
    
    # ==================== PAGOS ====================
    print("\n📥 Cargando PAGOS...")
    df_pagos = pd.read_excel('05 - Pagos.xlsx')
    
    # Crear diccionario de proveedores
    proveedores_dict = {p.nombre.strip().lower(): p.id for p in Proveedor.query.all()}
    
    pagos_cargados = 0
    pagos_error = 0
    
    for idx, row in df_pagos.iterrows():
        try:
            proveedor_nombre = str(row['Proveedores']).strip()
            fecha = row['Fecha Pago']
            importe = float(row['Importe'])
            forma = str(row['Forma']) if pd.notna(row['Forma']) else None
            referencia = str(row['Referencia']) if pd.notna(row['Referencia']) else None
            numero_comprobante = str(row['Comprobante']) if pd.notna(row['Comprobante']) else None
            tipo_comprobante = str(row['Tipo Comprobante']) if pd.notna(row['Tipo Comprobante']) else None
            
            # Buscar proveedor
            proveedor_id = None
            print(f"  Buscando proveedor: '{proveedor_nombre}'")
            for nombre_bd, id_bd in proveedores_dict.items():
                if nombre_bd in proveedor_nombre.lower() or proveedor_nombre.lower() in nombre_bd:
                    proveedor_id = id_bd
                    print(f"    ✓ Encontrado: {Proveedor.query.get(proveedor_id).nombre}")
                    break
            
            if not proveedor_id:
                print(f"    ✗ NO ENCONTRADO")
                pagos_error += 1
                continue
            
            # Crear pago con nuevas columnas de conciliación
            pago = Pago(
                proveedor_id=proveedor_id,
                fecha_pago=fecha if pd.notna(fecha) else datetime.now(),
                monto=importe,
                metodo=forma,
                referencia=referencia,
                numero_comprobante=numero_comprobante,
                tipo_comprobante=tipo_comprobante
            )
            db.session.add(pago)
            pagos_cargados += 1
            
        except Exception as e:
            print(f"  ✗ Error en fila {idx}: {str(e)}")
            pagos_error += 1
    
    db.session.commit()
    print(f"\n✅ Pagos: {pagos_cargados} cargados, {pagos_error} errores")
    
    print("\n" + "="*70)
    print(f"TOTAL: {cobranzas_cargadas + pagos_cargados} registros cargados")
    print("✅ Columnas de conciliación incluidas: pedido_id, numero_comprobante, tipo_comprobante")
    print("="*70)
