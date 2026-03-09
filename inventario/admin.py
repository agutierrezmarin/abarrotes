from django.contrib import admin
from .models import Categoria, Proveedor, Producto, LoteProducto, MovimientoInventario


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']
    search_fields = ['nombre']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'contacto', 'telefono', 'email']
    search_fields = ['nombre']


class LoteInline(admin.TabularInline):
    model = LoteProducto
    extra = 0


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio_venta', 'stock_actual', 'stock_minimo', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'codigo_barras']
    inlines = [LoteInline]


@admin.register(LoteProducto)
class LoteAdmin(admin.ModelAdmin):
    list_display = ['producto', 'numero_lote', 'cantidad', 'fecha_vencimiento', 'estado_vencimiento']
    list_filter = ['fecha_vencimiento']
    search_fields = ['producto__nombre', 'numero_lote']


@admin.register(MovimientoInventario)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'stock_anterior', 'stock_nuevo', 'usuario', 'fecha']
    list_filter = ['tipo', 'fecha']
    readonly_fields = ['fecha']
