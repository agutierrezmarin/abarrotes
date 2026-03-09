from django.contrib import admin
from .models import Venta, ItemVenta


class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['numero_ticket', 'vendedor', 'total', 'metodo_pago', 'estado', 'fecha_venta']
    list_filter = ['estado', 'metodo_pago', 'fecha_venta']
    readonly_fields = ['numero_ticket', 'fecha_creacion']
    inlines = [ItemVentaInline]
