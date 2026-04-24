#!/usr/bin/env python
"""Verificar cantidad de datos cargados"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'erp_app'))

from app import app
from models import Cliente, Proveedor, Producto, Pedido, ProveedorLogistico, Usuario

with app.app_context():
    print("=" * 70)
    print("📊 VERIFICACIÓN DE DATOS CARGADOS")
    print("=" * 70)
    print(f"👥 Clientes:        {Cliente.query.count()}")
    print(f"🏭 Proveedores:     {Proveedor.query.count()}")
    print(f"📦 Productos:       {Producto.query.count()}")
    print(f"📋 Pedidos:         {Pedido.query.count()}")
    print(f"🚚 Prov Logísticos: {ProveedorLogistico.query.count()}")
    print(f"👤 Usuarios:        {Usuario.query.count()}")
    print("=" * 70)
