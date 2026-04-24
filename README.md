# ERP - Sistema de Gestión Empresarial

¡Bienvenido! Este es tu nuevo ERP web basado en la estructura que tenías en Google Sheets.

## ✨ Nuevas funcionalidades

✅ **Autenticación por Email** - Login y registro de usuarios  
✅ **Gestión de Usuarios** - Control de acceso y permisos  
✅ **Gestión de Clientes** - Crear, editar y ver clientes  
✅ **Gestión de Proveedores** - Administrar proveedores  
✅ **Gestión de Productos** - Catálogo de productos por proveedor  
✅ **Pedidos/Ventas** - Crear pedidos con múltiples items  
✅ **Cobranzas** - Registrar cobros de clientes  
✅ **Pagos** - Registrar pagos a proveedores  
✅ **Reportes** - Análisis de ventas y saldos  
✅ **Datos Precargados** - Todos tus datos de Google Sheets importados

## 🚀 Cómo ejecutar

### Paso 1: Instalar dependencias
```powershell
pip install -r requirements.txt
```

### Paso 2: Ejecutar la aplicación
```powershell
python run.py
```

### Paso 3: Abrir en el navegador
Ve a: **http://localhost:5000**

## 📝 Credenciales de Acceso

### Cuenta de Administrador (ya creada)
- **Email:** `admin@erp.com`
- **Contraseña:** `admin123`

### Primera vez
1. Ve a http://localhost:5000
2. Inicia sesión con admin@erp.com / admin123
3. O registra tu propia cuenta haciendo clic en "Regístrate aquí"

## 📊 Estructura del proyecto

```
├── run.py                    # Script principal para ejecutar
├── requirements.txt          # Dependencias Python
├── migrate_data.py          # Script para migrar datos de Excel
│
└── erp_app/
    ├── app.py               # Aplicación Flask y rutas
    ├── models.py            # Modelos de base de datos
    ├── auth.py              # Sistema de autenticación
    ├── erp.db              # Base de datos (se crea automáticamente)
    │
    ├── templates/           # Páginas HTML
    │   ├── base.html        # Plantilla base con navegación
    │   ├── login.html       # Página de login
    │   ├── registro.html    # Página de registro
    │   ├── index.html       # Dashboard
    │   ├── clientes/
    │   ├── proveedores/
    │   ├── productos/
    │   ├── pedidos/
    │   ├── cobranzas/
    │   ├── pagos/
    │   └── reportes/
    │
    └── static/              # CSS y JavaScript
        ├── css/
        └── js/
```

## 🔐 Sistema de Autenticación

El ERP incluye un sistema completo de autenticación:

1. **Login seguro** - Contraseñas hasheadas con Werkzeug
2. **Registro de usuarios** - Validación de email y contraseña
3. **Control de sesiones** - Las páginas requieren estar logueado
4. **Roles de usuario** - Admin y Usuario regular

### Crear nuevos usuarios
1. Haz clic en "Regístrate aquí" en la página de login
2. Rellena el formulario con:
   - Nombre completo
   - Email
   - Contraseña (mínimo 6 caracteres)
3. Se creará la cuenta automáticamente

### Cambiar contraseña (Próxima actualización)
Se puede agregar funcionalidad para cambiar contraseña

## 📥 Importación de Datos

Ya se han importado automáticamente:
- ✓ 10 Proveedores
- ✓ 7 Proveedores Logísticos  
- ✓ 37 Productos
- ✓ Histórico de Pedidos (si está disponible)

Si necesitas reimportar:
```powershell
python migrate_data.py
```

## 💾 Funcionalidades principales

### 1. Dashboard
- Vista general de estadísticas
- Total de clientes, proveedores y pedidos
- Venta total y deuda de clientes
- Bienvenida personalizada

### 2. Usuarios (New!)
- Sistema de login con email
- Registro de nuevas cuentas
- Sesiones seguras
- Cerrar sesión

### 3. Clientes
- Crear nuevos clientes
- Ver saldo de cada cliente
- Historial de pedidos
- Edición de datos

### 4. Productos
- Gestión de productos por proveedor
- Controlar costo unitario y stock
- Clasificación, variedad y marca

### 5. Pedidos
- Crear pedidos con múltiples productos
- Cálculo automático de costos y resultados
- Seguimiento de estado (Pendiente, Cargado, Entregado)
- Historial completo

### 6. Reportes
- **Reporte de Ventas**: Análisis de cada venta, margen de ganancia
- **Reporte de Saldos**: Deuda de clientes y pagos a proveedores

## 🎯 Primeros pasos recomendados

1. **Inicia sesión** con admin@erp.com / admin123
2. **Ve al Dashboard** para ver estadísticas
3. **Explora los datos** ya importados
4. **Crea nuevos clientes** en la sección Clientes
5. **Crea pedidos** con los productos existentes
6. **Consulta reportes** para análisis

## ⚙️ Configuración

### Variable de sesión
```python
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui'
```
Cambia esta clave en producción para mayor seguridad.

### Base de datos
Usa SQLite por defecto (sin necesidad de servidor externo).
Para cambiar a PostgreSQL o MySQL, modifica `app.config['SQLALCHEMY_DATABASE_URI']`

## 🔧 Próximos pasos (Expandir el ERP)

Puedes agregar:
- 📊 Más reportes con gráficos
- 👥 Gestión de permisos por rol
- 📧 Envío de emails de confirmación
- 📱 App móvil
- 🔗 Integración con bancos
- 💾 Backup automático de BD
- 📈 Dashboard con gráficos
- 🔔 Notificaciones
- 📄 Impresión de reportes

## ⚠️ Notas importantes

- La base de datos se guarda en `erp_app/erp.db`
- Los datos persisten entre ejecuciones
- La aplicación usa SQLite, sin necesidad de servidor externo
- El interfaz es responsive y funciona en escritorio y móvil
- En desarrollo usa debug mode automáticamente
- Para producción, usa un servidor WSGI como Gunicorn

## 🐛 Solución de problemas

### Error: "puerto 5000 ya en uso"
```powershell
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Error: "No module named Flask"
```powershell
pip install -r requirements.txt
```

### Restablecer base de datos
Elimina `erp_app/erp.db` y ejecuta nuevamente `python run.py`

## 📧 Contacto y soporte

Si tienes dudas sobre cómo usar alguna funcionalidad, contacta al equipo de desarrollo.

---

**¡A disfrutar tu nuevo ERP!** 🚀

Versión 1.0 - Marzo 2026
