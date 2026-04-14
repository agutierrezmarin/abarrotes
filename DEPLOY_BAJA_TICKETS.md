# Despliegue — Funcionalidad de Baja de Tickets

> **Rama / commit:** funcionalidad `dar_de_baja_ticket`
> **Impacto en BD:** 1 migración aditiva (`0003_venta_campos_baja`) — solo agrega columnas nuevas, no modifica ni elimina nada existente
> **Tiempo estimado de corte:** < 2 minutos
> **Riesgo de rotura:** Bajo — la migración es retrocompatible y el código existente no cambia

---

## Qué cambia en esta entrega

| Archivo | Tipo de cambio |
|---|---|
| `ventas/models.py` | +3 campos en `Venta` (`observacion_baja`, `dado_de_baja_por`, `fecha_baja`) |
| `ventas/migrations/0003_venta_campos_baja.py` | Migración nueva |
| `ventas/views.py` | +vista `dar_de_baja_ticket`, actualiza `historial_ventas` |
| `ventas/urls.py` | +ruta `ventas/baja/<pk>/` |
| `templates/ventas/historial.html` | Reescritura — muestra bajas y botón para admin/gerente |
| `reportes/views.py` | +query `bajas_mes` en reporte admin y gerente |
| `templates/reportes/administrador.html` | +sección tickets dados de baja |
| `templates/reportes/gerente.html` | +sección tickets dados de baja |

---

## Paso 1 — Respaldo de base de datos (obligatorio)

Ejecuta esto **antes de cualquier otro paso**. Si algo falla, este respaldo es tu punto de retorno.

```bash
# En el servidor de producción
sudo -u postgres pg_dump tienda_db > /home/deploy/backups/tienda_db_$(date +%Y%m%d_%H%M).sql
```

Verifica que el archivo se creó y tiene contenido:

```bash
ls -lh /home/deploy/backups/tienda_db_*.sql | tail -1
```

> Si aún no tienes el directorio de backups: `mkdir -p /home/deploy/backups`

---

## Paso 2 — Subir el código al servidor

### Opción A — Con Git (recomendado)

```bash
cd /var/www/tienda/abarrotes   # ajusta a tu ruta real en producción

git fetch origin
git status                     # confirma que no hay cambios locales sin commitear
git pull origin main           # o la rama que uses
```

### Opción B — Con rsync desde tu máquina local

```bash
# Desde tu máquina local
rsync -avz --exclude='*.pyc' --exclude='__pycache__' --exclude='.env' --exclude='db.sqlite3' \
  /home/alejandro/Documents/proyectos-django/proyecto_tienda/abarrotes/ \
  usuario@ip-del-vps:/var/www/tienda/abarrotes/
```

---

## Paso 3 — Verificar la migración antes de aplicarla

Conéctate al servidor y comprueba que la migración está pendiente y es la esperada:

```bash
cd /var/www/tienda/abarrotes
source /var/www/tienda/venv/bin/activate

python manage.py showmigrations ventas
```

Resultado esperado:

```
ventas
 [X] 0001_initial
 [X] 0002_itemventa_es_paquete_itemventa_unidades_descontadas
 [ ] 0003_venta_campos_baja        ← debe aparecer sin [X]
```

Revisa el SQL que va a ejecutarse (sin aplicarlo aún):

```bash
python manage.py sqlmigrate ventas 0003_venta_campos_baja
```

Deberías ver únicamente instrucciones `ALTER TABLE ... ADD COLUMN` — sin `DROP`, sin `ALTER COLUMN`, sin `DELETE`. Si ves algo distinto, **detente y revisa**.

---

## Paso 4 — Aplicar la migración

La migración solo agrega columnas con valor por defecto `NULL` / `blank`, por lo que **no toca los registros existentes** y puede ejecutarse con la aplicación activa (zero-downtime migration).

```bash
python manage.py migrate ventas
```

Resultado esperado:

```
Operations to perform:
  Apply all migrations: ventas
Running migrations:
  Applying ventas.0003_venta_campos_baja... OK
```

Confirma el estado final:

