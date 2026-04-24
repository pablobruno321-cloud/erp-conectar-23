#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd

def analizar_pagos():
    """Analiza los pagos en el Excel para entender la distribución de clientes"""
    
    # Leer el Excel
    df = pd.read_excel('05 - Pagos.xlsx', sheet_name='Pagos')
    
    print("=== ANÁLISIS DE PAGOS ===")
    print(f"Total de registros: {len(df)}")
    
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
    
    # Mostrar primeros registros para entender el formato
    print(f"\n=== PRIMEROS 10 REGISTROS ===")
    print(df[['ID', 'Proveedores', 'Fecha Pago', 'Cliente', 'Importe']].head(10))

if __name__ == "__main__":
    analizar_pagos()