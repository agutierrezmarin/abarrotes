from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    CONDICION_PAGO_CHOICES = [
        ('contado', 'Contado'),
        ('7dias', 'Crédito 7 días'),
        ('15dias', 'Crédito 15 días'),
        ('30dias', 'Crédito 30 días'),
        ('60dias', 'Crédito 60 días'),
    ]

    nombre = models.CharField(max_length=200)
    nit = models.CharField(max_length=30, blank=True, verbose_name='NIT / RUC')
    contacto = models.CharField(max_length=100, blank=True, verbose_name='Nombre del contacto')
    telefono = models.CharField(max_length=20, blank=True)
    celular = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    direccion = models.CharField(max_length=250, blank=True, verbose_name='Dirección')
    ciudad = models.CharField(max_length=100, blank=True)
    sitio_web = models.URLField(blank=True, verbose_name='Sitio web')
    condicion_pago = models.CharField(
        max_length=10, choices=CONDICION_PAGO_CHOICES,
        default='contado', verbose_name='Condición de pago'
    )
    notas = models.TextField(blank=True, verbose_name='Notas internas')
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateField(default=timezone.localdate)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def total_productos(self):
        return self.productos.filter(activo=True).count()


class Producto(models.Model):
    UNIDAD_CHOICES = [
        ('pza', 'Pieza'),
        ('kg', 'Kilogramo'),
        ('lt', 'Litro'),
        ('caja', 'Caja'),
        ('paq', 'Paquete'),
        ('bolsa', 'Bolsa'),
    ]

    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='productos')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    unidad_medida = models.CharField(max_length=10, choices=UNIDAD_CHOICES, default='pza')
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock_actual = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5, help_text='Cantidad mínima antes de generar alerta')
    # ── Venta fraccionada (compra por caja, vende por unidad) ──
    unidades_por_paquete = models.PositiveIntegerField(
        default=1,
        help_text='Unidades que contiene cada paquete/caja (1 = no aplica fraccionado)'
    )
    nombre_paquete = models.CharField(
        max_length=30, blank=True, default='Caja',
        help_text='Nombre del paquete (ej: Caja, Paquete, Bolsa, Cartón)'
    )
    precio_venta_paquete = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Precio al vender el paquete completo (dejar vacío si no aplica)'
    )
    activo = models.BooleanField(default=True)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.codigo_barras or "Sin código"})'

    @property
    def stock_bajo(self):
        return self.stock_actual <= self.stock_minimo

    @property
    def precio_compra_unidad(self):
        """Costo real por unidad. Si tiene paquete: precio_compra / unidades_por_paquete."""
        if self.tiene_paquete and self.unidades_por_paquete > 0:
            return self.precio_compra / self.unidades_por_paquete
        return self.precio_compra

    @property
    def margen_ganancia(self):
        """Margen sobre costo unitario real (%)."""
        costo = self.precio_compra_unidad
        if costo > 0:
            return float((self.precio_venta - costo) / costo * 100)
        return 0

    @property
    def ganancia_por_unidad(self):
        """Ganancia neta en Bs. por unidad vendida."""
        return self.precio_venta - self.precio_compra_unidad

    @property
    def tiene_paquete(self):
        return self.unidades_por_paquete > 1

    @property
    def stock_en_paquetes(self):
        if self.unidades_por_paquete > 1:
            return self.stock_actual // self.unidades_por_paquete
        return None

    @property
    def stock_unidades_sueltas(self):
        if self.unidades_por_paquete > 1:
            return self.stock_actual % self.unidades_por_paquete
        return self.stock_actual


class LoteProducto(models.Model):
    """Registra lotes de productos con fecha de vencimiento"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=50, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_entrada = models.DateField(default=timezone.localdate)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Lote de Producto'
        verbose_name_plural = 'Lotes de Productos'
        ordering = ['fecha_vencimiento']

    def __str__(self):
        return f'{self.producto.nombre} - Lote {self.numero_lote or self.pk}'

    @property
    def dias_para_vencer(self):
        if self.fecha_vencimiento:
            delta = self.fecha_vencimiento - timezone.localdate()
            return delta.days
        return None

    @property
    def dias_vencido(self):
        dias = self.dias_para_vencer
        if dias is not None and dias < 0:
            return abs(dias)
        return 0

    @property
    def estado_vencimiento(self):
        dias = self.dias_para_vencer
        if dias is None:
            return 'sin_fecha'
        if dias < 0:
            return 'vencido'
        if dias <= 7:
            return 'critico'
        if dias <= 30:
            return 'proximo'
        return 'vigente'


class AlertaSilenciada(models.Model):
    """Alertas que el usuario ocultó permanentemente o pospuso."""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_silenciadas')
    tipo = models.CharField(max_length=20)       # 'stock' | 'vencimiento'
    objeto_id = models.IntegerField()             # producto.pk o lote.pk
    pospuesto_hasta = models.DateField(null=True, blank=True)  # None = permanente

    class Meta:
        unique_together = ('usuario', 'tipo', 'objeto_id')
        verbose_name = 'Alerta Silenciada'
        verbose_name_plural = 'Alertas Silenciadas'

    def __str__(self):
        return f'{self.usuario} | {self.tipo}:{self.objeto_id}'


class MovimientoInventario(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
        ('devolucion', 'Devolución'),
    ]

    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    stock_anterior = models.PositiveIntegerField()
    stock_nuevo = models.PositiveIntegerField()
    motivo = models.CharField(max_length=200, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Movimiento de Inventario'
        verbose_name_plural = 'Movimientos de Inventario'
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.producto.nombre} ({self.cantidad})'
