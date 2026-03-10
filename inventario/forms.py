from django import forms
from .models import Producto, LoteProducto, Proveedor


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'codigo_barras', 'nombre', 'descripcion', 'categoria', 'proveedor',
            'unidad_medida', 'precio_compra', 'precio_venta', 'stock_actual',
            'stock_minimo', 'activo', 'imagen',
            # Campos de venta fraccionada
            'unidades_por_paquete', 'nombre_paquete', 'precio_venta_paquete',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio_compra': forms.NumberInput(attrs={'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'step': '0.01'}),
            'precio_venta_paquete': forms.NumberInput(attrs={'step': '0.01'}),
        }
        labels = {
            'precio_compra': 'Precio de compra por paquete (Bs.)',
            'precio_venta': 'Precio de venta por unidad (Bs.)',
            'precio_venta_paquete': 'Precio de venta por paquete/caja (Bs.)',
            'unidades_por_paquete': 'Unidades por paquete',
            'nombre_paquete': 'Nombre del paquete',
        }


class LoteForm(forms.ModelForm):
    # Campo extra: ingresar la cantidad en paquetes en lugar de unidades
    ingresar_en_paquetes = forms.BooleanField(
        required=False,
        label='Ingresar cantidad en paquetes/cajas',
        help_text='Marca esta casilla si vas a registrar cuántas cajas/paquetes entran en lugar de unidades'
    )
    num_paquetes = forms.IntegerField(
        required=False, min_value=1,
        label='Número de paquetes/cajas recibidos',
        help_text='El sistema calculará automáticamente el total de unidades'
    )

    class Meta:
        model = LoteProducto
        fields = ['numero_lote', 'cantidad', 'fecha_vencimiento', 'fecha_entrada', 'precio_compra', 'notas']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrada': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'cantidad': 'Cantidad en unidades (se calcula automáticamente si usas paquetes)',
            'precio_compra': 'Precio de compra por paquete (Bs.)',
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = [
            'nombre', 'nit', 'contacto', 'telefono', 'celular',
            'email', 'direccion', 'ciudad', 'sitio_web',
            'condicion_pago', 'notas', 'activo',
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }


class AjusteStockForm(forms.Form):
    TIPO_CHOICES = [
        ('entrada', 'Entrada de mercancía'),
        ('salida', 'Salida de mercancía'),
        ('ajuste', 'Ajuste de inventario (valor absoluto)'),
    ]
    tipo = forms.ChoiceField(choices=TIPO_CHOICES)
    cantidad = forms.IntegerField(min_value=1)
    motivo = forms.CharField(max_length=200, required=True)
