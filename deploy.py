#!/usr/bin/env python3
"""
Deploy en 2 pasos: GitHub → Render
"""
import subprocess
import os
import sys

def run(cmd):
    return subprocess.run(cmd, shell=True).returncode == 0

os.chdir(os.path.dirname(__file__))

print("""
╔════════════════════════════════════════════════════════════════╗
║         🚀 DEPLOY ERP CONECTAR 23 - 2 PASOS RÁPIDOS          ║
╚════════════════════════════════════════════════════════════════╝
""")

# PASO 1: GitHub
print("""
┌─ PASO 1: CREAR REPO EN GITHUB ─────────────────────────────────┐
│                                                                 │
│ 1. Abre: https://github.com/new                               │
│ 2. Repository name:   erp-conectar-23                         │
│ 3. Descripción:       ERP Sistema de Gestión Empresarial      │
│ 4. ✓ Public                                                    │
│ 5. Click: "Create repository"                                 │
│ 6. Copia la URL HTTPS mostrada (ej: https://github.com...)   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
""")

repo_url = input("📌 Pega la URL de GitHub aquí: ").strip()
if not repo_url.startswith("https://github.com"):
    print("❌ URL inválida")
    sys.exit(1)

run("git remote remove origin 2>nul") or True
run(f"git remote add origin {repo_url}")
run("git branch -M main")
print("\n⏳ Subiendo código a GitHub...")

if not run("git push -u origin main"):
    print("⚠️  Posible error en push. Abre GitHub y verifica la sincronización.")
else:
    print("✅ ¡GitHub sincronizado!")

# PASO 2: Render
print("""
┌─ PASO 2: DESPLEGAR EN RENDER ──────────────────────────────────┐
│                                                                 │
│ 1. Abre: https://render.com                                   │
│ 2. Haz login (usa GitHub para sincronizar automático)         │
│ 3. Dashboard → New + → Web Service                            │
│ 4. Selecciona: erp-conectar-23                                │
│ 5. Rellena:                                                    │
│    Name: erp-conectar-23                                      │
│    Build: pip install -r requirements.txt                     │
│    Start: gunicorn --workers 4 --bind 0.0.0.0:$PORT \\       │
│            "erp_app.app:app"                                  │
│                                                                 │
│ 6. Environment variables (Add):                               │
│    SECRET_KEY = """)

import secrets
secret = secrets.token_urlsafe(50)
print(secret + """
│    FLASK_ENV = production
│                                                                 │
│ 7. Click: "Create Web Service"                                │
│ 8. ¡LISTO! Espera 3-5 minutos a que despliegue               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

📍 Tu app en: https://erp-conectar-23.onrender.com
🔑 Email:    pablobruno321@hotmail.com
🔐 Pass:     admin123
""")

input("\n✅ ¿Deploy completado? Presiona ENTER...")
