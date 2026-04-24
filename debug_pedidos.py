#!/usr/bin/env python
"""Debug para ver qué está pasando con los Pedidos"""
import pandas as pd
import sys, os
sys.path.insert(0, 'erp_app')
from app import app
from models import Cliente, Pedido
from datetime import datetime

with app.app_context():
    print("Leyendo PEDIDOS...")
    df = pd.read_excel('00 - PEDIDOS.xlsx', sheet_name='Tabla')
    print(f"Total de filas: {len(df)}")
    
    clientes_encontrados = 0
    clientes_no_encontrados = 0
    
    for idx in range(min(10, len(df))):
        row = df.iloc[idx]
        
        nombre_cliente_base = str(row.get('Cliente', '')).strip() if pd.notna(row.get('Cliente')) else None
        mercado = str(row.get('Mercado', '')).strip() if pd.notna(row.get('Mercado')) and str(row.get('Mercado')).lower() != 'nan' else None
        puesto = str(row.get('Puesto', '')).strip() if pd.notna(row.get('Puesto')) and str(row.get('Puesto')).lower() != 'nan' else None
        
        cliente = None
        
        # Intentar búsqueda 1
        if nombre_cliente_base and mercado and puesto:
            nombre_construido = f"{nombre_cliente_base} ({mercado} P{puesto})"
            cliente = Cliente.query.filter_by(nombre=nombre_construido).first()
        
        # Intentar búsqueda 2
        if not cliente and nombre_cliente_base:
            cliente = Cliente.query.filter(Cliente.nombre.like(f"%{nombre_cliente_base}%")).first()
        
        print(f"\nRow {idx}:")
        print(f"  Cliente: {nombre_cliente_base} | Mercado: {mercado} | Puesto: {puesto}")
        if cliente:
            print(f"  ✓ ENCONTRADO: {cliente.nombre}")
            clientes_encontrados += 1
        else:
            print(f"  ✗ NO ENCONTRADO")
            clientes_no_encontrados += 1
    
    print(f"\n\nReumen de primeras 10 filas:")
    print(f"  Clientes encontrados: {clientes_encontrados}")
    print(f"  Clientes no encontrados: {clientes_no_encontrados}")
