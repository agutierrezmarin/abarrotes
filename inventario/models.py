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
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


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
    def margen_ganancia(self):
        if self.precio_compra > 0:
            return ((self.precio_venta - self.precio_compra) / self.precio_compra) * 100
        return 0


class LoteProducto(models.Model):
    """Registra lotes de productos con fecha de vencimiento"""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=50, blank=True)
    cantidad = models.PositiveIntegerField()
    fecha_vencimiento = models.DateField(null=True, blank=True)
    fecha_entrada = models.DateField(default=timezone.now)
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
            delta = self.fecha_vencimiento - timezone.now().date()
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
