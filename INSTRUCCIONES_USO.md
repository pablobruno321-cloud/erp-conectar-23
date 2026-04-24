## 🚀 ERP - Sistema de Gestión Empresarial

Tu aplicación ERP está **LISTA Y FUNCIONANDO** en:
```
http://localhost:5000
```

---

## 📋 GUÍA DE USO INMEDIATA

### 1. Acceso a la Aplicación
Abre tu navegador y ve a: **http://localhost:5000**

### 2. Credenciales de Administrador
**Opción 1:**
- **Email:** `pablobruno321@hotmail.com`
- **Contraseña:** `admin123`

**Opción 2:**
- **Email:** `pablo.geba.river@gmail.com`
- **Contraseña:** `admin123`

Ambas cuentas tienen rol de **ADMINISTRADOR**.

---

## 🎯 NUEVAS FUNCIONALIDADES IMPLEMENTADAS

### 1. 📊 Dashboard con Gráficos Interactivos
- **Línea:** Ventas por Mes (últimos 12 meses)
- **Barras:** Ganancia por Mes
- **Doughnut:** Top 5 Clientes por Venta
- **Barras Horizontal:** Top 5 Productos más Vendidos

*Los gráficos se actualizan automáticamente con los datos de tu BD*

### 2. 👥 Panel de Administración de Usuarios
**Acceso:** Sidebar → ADMINISTRACIÓN → Usuarios (solo visible para admin)

**Funciones:**
- ✅ Ver lista de todos los usuarios registrados
- ✅ Crear nuevos usuarios con rol específico
- ✅ Editar nombre, rol y estado de usuarios
- ✅ Eliminar usuarios
- ✅ Resetear contraseña (genera nueva contraseña temporal)

**Crear nuevo usuario:**
1. Click en "+ Nuevo Usuario"
2. Completa: Nombre, Email, Rol
3. El sistema genera contraseña temporal automáticamente
4. Muestra la contraseña para que el usuario la copie

### 3. ✏️ Edición en Todos los Módulos
Todos los módulos ahora tienen botón "Editar":
- **Clientes:** Editar información (nombre, CUIT, teléfono, email, dirección)
- **Proveedores:** Editar información
- **Productos:** Editar información
- **Pedidos:** Editar cliente, fecha y items del pedido

### 4. 🗑️ Eliminación Controlada
Todos los módulos ahora tienen botón "Eliminar":
- Se pide confirmación antes de eliminar
- Las eliminaciones en cascada funcionan (si eliminas pedido, se borran sus items)

**Confirmación segura:**
```
¿Está seguro de que desea eliminar a "Nombre"?
[Cancelar] [OK]
```

### 5. 💾 Auto-Backup Automático
Los backups se generan automáticamente en:
```
C:\Users\Pablo\Desktop\Visual\Proyecto 2\WEBAPPS\1-Conectar23\backup_TIMESTAMP.xlsx
```

**Se crea un backup cuando:**
- Creas un nuevo cliente
- Creas un nuevo pedido

**Contenido del backup:**
- Hoja 1: Clientes
- Hoja 2: Proveedores
- Hoja 3: Productos
- Hoja 4: Pedidos

*Cada hoja está formateada con headers azules, bordes y ancho automático*

---

## 🎨 GUÍA VISUAL DE LA APLICACIÓN

```
┌─────────────────────────────────────────┐
│  SIDEBAR (Izquierda)                   │
├─────────────────────────────────────────┤
│ ERP                                     │
│                                         │
│ Inicio                                  │
│                                         │
│ MAESTROS                                │
│ • Clientes        ← Editar/Eliminar    │
│ • Proveedores     ← Editar/Eliminar    │
│ • Productos       ← Editar/Eliminar    │
│                                         │
│ TRANSACCIONES                           │
│ • Pedidos         ← Editar/Eliminar    │
│ • Cobranzas                             │
│ • Pagos                                 │
│                                         │
│ REPORTES                                │
│ • Ventas                                │
│ • Saldos                                │
│                                         │
│ ADMINISTRACIÓN  (Solo Admin)           │
│ • Usuarios  ← Crear/Editar/Eliminar   │
│             ← Resetear Password        │
└─────────────────────────────────────────┘
```

---

