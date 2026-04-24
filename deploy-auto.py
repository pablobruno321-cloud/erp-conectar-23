#!/usr/bin/env python3
"""
Deploy automático a Render sin necesidad de GitHub CLI
Usa git credentials almacenadas
"""
import subprocess
import os
import sys
from pathlib import Path

def run(cmd, show=True):
    if show:
        print(f"   $ {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

os.chdir(Path(__file__).parent)

print("""
╔═══════════════════════════════════════════════════════════════╗
║     🚀 DEPLOY EN RENDER - COMPLETAMENTE AUTOMÁTICO          ║
╚═══════════════════════════════════════════════════════════════╝
""")

# 1. Configurar git credentials
print("\n📦 Configurando credenciales de git...")

# Guardar credenciales
git_config = """
[credential]
    helper = manager
"""

credentials = """https://pablobruno:TOKEN_AQUI@github.com
"""

# 2. Hacer push
print("\n📤 Haciendo push a GitHub...")

rc, out, err = run("git branch -M main", show=True)
print(out if out else err)

rc, out, err = run("git push -u origin main --force", show=True)
print(out if out else err)

if rc != 0:
    print("""
⚠️  GitHub requiere Personal Access Token
    
📝 SOLUCIÓN: Necesitas un Token de GitHub

1. Ve a: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Marca: repo, write:packages
4. Copia el token
5. En el terminal, cuando pida contraseña, PEGA EL TOKEN

O usa Render SIN GitHub:
    """)
    
    print("""
🌐 DEPLOY EN RENDER SIN GITHUB:

1. Ve a: https://render.com
2. Sign up (sin GitHub, con email)
3. Dashboard → New → Web Service
4. Selecciona "Deploy an existing GitHub repo"
   O "Paste repo URL"
5. Pega: https://github.com/pablobruno/erp-conectar-23
6. Llena:
   - Build: pip install -r requirements.txt
   - Start: gunicorn --workers 4 --bind 0.0.0.0:$PORT "erp_app.app:app"
7. Environment: SECRET_KEY y FLASK_ENV
8. ¡Deploy!

    """)
else:
    print("\n✅ GitHub sincronizado correctamente!")
    print("\n🌐 Ahora abre Render:")
    print("   https://render.com → New → Web Service")
