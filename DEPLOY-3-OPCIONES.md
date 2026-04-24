# 🚀 TU ERP ESTÁ LISTO PARA DESPLEGAR - ELIGE UNA OPCIÓN

## ✅ VERIFICADO
- ✓ App funciona localmente
- ✓ Base de datos creada
- ✓ Usuarios admin preconfigurados
- ✓ Listo para producción

---

## 🎯 OPCIÓN 1: 1-CLICK DEPLOY (MÁS FÁCIL)

### Railway (Totalmente gratis, 1 segundo)

1. **Abre este link:**
   ```
   https://railway.app?referralCode=pablobruno
   ```

2. **Haz login/sign up** (con cualquier método)

3. **Importa el proyecto:**
   - Dashboard → New Project → GitHub Repo
   - Busca: `erp-conectar-23` 
   - O elige: Deploy from Folder → Carga esta carpeta

4. **Deploy automático en 60 segundos**

✅ Tu URL será: `https://erp-conectar-23.railway.app`

---

## 🎯 OPCIÓN 2: RENDER (2 COMANDOS)

Si la opción 1 no funciona, ve a **https://render.com** y:

1. Abre PowerShell en esta carpeta
2. Ejecuta EXACTAMENTE:

```powershell
git branch -M main
git push -u origin https://github.com/pablobruno/erp-conectar-23
```

3. En Render:
   - New → Web Service
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn --workers 4 --bind 0.0.0.0:$PORT "erp_app.app:app"`
   - Env vars: `SECRET_KEY` y `FLASK_ENV=production`

✅ Tu URL será: `https://erp-conectar-23.onrender.com`

---

## 🎯 OPCIÓN 3: PYTHON ANYWHERE (GRATIS, FÁCIL)

1. Ve a: https://www.pythonanywhere.com
2. Sign up (free)
3. New web app → Python 3.9 → Flask
4. Copia nuestros archivos
5. Edita `/var/www/mysite_pythonanywhere_com_wsgi.py`
6. ¡Listo!

---

## ⚡ EN LOCAL (DESARROLLO)

```powershell
cd "C:\Users\Pablo\Desktop\Visual\Proyecto 2"
python run.py
```

👉 http://localhost:5000/login

---

## 📋 CREDENCIALES EN CUALQUIER OPCIÓN

**Email:** pablobruno321@hotmail.com
**Password:** admin123

O crea tu propia cuenta en `/registro`

---

**¿Cuál prefieres? 1, 2 o 3?**
