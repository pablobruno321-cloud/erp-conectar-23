#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para migrar la información de clientes desde el Excel de Pagos
a la base de datos de pagos existentes.
"""

import pandas as pd
import sys
import os

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from erp_app.app import app, db
from erp_app.models import Pago, Cliente

def migrar_clientes_pagos():
    """Migra la información de clientes desde el Excel a los pagos existentes"""
    
    with app.app_context():
        print("=== MIGRACIÓN DE CLIENTES A PAGOS ===")
        
        # Leer el Excel
        df = pd.read_excel('05 - Pagos.xlsx', sheet_name='Pagos')
        print(f"Total de registros en Excel: {len(df)}")
        
        # Obtener pagos existentes en la base de datos
        pagos_db = Pago.query.all()
        print(f"Total de pagos en base de datos: {len(pagos_db)}")
        
        # Crear diccionario de clientes por nombre para búsqueda rápida
        clientes_dict = {}
        for cliente in Cliente.query.all():
            clientes_dict[cliente.nombre.upper().strip()] = cliente
        
        print(f"Total de clientes en base de datos: {len(clientes_dict)}")
        
        # Contadores
        actualizados = 0
        no_encontrados = 0
        sin_cliente = 0
        
        # Procesar cada pago del Excel
        for _, row in df.iterrows():
            if pd.isna(row['Cliente']) or row['Cliente'] == '':
                sin_cliente += 1
                continue
            
            # Normalizar nombre del cliente
            nombre_cliente = str(row['Cliente']).strip().upper()
            
            # Buscar cliente en la base de datos
            if nombre_cliente in clientes_dict:
                cliente = clientes_dict[nombre_cliente]
                
                # Buscar pago correspondiente en la base de datos
                # Buscamos por proveedor, fecha e importe
                pago = None
                for p in pagos_db:
                    if (p.proveedor.nombre == row['Proveedores'] and 
                        p.fecha_pago.date() == pd.to_datetime(row['Fecha Pago']).date() and
                        abs(p.monto - row['Importe']) < 1):  # Tolerancia de $1
                        
                        pago = p
                        break
                
                if pago:
                    # Actualizar el pago con el cliente
                    if pago.cliente_id != cliente.id:
                        pago.cliente_id = cliente.id
                        print(f"Actualizado pago {pago.id}: {pago.proveedor.nombre} - {pago.monto} -> Cliente: {cliente.nombre}")
                        actualizados += 1
                else:
                    print(f"No se encontró pago correspondiente para: {row['Proveedores']} - {row['Fecha Pago']} - {row['Importe']}")
                    no_encontrados += 1
            else:
                print(f"Cliente no encontrado en base de datos: {nombre_cliente}")
                no_encontrados += 1
        
        # Guardar cambios
        try:
            db.session.commit()
            print(f"\n=== RESULTADOS ===")
            print(f"Pagos actualizados: {actualizados}")
            print(f"Registros sin cliente: {sin_cliente}")
            print(f"No encontrados (cliente o pago): {no_encontrados}")
            print("Migración completada exitosamente!")
        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar cambios: {e}")

if __name__ == "__main__":
    migrar_clientes_pagos()