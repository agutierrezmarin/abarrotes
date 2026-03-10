# Guía de Registro de Productos — Casos de Uso Comunes

> Ejemplos prácticos para registrar diferentes tipos de productos en el sistema de inventario.

---

## Cómo usar esta guía

Cada caso de uso incluye:
- **Qué es** el producto y cómo se compra/vende
- **Qué datos ingresar** en cada campo del formulario
- **Errores comunes** a evitar

---

## Índice de casos

| # | Tipo | Ejemplo |
|---|------|---------|
| 1 | Producto simple (pieza) | Aceite vegetal 1 litro |
| 2 | Bebida fraccionada | Cerveza (caja de 24 botellas) |
| 3 | Snack fraccionado | Chicles (empaque de 12 unidades) |
| 4 | Producto a granel | Frijol negro (por kilogramo) |
| 5 | Producto perecedero | Leche fresca |
| 6 | Higiene y limpieza | Jabón de tocador en barra |
| 7 | Producto multi-presentación | Agua purificada (botella 600ml y garrafón 20L) |
| 8 | Bolsa de frituras (docena) | Sabritas 45g en docena |
| 9 | Producto sin código de barras | Tamales artesanales |
| 10 | Servicio / cobro especial | Cobro de bolsa |

---

## Caso 1 — Aceite Vegetal 1 Litro

**Descripción:** Producto simple con una sola presentación. Se compra y se vende igual, por botella/pieza.

### Paso 1 — Tipo de producto
- Seleccionar: **Producto Simple**

### Paso 2 — Información
| Campo | Valor | Notas |
|---|---|---|
| Nombre | `Aceite Vegetal 1 Litro` | Incluir la medida en el nombre |
| Código de barras | `7501234567890` | Escanear si tienes lector |
| Categoría | `Abarrotes` | |
| Proveedor | `Distribuidora XYZ` | |
| Unidad de medida | `Pieza` | Una botella = una pieza |

### Paso 3 — Precios
| Campo | Valor |
|---|---|
| Precio de compra | `Bs. 18.00` |
| Precio de venta | `Bs. 23.00` |

- **Margen esperado:** ~27.7% ✅

### Paso 4 — Stock
| Campo | Valor |
|---|---|
| Stock inicial | `36` (si llegaron 3 cajas de 12) |
| Stock mínimo | `6` |

> ⚠️ Nota: aunque vengan en cajas del proveedor, si **vendes solo por botella**, este es un producto simple. El campo "stock inicial" se llena en unidades (botellas).

---

## Caso 2 — Cerveza (Caja de 24 Botellas)

**Descripción:** Se compra por caja, pero se puede vender botella individual **o** caja completa. Caso típico de producto fraccionado.

### Paso 1 — Tipo de producto
- Seleccionar: **Compra por Caja / Vende por Unidad**

### Paso 2 — Información
| Campo | Valor |
|---|---|
| Nombre | `Cerveza Paceña 620ml` |
| Código de barras | (el de la botella individual) |
| Categoría | `Bebidas` |
| Unidad de medida | `Pieza` |

### Paso 3 — Precios

**Precios base:**
| Campo | Valor | Descripción |
|---|---|---|
| Precio de compra | `Bs. 120.00` | Costo de la caja completa (24 botellas) |
| Precio de venta / unidad | `Bs. 7.00` | Precio de 1 botella al cliente |

**Configuración fraccionada:**
| Campo | Valor |
|---|---|
| Unidades por caja | `24` |
| Nombre del paquete | `Caja` |
| Precio venta / caja | `Bs. 140.00` (opcional) |

**Vista previa automática:**
```
Costo de compra (caja):  Bs. 120.00
Unidades por caja:       24 botellas
Costo por botella:       Bs. 5.00
Precio venta / botella:  Bs. 7.00    → margen +40%
Precio venta / caja:     Bs. 140.00  → margen +16.7%
```

### Paso 4 — Stock
| Campo | Valor | Descripción |
|---|---|---|
| Stock inicial | `96` | Tienes 4 cajas = 4 × 24 = 96 botellas |
| Stock mínimo | `24` | Alertar cuando quede menos de 1 caja |

---

## Caso 3 — Chicles (Empaque de 12 unidades)

**Descripción:** Producto pequeño que se compra en empaques y se vende por pieza individual o por empaque.

### Paso 1 — Tipo de producto
- Seleccionar: **Compra por Caja / Vende por Unidad**

### Paso 3 — Precios
| Campo | Valor |
|---|---|
| Precio de compra | `Bs. 8.00` (por empaque de 12) |
| Precio de venta / unidad | `Bs. 1.00` (por chicle) |
| Unidades por paquete | `12` |
| Nombre del paquete | `Empaque` |
| Precio venta / empaque | `Bs. 10.00` (si vendes el empaque completo) |