## 📝 PASOS PARA COMENZAR A USAR

### Paso 1: Login
1. Ve a http://localhost:5000
2. Usa credenciales de admin
3. Click "Iniciar Sesión"

### Paso 2: Explora el Dashboard
- Verás gráficos con datos actuales (algunos vacíos si no hay datos aún)
- Click en "Inicio" para volver al dashboard desde cualquier página

### Paso 3: Agrega Datos
- Haz click en "+ Nuevo Cliente"
- Haz click en "+ Nuevo Producto"
- Haz click en "+ Nuevo Pedido"
- **Los datos se guardarán automáticamente y se crearán backups**

### Paso 4: Edita y Elimina
- En cualquier lista (Clientes, Proveedores, etc.) verás:
  - Botón "Editar" → Modifica el registro
  - Botón "Eliminar" → Borra el registro (con confirmación)

### Paso 5: Gestiona Usuarios (Admin Only)
- Click en "ADMINISTRACIÓN" → "Usuarios"
- "+ Nuevo Usuario" para crear nuevas cuentas
- Click "Editar" para cambiar rol o estado
- Click "Resetear Password" para generar nueva contraseña

---

## 🔑 CARACTERÍSTICAS DE SEGURIDAD

✅ **Autenticación:** Login con email y contraseña (hashadas con Werkzeug)
✅ **Roles:** Sistema de roles (usuario/admin)
✅ **Protección:** Solo admins ven panel de administración
✅ **Control de Acceso:** Todas las rutas requieren login
✅ **Contraseñas Temporales:** Generadas con `secrets.token_urlsafe(10)`

---

## 📊 ESTRUCTURA DE DATOS

**La aplicación usa SQLite con 8 tablas principales:**

1. **Usuario** - Cuentas de usuario (email, role, password)
2. **Cliente** - Clientes de la empresa
3. **Proveedor** - Proveedores de productos
4. **Producto** - Catálogo de productos
5. **Pedido** - Órdenes de compra/venta
6. **ItemPedido** - Items dentro de cada pedido
7. **Pago** - Pagos realizados
8. **Cobranza** - Cobranzas recibidas
9. **ProveedorLogistico** - Proveedores de logística

Base de datos: `erp_app/erp.db`

---

## 🛠️ COMMANDS ÚTILES

**Ver estado del servidor:**
- Verás logs en la consola PowerShell

**Detener el servidor:**
- Presiona `Ctrl+C` en la terminal donde está corriendo

**Reiniciar:**
- Cierra la aplicación (Ctrl+C)
- Ejecuta nuevamente: `python run.py`

**Acceso a BD directamente:**
- Usa DB Browser para SQLite si necesitas ver datos
- Archivo: `c:\Users\Pablo\Desktop\Visual\Proyecto 2\erp_app\erp.db`

---

## 💡 TIPS

1. **Los gráficos necesitan datos:** Crea algunos clientes y pedidos para ver los gráficos poblarse
2. **Backups son automáticos:** No necesitas hacer nada, se crean al agregar datos
3. **Contraseñas temporales:** Cópialas de la pantalla de confirmación
4. **Confirmaciones:** Siempre pide confirmación antes de eliminar

---

## ⚠️ SOLUCIÓN DE PROBLEMAS

**Si la aplicación no inicia:**
1. Verifica que Python 3.9+ esté instalado
2. Verifica que estés en la carpeta "Proyecto 2"
3. Asegúrate que el puerto 5000 no esté en uso

**Si hay error en gráficos:**
- Los gráficos necesitan datos en la BD
- Agregue un cliente y un pedido primero

**Si no ves cambios:**
- Refresca la página (F5 o Ctrl+R)
- Limpia caché (Ctrl+Shift+Delete)

---

## 🎉 ¡LISTO PARA USAR!

Tu ERP está configurado con:
- ✅ 2 cuentas admin precargadas
- ✅ Dashboard con gráficos interactivos
- ✅ Panel de gestión de usuarios
- ✅ Edición/Eliminación en todos los módulos
- ✅ Auto-backup automático
- ✅ Sistema de autenticación seguro

**¡Accede a http://localhost:5000 ahora mismo!**

---

*Para cualquier cambio o mejora, solo avísame.*
