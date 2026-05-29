"""Punto de entrada WSGI para Gunicorn / servidores Linux."""
from erp_app.app import app, init_db

init_db()
