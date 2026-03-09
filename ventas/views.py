from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from inventario.models import Producto, MovimientoInventario
from .models import Venta, ItemVenta
from .forms import BuscarProductoForm, ItemVentaForm, CompletarVentaForm


@login_required
def punto_venta(request):
    """Vista principal del punto de venta (caja)"""
    # Obtener o crear venta en proceso en la sesión
    venta_id = request.session.get('venta_activa_id')
    venta = None
    if venta_id:
        try:
            venta = Venta.objects.get(pk=venta_id, estado='pendiente')
        except Venta.DoesNotExist:
            del request.session['venta_activa_id']

    if not venta:
        venta = Venta.objects.create(
            numero_ticket=Venta.generar_numero_ticket(),
            vendedor=request.user,
            estado='pendiente'
        )
        request.session['venta_activa_id'] = venta.pk

    items = venta.items.select_related('producto').all()
    buscar_form = BuscarProductoForm()

    return render(request, 'ventas/punto_venta.html', {
        'venta': venta,
        'items': items,
        'buscar_form': buscar_form,
    })


@login_required
def agregar_item(request):
    if request.method == 'POST':
        venta_id = request.session.get('venta_activa_id')
        if not venta_id:
            messages.error(request, 'No hay venta activa.')
            return redirect('ventas:punto_venta')

        venta = get_object_or_404(Venta, pk=venta_id, estado='pendiente')
        producto_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 1))

        try:
            producto = Producto.objects.get(pk=producto_id, activo=True)
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado.')
            return redirect('ventas:punto_venta')

        if producto.stock_actual < cantidad:
            messages.error(request, f'Stock insuficiente. Disponible: {producto.stock_actual}')
            return redirect('ventas:punto_venta')

        # Agregar o actualizar item
        item, creado = ItemVenta.objects.get_or_create(
            venta=venta, producto=producto,
            defaults={'precio_unitario': producto.precio_venta, 'cantidad': cantidad}
        )
        if not creado:
            item.cantidad += cantidad
            item.save()

        venta.calcular_totales()
        messages.success(request, f'"{producto.nombre}" agregado.')
    return redirect('ventas:punto_venta')


@login_required
def quitar_item(request, item_id):
    venta_id = request.session.get('venta_activa_id')
    item = get_object_or_404(ItemVenta, pk=item_id, venta_id=venta_id)
    venta = item.venta
    item.delete()
    venta.calcular_totales()
    messages.success(request, 'Producto eliminado del ticket.')
    return redirect('ventas:punto_venta')


@login_required
@transaction.atomic
def completar_venta(request):
    if request.method == 'POST':
        venta_id = request.session.get('venta_activa_id')
        venta = get_object_or_404(Venta, pk=venta_id, estado='pendiente')

        if not venta.items.exists():
            messages.error(request, 'No hay productos en el ticket.')
            return redirect('ventas:punto_venta')

        form = CompletarVentaForm(request.POST)
        if form.is_valid():
            venta.metodo_pago = form.cleaned_data['metodo_pago']
            venta.monto_recibido = form.cleaned_data['monto_recibido']
            venta.descuento = form.cleaned_data.get('descuento', 0)
            venta.calcular_totales()

            if venta.metodo_pago == 'efectivo' and venta.monto_recibido < venta.total:
                messages.error(request, 'El monto recibido es insuficiente.')
                return redirect('ventas:punto_venta')

            # Verificar stock antes de descontar
            for item in venta.items.select_related('producto').all():
                if item.producto.stock_actual < item.cantidad:
                    messages.error(request, f'Stock insuficiente para "{item.producto.nombre}". Disponible: {item.producto.stock_actual}')
                    return redirect('ventas:punto_venta')

            # Descontar stock
            for item in venta.items.select_related('producto').all():
                producto = item.producto
                stock_anterior = producto.stock_actual
                producto.stock_actual -= item.cantidad
                producto.save()
                MovimientoInventario.objects.create(
                    producto=producto, tipo='salida', cantidad=item.cantidad,
                    stock_anterior=stock_anterior, stock_nuevo=producto.stock_actual,
                    motivo=f'Venta ticket #{venta.numero_ticket}', usuario=request.user
                )

            venta.estado = 'completada'
            venta.fecha_venta = timezone.now()
            venta.save()

            del request.session['venta_activa_id']
            messages.success(request, f'Venta completada. Ticket #{venta.numero_ticket}')
            return redirect('ventas:ticket', pk=venta.pk)
    return redirect('ventas:punto_venta')


@login_required
def ticket_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    return render(request, 'ventas/ticket.html', {'venta': venta, 'items': venta.items.select_related('producto').all()})


@login_required
def historial_ventas(request):
    ventas = Venta.objects.filter(estado='completada').select_related('vendedor').order_by('-fecha_venta')
    return render(request, 'ventas/historial.html', {'ventas': ventas})


@login_required
def buscar_producto_ajax(request):
    from django.http import JsonResponse
    query = request.GET.get('q', '')
    productos = Producto.objects.filter(
        activo=True, stock_actual__gt=0
    ).filter(
        nombre__icontains=query
    )[:10] if query else []

    data = [{'id': p.pk, 'nombre': p.nombre, 'precio': str(p.precio_venta),
              'stock': p.stock_actual, 'unidad': p.get_unidad_medida_display()} for p in productos]
    return JsonResponse({'productos': data})
