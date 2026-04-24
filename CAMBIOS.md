# Resumen de Cambios - ERP Sistema de Gestión Empresarial

## Cambios Realizados

### 1. Dashboard con Gráficos
✅ **Archivo:** `erp_app/templates/index.html`
- Agregado Chart.js CDN
- 4 gráficos interactivos:
  - Línea: Ventas por Mes
  - Barras: Ganancia por Mes
  - Doughnut: Top 5 Clientes
  - Barras Horizontal: Top 5 Productos

✅ **Archivo:** `erp_app/app.py` - Función `inicio()`
- Cálculo de ventas por mes (últimos 12 meses)
- Cálculo de ganancia por mes
- Top 5 clientes por monto de venta
- Top 5 productos por cantidad vendida

### 2. Autenticación y Usuarios Predeterminados
✅ **Usuarios Admin Precargados:**
- Email: `pablobruno321@hotmail.com` | Contraseña: `admin123`
- Email: `pablo.geba.river@gmail.com` | Contraseña: `admin123`
- Se crean automáticamente en la inicialización de la BD

### 3. Panel de Administración de Usuarios
✅ **Archivos Nuevos:**
- `erp_app/templates/admin/usuarios.html` - Listado de usuarios con opciones de editar/eliminar
- `erp_app/templates/admin/usuario_form.html` - Formulario para crear/editar usuarios
- `erp_app/templates/admin/usuario_creado.html` - Confirmación de usuario creado con contraseña temporal

✅ **Rutas Implementadas (Solo Admin):**
- GET/POST `/admin/usuarios` - Listar y crear usuarios
- GET/POST `/admin/usuarios/<id>/editar` - Editar usuario
- POST `/admin/usuarios/<id>/eliminar` - Eliminar usuario
- POST `/admin/usuarios/<id>/resetear-password` - Generar nueva contraseña temporal

✅ **Características:**
- Gestión de roles (usuario/admin)
- Activación/desactivación de usuarios
- Generación de contraseñas temporales
- Reseteo de contraseñas

### 4. Funcionalidad de Edición y Eliminación
✅ **Módulos Afectados:**
- **Clientes:** Editar ✅ | Eliminar ✅
- **Proveedores:** Editar ✅ (nueva ruta) | Eliminar ✅
- **Productos:** Editar ✅ (nueva ruta) | Eliminar ✅
- **Pedidos:** Editar ✅ (nueva ruta) | Eliminar ✅ (con cascada de items)

✅ **Cambios en Plantillas:**
- `erp_app/templates/clientes/lista.html` - Botón eliminar
- `erp_app/templates/proveedores/lista.html` - Botones editar/eliminar
- `erp_app/templates/productos/lista.html` - Botones editar/eliminar
- `erp_app/templates/pedidos/lista.html` - Botones editar/eliminar

✅ **Confirmación de Eliminación:**
- Diálogos de confirmación con AJAX
- Recarga de página automática tras eliminar

### 5. Auto-Backup a Carpeta WEBAPPS
✅ **Archivo:** `erp_app/backup_excel.py` (Existente)
- Genera backups en: `WEBAPPS/1-Conectar23/backup_TIMESTAMP.xlsx`
- Incluye 4 hojas: Clientes, Proveedores, Productos, Pedidos
- Formato profesional con headers, bordes y ancho automático

✅ **Integración Automática:**
- Backup al crear nuevo cliente
- Backup al crear nuevo pedido
- Se puede extender a otros módulos

### 6. Actualización de Navegación
✅ **Archivo:** `erp_app/templates/base.html`
- Nueva sección "ADMINISTRACIÓN" en el sidebar (solo visible para admin)
- Link a panel de usuarios: `/admin/usuarios`

## Credenciales de Acceso

### Administradores Precargados:
```
Email: pablobruno321@hotmail.com
Contraseña: admin123
Rol: Administrador

Email: pablo.geba.river@gmail.com
Contraseña: admin123
Rol: Administrador
```

## Próximos Pasos para Pruebas

1. **Iniciar la aplicación:**
   ```bash
   cd "c:\Users\Pablo\Desktop\Visual\Proyecto 2"
   python run.py
   ```

2. **Acceder en navegador:**
   ```
   http://localhost:5000
   ```

3. **Login con admin:**
   - Email: `pablobruno321@hotmail.com`
   - Contraseña: `admin123`

4. **Funcionalidades a las que puedes acceder:**
   - Dashboard con gráficos interactivos
   - Panel de Administración → Gestión de Usuarios
   - Editar/Eliminar en todas las secciones (Clientes, Proveedores, Productos, Pedidos)
   - Backups automáticos en `WEBAPPS/1-Conectar23`

## Notas Técnicas

- Los gráficos se actualizan dinámicamente según los datos en la BD
- El backup se crea automáticamente JSON con timestamp
- Las eliminaciones son en cascada (ej: eliminar pedido borra sus items)
- Las contraseñas temporales se generan con `secrets.token_urlsafe(10)`
- Todas las rutas admin están protegidas con decorador `@admin_requerido`
