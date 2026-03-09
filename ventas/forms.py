from django import forms


class BuscarProductoForm(forms.Form):
    buscar = forms.CharField(max_length=200, required=False,
                             widget=forms.TextInput(attrs={'placeholder': 'Buscar por nombre o código...', 'autofocus': True}))


class ItemVentaForm(forms.Form):
    producto_id = forms.IntegerField(widget=forms.HiddenInput)
    cantidad = forms.IntegerField(min_value=1, initial=1)


class CompletarVentaForm(forms.Form):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('fiado', 'Fiado'),
    ]
    metodo_pago = forms.ChoiceField(choices=METODO_PAGO_CHOICES)
    monto_recibido = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    descuento = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0, required=False, initial=0)
