# ⚡ DEPLOY EN 5 PASOS - CHEAT SHEET

## STEP 1: GitHub
```bash
cd "c:\Users\Pablo\Desktop\Visual\Proyecto 2"
git init
git add .
git commit -m "Initial: ERP System"
git remote add origin https://github.com/TU_USUARIO/erp-system.git
git branch -M main
git push -u origin main
```

## STEP 2: Render.com
1. Ve a https://render.com
2. Sign up con GitHub
3. Dashboard → New → Web Service
4. Selecciona tu repo `erp-system`

## STEP 3: Configuración Render
| Campo | Valor |
|-------|-------|
| Name | `erp-system` |
| Environment | `Python 3` |
| Region | `Ohio` |
| Build | `pip install -r requirements.txt` |
| Start | `gunicorn --workers 3 --bind 0.0.0.0:$PORT run:app` |

## STEP 4: Environment Variables (en Render)
| Key | Value |
|-----|-------|
| `SECRET_KEY` | (corre esto en tu terminal) |
| `FLASK_ENV` | `production` |

```python
# Para generar SECRET_KEY segura:
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## STEP 5: Deploy
- Click "Deploy Web Service"
- Espera 3-5 minutos
- ¡Listo! Tu URL es: `https://erp-system.onrender.com`

---

## 🔑 Próximo: Configura Admin
1. Abre tu URL
2. Crea usuario con `/registro` O
3. Va a `/admin/usuarios` (si ya existe admin)
4. Agrega usuarios con permisos

---

## ✅ Verificar que funciona
- Login en `/login`
- Dashboard en `/erp/1`
- Admin panel en `/admin/usuarios` (solo admin)
- Settings en `/configuracion`

---

**¡Listo en menos de 10 minutos!** 🚀
