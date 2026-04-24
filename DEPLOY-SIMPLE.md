# 🚀 DEPLOY A RENDER - INSTRUCCIONES SIMPLES

## ✅ Estado Actual
- ✓ Código corregido y funcionando
- ✓ Git inicializado y committed
- ✓ Listo para Render

## 📤 STEP 1: Push a GitHub

Abre PowerShell aquí y ejecuta EXACTAMENTE esto:

```powershell
# 1. Crear repositorio en GitHub
# Ve a: https://github.com/new
# - Repository name: erp-conectar-23
# - Description: ERP Sistema de Gestión Empresarial
# - Public: ✓
# - Create repository

# 2. Copia la URL HTTPS y ejecuta:
git remote add origin https://github.com/TU_USUARIO/erp-conectar-23
git branch -M main
git push -u origin main

# Si pide credenciales, usa tu GitHub token
```

## 🌐 STEP 2: Deploy en Render

1. Ve a: **https://render.com**
2. Login/Sign up
3. **New + → Web Service**
4. Conecta tu repositorio **erp-conectar-23**
5. Rellena EXACTO así:

```
Name:         erp-conectar-23
Environment:  Python 3
Build:        pip install -r requirements.txt
Start:        gunicorn --workers 4 --bind 0.0.0.0:$PORT "erp_app.app:app"
Region:       Ohio (o tu preferencia)
```

6. Environment Variables (Add):

```
SECRET_KEY = w5pnEnaifidSqjTv2pNysmeDvWKqa26CfCZhcKwER52lmGiCmUbey60PSk0n6AgZVMg
FLASK_ENV = production
```

7. **Create Web Service**

⏳ Espera 3-5 minutos a que despliegue

## ✅ RESULTADO

Tu app estará en: **https://erp-conectar-23.onrender.com**

### Credenciales
- 📧 Email: `pablobruno321@hotmail.com`
- 🔐 Contraseña: `admin123`

## 🏠 O USA EN LOCAL

Para desarrollo local:
```powershell
cd "C:\Users\Pablo\Desktop\Visual\Proyecto 2"
python run.py
```

Luego abre: **http://127.0.0.1:5000/login**

---

**¿Problemas?** Chequea:
- ✓ El repo existe en GitHub y es PÚBLICO
- ✓ El nombre de la app en Render NO tiene mayúsculas
- ✓ Las variables de entorno están sin comillas
- ✓ Esperaste los 3-5 minutos de deploy
