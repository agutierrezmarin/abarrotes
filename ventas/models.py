from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from inventario.models import Producto


class Venta(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('devolucion', 'Devolución'),
    ]
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('fiado', 'Fiado'),
    ]

    numero_ticket = models.CharField(max_length=20, unique=True)
    vendedor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ventas')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='completada')
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES, default='efectivo')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_recibido = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notas = models.TextField(blank=True)
    fecha_venta = models.DateTimeField(default=timezone.now)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'Ventas'
        ordering = ['-fecha_venta']

    def __str__(self):
        return f'Ticket #{self.numero_ticket} - ${self.total}'

    def calcular_totales(self):
        self.subtotal = sum(item.subtotal for item in self.items.all())
        self.total = self.subtotal - self.descuento
        self.cambio = max(0, self.monto_recibido - self.total)
        self.save()

    @classmethod
    def generar_numero_ticket(cls):
        from datetime import datetime
        prefijo = datetime.now().strftime('%Y%m%d')
        ultimo = cls.objects.filter(numero_ticket__startswith=prefijo).count() + 1
        return f'{prefijo}-{ultimo:04d}'


class ItemVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name='items_venta')
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    es_paquete = models.BooleanField(default=False, help_text='True si se vendió como paquete/caja completa')
    unidades_descontadas = models.PositiveIntegerField(default=0, help_text='Unidades reales descontadas del stock')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Item de Venta'
        verbose_name_plural = 'Items de Venta'

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'

    def save(self, *args, **kwargs):
        self.subtotal = (self.precio_unitario * self.cantidad) - self.descuento
        if not self.unidades_descontadas:
            if self.es_paquete and self.producto_id:
                try:
                    upq = self.producto.unidades_por_paquete
                    self.unidades_descontadas = self.cantidad * upq
                except Exception:
                    self.unidades_descontadas = self.cantidad
            else:
                self.unidades_descontadas = self.cantidad
        super().save(*args, **kwargs)
