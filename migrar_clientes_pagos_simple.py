#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simple para migrar la información de clientes desde el Excel de Pagos
a la base de datos de pagos existentes.
"""

import pandas as pd
import sys
import os

# Añadir el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def migrar_clientes_pagos():
    """Migra la información de clientes desde el Excel a los pagos existentes"""
    
    print("=== MIGRACIÓN DE CLIENTES A PAGOS ===")
    
    # Leer el Excel
    df = pd.read_excel('05 - Pagos.xlsx', sheet_name='Pagos')
    print(f"Total de registros en Excel: {len(df)}")
    
    # Contar pagos por cliente
    clientes_con_pagos = df['Cliente'].value_counts()
    print(f"\n=== PAGOS POR CLIENTE ===")
    for cliente, cantidad in clientes_con_pagos.items():
        if pd.notna(cliente) and cliente != '':
            print(f'{cliente}: {cantidad} pagos')
    
    total_con_cliente = clientes_con_pagos.sum()
    total_sin_cliente = df['Cliente'].isna().sum()
    
    print(f'\nTotal de pagos con cliente: {total_con_cliente}')
    print(f'Total de pagos sin cliente: {total_sin_cliente}')
    print(f'Porcentaje con cliente: {(total_con_cliente / len(df) * 100):.1f}%')
    
    print("\n=== RESUMEN ===")
    print("Los siguientes clientes tienen pagos registrados en el Excel:")
    for cliente, cantidad in clientes_con_pagos.items():
        if pd.notna(cliente) and cliente != '':
            print(f"- {cliente}: {cantidad} pagos")
    
    print(f"\nPara migrar esta información al ERP, deberás:")
    print("1. Crear los clientes en el ERP (si no existen)")
    print("2. Registrar los pagos en el formulario de pagos")
    print("3. Asignar el cliente correspondiente en cada pago")
    
    print("\n=== PRIMEROS 10 REGISTROS PARA REFERENCIA ===")
    print(df[['ID', 'Proveedores', 'Fecha Pago', 'Cliente', 'Importe', 'Comentarios']].head(10))

if __name__ == "__main__":
    migrar_clientes_pagos()