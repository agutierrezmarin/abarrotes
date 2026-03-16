# Guía: Ajustar Stock vs Agregar Lote

## ¿Cuál es la diferencia?

El sistema tiene dos formas de modificar el inventario de un producto. Elegir la correcta es importante para mantener un historial limpio y que las alertas de vencimiento funcionen bien.

| | Ajustar Stock | Agregar Lote |
|---|---|---|
| **¿Qué hace?** | Modifica directamente el número de unidades | Registra una entrada de mercancía con fecha de caducidad |
| **¿Registra fecha de vencimiento?** | No | Sí |
| **¿Genera movimiento en el historial?** | Sí | Sí (automáticamente) |
| **¿Cuándo usarlo?** | Correcciones, pérdidas, merma | Compras nuevas al proveedor |

---

## Agregar Lote

**Ruta:** Detalle del producto → botón *Agregar Lote*

### Cuándo usarlo

Usa **Agregar Lote** siempre que recibas mercancía del proveedor. Es la forma principal de ingresar stock.

- Llegó un pedido nuevo de refrescos, galletas, lácteos, etc.
- Recibiste una caja de productos con fecha de vencimiento impresa
- Compraste mercancía y necesitas registrar cuándo vence para que el sistema te avise

### Qué información registra

- **Número de lote** — el código impreso en el empaque (ej. `L2026-045`). Déjalo vacío si no tiene.
- **Cantidad** — cuántas unidades entran. Si el producto es fraccionado (compra por caja), puedes marcar "ingresar en paquetes" y el sistema calcula las unidades automáticamente.
- **Fecha de vencimiento** — el sistema usará esta fecha para mostrarte alertas cuando el producto esté por vencer o ya vencido.
- **Fecha de entrada** — cuándo llegó la mercancía (por defecto hoy).
- **Precio de compra** — costo del lote en esa compra.

### Ejemplo práctico

> Compraste 3 cajas de leche (24 unidades por caja = 72 unidades) que vencen el 15 de abril.
>
> 1. Entra al detalle de *Leche entera 1L*
> 2. Clic en **Agregar Lote**
> 3. Marca "Ingresar en paquetes", escribe `3` cajas
> 4. Escribe la fecha de vencimiento: `2026-04-15`
> 5. Guarda — el stock sube 72 unidades y el sistema empezará a alertar 7 días antes del vencimiento

---

## Ajustar Stock

**Ruta:** Detalle del producto → botón *Ajustar Stock*

### Cuándo usarlo

Usa **Ajustar Stock** para situaciones que no son una compra normal al proveedor: correcciones, pérdidas, conteos físicos o salidas manuales.

### Tipos de ajuste disponibles

#### Entrada de mercancía
Stock aumenta en la cantidad indicada.

- Usarlo **solo** cuando no hay fecha de vencimiento que registrar (productos sin caducidad como bolsas, detergentes genéricos, etc.)
- Si el producto tiene fecha de vencimiento, es mejor usar **Agregar Lote** en su lugar

#### Salida de mercancía
Stock disminuye en la cantidad indicada.

- Producto dañado o roto que hay que retirar del inventario
- Muestra o degustación entregada sin venta
- Robo o extravío detectado
- Merma por manipulación

#### Ajuste de inventario (valor absoluto)
El stock queda exactamente en el número que escribas, sin importar lo que había antes.

- Después de hacer un **conteo físico** del inventario y hay diferencia con lo que dice el sistema
- Corrección de un error de registro anterior
- Primera vez que se carga el stock de un producto ya existente

### Ejemplo práctico

> Al hacer el conteo físico de fin de mes, el sistema dice que hay 48 unidades de arroz, pero en el almacén solo hay 43.
>
> 1. Entra al detalle de *Arroz 1kg*
> 2. Clic en **Ajustar Stock**
> 3. Tipo: *Ajuste de inventario*
> 4. Cantidad: `43`
> 5. Motivo: `Conteo físico mensual - marzo 2026`
> 6. Guarda — el stock queda en 43 y queda registrado en el historial

---

## Resumen rápido para decidir

```
¿Llegó mercancía del proveedor?
  └─ Sí → AGREGAR LOTE
       ├─ ¿Tiene fecha de vencimiento? → Registrarla en el lote
       └─ ¿No tiene fecha de vencimiento? → Dejar vacío el campo

¿Es una corrección o pérdida?
  └─ Sí → AJUSTAR STOCK
       ├─ ¿Conteo físico diferente al sistema? → Tipo: Ajuste (valor absoluto)
       ├─ ¿Producto dañado / robo / merma? → Tipo: Salida
       └─ ¿Entrada sin fecha de vencimiento? → Tipo: Entrada
```

---

## Buenas prácticas

1. **Siempre escribe un motivo claro** al ajustar stock. El historial de movimientos ayuda a detectar problemas recurrentes (mucha merma, diferencias frecuentes en conteo, etc.).

2. **Registra la fecha de vencimiento siempre que puedas**. Es la base del sistema de alertas. Sin ella, el sistema no puede avisarte cuando un producto está por vencer.

3. **No uses "Ajustar Stock - Entrada" como sustituto de "Agregar Lote"** si el producto tiene fecha de caducidad. Perderás el control de vencimientos.

4. **Haz conteos físicos periódicos** (semanal o mensual) y usa *Ajuste de inventario* para mantener el sistema sincronizado con la realidad del almacén.

5. **El número de lote es opcional**, pero si el proveedor lo incluye en el empaque, regístralo. Facilita identificar qué unidades retirar si hay un problema de calidad.
