# Render — arranque del ERP (español)

## Qué tenés que tener en Settings

| Campo | Valor |
|-------|--------|
| **Root Directory** | vacío |
| **Build Command** | `pip install --upgrade pip && pip install gunicorn==21.2.0 && pip install -r requirements.txt` |
| **Start Command** | `python -m gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 120 wsgi:app` |

Repositorio conectado: `pablobruno321-cloud/erp-conectar-23` rama `main`.

Después: **Manual Deploy** → **Deploy latest commit**.

## Si falla

En **Logs**, la línea `Running '...'` tiene que decir `wsgi:app`, no `erp_app.app:app` ni solo `wsgi:app` sin `python -m gunicorn`.

Variable **DATABASE_URL** = connection string de Neon (PostgreSQL).
