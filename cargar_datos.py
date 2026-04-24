#!/usr/bin/env python
"""
Script mejorado para migrar TODOS los datos de Excel a la base de datos
Ejecutar: python cargar_datos.py
"""

import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

from app import app, db
from models import Cliente, Proveedor, Producto, Pedido, ItemPedido, ProveedorLogistico, Usuario, Cobranza, Pago

def cargar_datos():
    with app.app_context():
        # Recrear todas las tablas para actualizar esquema
        db.drop_all()
        db.create_all()
        
        base_path = Path(__file__).parent
        
        # ==================== CLIENTES ====================
        print("\n" + "="*70)
        print("👥 CARGANDO CLIENTES...")
        print("="*70)
        try:
            archivo = base_path / '01 - Clientes.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"📄 Archivo encontrado. Filas: {len(df)}")
                
                clientes_creados = 0
                for idx, row in df.iterrows():
                    # Usar Mercado + Puesto + Contacto como nombre combinado
                    mercado = str(row.get('Mercado', '')).strip() if pd.notna(row.get('Mercado')) else ''
                    puesto = str(row.get('Puesto', '')).strip() if pd.notna(row.get('Puesto')) else ''
                    contacto = str(row.get('Contacto', '')).strip() if pd.notna(row.get('Contacto')) else ''
                    cuit = str(row.get('CUIT', '')).strip() if pd.notna(row.get('CUIT')) else None
                    telefono = str(row.get('Tel.', '')).strip() if pd.notna(row.get('Tel.')) else None
                    direccion = str(row.get('Dirreccion', '')).strip() if pd.notna(row.get('Dirreccion')) else None
                    
                    # Crear nombre combinado
                    nombre = f"{contacto} ({mercado} P{puesto})" if contacto and mercado and puesto else contacto or mercado
                    
                    if nombre and nombre.lower() not in ['nan', '']:
                        # Verificar si existe
                        cliente_existente = Cliente.query.filter_by(nombre=nombre).first()
                        if not cliente_existente:
                            cliente = Cliente(
                                nombre=nombre,
                                cuit=cuit if cuit != 'nan' else None,
                                telefono=telefono if telefono != 'nan' else None,
                                direccion=direccion if direccion != 'nan' else None,
                                activo=True
                            )
                            db.session.add(cliente)
                            clientes_creados += 1
                            if clientes_creados % 50 == 0:
                                db.session.commit()
                                print(f"  ✓ {clientes_creados} clientes procesados...")
                
                db.session.commit()
                print(f"✅ {clientes_creados} clientes cargados\n")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            db.session.rollback()
        
        # ==================== PROVEEDORES ====================
        print("="*70)
        print("🏭 CARGANDO PROVEEDORES...")
        print("="*70)
        try:
            archivo = base_path / '02 - Proveedores.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"📄 Archivo encontrado. Filas: {len(df)}")
                
                prov_creados = 0
                for idx, row in df.iterrows():
                    nombre = str(row.get('Proveedor', row.get('Razon social', ''))).strip()
                    cuit = str(row.get('Cuit', row.get('CUIT', ''))).strip() if pd.notna(row.get('Cuit', row.get('CUIT'))) else None
                    telefono = str(row.get('Tel', row.get('Telefono', ''))).strip() if pd.notna(row.get('Tel', row.get('Telefono'))) else None
                    
                    if nombre and nombre.lower() not in ['nan', 'proveedor', '']:
                        prov_existente = Proveedor.query.filter_by(nombre=nombre).first()
                        if not prov_existente:
                            proveedor = Proveedor(
                                nombre=nombre,
                                cuit=cuit if cuit != 'nan' else None,
                                telefono=telefono if telefono != 'nan' else None,
                                activo=True
                            )
                            db.session.add(proveedor)
                            prov_creados += 1
                            if prov_creados % 50 == 0:
                                db.session.commit()
                                print(f"  ✓ {prov_creados} proveedores procesados...")
                
                db.session.commit()
                print(f"✅ {prov_creados} proveedores cargados\n")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            db.session.rollback()
        
        # ==================== PROVEEDORES LOGÍSTICOS ====================
        print("="*70)
        print("🚚 CARGANDO PROVEEDORES LOGÍSTICOS...")
        print("="*70)
        try:
            archivo = base_path / '03 - Prov. Logisticos.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"📄 Archivo encontrado. Filas: {len(df)}")
                
                prov_log_creados = 0
                for idx, row in df.iterrows():
                    nombre = str(row.get('Proveedor', '')).strip() if pd.notna(row.get('Proveedor')) else None
                    telefono = str(row.get('Telefono', '')).strip() if pd.notna(row.get('Telefono')) else None
                    
                    if nombre and nombre.lower() not in ['nan', '']:
                        prov_log_existente = ProveedorLogistico.query.filter_by(nombre=nombre).first()
                        if not prov_log_existente:
                            prov_log = ProveedorLogistico(
                                nombre=nombre,
                                telefono=telefono if telefono != 'nan' else None,
                            )
                            db.session.add(prov_log)
                            prov_log_creados += 1
                
                db.session.commit()
                print(f"✅ {prov_log_creados} proveedores logísticos cargados\n")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            db.session.rollback()
        
        # ==================== PRODUCTOS ====================
        print("="*70)
        print("📦 CARGANDO PRODUCTOS...")
        print("="*70)
        try:
            archivo = base_path / '06 - Base productos por proveedores.xlsx'
            if archivo.exists():
                df = pd.read_excel(archivo)
                print(f"📄 Archivo encontrado. Filas: {len(df)}")
                
                prod_creados = 0
                for idx, row in df.iterrows():
                    nombre_prod = str(row.get('Fruta', row.get('Producto', ''))).strip()
                    nombre_prov = str(row.get('Proveedor', '')).strip() if pd.notna(row.get('Proveedor')) else None
                    variedad = str(row.get('Varidad', row.get('Variedad', ''))).strip() if pd.notna(row.get('Varidad', row.get('Variedad'))) else None
                    clasificacion = str(row.get('Clasificacion', '')).strip() if pd.notna(row.get('Clasificacion')) else None
                    
                    if nombre_prod and nombre_prod.lower() not in ['nan', '', 'fruta']:
                        # Buscar o crear proveedor
                        proveedor = None
                        if nombre_prov and nombre_prov.lower() != 'nan':
                            proveedor = Proveedor.query.filter_by(nombre=nombre_prov).first()
                        
                        if not proveedor:
                            proveedor = Proveedor.query.first()
                        
                        if proveedor:
                            # Crear nombre único con variedad
                            nombre_completo = f"{nombre_prod}" + (f" ({variedad})" if variedad and variedad != 'nan' else "")
                            
                            prod_existente = Producto.query.filter_by(nombre=nombre_completo, proveedor_id=proveedor.id).first()
                            if not prod_existente:
                                producto = Producto(
                                    nombre=nombre_completo,
                                    proveedor_id=proveedor.id,
                                    variedad=variedad if variedad != 'nan' else None,
                                    clasificacion=clasificacion if clasificacion != 'nan' else None,
                                    costo_unitario=0,
                                    stock=0,
                                    activo=True
                                )
                                db.session.add(producto)
                                prod_creados += 1
                                if prod_creados % 100 == 0:
                                    db.session.commit()
                                    print(f"  ✓ {prod_creados} productos procesados...")
                
                db.session.commit()
                print(f"✅ {prod_creados} productos cargados\n")
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            db.session.rollback()
        
        # ==================== PEDIDOS ====================
        print("="*70)
        print("📋 CARGANDO PEDIDOS...")
        print("="*70)
        try:
            archivo = base_path / '00 - PEDIDOS.xlsx'
            if archivo.exists():
                sheet_names = pd.ExcelFile(archivo).sheet_names
                df = pd.read_excel(archivo, sheet_name='Tabla')
                print(f"📄 Archivo encontrado. Filas: {len(df)}")
                
                pedidos_creados = 0
                pedidos_sin_cliente = 0
                
                for idx, row in df.iterrows():
                    # Obtener datos del cliente
                    nombre_cliente_base = str(row.get('Cliente', '')).strip() if pd.notna(row.get('Cliente')) else None
                    mercado = str(row.get('Mercado', '')).strip() if pd.notna(row.get('Mercado')) and str(row.get('Mercado')).lower() != 'nan' else None
                    puesto = str(row.get('Puesto', '')).strip() if pd.notna(row.get('Puesto')) and str(row.get('Puesto')).lower() != 'nan' else None
                    
                    cliente = None
                    
                    # Intentar búsqueda 1: Nombre completo construido
                    if nombre_cliente_base and mercado and puesto:
                        nombre_construido = f"{nombre_cliente_base} ({mercado} P{puesto})"
                        cliente = Cliente.query.filter_by(nombre=nombre_construido).first()
                    
                    # Intentar búsqueda 2: Nombre con LIKE parcial
                    if not cliente and nombre_cliente_base:
                        cliente = Cliente.query.filter(Cliente.nombre.like(f"%{nombre_cliente_base}%")).first()
                    
                    if cliente:
                        try:
                            # Procesar fecha
                            fecha = row.get('Fecha Vta', row.get('Fecha'))
                            if pd.notna(fecha) and hasattr(fecha, 'strftime'):
                                pass  # Usar la fecha tal cual
                            else:
                                fecha = datetime.now()
                            
                            numero = f"PED-{cliente.id}-{idx:05d}"
                            
                            pedido_existente = Pedido.query.filter_by(numero=numero).first()
                            if not pedido_existente:
                                costo_total = float(row.get('C. Total', 0)) if pd.notna(row.get('C. Total')) else 0
                                precio_venta = float(row.get('P. Total', 0)) if pd.notna(row.get('P. Total')) else 0
                                resultado = float(row.get('Resultado', 0)) if pd.notna(row.get('Resultado')) else 0
                                
                                # Convertir strings 'SI' a booleanos
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
                        except Exception as e:
                            print(f"  ⚠️  Error procesando pedido {idx}: {e}")
                            db.session.rollback()
                    else:
                        pedidos_sin_cliente += 1
                
                db.session.commit()
                print(f"✅ {pedidos_creados} pedidos cargados")
                if pedidos_sin_cliente > 0:
                    print(f"⚠️  {pedidos_sin_cliente} pedidos sin cliente asignado\n")
                else:
                    print()
            else:
                print(f"⚠️  Archivo no encontrado: {archivo}\n")
        except Exception as e:
            print(f"❌ Error: {e}\n")
            db.session.rollback()
        
        print("="*70)
        print("🎉 ¡MIGRACIÓN COMPLETADA!")
        print("="*70)
        
        # Mostrar estadísticas
        print(f"\n📊 TOTALES EN LA BASE DE DATOS:")
        print(f"   • Clientes: {Cliente.query.count()}")
        print(f"   • Proveedores: {Proveedor.query.count()}")
        print(f"   • Productos: {Producto.query.count()}")
        print(f"   • Pedidos: {Pedido.query.count()}")
        print(f"   • Prov. Logísticos: {ProveedorLogistico.query.count()}")


if __name__ == '__main__':
    cargar_datos()
