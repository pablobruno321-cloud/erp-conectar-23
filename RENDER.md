# Publicar GRATIS en Render (+ base de datos Neon)

Render publica tu ERP **sin pagar**. Para que **no se pierdan los datos**, usamos **Neon** (PostgreSQL gratis) como base en la nube.

| Servicio | Costo | Para qué |
|----------|-------|----------|
| **Render** | Gratis | Publica la web (URL https) |
| **Neon** | Gratis | Guarda clientes, pedidos, cobranzas… |

> Render gratis **se duerme** si nadie entra ~15 min. El primer acceso tarda ~30 s en despertar. Es normal.

---

## Parte 1 — Base de datos gratis (Neon) — 5 min

1. Entrá a **[https://neon.tech](https://neon.tech)** → Sign up (gratis).
2. **New project** → nombre ej. `erp-conectar23`.
3. Copiá la **Connection string** (PostgreSQL), algo como:
   ```
   postgresql://usuario:password@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Guardala — la vas a pegar en Render.

---

## Parte 2 — Subir el código a GitHub — 10 min

Render despliega desde GitHub. Si no tenés repo:

1. **[github.com](https://github.com)** → cuenta gratis → **New repository** → nombre `erp-conectar23` → **Create**.
2. En tu PC (PowerShell), en la carpeta del proyecto:

```powershell
cd "C:\Users\Pablo\Desktop\Visual\Proyecto 2"
git init
git add .
git commit -m "ERP listo para Render"
git branch -M main
git remote add origin https://github.com/TU-USUARIO/erp-conectar23.git
git push -u origin main
```

(Reemplazá `TU-USUARIO` por tu usuario de GitHub.)

> `erp.db` **no se sube** (está en .gitignore). Los datos los pasás en el Paso 4.

---

## Parte 3 — Publicar en Render — 5 min

1. **[https://render.com](https://render.com)** → Sign up (gratis, podés entrar con GitHub).
2. **New +** → **Blueprint** (o **Web Service** si no ves Blueprint).
3. Conectá tu repo `erp-conectar23`.
4. Render detecta `render.yaml` → **Apply**.
5. En **Environment** del servicio, agregá manualmente:
   - **Key:** `DATABASE_URL`
   - **Value:** la connection string de Neon (Paso 1)
6. Esperá el deploy (5–10 min). Te da una URL:
   ```
   https://erp-conectar23.onrender.com
   ```

---

## Parte 4 — Pasar TUS datos de la PC a la nube — 5 min

En tu PC, con la misma `DATABASE_URL` de Neon:

```powershell
cd "C:\Users\Pablo\Desktop\Visual\Proyecto 2"
pip install psycopg2-binary pandas
set DATABASE_URL=postgresql://...tu-string-de-neon...
python scripts/migrar_a_postgres.py
```

Eso copia todo de `erp_app\erp.db` a Neon. Después entrá a la URL de Render con **el mismo login** de siempre.

---

## Listo — cómo usarlo

- **Vos y tu equipo:** `https://tu-app.onrender.com/login`
- **Tu PC apagada:** ✅ Sigue funcionando
- **Mismos datos para todos:** ✅ Una sola base en Neon
- **Crear usuarios:** Admin → Usuarios (igual que antes)

---

## Limitaciones del plan gratis

| Tema | Qué pasa |
|------|----------|
| Inactividad | Tras ~15 min sin uso, la web duerme; el 1.er click tarda ~30 s |
| Adjuntos remitos | En Render gratis el disco es temporal; los PDF/imágenes pueden perderse al **redeploy**. Los pedidos y montos en la DB sí quedan en Neon |
| Muchos usuarios a la vez | Plan free = recursos limitados; alcanza para equipos chicos |

Si más adelante necesitás más: Render paid ~USD 7/mes o VPS ~USD 5/mes.

---

## Si falla el deploy

- Logs en Render → tu servicio → **Logs**
- Error común: falta `DATABASE_URL` → agregala en Environment
- Error Postgres: la URL debe empezar con `postgresql://` y tener `?sslmode=require`

---

## Resumen

```
GitHub (código) → Render (web gratis) → Neon (datos gratis)
         ↑
   migrar_a_postgres.py (copia erp.db una vez)
```

Cuando tengas la URL de Render o te trabes en GitHub/Neon, escribime en qué paso estás y lo resolvemos.
