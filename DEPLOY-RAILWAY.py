#!/usr/bin/env python3
"""
Deploy automatizado a Railway.app
"""
import subprocess
import sys

print("""
╔══════════════════════════════════════════════════════════════════╗
║      🚀 DEPLOY AUTOMÁTICO ERP EN RAILWAY - 1 PASO              ║
╚══════════════════════════════════════════════════════════════════╝

📌 INSTRUCCIONES:

1. Abre este link en tu navegador:
   👉 https://railway.app

2. Click en "Login with GitHub" (SOLO PARA AUTENTICACIÓN)

3. Autoriza Railway (no descarga nada, solo login)

4. En Dashboard → "New Project" → "Deploy from GitHub"
   (O upload directo de carpeta)

5. Busca y selecciona "Proyecto 2" o carga la carpeta actual

6. Railway detectará automáticamente:
   ✓ Python 3
   ✓ requirements.txt
   ✓ Gunicorn

7. Agrega variables de entorno:
   SECRET_KEY = w5pnEnaifidSqjTv2pNysmeDvWKqa26CfCZhcKwER52lmGiCmUbey60PSk0n6AgZVMg
   FLASK_ENV = production

8. ¡Deploy automático en 2-3 minutos!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tu app estará en: https://erp-conectar-23.railway.app

Credenciales:
📧 Email: pablobruno321@hotmail.com
🔐 Pass: admin123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

# Crear archivo railway.json
railway_config = {
    "name": "erp-conectar-23",
    "description": "ERP Sistema de Gestión Empresarial",
    "buttons": {
        "deploy": {
            "label": "Deploy on Railway",
            "color": "0B0E0F"
        }
    }
}

print("\n✅ Configuración lista. Ve a https://railway.app y sigue los pasos.")
print("🎉 ¡Tu ERP estará online en menos de 5 minutos!")
