#!/usr/bin/env python
"""
Script para migrar datos de Excel a la base de datos
Ejecutar: python migrate_data.py
"""

import pandas as pd
import os
import sys
from datetime import datetime
from pathlib import Path

# Agregar erp_app al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

from app import app, db
from models import Cliente, Proveedor, Producto, Pedido, ItemPedido, ProveedorLogistico, Usuario

def migrar_datos():
    with app.app_context():
        # Crear usuario admin por defecto
        print("Creando usuario admin...")
        try:
            admin = Usuario.query.filter_by(email='admin@erp.com').first()
            if not admin:
                admin = Usuario(
                    email='admin@erp.com',
                    nombre='Administrador',
                    rol='admin',
                    activo=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ Usuario admin creado: admin@erp.com / admin123")
            else:
                print("✓ Usuario admin ya existe")
        except Exception as e:
            print(f"Error al crear admin: {e}")
        
        # Rutas de los archivos Excel
        base_path = Path(__file__).parent
        excel_files = {
            'clientes': base_path / '01 - Clientes.xlsx',
            'proveedores': base_path / '02 - Proveedores.xlsx',
            'prov_logisticos': base_path / '03 - Prov. Logisticos.xlsx',
            'productos': base_path / '06 - Base productos por proveedores.xlsx',
            'pedidos': base_path / '00 - PEDIDOS.xlsx',
        }
        
        # ==================== CLIENTES ====================
        print("\n⏳ Migrando clientes...")
        try:
            if excel_files['clientes'].exists():
                df_clientes = pd.read_excel(excel_files['clientes'])
                
                # Las columnas varían, detectar automáticamente
                col_nombre = next((col for col in df_clientes.columns if 'nombre' in col.lower() or 'cliente' in col.lower()), df_clientes.columns[0])
                col_cuit = next((col for col in df_clientes.columns if 'cuit' in col.lower()), None)
                col_telefono = next((col for col in df_clientes.columns if 'teléfono' in col.lower() or 'telefono' in col.lower()), None)
                
                clientes_creados = 0
                for idx, row in df_clientes.iterrows():
                    nombre = str(row[col_nombre]).strip() if pd.notna(row[col_nombre]) else None
                    
                    if nombre and nombre.lower() != 'nan' and nombre != '' and nombre.lower() != 'cliente':
                        cliente_existente = Cliente.query.filter_by(nombre=nombre).first()
                        if not cliente_existente:
                            cliente = Cliente(
                                nombre=nombre,
                                cuit=str(row[col_cuit]).strip() if col_cuit and pd.notna(row[col_cuit]) else None,
                                telefono=str(row[col_telefono]).strip() if col_telefono and pd.notna(row[col_telefono]) else None,
                            )
                            db.session.add(cliente)
                            clientes_creados += 1
                
                if clientes_creados > 0:
                    db.session.commit()
                    print(f"✓ {clientes_creados} clientes importados")
                else:
                    print("✓ No hay nuevos clientes para importar")
        except Exception as e:
            print(f"✗ Error al migrar clientes: {e}")
            db.session.rollback()
        
        # ==================== PROVEEDORES ====================
        print("\n⏳ Migrando proveedores...")
        try:
            if excel_files['proveedores'].exists():
                df_prov = pd.read_excel(excel_files['proveedores'])
                
                col_nombre = next((col for col in df_prov.columns if 'nombre' in col.lower() or 'proveedor' in col.lower()), df_prov.columns[0])
                col_cuit = next((col for col in df_prov.columns if 'cuit' in col.lower()), None)
                col_telefono = next((col for col in df_prov.columns if 'teléfono' in col.lower() or 'telefono' in col.lower()), None)
                
                prov_creados = 0
                for idx, row in df_prov.iterrows():
                    nombre = str(row[col_nombre]).strip() if pd.notna(row[col_nombre]) else None
                    
                    if nombre and nombre.lower() != 'nan' and nombre != '' and nombre.lower() != 'proveedor':
                        prov_existente = Proveedor.query.filter_by(nombre=nombre).first()
                        if not prov_existente:
                            proveedor = Proveedor(
                                nombre=nombre,
                                cuit=str(row[col_cuit]).strip() if col_cuit and pd.notna(row[col_cuit]) else None,
                                telefono=str(row[col_telefono]).strip() if col_telefono and pd.notna(row[col_telefono]) else None,
                            )
                            db.session.add(proveedor)
                            prov_creados += 1
                
                if prov_creados > 0:
                    db.session.commit()
                    print(f"✓ {prov_creados} proveedores importados")
                else:
                    print("✓ No hay nuevos proveedores para importar")
        except Exception as e:
            print(f"✗ Error al migrar proveedores: {e}")
            db.session.rollback()
        
        # ==================== PROVEEDORES LOGÍSTICOS ====================
        print("\n⏳ Migrando proveedores logísticos...")
        try:
            if excel_files['prov_logisticos'].exists():
                df_prov_log = pd.read_excel(excel_files['prov_logisticos'])
                
                col_nombre = next((col for col in df_prov_log.columns if 'nombre' in col.lower()), df_prov_log.columns[0])
                col_telefono = next((col for col in df_prov_log.columns if 'teléfono' in col.lower() or 'telefono' in col.lower()), None)
                
                prov_log_creados = 0
                for idx, row in df_prov_log.iterrows():
                    nombre = str(row[col_nombre]).strip() if pd.notna(row[col_nombre]) else None
                    
                    if nombre and nombre.lower() != 'nan' and nombre != '':
                        prov_log_existente = ProveedorLogistico.query.filter_by(nombre=nombre).first()
                        if not prov_log_existente:
                            prov_log = ProveedorLogistico(
                                nombre=nombre,
                                telefono=str(row[col_telefono]).strip() if col_telefono and pd.notna(row[col_telefono]) else None,
                            )
                            db.session.add(prov_log)
                            prov_log_creados += 1
                
                if prov_log_creados > 0:
                    db.session.commit()
                    print(f"✓ {prov_log_creados} proveedores logísticos importados")
                else:
                    print("✓ No hay nuevos proveedores logísticos para importar")
        except Exception as e:
            print(f"✗ Error al migrar proveedores logísticos: {e}")
            db.session.rollback()
        
        # ==================== PRODUCTOS ====================
        print("\n⏳ Migrando productos...")
        try:
            if excel_files['productos'].exists():
                df_prod = pd.read_excel(excel_files['productos'])
                
                col_fruta = next((col for col in df_prod.columns if 'fruta' in col.lower() or 'nombre' in col.lower() or 'producto' in col.lower()), df_prod.columns[0] if len(df_prod.columns) > 0 else None)
                col_proveedor = next((col for col in df_prod.columns if 'proveedor' in col.lower()), None)
                col_clasificacion = next((col for col in df_prod.columns if 'clasificación' in col.lower() or 'clasificacion' in col.lower()), None)
                col_variedad = next((col for col in df_prod.columns if 'variedad' in col.lower()), None)
                col_marca = next((col for col in df_prod.columns if 'marca' in col.lower()), None)
                col_envase = next((col for col in df_prod.columns if 'envase' in col.lower()), None)
                col_costo = next((col for col in df_prod.columns if 'costo' in col.lower() or 'precio' in col.lower()), None)
                
                prod_creados = 0
                for idx, row in df_prod.iterrows():
                    nombre_prod = str(row[col_fruta]).strip() if col_fruta and pd.notna(row[col_fruta]) else None
                    nombre_prov = str(row[col_proveedor]).strip() if col_proveedor and pd.notna(row[col_proveedor]) else None
                    
                    if nombre_prod and nombre_prod.lower() != 'nan' and nombre_prod != '':
                        # Buscar o crear proveedor
                        proveedor = None
                        if nombre_prov and nombre_prov.lower() != 'nan':
                            proveedor = Proveedor.query.filter_by(nombre=nombre_prov).first()
                        
                        if not proveedor:
                            proveedor = Proveedor.query.first()
                        
                        if proveedor:
                            producto_existente = Producto.query.filter_by(nombre=nombre_prod, proveedor_id=proveedor.id).first()
                            if not producto_existente:
                                producto = Producto(
                                    nombre=nombre_prod,
                                    proveedor_id=proveedor.id,
                                    clasificacion=str(row[col_clasificacion]).strip() if col_clasificacion and pd.notna(row[col_clasificacion]) else None,
                                    variedad=str(row[col_variedad]).strip() if col_variedad and pd.notna(row[col_variedad]) else None,
                                    marca=str(row[col_marca]).strip() if col_marca and pd.notna(row[col_marca]) else None,
                                    envase=str(row[col_envase]).strip() if col_envase and pd.notna(row[col_envase]) else None,
                                    costo_unitario=float(row[col_costo]) if col_costo and pd.notna(row[col_costo]) and str(row[col_costo]).replace('.','').replace('-','').isdigit() else 0
                                )
                                db.session.add(producto)
                                prod_creados += 1
                
                if prod_creados > 0:
                    db.session.commit()
                    print(f"✓ {prod_creados} productos importados")
                else:
                    print("✓ No hay nuevos productos para importar")
        except Exception as e:
            print(f"✗ Error al migrar productos: {e}")
            db.session.rollback()
        
        # ==================== PEDIDOS ====================
        print("\n⏳ Migrando pedidos...")
        try:
            if excel_files['pedidos'].exists():
                # Leer la primera hoja "Tabla"
                df_pedidos = pd.read_excel(excel_files['pedidos'], sheet_name='Tabla')
                
                col_fecha = next((col for col in df_pedidos.columns if 'fecha' in col.lower() and 'vta' in col.lower()), None)
                col_cliente = next((col for col in df_pedidos.columns if 'cliente' in col.lower()), None)
                col_fruta = next((col for col in df_pedidos.columns if 'fruta' in col.lower()), None)
                col_cantidad = next((col for col in df_pedidos.columns if 'cantidad' in col.lower() or 'pallets' in col.lower()), None)
                col_mercado = next((col for col in df_pedidos.columns if 'mercado' in col.lower()), None)
                col_puesto = next((col for col in df_pedidos.columns if 'puesto' in col.lower()), None)
                col_pv = next((col for col in df_pedidos.columns if 'pv' in col.lower()), None)
                col_c_total = next((col for col in df_pedidos.columns if 'c. total' in col.lower() or 'costo' in col.lower()), None)
                col_p_total = next((col for col in df_pedidos.columns if 'p. total' in col.lower() or 'precio' in col.lower()), None)
                
                pedidos_creados = 0
                for idx, row in df_pedidos.iterrows():
                    fecha_vta = row[col_fecha] if col_fecha and pd.notna(row[col_fecha]) else datetime.now()
                    nombre_cliente = str(row[col_cliente]).strip() if col_cliente and pd.notna(row[col_cliente]) else None
                    nombre_fruta = str(row[col_fruta]).strip() if col_fruta and pd.notna(row[col_fruta]) else None
                    
                    if nombre_cliente and nombre_cliente.lower() != 'nan' and nombre_cliente != '':
                        cliente = Cliente.query.filter_by(nombre=nombre_cliente).first()
                        if cliente:
                            numero_pedido = f"PED-{int(idx)}-{fecha_vta.strftime('%Y%m%d') if hasattr(fecha_vta, 'strftime') else '00000000'}"
                            pedido_existente = Pedido.query.filter_by(numero=numero_pedido).first()
                            
                            if not pedido_existente:
                                try:
                                    pedido = Pedido(
                                        numero=numero_pedido,
                                        cliente_id=cliente.id,
                                        fecha_venta=fecha_vta if hasattr(fecha_vta, 'strftime') else datetime.now(),
                                        mercado=str(row[col_mercado]).strip() if col_mercado and pd.notna(row[col_mercado]) else None,
                                        puesto=str(row[col_puesto]).strip() if col_puesto and pd.notna(row[col_puesto]) else None,
                                        costo_total=float(row[col_c_total]) if col_c_total and pd.notna(row[col_c_total]) and isinstance(row[col_c_total], (int, float)) else 0,
                                        precio_venta_total=float(row[col_p_total]) if col_p_total and pd.notna(row[col_p_total]) and isinstance(row[col_p_total], (int, float)) else 0,
                                    )
                                    
                                    # Calcular resultado
                                    pedido.resultado = pedido.precio_venta_total - pedido.costo_total
                                    
                                    # Agregar item si hay producto
                                    if nombre_fruta and nombre_fruta.lower() != 'nan':
                                        producto = Producto.query.filter(Producto.nombre.ilike(f'%{nombre_fruta}%')).first()
                                        if not producto:
                                            # Crear producto si no existe
                                            proveedor = Proveedor.query.first()
                                            if proveedor:
                                                producto = Producto(
                                                    nombre=nombre_fruta,
                                                    proveedor_id=proveedor.id
                                                )
                                                db.session.add(producto)
                                                db.session.flush()
                                        
                                        if producto:
                                            cantidad = float(row[col_cantidad]) if col_cantidad and pd.notna(row[col_cantidad]) and isinstance(row[col_cantidad], (int, float)) else 1
                                            precio_unitario = (pedido.precio_venta_total / cantidad) if cantidad > 0 else 0
                                            
                                            item = ItemPedido(
                                                producto_id=producto.id,
                                                cantidad=cantidad,
                                                precio_unitario=precio_unitario,
                                                subtotal=pedido.precio_venta_total
                                            )
                                            pedido.items.append(item)
                                    
                                    # Actualizar saldo del cliente
                                    cliente.saldo += pedido.precio_venta_total
                                    
                                    db.session.add(pedido)
                                    pedidos_creados += 1
                                except Exception as e:
                                    print(f"⚠ Error en pedido {idx}: {e}")
                                    continue
                
                if pedidos_creados > 0:
                    db.session.commit()
                    print(f"✓ {pedidos_creados} pedidos importados")
                else:
                    print("✓ No hay nuevos pedidos para importar")
        except Exception as e:
            print(f"✗ Error al migrar pedidos: {e}")
            db.session.rollback()
        
        print("\n" + "="*60)
        print("✓ Migración completada")
        print("="*60)

if __name__ == '__main__':
    migrar_datos()
