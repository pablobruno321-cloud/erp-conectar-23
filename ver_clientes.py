#!/usr/bin/env python
import sys, os
sys.path.insert(0, 'erp_app')
from app import app
from models import Cliente, Pedido
with app.app_context():
    print("Clientes en BD:")
    clientes = Cliente.query.all()
    for c in clientes[:5]:
        print(f"  {c.id}: '{c.nombre}'")
    print(f"  ... Total: {len(clientes)}")
    
    # Verificar si hay coincidencias con los nombres de PEDIDOS
    print("\nPrimeras 3 filas de PEDIDOS como búsqueda:")
    import pandas as pd
    df = pd.read_excel('00 - PEDIDOS.xlsx', sheet_name='Tabla')
    for idx in range(min(3, len(df))):
        cliente_nombre = df.iloc[idx]['Cliente']
        mercado = df.iloc[idx].get('Mercado', '')
        puesto = df.iloc[idx].get('Puesto', '')
        
        # Nombre construido como en BD
        nombre_construido = f"{cliente_nombre} ({mercado} P{puesto})"
        
        # Búsqueda en BD
        found = Cliente.query.filter_by(nombre=nombre_construido).first()
        print(f"  Row {idx}: '{cliente_nombre}' + '{mercado}' P{puesto}")
        print(f"    Construido: '{nombre_construido}'")
        print(f"    Encontrado: {found.nombre if found else 'NO ENCONTRADO'}")
