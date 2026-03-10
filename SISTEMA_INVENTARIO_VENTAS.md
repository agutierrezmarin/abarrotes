# Sistema de Inventario y Ventas — Tienda de Abarrotes

> Documentación funcional: casos de uso, flujos y reglas de negocio.

---

## Tabla de contenido

1. [Descripción general](#1-descripción-general)
2. [Tecnología](#2-tecnología)
3. [Roles de usuario](#3-roles-de-usuario)
4. [Módulo de Usuarios y Perfiles](#4-módulo-de-usuarios-y-perfiles)
5. [Módulo de Inventario](#5-módulo-de-inventario)
6. [Módulo de Ventas](#6-módulo-de-ventas)
7. [Módulo de Reportes](#7-módulo-de-reportes)
8. [Reglas de negocio clave](#8-reglas-de-negocio-clave)
9. [Flujos principales](#9-flujos-principales)

---

## 1. Descripción general

Sistema web para la gestión de una tienda de abarrotes. Permite administrar el inventario de productos (incluyendo lotes con fecha de vencimiento), registrar ventas en el punto de caja, controlar usuarios con distintos niveles de acceso y consultar reportes de desempeño.

El sistema está diseñado para operar desde cualquier dispositivo (PC de escritorio, tablet o celular) gracias a su interfaz responsiva.

---

## 2. Tecnología

| Componente | Detalle |
|---|---|
| Backend | Django 6.0.3 / Python 3.13 |
| Base de datos | SQLite (desarrollo) |
| Frontend | Bootstrap 5.3 + Font Awesome |
| Autenticación | Sistema nativo de Django (`django.contrib.auth`) |
| Media (imágenes) | Almacenamiento local (`MEDIA_ROOT`) |

**Estructura de aplicaciones Django:**

```
abarrotes/          ← configuración del proyecto
inventario/         ← productos, lotes, movimientos
ventas/             ← punto de venta, tickets, items
reportes/           ← dashboards por rol
usuarios/           ← gestión de cuentas y perfiles
```

---

## 3. Roles de usuario

El sistema usa los **grupos de Django** para definir permisos:

| Rol | Acceso |
|---|---|
| **Superusuario** | Acceso total, incluyendo Django Admin |
| **Administrador** | Inventario, ventas, reportes generales, gestión de usuarios |
| **Gerente** | Inventario (solo lectura), ventas, reportes gerenciales y de administrador |
| **Vendedor** | Solo punto de venta, historial propio y reporte de sus ventas |

> Los menús del sidebar se muestran u ocultan automáticamente según el rol del usuario autenticado.

---

## 4. Módulo de Usuarios y Perfiles

### 4.1 Gestión de cuentas (solo Administrador / Superusuario)

**CU-U01 — Crear usuario**

1. El administrador accede a **Administración → Gestión de Usuarios**.
2. Hace clic en **Nuevo Usuario**.
3. Completa: nombre de usuario, contraseña, nombre completo, correo, rol (grupo) y estado activo/inactivo.
4. Al guardar, el sistema crea automáticamente un **Perfil** vacío asociado al nuevo usuario (via señal `post_save`).

**CU-U02 — Editar cuenta de otro usuario**

- El administrador puede cambiar: datos básicos, grupo (rol) y estado de la cuenta.

**CU-U03 — Activar / desactivar usuario**

- Un botón de alternancia en la lista permite activar o desactivar una cuenta sin eliminarla.
- Un usuario no puede desactivarse a sí mismo.

**CU-U04 — Ver perfil de otro usuario**

- El administrador puede consultar el perfil completo de cualquier usuario desde la lista.

---

### 4.2 Perfil personal (todos los usuarios)

**CU-U05 — Ver mi perfil**

- Accesible desde el menú **Cuenta → Mi Perfil** o desde el dropdown de usuario en el topbar.
- Muestra: foto, nombre, correo, rol, estado, datos de contacto, número de empleado, fecha de ingreso, edad y antigüedad calculadas automáticamente.

**CU-U06 — Editar mi perfil**

- El usuario puede actualizar: nombre, apellido, correo, fotografía, teléfono, dirección, fecha de nacimiento, número de empleado, fecha de ingreso y una breve biografía.
- La foto se almacena en `media/perfiles/`.

**CU-U07 — Cambiar contraseña**

- El usuario debe ingresar su contraseña actual para confirmar identidad.
- El sistema verifica que la nueva contraseña y su confirmación coincidan.
- Al cambiar exitosamente, la sesión se mantiene activa (no se cierra la sesión).

---

## 5. Módulo de Inventario

### 5.1 Productos

**CU-I01 — Registrar producto**

1. Ir a **Inventario → Productos → Nuevo Producto**.
2. Completar los campos obligatorios: nombre, precio de compra, precio de venta.
3. Campos opcionales: código de barras, categoría, proveedor, unidad de medida, stock inicial, stock mínimo, descripción, imagen, estado activo.
4. Si el producto se compra por paquete/caja y se vende por unidad, configurar la sección **Compra por Caja / Venta por Unidad** (ver §5.3).
5. Un preview en tiempo real muestra el costo por unidad, precio de venta por unidad y precio de venta por paquete.

**CU-I02 — Editar producto**

- Desde la lista de productos → botón de edición.
- Todos los campos son editables incluyendo la configuración de paquete.

**CU-I03 — Consultar lista de productos**

- La lista muestra: nombre, código de barras, categoría, precio de venta, stock actual, estado activo/inactivo.
- Los productos con stock en o por debajo del mínimo se destacan visualmente (alerta).

---

### 5.2 Lotes y entradas de mercancía

Cada entrada de mercancía se registra como un **Lote** para permitir el control de fechas de vencimiento y trazabilidad de precios de compra.

**CU-I04 — Registrar lote (entrada de mercancía)**

1. Desde el detalle de un producto → **Agregar Lote**.
2. Completar: número de lote (opcional), cantidad, fecha de vencimiento (opcional), precio de compra del lote, fecha de entrada, notas.
3. **Modo paquetes:** si el producto tiene configuración de paquete, el formulario ofrece la opción de ingresar la cantidad en cajas/paquetes recibidos. El sistema convierte automáticamente: `cantidad_unidades = num_paquetes × unidades_por_paquete`.
4. Al guardar, el stock del producto se incrementa en `cantidad` (siempre en unidades base).
5. Se genera un `MovimientoInventario` de tipo `entrada` con registro del usuario y stock antes/después.

**CU-I05 — Ver historial de movimientos de un producto**

- Muestra todos los movimientos: entradas de lotes, salidas por venta, ajustes manuales y devoluciones.
- Incluye: fecha, tipo, cantidad, stock anterior, stock nuevo, motivo y usuario responsable.

---

### 5.3 Sistema de compra por paquete / venta por unidad

Permite manejar productos que se compran en presentación mayorista (cajas, paquetes, cartones) pero se venden al detalle (unidades individuales) o también en paquete completo.

**Configuración en el producto:**

| Campo | Descripción |
|---|---|
| `unidades_por_paquete` | Cuántas unidades contiene 1 paquete. `1` = no aplica. |
| `nombre_paquete` | Etiqueta del paquete: "Caja", "Paquete", "Cartón", "Bolsa" |
| `precio_venta_paquete` | Precio al vender el paquete completo (opcional) |

**Ejemplo — Cerveza:**

```
Precio compra:        Bs. 120  (por caja de 24 botellas)
Unidades por paquete: 24
Nombre paquete:       Caja
Precio venta/unidad:  Bs. 7
Precio venta/caja:    Bs. 140

Costo por botella ≈ Bs. 5.00
Margen por botella:   Bs. 2.00 (40%)
Margen por caja:      Bs. 20.00 (16.7%)
```

**El stock siempre se almacena en unidades base.** Los valores de paquetes se calculan dinámicamente:

```python
stock_en_paquetes    = stock_actual // unidades_por_paquete  # 48 botellas → 2 cajas
stock_unidades_sueltas = stock_actual % unidades_por_paquete  # 48 botellas → 0 sueltas
```

---

### 5.4 Alertas de vencimiento

**CU-I06 — Consultar alertas de vencimiento**

- Accesible desde **Inventario → Alertas Vencimiento**.
- Muestra todos los lotes clasificados por estado:

| Estado | Condición |
|---|---|
| **Vencido** | Fecha de vencimiento ya pasó |
| **Crítico** | Vence en ≤ 7 días |
| **Próximo** | Vence en ≤ 30 días |
| **Vigente** | Vence en > 30 días |
| **Sin fecha** | No se registró fecha de vencimiento |

- El reporte del administrador también muestra los lotes próximos a vencer (≤ 30 días).

---

## 6. Módulo de Ventas

### 6.1 Punto de Venta

**CU-V01 — Realizar una venta**

1. El vendedor accede a **Ventas → Punto de Venta**.
2. **Buscar producto:** escribe nombre o código de barras en el buscador. La búsqueda es AJAX (sin recargar página) y devuelve resultados en tiempo real.
3. El resultado muestra el producto con su precio por unidad y, si aplica, precio por paquete.
4. Al seleccionar un producto, aparece un modal para elegir:
   - **Tipo de venta:** por unidad o por paquete (si el producto lo soporta).
   - **Cantidad:** número de unidades o paquetes a vender.
5. El ítem se agrega al ticket con: nombre, tipo (unidad/paquete), precio, cantidad, subtotal y unidades que se descontarán del stock.
6. Se puede agregar descuento por ítem o eliminar ítems del ticket antes de cerrar.
7. Al finalizar, el vendedor selecciona el **método de pago** (efectivo, tarjeta, transferencia, fiado) e ingresa el monto recibido.
8. El sistema verifica stock suficiente para todos los ítems antes de procesar.
9. Se genera el ticket con número único formato `YYYYMMDD-####`.
10. El stock se descuenta automáticamente usando `unidades_descontadas` de cada ítem.

**CU-V02 — Cancelar carrito**

- El botón "Cancelar" limpia el carrito actual sin afectar el inventario.

**CU-V03 — Ver ticket generado**

- Al completar la venta, se muestra el ticket con todos los detalles: ítems, totales, método de pago, cambio y nombre del vendedor.

---

### 6.2 Historial de ventas

**CU-V04 — Consultar historial**

- Accesible desde **Ventas → Historial**.
- Muestra todas las ventas completadas con: número de ticket, fecha, vendedor, total y método de pago.
- El vendedor solo ve sus propias ventas; el administrador ve todas.

**CU-V05 — Ver detalle de venta**

- Al hacer clic en un ticket se despliega el detalle con todos los ítems vendidos, precios, cantidades y si fue venta por paquete o unidad.

---

### 6.3 Control de stock en ventas

Para cada `ItemVenta`, el campo `unidades_descontadas` registra el impacto real en el inventario:

```
Venta de 2 cajas de cerveza (24 unidades/caja):
  es_paquete = True
  cantidad = 2
  unidades_descontadas = 2 × 24 = 48   ← se restan del stock_actual

Venta de 3 botellas sueltas:
  es_paquete = False
  cantidad = 3
  unidades_descontadas = 3              ← se restan del stock_actual
```

Si el stock es insuficiente al momento de completar la venta, el sistema muestra un error y no procesa el cobro.

---

## 7. Módulo de Reportes

### 7.1 Reporte del vendedor (CU-R01)

Accesible para **todos los usuarios**.

Muestra las ventas del usuario en el **día actual**:
- Número de ventas realizadas.
- Total acumulado del día.
- Promedio por venta.
- Lista de cada venta con hora, ticket y monto.

---

### 7.2 Reporte del administrador (CU-R02)

Accesible para **Administrador, Gerente y Superusuario**.

Contiene:
- **Resúmenes de ventas:** hoy, semana actual y mes actual (número de transacciones + total Bs.).
- **Top 10 productos más vendidos del mes:** nombre, unidades vendidas e ingresos generados.
- **Productos con stock bajo:** lista de productos cuyo stock ≤ stock mínimo configurado.
- **Alertas de vencimiento próximas:** lotes que vencen en los siguientes 30 días.

---

### 7.3 Reporte gerencial (CU-R03)

Accesible solo para **Gerente y Superusuario**.

Contiene:
- **Rendimiento por vendedor del mes:** número de ventas, total vendido y promedio por venta.
- **Ventas por día del mes:** tabla con número de transacciones y monto diario (útil para gráficas).
- **Utilidad estimada por producto:** ingresos, costo estimado (cantidad × precio_compra) y utilidad bruta para los 10 productos con más ingresos del mes.

> Nota: la utilidad es estimada porque usa el precio de compra actual del producto, no el precio histórico del lote.

---

## 8. Reglas de negocio clave

### Inventario

- El **stock siempre se gestiona en unidades base** (no en paquetes). Los paquetes son una representación calculada.
- El **stock mínimo** genera una alerta visual en el dashboard y en el reporte del administrador cuando `stock_actual ≤ stock_minimo`.
- Cada entrada de mercancía genera un **MovimientoInventario** de tipo `entrada` con trazabilidad completa.
- Cada venta genera implícitamente una salida de stock (sin crear registro en `MovimientoInventario` separado; el descuento es directo sobre `Producto.stock_actual`).

### Ventas

- Una venta no puede completarse si algún producto no tiene suficiente stock.
- El número de ticket es único y se genera con el formato `YYYYMMDD-####` incrementando el contador diario.
- Los métodos de pago disponibles son: efectivo, tarjeta, transferencia y fiado.
- El cambio se calcula como `max(0, monto_recibido − total)`.
- Los descuentos pueden aplicarse a nivel de ítem individual.

### Usuarios

- Un usuario no puede desactivarse a sí mismo.
- Al crear un usuario, su Perfil se crea automáticamente vacío.
- Un vendedor solo puede ver sus propias ventas e historial.
- Cambiar contraseña no cierra la sesión activa.

---

## 9. Flujos principales

### Flujo A — Entrada de mercancía con paquetes

```
Administrador
  │
  ├─ Inventario → Productos → [Producto] → Agregar Lote
  │
  ├─ Selecciona "Ingresar por cajas recibidas"
  │    Ingresa: 4 cajas, precio compra Bs. 120
  │
  ├─ Sistema calcula: 4 × 24 = 96 unidades
  │
  └─ Guarda lote
       → LoteProducto(cantidad=96, precio_compra=120)
       → Producto.stock_actual += 96
       → MovimientoInventario(tipo='entrada', cantidad=96)
```

---

### Flujo B — Venta por unidad y por paquete (misma sesión)

```
Vendedor
  │
  ├─ Busca "Cerveza" → resultado con precio Bs. 7/botella | Bs. 140/caja
  │
  ├─ Selecciona "Por unidad" → cantidad: 3
  │    ItemVenta(cantidad=3, es_paquete=False, unidades_descontadas=3)
  │
  ├─ Agrega nuevamente "Cerveza" → selecciona "Por caja" → cantidad: 1
  │    ItemVenta(cantidad=1, es_paquete=True, unidades_descontadas=24)
  │
  ├─ Ticket:
  │    Cerveza ×3 (unidad)    Bs. 21.00
  │    Cerveza ×1 [Caja]      Bs. 140.00
  │    ─────────────────────────────────
  │    Total                  Bs. 161.00
  │
  └─ Completar venta (efectivo, recibe Bs. 200)
       → Venta.cambio = Bs. 39.00
       → Producto.stock_actual -= 27  (3 + 24)
```

---

### Flujo C — Alerta de stock bajo

```
Sistema (automático)
  │
  └─ En cada carga del dashboard o reporte admin:
       Consulta: Producto WHERE stock_actual <= stock_minimo AND activo=True
       → Muestra lista de productos en alerta
       → El administrador puede ingresar nuevo lote para reponer stock
```

---

*Documento generado a partir del código fuente del proyecto. Última actualización: 2026-03-09.*
