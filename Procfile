web: gunicorn --workers 1 --threads 8 --timeout 120 wsgi:app
release: python -c "from erp_app.app import app, init_db; init_db()"