```bash
python manage.py showmigrations ventas
# Los tres deben aparecer con [X]
```

---

## Paso 5 — Verificación de integridad del proyecto

```bash
python manage.py check --deploy
```

No debe haber errores críticos. Las advertencias sobre HTTPS/HSTS son normales si ya estaban antes de este despliegue.

---

## Paso 6 — Recolectar archivos estáticos

Solo es necesario si modificaste CSS o JS. En esta entrega los cambios son solo en templates Python/HTML, por lo que puedes omitirlo. Si tienes dudas, ejecútalo de todas formas — no causa daño:

```bash
python manage.py collectstatic --noinput
```

---

## Paso 7 — Reiniciar Gunicorn

```bash
sudo systemctl restart tienda.service
sudo systemctl status tienda.service    # debe mostrar "active (running)"
```

---

## Paso 8 — Verificación en producción

Realiza estas comprobaciones en el navegador con un usuario de **Administrador** o **Gerente**:

### 8.1 Historial de ventas (`/ventas/historial/`)

- [ ] La tabla carga sin errores 500
- [ ] Las ventas completadas muestran el botón **"Dar de baja"**
- [ ] Un usuario vendedor (sin rol admin/gerente) **no ve** el botón de baja
- [ ] Al hacer clic en "Dar de baja" se abre el modal con el número y total del ticket
- [ ] El botón de confirmar está deshabilitado si el campo de observación está vacío
- [ ] Al confirmar con observación, el ticket aparece tachado en rojo con estado "Baja"
- [ ] El stock de los productos del ticket se revirtió (verificar en inventario)

### 8.2 Reportes

- [ ] `/reportes/administrador/` carga sin errores y muestra la sección **"Tickets Dados de Baja — Este Mes"**
- [ ] `/reportes/gerente/` carga sin errores y muestra la misma sección
- [ ] Si no hay bajas en el mes, la sección muestra "Sin tickets dados de baja este mes."

### 8.3 Funcionalidad anterior (regresión)

- [ ] El punto de venta (`/ventas/`) sigue funcionando normalmente
- [ ] Completar una venta nueva funciona y descuenta stock
- [ ] Los tickets completados siguen apareciendo en historial con badge verde

---

## Rollback — Si algo falla

### Revertir la migración

```bash
# Vuelve al estado anterior a 0003
python manage.py migrate ventas 0002_itemventa_es_paquete_itemventa_unidades_descontadas
```

Esto elimina las columnas `observacion_baja`, `dado_de_baja_por` y `fecha_baja` de la tabla `ventas_venta`. Los registros existentes no se alteran.

### Revertir el código

```bash
# Si usas Git
git revert HEAD        # crea un commit de reversión (seguro para producción)
# o bien
git checkout HEAD~1 -- ventas/views.py ventas/urls.py ventas/models.py \
    templates/ventas/historial.html \
    reportes/views.py \
    templates/reportes/administrador.html \
    templates/reportes/gerente.html
```

### Restaurar el backup de BD (solo si es necesario)

```bash
sudo -u postgres psql -c "DROP DATABASE tienda_db;"
sudo -u postgres psql -c "CREATE DATABASE tienda_db OWNER tienda_user;"
sudo -u postgres psql tienda_db < /home/deploy/backups/tienda_db_YYYYMMDD_HHMM.sql
```

### Reiniciar Gunicorn tras el rollback

```bash
sudo systemctl restart gunicorn
```

---

## Notas de operación

- Los tickets dados de baja quedan con `estado = 'cancelada'` y se muestran en el historial. No se eliminan de la base de datos.
- Cada baja genera un `MovimientoInventario` de tipo `ajuste` con el motivo truncado a 80 caracteres, trazable desde el módulo de inventario.
- Solo usuarios del grupo **Administrador**, **Gerente** o superusuario pueden dar de baja tickets. Un vendedor ve el historial pero no el botón de baja.
- Los reportes siguen contabilizando únicamente ventas con `estado = 'completada'` en sus totales e indicadores. Las bajas aparecen en una sección separada como registro de auditoría.
