import pandas as pd

excel_file = '07 - Costos Proveedor _ Pricing.xlsx'
sheets = pd.ExcelFile(excel_file).sheet_names
print('Hojas disponibles:', sheets)

for sheet in sheets:
    print(f'\n{"="*70}')
    print(f'HOJA: {sheet}')
    print("="*70)
    df = pd.read_excel(excel_file, sheet_name=sheet)
    print(f'Columnas: {list(df.columns)}')
    print(f'Total de filas: {len(df)}\n')
    print(df.head(10))
