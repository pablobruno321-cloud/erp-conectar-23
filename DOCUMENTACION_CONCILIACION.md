# Documentación de Conciliación de Pagos y Cobranzas

## Resumen de Cambios

Se han implementado mejoras significativas en el sistema de pagos y cobranzas para incluir columnas de conciliación que permiten relacionar estos movimientos con pedidos específicos.

## Cambios Realizados

### 1. Modelo de Datos (erp_app/models.py)

**Cobranza:**
- `pedido_id`: Relación con el pedido al que se concilia la cobranza
- `numero_comprobante`: Número del comprobante de cobro
- `tipo_comprobante`: Tipo de comprobante (Factura, Recibo, Nota de Crédito, Otro)

**Pago:**
- `pedido_id`: Relación con el pedido al que se concilia el pago
- `numero_comprobante`: Número del comprobante de pago
- `tipo_comprobante`: Tipo de comprobante (Factura, Recibo, Nota de Crédito, Otro)

### 2. Formularios Web

**Cobranzas (erp_app/templates/cobranzas/formulario.html):**
- Se eliminó la referencia a la variable `pedidos` que no estaba definida
- El formulario ahora funciona correctamente

**Pagos (erp_app/templates/pagos/formulario.html):**
- Se agregaron campos para `pedido_id`, `numero_comprobante` y `tipo_comprobante`
- Se incluye un selector para relacionar el pago con un pedido específico

### 3. Rutas y Controladores (erp_app/app.py)

**Nuevas rutas:**
- `/conciliacion`: Vista general de conciliación
- `/conciliar/cobranza/<id>`: Conciliar una cobranza específica
- `/conciliar/pago/<id>`: Conciliar un pago específico

**Funcionalidades:**
- Listado de cobranzas y pagos sin conciliar
- Resumen de saldos (CxC y CxP)
- Selección de pedidos para conciliación

### 4. Plantillas HTML

**Nuevas plantillas:**
- `conciliacion.html`: Vista principal de conciliación
- `conciliacion_cobranza.html`: Formulario para conciliar cobranzas
- `conciliacion_pago.html`: Formulario para conciliar pagos

### 5. Carga de Datos (cargar_cobranzas_pagos.py)

**Mejoras:**
- Se agregó soporte para las nuevas columnas de conciliación
- Se incluyen campos para `referencia`, `numero_comprobante` y `tipo_comprobante`
- Mejor manejo de errores y validación de datos

## Uso del Sistema de Conciliación

### 1. Registrar Cobranzas y Pagos

Al registrar una cobranza o pago, ahora se pueden incluir:
- **Número de comprobante**: Para identificar el documento
- **Tipo de comprobante**: Para clasificar el tipo de documento
- **Pedido relacionado**: Para conciliar directamente con un pedido

### 2. Conciliación Manual

Si una cobranza o pago no se concilió al momento de su registro:

1. Ir a **Conciliación** en el menú
2. Seleccionar la cobranza o pago sin conciliar
3. Elegir el pedido correspondiente
4. Confirmar la conciliación

### 3. Beneficios de la Conciliación

- **Seguimiento preciso**: Saber exactamente qué pedidos están pagados/cobrados
- **Control de deudas**: Visualizar saldos pendientes por cliente/proveedor
- **Auditoría**: Relacionar cada movimiento con su documento correspondiente
- **Reportes**: Generar reportes más detallados y precisos

## Comandos Útiles

### Probar la funcionalidad
```bash
python test_conciliacion.py
```

### Cargar datos con conciliación
```bash
python cargar_cobranzas_pagos.py
```

### Iniciar la aplicación
```bash
python erp_app/app.py
```

## Notas Técnicas

### Base de Datos
Los cambios en el modelo de datos requieren que la base de datos tenga las nuevas columnas. Si se utiliza una base de datos existente, se deben agregar las columnas manualmente o recrear la base de datos.

### Relaciones
- `Cobranza.pedido_id` → `Pedido.id`
- `Pago.pedido_id` → `Pedido.id`

### Validaciones
- Las conciliaciones son opcionales al registrar cobranzas/pagos
- Se pueden conciliar múltiples cobranzas/pagos con el mismo pedido
- No se valida que el monto conciliado coincida exactamente con el monto del pedido (para permitir pagos parciales)

## Próximos Pasos Sugeridos

1. **Validación de montos**: Implementar validación para evitar conciliar más del monto del pedido
2. **Pagos parciales**: Mejorar el manejo de pagos/cobranzas parciales
3. **Reportes avanzados**: Crear reportes específicos para conciliación
4. **Exportación**: Permitir exportar reportes de conciliación a Excel
5. **Notificaciones**: Alertar cuando hay movimientos sin conciliar por más de X días