```
Costo por chicle:  Bs. 0.67
Venta por chicle:  Bs. 1.00  → margen +49%
Venta x empaque:   Bs. 10.00 → margen +25%
```

### Paso 4 — Stock
| Campo | Valor |
|---|---|
| Stock inicial | `120` (10 empaques × 12 chicles) |
| Stock mínimo | `24` (alertar cuando queden menos de 2 empaques) |

---

## Caso 4 — Frijol Negro (a Granel)

**Descripción:** Producto que se compra por bulto/costal y se vende por kilogramo.

### Paso 1 — Tipo de producto
- Seleccionar: **A Granel / Por Peso**

### Paso 2 — Información
| Campo | Valor |
|---|---|
| Nombre | `Frijol Negro` |
| Unidad de medida | `Kilogramo` |

### Paso 3 — Precios
| Campo | Valor | Descripción |
|---|---|---|
| Precio de compra | `Bs. 6.50` | Costo por kg (precio de compra ÷ kg totales del costal) |
| Precio de venta | `Bs. 9.00` | Precio al cliente por kg |

> **Cálculo:** Si compraste un costal de 50 kg a Bs. 325.00, el precio de compra por kg = 325 / 50 = **Bs. 6.50**

### Paso 4 — Stock
| Campo | Valor |
|---|---|
| Stock inicial | `50` (kg del costal) |
| Stock mínimo | `5` (alertar cuando queden 5 kg) |

---

## Caso 5 — Leche Fresca (Producto Perecedero)

**Descripción:** Producto con fecha de vencimiento crítica. El registro del producto es simple, pero al agregar lotes se debe registrar la fecha de vencimiento.

### Paso 1 — Tipo de producto
- Seleccionar: **Producto Simple**

### Paso 2 — Información
| Campo | Valor |
|---|---|
| Nombre | `Leche Fresca PIL 1 Litro` |
| Categoría | `Lácteos` |
| Unidad de medida | `Pieza` |

### Paso 3 — Precios
| Campo | Valor |
|---|---|
| Precio de compra | `Bs. 6.50` |
| Precio de venta | `Bs. 8.00` |

### Paso 4 — Stock
| Campo | Valor |
|---|---|
| Stock inicial | `0` ← Dejar en cero |
| Stock mínimo | `10` |

> 💡 **Recomendación:** Para productos perecederos, deja el stock inicial en **0** y registra la mercancía mediante **Agregar Lote** para poder ingresar la fecha de vencimiento. El sistema mostrará alertas cuando el lote esté próximo a vencer.

**Flujo después del registro:**
1. Inventario → Ver producto → Agregar Lote
2. Ingresar: cantidad, fecha de vencimiento, precio de compra del lote
3. El sistema agrega el stock y activa el monitoreo de vencimiento

---

## Caso 6 — Jabón de Tocador (Higiene)

**Descripción:** Producto empacado individualmente. Se compra en cajas de 6 barras, pero solo se vende por pieza.

### Paso 1 — Tipo de producto
- Seleccionar: **Producto Simple** (si no vendes la caja completa)
- O: **Compra por Caja / Vende por Unidad** (si a veces vendes la caja de 6)

### Paso 3 — Precios (opción Producto Simple)
| Campo | Valor | Descripción |
|---|---|---|
| Precio de compra | `Bs. 3.50` | Costo por barra (caja Bs. 21 ÷ 6) |
| Precio de venta | `Bs. 5.00` | Precio al cliente por barra |

> **Diferencia clave:** si el proveedor te cobra Bs. 21 por la caja de 6, pero nunca vendes la caja completa, calculas el costo por unidad tú mismo (21/6 = 3.50) y lo registras como producto simple.

---

## Caso 7 — Agua Purificada (dos presentaciones)

**Descripción:** El mismo producto existe en dos formatos distintos. Se recomienda registrarlos como **dos productos separados**.

### Producto A: Agua 600ml
| Campo | Valor |
|---|---|
| Nombre | `Agua Purificada 600ml` |
| Precio de compra | `Bs. 1.20` |
| Precio de venta | `Bs. 2.00` |

### Producto B: Garrafón 20L
| Campo | Valor |
|---|---|
| Nombre | `Garrafón Agua 20 Litros` |
| Precio de compra | `Bs. 18.00` |
| Precio de venta | `Bs. 25.00` |
| Unidad de medida | `Litro` |

