"""
Arranque en la nube (Render).
Misma idea que run.py en tu PC: carpeta del proyecto + importar erp_app.
"""
import os
import sys

_raiz = os.path.dirname(os.path.abspath(__file__))
if _raiz not in sys.path:
    sys.path.insert(0, _raiz)

from erp_app.app import app, init_db

init_db()
