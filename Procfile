web: python -c "from erp_app.app import init_db; init_db()" && python -m gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 erp_app.app:app
release: python -c "from erp_app.app import app, init_db; init_db()"
