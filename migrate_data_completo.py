#!/usr/bin/env python
"""
Script para migrar TODOS los datos de Excel a la base de datos
Ejecutar: python migrate_data_completo.py
"""

import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar erp_app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

from app import app, db
from models import Cliente, Proveedor, Producto, Pedido, ItemPedido, ProveedorLogistico, Usuario, Cobranza, Pago

def migrar_datos_completo():
    with app.app_context():
        base_path = Path(__file__).parent
        
        # ==================== CLIENTES ====================
        print("\n" + "="*60)
        print("⏳ Cargando CLIENTES...")
        print("="*60)
        try:
            archivo = base_path / '01 - Clientes.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"Archivo encontrado. Columnas: {list(df.columns)}")
                
                # Detectar columnas
                col_nombre = next((col for col in df.columns if 'nombre' in col.lower() or 'cliente' in col.lower()), df.columns[0] if len(df.columns) > 0 else None)
                col_cuit = next((col for col in df.columns if 'cuit' in col.lower()), None)
                col_telefono = next((col for col in df.columns if 'teléfono' in col.lower() or 'telefono' in col.lower()), None)
                col_email = next((col for col in df.columns if 'email' in col.lower() or 'mail' in col.lower()), None)
                col_direccion = next((col for col in df.columns if 'dirección' in col.lower() or 'direccion' in col.lower()), None)
                
                clientes_creados = 0
                for idx, row in df.iterrows():
                    nombre = str(row[col_nombre]).strip() if pd.notna(row[col_nombre]) else None
                    
                    if nombre and nombre.lower() not in ['nan', 'cliente', '']:
                        cliente_existente = Cliente.query.filter_by(nombre=nombre).first()
                        if not cliente_existente:
                            cliente = Cliente(
                                nombre=nombre,
                                cuit=str(row[col_cuit]).strip() if col_cuit and pd.notna(row[col_cuit]) else None,
                                telefono=str(row[col_telefono]).strip() if col_telefono and pd.notna(row[col_telefono]) else None,
                                email=str(row[col_email]).strip() if col_email and pd.notna(row[col_email]) else None,
                                direccion=str(row[col_direccion]).strip() if col_direccion and pd.notna(row[col_direccion]) else None,
                                activo=True
                            )
                            db.session.add(cliente)
                            clientes_creados += 1
                
                db.session.commit()
                print(f"✅ {clientes_creados} clientes cargados")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        
        # ==================== PROVEEDORES ====================
        print("\n" + "="*60)
        print("⏳ Cargando PROVEEDORES...")
        print("="*60)
        try:
            archivo = base_path / '02 - Proveedores.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"Archivo encontrado. Columnas: {list(df.columns)}")
                
                col_nombre = next((col for col in df.columns if 'nombre' in col.lower() or 'proveedor' in col.lower()), df.columns[0] if len(df.columns) > 0 else None)
                col_cuit = next((col for col in df.columns if 'cuit' in col.lower()), None)
                col_telefono = next((col for col in df.columns if 'teléfono' in col.lower() or 'telefono' in col.lower()), None)
                
                prov_creados = 0
                for idx, row in df.iterrows():
                    nombre = str(row[col_nombre]).strip() if pd.notna(row[col_nombre]) else None
                    
                    if nombre and nombre.lower() not in ['nan', 'proveedor', '']:
                        prov_existente = Proveedor.query.filter_by(nombre=nombre).first()
                        if not prov_existente:
                            proveedor = Proveedor(
                                nombre=nombre,
                                cuit=str(row[col_cuit]).strip() if col_cuit and pd.notna(row[col_cuit]) else None,
                                telefono=str(row[col_telefono]).strip() if col_telefono and pd.notna(row[col_telefono]) else None,
                                activo=True
                            )
                            db.session.add(proveedor)
                            prov_creados += 1
                
                db.session.commit()
                print(f"✅ {prov_creados} proveedores cargados")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        
        # ==================== PROVEEDORES LOGÍSTICOS ====================
        print("\n" + "="*60)
        print("⏳ Cargando PROVEEDORES LOGÍSTICOS...")
        print("="*60)
        try:
            archivo = base_path / '03 - Prov. Logisticos.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"Archivo encontrado. Columnas: {list(df.columns)}")
                
                col_nombre = next((col for col in df.columns if 'nombre' in col.lower()), df.columns[0] if len(df.columns) > 0 else None)
                col_telefono = next((col for col in df.columns if 'teléfono' in col.lower() or 'telefono' in col.lower()), None)
                
                prov_log_creados = 0
                for idx, row in df.iterrows():
                    nombre = str(row[col_nombre]).strip() if pd.notna(row[col_nombre]) else None
                    
                    if nombre and nombre.lower() not in ['nan', '']:
                        prov_log_existente = ProveedorLogistico.query.filter_by(nombre=nombre).first()
                        if not prov_log_existente:
                            prov_log = ProveedorLogistico(
                                nombre=nombre,
                                telefono=str(row[col_telefono]).strip() if col_telefono and pd.notna(row[col_telefono]) else None,
                            )
                            db.session.add(prov_log)
                            prov_log_creados += 1
                
                db.session.commit()
                print(f"✅ {prov_log_creados} proveedores logísticos cargados")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        
        # ==================== PRODUCTOS ====================
        print("\n" + "="*60)
        print("⏳ Cargando PRODUCTOS...")
        print("="*60)
        try:
            archivo = base_path / '06 - Base productos por proveedores.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"Archivo encontrado. Columnas: {list(df.columns)}")
                
                col_producto = next((col for col in df.columns if 'producto' in col.lower() or 'fruta' in col.lower() or 'nombre' in col.lower()), df.columns[0] if len(df.columns) > 0 else None)
                col_proveedor = next((col for col in df.columns if 'proveedor' in col.lower()), None)
                col_costo = next((col for col in df.columns if 'costo' in col.lower()), None)
                
                prod_creados = 0
                for idx, row in df.iterrows():
                    nombre_prod = str(row[col_producto]).strip() if pd.notna(row[col_producto]) else None
                    nombre_prov = str(row[col_proveedor]).strip() if col_proveedor and pd.notna(row[col_proveedor]) else None
                    
                    if nombre_prod and nombre_prod.lower() not in ['nan', '']:
                        # Buscar proveedor
                        proveedor = None
                        if nombre_prov and nombre_prov.lower() != 'nan':
                            proveedor = Proveedor.query.filter_by(nombre=nombre_prov).first()
                        
                        if not proveedor:
                            proveedor = Proveedor.query.first()
                        
                        if proveedor:
                            prod_existente = Producto.query.filter_by(nombre=nombre_prod, proveedor_id=proveedor.id).first()
                            if not prod_existente:
                                costo = 0
                                if col_costo and pd.notna(row[col_costo]):
                                    try:
                                        costo = float(row[col_costo])
                                    except:
                                        costo = 0
                                
                                producto = Producto(
                                    nombre=nombre_prod,
                                    proveedor_id=proveedor.id,
                                    costo_unitario=costo,
                                    precio_venta=costo * 1.3 if costo > 0 else 0,  # Markup 30%
                                    stock=0,
                                    activo=True
                                )
                                db.session.add(producto)
                                prod_creados += 1
                
                db.session.commit()
                print(f"✅ {prod_creados} productos cargados")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        
        # ==================== PEDIDOS ====================
        print("\n" + "="*60)
        print("⏳ Cargando PEDIDOS...")
        print("="*60)
        try:
            archivo = base_path / '00 - PEDIDOS.xlsx'
            if archivo.exists():
                # Intentar leer diferentes hojas
                sheet_names = pd.ExcelFile(archivo).sheet_names
                print(f"Hojas disponibles: {sheet_names}")
                
                df = None
                for sheet in ['Tabla', 'Sheet1', 'Pedidos', 'PEDIDOS']:
                    if sheet in sheet_names:
                        df = pd.read_excel(archivo, sheet_name=sheet)
                        print(f"Usando hoja: {sheet}")
                        break
                
                if df is None:
                    df = pd.read_excel(archivo)
                
                print(f"Columnas: {list(df.columns)}")
                
                col_fecha = next((col for col in df.columns if 'fecha' in col.lower()), None)
                col_cliente = next((col for col in df.columns if 'cliente' in col.lower()), None)
                col_producto = next((col for col in df.columns if 'producto' in col.lower() or 'fruta' in col.lower()), None)
                col_cantidad = next((col for col in df.columns if 'cantidad' in col.lower() or 'pallet' in col.lower()), None)
                col_pv = next((col for col in df.columns if 'pv' in col.lower() or 'precio venta' in col.lower()), None)
                col_costo = next((col for col in df.columns if 'costo' in col.lower()), None)
                col_mercado = next((col for col in df.columns if 'mercado' in col.lower()), None)
                
                pedidos_creados = 0
                for idx, row in df.iterrows():
                    nombre_cliente = str(row[col_cliente]).strip() if col_cliente and pd.notna(row[col_cliente]) else None
                    
                    if nombre_cliente and nombre_cliente.lower() not in ['nan', '']:
                        cliente = Cliente.query.filter_by(nombre=nombre_cliente).first()
                        if cliente:
                            fecha = row[col_fecha] if col_fecha and pd.notna(row[col_fecha]) else datetime.now()
                            if not hasattr(fecha, 'strftime'):
                                fecha = datetime.now()
                            
                            numero = f"PED-{idx:05d}-{fecha.strftime('%Y%m%d')}"
                            
                            pedido_existente = Pedido.query.filter_by(numero=numero).first()
                            if not pedido_existente:
                                cantidad = float(row[col_cantidad]) if col_cantidad and pd.notna(row[col_cantidad]) else 0
                                pv_total = float(row[col_pv]) if col_pv and pd.notna(row[col_pv]) else 0
                                costo_total = float(row[col_costo]) if col_costo and pd.notna(row[col_costo]) else 0
                                
                                pedido = Pedido(
                                    numero=numero,
                                    cliente_id=cliente.id,
                                    fecha_venta=fecha,
                                    mercado=str(row[col_mercado]).strip() if col_mercado and pd.notna(row[col_mercado]) else None,
                                    precio_venta_total=pv_total,
                                    costo_total=costo_total,
                                    resultado=pv_total - costo_total,
                                    cargado=True,
                                    entregado=True
                                )
                                db.session.add(pedido)
                                pedidos_creados += 1
                
                db.session.commit()
                print(f"✅ {pedidos_creados} pedidos cargados")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}")
        except Exception as e:
            print(f"❌ Error: {e}")
            db.session.rollback()
        
        print("\n" + "="*60)
        print("✅ MIGRACIÓN COMPLETADA")
        print("="*60)

if __name__ == '__main__':
    migrar_datos_completo()