> ✅ **Recomendación:** Registra cada presentación como un producto independiente con su propio código de barras. Evita combinarlos en uno solo para mantener el control de stock correcto.

---

## Caso 8 — Bolsas de Frituras (Docena)

**Descripción:** Producto pequeño que se puede vender suelto o por docena al por mayor.

### Paso 1 — Tipo
- Seleccionar: **Compra por Caja / Vende por Unidad**

### Paso 3 — Precios
| Campo | Valor |
|---|---|
| Precio de compra | `Bs. 18.00` (por docena de 12 bolsas) |
| Precio de venta | `Bs. 2.00` (por bolsa suelta) |
| Unidades por paquete | `12` |
| Nombre del paquete | `Docena` |
| Precio venta / docena | `Bs. 22.00` |

```
Costo por bolsa:   Bs. 1.50
Venta por bolsa:   Bs. 2.00 → margen +33%
Venta x docena:    Bs. 22.00 → margen +22%
```

---

## Caso 9 — Tamales Artesanales (Sin Código de Barras)

**Descripción:** Producto local sin empaque comercial. Se vende por pieza.

### Paso 2 — Información
| Campo | Valor |
|---|---|
| Nombre | `Tamal Rojo` |
| Código de barras | *(dejar vacío)* |
| Categoría | `Alimentos preparados` |
| Unidad de medida | `Pieza` |

> 💡 Sin código de barras, el vendedor busca el producto por nombre en el punto de venta. Usa nombres descriptivos y únicos.

### Paso 3 — Precios
| Campo | Valor |
|---|---|
| Precio de compra | `Bs. 4.00` (costo de ingredientes estimado) |
| Precio de venta | `Bs. 7.00` |

---

## Caso 10 — Cobro de Bolsa (Servicio)

**Descripción:** No es un producto físico perecedero, sino un cobro por servicio. Se gestiona como producto simple.

### Paso 1 — Tipo
- Seleccionar: **Otros / Servicio**

### Paso 2 — Información
| Campo | Valor |
|---|---|
| Nombre | `Bolsa Plástica` |
| Código de barras | *(dejar vacío)* |
| Categoría | `Servicios` |

### Paso 3 — Precios
| Campo | Valor |
|---|---|
| Precio de compra | `Bs. 0.10` (costo del rollo de bolsas) |
| Precio de venta | `Bs. 0.50` |

### Paso 4 — Stock
| Campo | Valor |
|---|---|
| Stock inicial | `500` (estimado de bolsas disponibles) |
| Stock mínimo | `50` |

---

## Tabla resumen rápido

| Situación | Tipo en formulario | ¿Precio compra es de...? | Unidades por paquete |
|---|---|---|---|
| Compra y vende por pieza/unidad | Simple | Cada pieza | 1 |
| Compra caja, solo vende suelto | Simple | Calcula costo/pieza tú | 1 |
| Compra caja, vende suelto **y** caja | Fraccionado | La caja completa | N (ej: 24) |
| Vende por kg o litro | A Granel | Por kg/lt | 1 |
| Producto sin stock real | Otro/Servicio | Costo estimado | 1 |
| Producto perecedero | Simple o Fraccionado | Normal | Normal |

---

## Errores comunes al registrar productos

### ❌ Error 1: Precio de compra por unidad en producto fraccionado
- **Mal:** Producto con 24 uds/caja, precio de compra = Bs. 5.00 (precio de **botella**)
- **Bien:** Precio de compra = Bs. 120.00 (precio de la **caja** completa)
- El sistema calcula automáticamente: 120 ÷ 24 = Bs. 5.00/botella

### ❌ Error 2: Stock en cajas en lugar de unidades
- **Mal:** Tienes 4 cajas de cerveza, pones stock = 4
- **Bien:** 4 cajas × 24 botellas = stock = **96**
- El formulario te muestra el equivalente en cajas automáticamente

### ❌ Error 3: Nombre poco descriptivo
- **Mal:** `Refresco`, `Jabón`, `Aceite`
- **Bien:** `Coca-Cola 600ml`, `Jabón Dove 90g`, `Aceite Sao 1 Litro`

### ❌ Error 4: Stock mínimo demasiado alto o bajo
- Si el stock mínimo es muy alto, recibirás alertas constantemente
- Si es muy bajo (ej: 1), el sistema casi nunca te avisará
- **Regla sugerida:** stock mínimo = 1 semana de ventas promedio del producto

### ❌ Error 5: No registrar fecha de vencimiento en perecederos
- Para lácteos, pan, carnes: siempre registra la mercancía via **Lotes** con su fecha de vencimiento
- Esto activa las alertas de vencimiento del sistema

---

*Última actualización: 2026-03-10*
