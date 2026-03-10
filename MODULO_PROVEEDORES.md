# Módulo de Proveedores — Guía de Uso y Casos Prácticos

> Documentación del módulo de gestión de proveedores del sistema de inventario.

---

## Tabla de contenido

1. [¿Qué es un proveedor en este sistema?](#1-qué-es-un-proveedor-en-este-sistema)
2. [Acceso y permisos](#2-acceso-y-permisos)
3. [Campos del formulario](#3-campos-del-formulario)
4. [Vistas disponibles](#4-vistas-disponibles)
5. [Casos de uso comunes](#5-casos-de-uso-comunes)
6. [Relación con productos](#6-relación-con-productos)
7. [Condiciones de pago](#7-condiciones-de-pago)
8. [Buenas prácticas](#8-buenas-prácticas)

---

## 1. ¿Qué es un proveedor en este sistema?

Un **proveedor** es la empresa o persona que suministra los productos a la tienda. El módulo permite:

- Registrar los datos de contacto completos de cada proveedor
- Asociar productos al proveedor que los suministra
- Consultar qué productos viene de cada proveedor y su estado de stock
- Llevar control de las condiciones de pago (contado, crédito 15 días, etc.)
- Activar o desactivar proveedores sin eliminar el historial

**URL del módulo:** `/inventario/proveedores/`

---

## 2. Acceso y permisos

| Acción | Vendedor | Administrador | Gerente | Superusuario |
|---|:---:|:---:|:---:|:---:|
| Ver lista de proveedores | ✗ | ✅ | ✅ | ✅ |
| Ver detalle de proveedor | ✗ | ✅ | ✅ | ✅ |
| Crear proveedor | ✗ | ✅ | ✅ | ✅ |
| Editar proveedor | ✗ | ✅ | ✅ | ✅ |
| Activar / desactivar | ✗ | ✅ | ✅ | ✅ |

> El módulo de Proveedores es exclusivo del área de Inventario. Los vendedores no tienen acceso.

---

## 3. Campos del formulario

### Sección: Datos del Proveedor

| Campo | Tipo | Requerido | Descripción |
|---|---|:---:|---|
| **Nombre** | Texto (200 car.) | Sí | Nombre comercial de la empresa o persona |
| **NIT / RUC** | Texto (30 car.) | No | Número de identificación tributaria |
| **Nombre del contacto** | Texto (100 car.) | No | Persona de referencia para pedidos o pagos |
| **Teléfono fijo** | Texto (20 car.) | No | Número de teléfono convencional |
| **Celular / WhatsApp** | Texto (20 car.) | No | Número móvil para contacto rápido |
| **Correo electrónico** | Email | No | Correo de contacto o pedidos |
| **Sitio web** | URL | No | Página web del proveedor (incluir https://) |
| **Dirección** | Texto (250 car.) | No | Dirección física del proveedor |
| **Ciudad** | Texto (100 car.) | No | Ciudad donde opera el proveedor |

### Sección: Condiciones Comerciales

| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| **Condición de pago** | Selección | Contado | Plazo de pago acordado |
| **Proveedor activo** | Checkbox | ✅ Activo | Si está desactivado no afecta los productos asociados |
| **Notas internas** | Texto largo | — | Observaciones privadas: descuentos, horarios, acuerdos |

---

## 4. Vistas disponibles

### Lista de proveedores — `/inventario/proveedores/`

- Muestra todos los proveedores activos por defecto
- Filtro para mostrar también inactivos
- Búsqueda por nombre, contacto o ciudad
- Estadísticas: total de proveedores y cuántos están activos
- Columna con conteo de productos activos por proveedor

### Detalle de proveedor — `/inventario/proveedores/<id>/`

- Datos completos de contacto en la columna izquierda
- Lista de **todos los productos activos** asociados en la columna derecha
- Indicador visual de stock bajo por producto
- Botones de acción: Editar y Activar/Desactivar

### Formulario — `/inventario/proveedores/nuevo/` y `/inventario/proveedores/<id>/editar/`

- Formulario en dos secciones: Datos del Proveedor y Condiciones Comerciales
- Textos de ayuda en campos que lo requieren

### Toggle activo — `/inventario/proveedores/<id>/toggle/`

- Cambia el estado activo/inactivo del proveedor en un clic
- **No elimina** el proveedor ni sus productos asociados

---

## 5. Casos de uso comunes

---

### Caso 1 — Distribuidora de bebidas (proveedor mayorista)

**Situación:** La tienda compra cervezas, refrescos y aguas a una distribuidora grande que da crédito a 30 días.

**Datos a registrar:**

| Campo | Valor |
|---|---|
| Nombre | `Distribuidora El Gato S.R.L.` |
| NIT | `1234567` |
| Contacto | `Carlos Mamani` |
| Celular | `+591 72345678` |
| Email | `pedidos@elgato.com` |
| Ciudad | `La Paz` |
| Condición de pago | `Crédito 30 días` |
| Notas | `Entrega los martes y viernes. Descuento del 5% en pedidos mayores a Bs. 1000.` |

**Productos asociados:** Cerveza Paceña, Coca-Cola 2L, Agua Potosí 600ml

---

### Caso 2 — Panadería local (proveedor de perecederos)

**Situación:** Una panadería del barrio entrega pan fresco todos los días. Pago de contado al recibir.

| Campo | Valor |
|---|---|
| Nombre | `Panadería Don Aurelio` |
| Contacto | `Aurelio Quispe` |
| Celular | `+591 71234567` |
| Dirección | `Calle Murillo 234, Villa Fatima` |
| Ciudad | `La Paz` |
| Condición de pago | `Contado` |
| Notas | `Entrega entre 6:00 y 7:00 am. Llama con un día de anticipación para pedidos grandes.` |

---

### Caso 3 — Proveedor de abarrotes secos (mercado)

**Situación:** Un vendedor del mercado que surte frijol, arroz y azúcar a granel.

| Campo | Valor |
|---|---|
| Nombre | `Sra. Rosario Condori` |
| Contacto | `Rosario Condori` |
| Celular | `+591 70000000` |
| Dirección | `Puesto 45, Mercado Rodríguez` |
| Ciudad | `La Paz` |
| Condición de pago | `Contado` |
| Notas | `Trabaja lunes a sábado. El frijol negro es de cosecha propia de Caranavi.` |

---

### Caso 4 — Empresa distribuidora de cigarros y golosinas

**Situación:** Distribuidor con representante que pasa cada semana. Da crédito a 15 días.

| Campo | Valor |
|---|---|
| Nombre | `Distribuidora Nacional Ltda.` |
| NIT | `9876543` |
| Contacto | `Luis Flores (rep. de ventas)` |
| Teléfono | `(02) 2456789` |
| Celular | `+591 79876543` |
| Email | `ventas@disnacional.bo` |
| Sitio web | `https://www.disnacional.bo` |
| Ciudad | `La Paz` |
| Condición de pago | `Crédito 15 días` |
| Notas | `El representante pasa los miércoles. Mínimo de pedido: Bs. 500.` |

---

### Caso 5 — Desactivar un proveedor sin perder historial

**Situación:** Un proveedor dejó de operar o ya no trabajas con él, pero no quieres eliminar sus datos porque los productos registrados lo tienen como referencia.

**Pasos:**
1. Ir a `/inventario/proveedores/<id>/`
2. Hacer clic en **"Desactivar"**
3. El proveedor desaparece de la lista principal (filtro "Solo activos")
4. Sus productos **mantienen** la referencia al proveedor
5. Para reactivar: ir de nuevo al detalle y hacer clic en **"Activar"**

> ✅ No uses "eliminar" si el proveedor tiene productos asociados. Solo desactívalo.

---

### Caso 6 — Buscar proveedores por ciudad

**Situación:** Necesitas contactar a todos los proveedores de Cochabamba porque hay una feria.

1. Ir a `/inventario/proveedores/`
2. En el cuadro de búsqueda, escribe `Cochabamba`
3. La búsqueda filtra por nombre, contacto y ciudad simultáneamente

---

### Caso 7 — Actualizar condición de pago después de negociar

**Situación:** Un proveedor que antes vendía de contado ahora te da 15 días de crédito.

1. Ir al detalle del proveedor
2. Clic en **Editar**
3. Cambiar **Condición de pago** de `Contado` a `Crédito 15 días`
4. Agregar en **Notas**: `"A partir de marzo 2026, crédito aprobado por Bs. 5000 máximos."`
5. Guardar

---

## 6. Relación con productos

Al registrar o editar un **Producto**, hay un campo `Proveedor` que lo vincula al módulo:

- Desde el detalle del proveedor puedes ver todos sus productos de un vistazo
- El listado muestra: nombre, stock actual, precio de compra y precio de venta
- Productos con **stock bajo** se marcan con fondo amarillo y un ícono de advertencia
- Desde ahí puedes ir directamente al detalle del producto o agregar un lote

**Ejemplo de vista en detalle de proveedor:**

```
Distribuidora El Gato
  ├── Cerveza Paceña 620ml     Stock: 96 uds   ✅
  ├── Coca-Cola 2L             Stock:  4 uds   ⚠️ (stock bajo)
  └── Agua Potosí 600ml        Stock: 144 uds  ✅
```

---

## 7. Condiciones de pago

| Opción | Significado | Cuándo usarla |
|---|---|---|
| **Contado** | Pagas al recibir la mercancía | Vendedores informales, mercados |
| **Crédito 7 días** | Tienes 7 días para pagar | Proveedores pequeños con poco crédito |
| **Crédito 15 días** | Tienes 15 días para pagar | Distribuidoras locales |
| **Crédito 30 días** | Tienes 30 días para pagar | Distribuidoras grandes o empresas |
| **Crédito 60 días** | Tienes 60 días para pagar | Acuerdos especiales con empresas grandes |

> ⚠️ **Nota:** El sistema registra la condición como referencia informativa. No gestiona automáticamente fechas de vencimiento de pago ni alertas de deuda pendiente (esa sería una funcionalidad de cuentas por pagar).

---

## 8. Buenas prácticas

### ✅ Sí hacer

- **Registrar el celular o WhatsApp** del contacto: es el canal más rápido para hacer pedidos de urgencia
- **Usar el campo Notas** para guardar acuerdos verbales: descuentos por volumen, días de entrega, productos con mejor precio
- **Verificar el NIT** si el proveedor emite facturas: necesario para la contabilidad
- **Agregar el sitio web** en distribuidoras grandes: facilita consultar catálogo y precios en línea
- **Revisar el stock de productos** desde el detalle del proveedor antes de hacer un pedido

### ❌ No hacer

- No elimines un proveedor si tiene productos asociados. Solo **desactívalo**
- No uses el campo Nombre para poner notas (`"Distribuidora - no funciona bien"`). Usa el campo Notas
- No dejes el nombre en mayúsculas sin consistencia. Usa nombre comercial real
- No registres al mismo proveedor dos veces con nombres ligeramente distintos (`"Dist. El Gato"` vs `"Distribuidora El Gato"`)

---

## URLs de referencia rápida

| Acción | URL |
|---|---|
| Lista de proveedores | `/inventario/proveedores/` |
| Nuevo proveedor | `/inventario/proveedores/nuevo/` |
| Detalle | `/inventario/proveedores/<id>/` |
| Editar | `/inventario/proveedores/<id>/editar/` |
| Activar/Desactivar | `/inventario/proveedores/<id>/toggle/` |

---

*Última actualización: 2026-03-10*
