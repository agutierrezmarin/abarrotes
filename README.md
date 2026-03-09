# 🛒 Sistema de Gestión para Tienda de Abarrotes

Sistema web completo para la administración de inventario, punto de venta, reportes y gestión de usuarios de una tienda de abarrotes, desarrollado con **Django 6** y **Bootstrap 5**.

---

## Características principales

### 📦 Inventario
- Registro de productos con código de barras, categoría y proveedor
- Control de stock con umbral mínimo configurable
- Registro de lotes con fechas de vencimiento
- Alertas automáticas: stock bajo, próximos a vencer (7 / 30 días), vencidos
- Historial completo de movimientos (entradas, salidas, ajustes, devoluciones)

### 🧾 Punto de Venta
- Búsqueda de productos en tiempo real (AJAX)
- Ticket con número único por día
- Métodos de pago: efectivo, tarjeta, transferencia, fiado
- Descuentos por venta y cálculo automático de cambio
- Verificación de stock al momento de cobrar
- Ticket imprimible desde el navegador

### 📊 Reportes por Rol
- **Vendedor:** ventas propias del día, total recaudado y promedio por ticket
- **Administrador:** resumen hoy / semana / mes, top 10 productos, alertas de stock y vencimiento
- **Gerente:** rendimiento por vendedor, utilidad estimada por producto, ventas diarias del mes

### 👥 Gestión de Usuarios
- Registro de nuevos usuarios con asignación de rol
- Edición de datos y cambio de contraseña
- Activar / desactivar cuentas
- Acceso exclusivo para Administrador y Superusuario

---

## Tecnologías

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3.13 / Django 6.0 |
| Base de datos | SQLite |
| Frontend | Bootstrap 5.3 + Font Awesome 6 |
| Autenticación | Django Auth (grupos y permisos) |
| Zona horaria | America/La_Paz (Bolivia) |
| Moneda | Bolivianos (Bs.) |

---

## Roles del sistema

| Rol | Acceso |
|-----|--------|
| **Vendedor** | Punto de venta, historial propio, reporte del día |
| **Administrador** | Todo lo anterior + inventario, gestión de usuarios, reporte admin |
| **Gerente** | Todo lo anterior + reporte gerencial con utilidades y rendimiento |
| **Superusuario** | Acceso total incluyendo panel `/admin/` de Django |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd abarrotes
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 3. Instalar dependencias

```bash
pip install django pillow
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Cargar datos iniciales

Crea los grupos de roles, usuarios de prueba y categorías base:

```bash
python manage.py shell < setup_inicial.py
```

### 6. Ejecutar el servidor

```bash
python manage.py runserver
```

Acceder en: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Usuarios de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Superusuario |
| `supervisor` | `super123` | Administrador |
| `gerente` | `gerente123` | Gerente |
| `vendedor1` | `vendedor123` | Vendedor |

Panel de administración Django: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Estructura del proyecto

```
abarrotes/
├── abarrotes/          # Configuración principal (settings, urls, wsgi)
├── inventario/         # Modelos, vistas y formularios de inventario
├── ventas/             # Lógica del punto de venta
├── reportes/           # Reportes diferenciados por rol
├── usuarios/           # Gestión de usuarios y roles
├── templates/          # HTML organizados por app
│   ├── base.html
│   ├── auth/
│   ├── inventario/
│   ├── ventas/
│   ├── reportes/
│   └── usuarios/
├── manage.py
├── setup_inicial.py    # Script de configuración inicial
├── .gitignore
└── README.md
```

---

## URLs principales

| URL | Descripción |
|-----|-------------|
| `/` | Inicio (redirige según rol) |
| `/inventario/` | Dashboard de inventario |
| `/inventario/productos/` | Lista de productos |
| `/inventario/alertas/` | Alertas de vencimiento |
| `/ventas/` | Punto de venta |
| `/ventas/historial/` | Historial de ventas |
| `/reportes/vendedor/` | Reporte del vendedor |
| `/reportes/administrador/` | Reporte del administrador |
| `/reportes/gerente/` | Reporte gerencial |
| `/usuarios/` | Gestión de usuarios |
| `/admin/` | Panel de administración Django |
