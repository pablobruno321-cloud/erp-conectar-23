#!/usr/bin/env python
"""
Carga de pedidos con debugging detallado
"""
import pandas as pd
import sys, os
sys.path.insert(0, 'erp_app')
from app import app
from models import Cliente, Pedido, db
from datetime import datetime

with app.app_context():
    df = pd.read_excel('00 - PEDIDOS.xlsx', sheet_name='Tabla')
    print(f"Total de filas: {len(df)}")
    
    pedidos_creados = 0
    pedidos_sin_cliente = 0
    pedidos_con_error = 0
    
    for idx, row in df.iterrows():
        try:
            # Obtener datos del cliente
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
            
            if cliente:
                # Procesar fecha
                fecha = row.get('Fecha Vta', row.get('Fecha'))
                if pd.notna(fecha) and hasattr(fecha, 'strftime'):
                    pass  
                else:
                    fecha = datetime.now()
                
                numero = f"PED-{cliente.id}-{idx:05d}"
                
                pedido_existente = Pedido.query.filter_by(numero=numero).first()
                if not pedido_existente:
                    costo_total = float(row.get('C. Total', 0)) if pd.notna(row.get('C. Total')) else 0
                    precio_venta = float(row.get('P. Total', 0)) if pd.notna(row.get('P. Total')) else 0
                    resultado = float(row.get('Resultado', 0)) if pd.notna(row.get('Resultado')) else 0
                    
                    # Convertir strings de SI/NO a booleanos
                    cargado = str(row.get('Cargado', 'SI')).upper() == 'SI' if pd.notna(row.get('Cargado')) else True
                    entregado = str(row.get('Entregado', 'SI')).upper() == 'SI' if pd.notna(row.get('Entregado')) else True
                    
                    pedido = Pedido(
                        numero=numero,
                        cliente_id=cliente.id,
                        fecha_venta=fecha,
                        mercado=mercado or nombre_cliente_base,
                        puesto=puesto or '',
                        cargado=cargado,
                        entregado=entregado,
                        costo_total=costo_total,
                        precio_venta_total=precio_venta,
                        resultado=resultado
                    )
                    db.session.add(pedido)
                    pedidos_creados += 1
                    
                    if pedidos_creados % 50 == 0:
                        db.session.commit()
                        print(f"  ✓ {pedidos_creados} pedidos procesados...")
            else:
                pedidos_sin_cliente += 1
        
        except Exception as e:
            pedidos_con_error += 1
            print(f"Error en row {idx}: {e}")
            db.session.rollback()
    
    db.session.commit()
    
    print(f"\n✅ Pedidos creados: {pedidos_creados}")
    print(f"⚠️  Sin cliente: {pedidos_sin_cliente}")
    print(f"❌ Con error: {pedidos_con_error}")
    print(f"Total BD: {Pedido.query.count()}")
