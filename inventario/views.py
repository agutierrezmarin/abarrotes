from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from .models import Producto, Categoria, Proveedor, LoteProducto, MovimientoInventario
from .forms import ProductoForm, LoteForm, AjusteStockForm


@login_required
def dashboard_inventario(request):
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    alertas = []

    # Alertas de stock bajo
    for p in productos:
        if p.stock_bajo:
            alertas.append({'tipo': 'stock', 'nivel': 'warning', 'mensaje': f'Stock bajo: {p.nombre} ({p.stock_actual} {p.get_unidad_medida_display()})'})

    # Alertas de vencimiento
    hoy = timezone.now().date()
    lotes_criticos = LoteProducto.objects.filter(
        fecha_vencimiento__lte=hoy + timedelta(days=7),
        fecha_vencimiento__gte=hoy
    ).select_related('producto')
    lotes_vencidos = LoteProducto.objects.filter(fecha_vencimiento__lt=hoy).select_related('producto')

    for lote in lotes_criticos:
        alertas.append({'tipo': 'vencimiento', 'nivel': 'danger', 'mensaje': f'Por vencer: {lote.producto.nombre} - Lote {lote.numero_lote or lote.pk} vence el {lote.fecha_vencimiento}'})
    for lote in lotes_vencidos:
        alertas.append({'tipo': 'vencimiento', 'nivel': 'critical', 'mensaje': f'¡VENCIDO!: {lote.producto.nombre} - Lote {lote.numero_lote or lote.pk} venció el {lote.fecha_vencimiento}'})

    context = {
        'total_productos': productos.count(),
        'productos_stock_bajo': sum(1 for p in productos if p.stock_bajo),
        'lotes_por_vencer': lotes_criticos.count(),
        'lotes_vencidos': lotes_vencidos.count(),
        'alertas': alertas,
        'productos_recientes': productos.order_by('-fecha_actualizacion')[:5],
    }
    return render(request, 'inventario/dashboard.html', context)


@login_required
def lista_productos(request):
    query = request.GET.get('q', '')
    categoria_id = request.GET.get('categoria', '')
    productos = Producto.objects.filter(activo=True).select_related('categoria', 'proveedor')

    if query:
        productos = productos.filter(Q(nombre__icontains=query) | Q(codigo_barras__icontains=query))
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)

    categorias = Categoria.objects.all()
    return render(request, 'inventario/productos.html', {
        'productos': productos,
        'categorias': categorias,
        'query': query,
        'categoria_sel': categoria_id,
    })


@login_required
def detalle_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    lotes = producto.lotes.all().order_by('fecha_vencimiento')
    movimientos = producto.movimientos.all()[:10]
    return render(request, 'inventario/detalle_producto.html', {
        'producto': producto, 'lotes': lotes, 'movimientos': movimientos
    })


@login_required
def crear_producto(request):
    if not request.user.groups.filter(name__in=['Administrador', 'Gerente']).exists() and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para crear productos.')
        return redirect('inventario:lista_productos')

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            MovimientoInventario.objects.create(
                producto=producto, tipo='entrada',
                cantidad=producto.stock_actual, stock_anterior=0,
                stock_nuevo=producto.stock_actual,
                motivo='Stock inicial', usuario=request.user
            )
            messages.success(request, f'Producto "{producto.nombre}" creado correctamente.')
            return redirect('inventario:detalle_producto', pk=producto.pk)
    else:
        form = ProductoForm()
    return render(request, 'inventario/form_producto.html', {'form': form, 'titulo': 'Nuevo Producto'})


@login_required
def editar_producto(request, pk):
    if not request.user.groups.filter(name__in=['Administrador', 'Gerente']).exists() and not request.user.is_superuser:
        messages.error(request, 'No tienes permisos para editar productos.')
        return redirect('inventario:lista_productos')

    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f'Producto "{producto.nombre}" actualizado.')
            return redirect('inventario:detalle_producto', pk=producto.pk)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/form_producto.html', {'form': form, 'titulo': 'Editar Producto', 'producto': producto})


@login_required
def ajustar_stock(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = AjusteStockForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data['cantidad']
            tipo = form.cleaned_data['tipo']
            motivo = form.cleaned_data['motivo']
            stock_anterior = producto.stock_actual

            if tipo == 'entrada':
                producto.stock_actual += cantidad
            elif tipo == 'salida':
                if cantidad > producto.stock_actual:
                    messages.error(request, 'No hay suficiente stock.')
                    return redirect('inventario:detalle_producto', pk=pk)
                producto.stock_actual -= cantidad
            elif tipo == 'ajuste':
                producto.stock_actual = cantidad

            producto.save()
            MovimientoInventario.objects.create(
                producto=producto, tipo=tipo, cantidad=cantidad,
                stock_anterior=stock_anterior, stock_nuevo=producto.stock_actual,
                motivo=motivo, usuario=request.user
            )
            messages.success(request, 'Stock actualizado correctamente.')
            return redirect('inventario:detalle_producto', pk=pk)
    else:
        form = AjusteStockForm()
    return render(request, 'inventario/ajuste_stock.html', {'form': form, 'producto': producto})


@login_required
def agregar_lote(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            lote = form.save(commit=False)
            lote.producto = producto
            lote.save()
            # Actualizar stock del producto
            stock_anterior = producto.stock_actual
            producto.stock_actual += lote.cantidad
            producto.save()
            MovimientoInventario.objects.create(
                producto=producto, tipo='entrada', cantidad=lote.cantidad,
                stock_anterior=stock_anterior, stock_nuevo=producto.stock_actual,
                motivo=f'Entrada de lote {lote.numero_lote or lote.pk}', usuario=request.user
            )
            messages.success(request, 'Lote agregado y stock actualizado.')
            return redirect('inventario:detalle_producto', pk=pk)
    else:
        form = LoteForm()
    return render(request, 'inventario/form_lote.html', {'form': form, 'producto': producto})


@login_required
def alertas_vencimiento(request):
    hoy = timezone.now().date()
    lotes_vencidos = LoteProducto.objects.filter(fecha_vencimiento__lt=hoy).select_related('producto')
    lotes_criticos = LoteProducto.objects.filter(
        fecha_vencimiento__range=[hoy, hoy + timedelta(days=7)]
    ).select_related('producto')
    lotes_proximos = LoteProducto.objects.filter(
        fecha_vencimiento__range=[hoy + timedelta(days=8), hoy + timedelta(days=30)]
    ).select_related('producto')

    return render(request, 'inventario/alertas_vencimiento.html', {
        'lotes_vencidos': lotes_vencidos,
        'lotes_criticos': lotes_criticos,
        'lotes_proximos': lotes_proximos,
    })
