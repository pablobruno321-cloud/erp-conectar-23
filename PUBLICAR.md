# Publicar en 20 minutos — Render + Neon

## Lo que YA tenés
- Repo GitHub: **https://github.com/pablobruno/erp-conectar-23**
- Código listo (`render.yaml`, migración a Postgres)

---

## PASO 1 — Neon (base de datos) — 5 min

1. Abrí **https://neon.tech** → **Sign up** (Google/GitHub).
2. **New project** → nombre: `erp-conectar23` → región cercana (ej. US East).
3. En el proyecto, pestaña **Dashboard** → **Connection string** → copiá la que dice **PostgreSQL**.
4. Debe verse así (guardala en el Bloc de notas):
   ```
   postgresql://neondb_owner:XXXX@ep-xxxxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

---

## PASO 2 — Subir código a GitHub — 2 min

En PowerShell (yo puedo hacer el push si ya está commiteado):

```powershell
cd "C:\Users\Pablo\Desktop\Visual\Proyecto 2"
git add .
git commit -m "Deploy Render + Neon"
git push origin main
```

---

## PASO 3 — Render (publicar web) — 10 min

1. **https://render.com** → **Get started** → entrá con **GitHub**.
2. Autorizá acceso a GitHub.
3. **New +** → **Blueprint**.
4. Elegí el repo **`erp-conectar-23`** (o `erp-conectar23`).
5. Render lee `render.yaml` → **Apply**.
6. Antes de que termine (o después en **Environment**):
   - **Add Environment Variable**
   - **Key:** `DATABASE_URL`
   - **Value:** pegá la connection string de Neon (Paso 1)
7. Esperá **Deploy live** (barra verde, 5–15 min).
8. Arriba verás la URL, ej.:
   ```
   https://erp-conectar-23.onrender.com
   ```
   Abrí: `https://TU-URL.onrender.com/login`

---

## PASO 4 — Copiar TUS datos a Neon — 5 min

En tu PC:

1. Doble clic en **`migrar_datos_nube.bat`**
2. Pegá la misma **DATABASE_URL** de Neon
3. Enter y esperá “Listo”

Volvé a la URL de Render → login con tu usuario de siempre.

---

## Si algo falla

| Problema | Solución |
|----------|----------|
| Deploy falla en Render | **Logs** del servicio → copiame el error |
| Login no funciona | Falta Paso 4 (migrar datos) o `DATABASE_URL` mal pegada |
| Página tarda mucho | Normal la 1ª vez tras 15 min sin uso (Render despierta) |
| Build error pandas | Avisame — a veces Render tarda en instalar |

---

## Checklist

- [ ] Cuenta Neon + connection string copiada
- [ ] Push a GitHub
- [ ] Render Blueprint + `DATABASE_URL` en Environment
- [ ] URL Render abre `/login`
- [ ] `migrar_datos_nube.bat` ejecutado
- [ ] Entrás con tu admin y ves tus clientes/pedidos

Cuando termines el **Paso 1**, pegame la connection string **sin la contraseña** (reemplazá XXXX) o decime en qué paso estás trabado.
