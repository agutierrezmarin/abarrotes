from django import forms
from .models import Producto, LoteProducto


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo_barras', 'nombre', 'descripcion', 'categoria', 'proveedor',
                  'unidad_medida', 'precio_compra', 'precio_venta', 'stock_actual',
                  'stock_minimo', 'activo', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'precio_compra': forms.NumberInput(attrs={'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'step': '0.01'}),
        }


class LoteForm(forms.ModelForm):
    class Meta:
        model = LoteProducto
        fields = ['numero_lote', 'cantidad', 'fecha_vencimiento', 'fecha_entrada', 'precio_compra', 'notas']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'fecha_entrada': forms.DateInput(attrs={'type': 'date'}),
            'notas': forms.Textarea(attrs={'rows': 2}),
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
