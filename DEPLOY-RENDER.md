# 🚀 Guía de Deploy en Render (GRATIS)

Tu app ya está lista para publicarse en internet sin costo. Aquí está el paso a paso.

---

## 📋 Requisitos previos

1. Cuenta en **GitHub** (gratis)
2. Cuenta en **Render** (gratis) - https://render.com
3. Tu código en un repositorio de GitHub

---

## 🔧 Paso 1: Sube tu proyecto a GitHub

### 1.1 Crear repositorio en GitHub

```bash
# Si no lo has hecho aún, ve a https://github.com/new
# Nombre: erp-system
# Descripción: Sistema ERP de Gestión Empresarial
# Privado o Público (tu elección)
```

### 1.2 Inicializar Git localmente y subir código

```bash
cd c:\Users\Pablo\Desktop\Visual\Proyecto 2

# Inicializar repositorio git
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "Initial commit: Sistema ERP"

# Agregar repositorio remoto (reemplaza USERNAME con tu usuario de GitHub)
git remote add origin https://github.com/USERNAME/erp-system.git

# Subirlo a GitHub (rama main)
git branch -M main
git push -u origin main
```

---

## 🌐 Paso 2: Deploy en Render

### 2.1 Crear servicio web en Render

1. Ve a **https://render.com** y crea cuenta (usa Google/GitHub para más rápido)
2. Dashboard → **New +** → **Web Service**
3. Selecciona "Deploy an existing project from a Git repository"
4. Conecta tu cuenta GitHub y autoriza
5. Busca y selecciona `erp-system` (tu repositorio)

### 2.2 Configurar el servicio

- **Name**: `erp-system` (o como prefieras)
- **Environment**: `Python 3`
- **Region**: `Ohio` o la más cercana a ti
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn --workers 3 --bind 0.0.0.0:$PORT run:app`

### 2.3 Agregar variables de entorno (importante)

En la sección **Environment**, agrega:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | `tu-clave-super-secreta-aqui-min50-caracteres` |
| `FLASK_ENV` | `production` |

> Tip: genera una clave segura con:
> ```python
> import secrets
> print(secrets.token_urlsafe(50))
> ```

### 2.4 Plan y Deploy

- Plan: **Free** (tiene limitaciones pero funciona)
  - Gratis 750 horas/mes (24×365 = 8760h, así que OK para siempre-on)
  - se duerme si inactivo 15 min, se despierta en ~30seg
- Presiona **Deploy Web Service**
- Espera 3-5 minutos mientras compila

---

## ✅ Paso 3: Verifica que está corriendo

1. El dashboard de Render te mostrará un enlace como:
   ```
   https://erp-system.onrender.com
   ```

2. Haz clic y deberías ver:
   - La página de login
   - Puedes registrarte o usar credenciales de admin preexistentes

3. **Comparte este enlace** con quienes necesiten acceso
   - Solo pueden entrar con usuario + contraseña
   - Tienes control total desde `/admin/usuarios`

---

## 🔒 Seguridad (IMPORTANTE)

✅ **Render proporciona automáticamente:**
- HTTPS y certificado SSL (gratis)
- Firewall y protección DDoS

✅ **Tu app ya tiene:**
- Control de usuarios con login
- Admin panel para gestionar accesos
- Roles y permisos

⚠️ **Deberías hacer:**
- Cambiar `SECRET_KEY` a algo único y fuerte
- Crear usuarios admin con contraseñas seguras en `/admin/usuarios`
- NO guardes contraseñas en el código
- Revisa `/configuracion` para cambiar tu password

---

## 🚨 Troubleshooting

### "La app se duerme"
- Render duerme apps gratuitas si inactivas 15 min
- Se despiertan automáticamente, tarda ~30seg
- Solución: upgrade a plan "Starter" ($7/mes) si necesitas siempre-on

### "Error 500 o 503"
- Ve a Render Dashboard → Logs
- Mira qué error específico hay
- Generalmente es falta de dependencias en `requirements.txt`

### Cambios no aparecen
- Hace push nuevamente a GitHub
- Render detecta automáticamente cambios en `main`
- Redeploy 1-2 min después de hacer push

---

## 📊 Monitorear tu app

En el dashboard de Render:
- **Logs** → ver errores en tiempo real
- **Metrics** → CPU, memoria, requests
- **Deployments** → historial y rollback

---

## 🎯 URL final pública

Una vez deployado, comparte:
```
https://erp-system.onrender.com/
```

Usuarios pueden:
- Registrarse en `/registro`
- Loguearse en `/login`
- Acceder solo a funcionalidades autorizadas

Admin puede:
- Crear/editar/eliminar usuarios en `/admin/usuarios`
- Cambiar permisos y roles
- Inactivar usuarios

---

## 💡 Próximos pasos (opcional)

1. **Dominio personalizado**: $10/mes en Render → mapealo
   - Ejemplo: `https://erp-tunegocio.com`

2. **Base de datos PostgreSQL**: upgrade gratis en plan hobby
   - Reemplaza SQLite por PostgreSQL para mejor escala

3. **Backups automáticos**: configura en Render → Settings

4. **2FA**: agrega autenticación de dos factores en `/configuracion`

---

## 🤝 Soporte rápido

Si algo falla:
1. Verifica en Render Logs el mensaje de error exacto
2. Asegúrate `requirements.txt` tiene todas las dependencias
3. Confirma `run.py` apunta correcto a `app.py`

---

**¡Listo! Tu ERP ya estará en internet en menos de 10 minutos.** 🚀
