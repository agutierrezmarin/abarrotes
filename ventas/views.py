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

        es_paquete = request.POST.get('es_paquete') == '1'
        upq = producto.unidades_por_paquete  # units per package

        # Calcular cuántas unidades se necesitan del stock
        unidades_necesarias = cantidad * upq if es_paquete else cantidad

        if producto.stock_actual < unidades_necesarias:
            disponible = producto.stock_en_paquetes if es_paquete else producto.stock_actual
            unidad_disp = producto.nombre_paquete if es_paquete else producto.get_unidad_medida_display()
            messages.error(request, f'Stock insuficiente. Disponible: {disponible} {unidad_disp}')
            return redirect('ventas:punto_venta')

        precio = producto.precio_venta_paquete if (es_paquete and producto.precio_venta_paquete) else producto.precio_venta
        unidades_desc = cantidad * upq if es_paquete else cantidad

        # Agregar o actualizar item (separamos línea de unidad vs paquete)
        item, creado = ItemVenta.objects.get_or_create(
            venta=venta, producto=producto, es_paquete=es_paquete,
            defaults={
                'precio_unitario': precio,
                'cantidad': cantidad,
                'unidades_descontadas': unidades_desc,
            }
        )
        if not creado:
            item.cantidad += cantidad
            item.unidades_descontadas += unidades_desc
            item.save()

        venta.calcular_totales()
        tipo_label = producto.nombre_paquete if es_paquete else producto.get_unidad_medida_display()
        messages.success(request, f'"{producto.nombre}" agregado ({cantidad} {tipo_label}).')
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

            # Verificar stock antes de descontar (usando unidades_descontadas reales)
            for item in venta.items.select_related('producto').all():
                uds = item.unidades_descontadas or item.cantidad
                if item.producto.stock_actual < uds:
                    messages.error(request, f'Stock insuficiente para "{item.producto.nombre}". Disponible: {item.producto.stock_actual} uds.')
                    return redirect('ventas:punto_venta')

            # Descontar stock (siempre en unidades base)
            for item in venta.items.select_related('producto').all():
                producto = item.producto
                uds = item.unidades_descontadas or item.cantidad
                stock_anterior = producto.stock_actual
                producto.stock_actual -= uds
                producto.save()
                tipo_label = f'{item.cantidad} {producto.nombre_paquete}' if item.es_paquete else f'{item.cantidad} uds.'
                MovimientoInventario.objects.create(
                    producto=producto, tipo='salida', cantidad=uds,
                    stock_anterior=stock_anterior, stock_nuevo=producto.stock_actual,
                    motivo=f'Venta ticket #{venta.numero_ticket} ({tipo_label})', usuario=request.user
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

    data = []
    for p in productos:
        item = {
            'id': p.pk,
            'nombre': p.nombre,
            'precio': str(p.precio_venta),
            'stock': p.stock_actual,
            'unidad': p.get_unidad_medida_display(),
            'tiene_paquete': p.tiene_paquete,
            'upq': p.unidades_por_paquete,
            'nombre_paquete': p.nombre_paquete or 'Caja',
            'precio_paquete': str(p.precio_venta_paquete) if p.precio_venta_paquete else None,
            'stock_paquetes': p.stock_en_paquetes,
        }
        data.append(item)
    return JsonResponse({'productos': data})
