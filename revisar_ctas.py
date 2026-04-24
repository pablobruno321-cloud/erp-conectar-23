import pandas as pd
import os

files = [
    '00 - PEDIDOS.xlsx',
    '01 - Clientes.xlsx',
    '04 - Cobranzas.xlsx',
    '05 - Pagos.xlsx'
]

for file in files:
    if os.path.exists(file):
        print(f"\n{'='*70}")
        print(f"ARCHIVO: {file}")
        print("="*70)
        
        xls = pd.ExcelFile(file)
        print(f"Hojas: {xls.sheet_names}\n")
        
        for sheet in xls.sheet_names:
            df = pd.read_excel(file, sheet_name=sheet)
            print(f"\n--- HOJA: {sheet} ---")
            print(f"Columnas: {list(df.columns)}")
            print(f"Filas: {len(df)}")
            if len(df) > 0:
                print(df.head(3))
