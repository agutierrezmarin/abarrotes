from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from datetime import timedelta, date
from .models import Producto, Categoria, Proveedor, LoteProducto, MovimientoInventario, AlertaSilenciada
from .forms import ProductoForm, LoteForm, AjusteStockForm, ProveedorForm


@login_required
def dashboard_inventario(request):
    productos = Producto.objects.filter(activo=True).select_related('categoria')
    alertas = []
    hoy_dashboard = timezone.localdate()

    # IDs silenciados por este usuario (permanente o que aún no se deben mostrar)
    silenciadas = AlertaSilenciada.objects.filter(
        usuario=request.user
    ).values('tipo', 'objeto_id', 'pospuesto_hasta')
    silenciadas_map = {
        (s['tipo'], s['objeto_id']): s['pospuesto_hasta']
        for s in silenciadas
    }

    def _silenciada(tipo, objeto_id):
        key = (tipo, objeto_id)
        if key not in silenciadas_map:
            return False
        pospuesto = silenciadas_map[key]
        if pospuesto is None:
            return True           # permanente
        return hoy_dashboard < pospuesto  # pospuesta y aún no ha llegado la fecha

    # Alertas de stock bajo
    for p in productos:
        if p.stock_bajo and not _silenciada('stock', p.pk):
            alertas.append({'tipo': 'stock', 'objeto_id': p.pk, 'nivel': 'warning', 'mensaje': f'Stock bajo: {p.nombre} ({p.stock_actual} {p.get_unidad_medida_display()})'})

    # Alertas de vencimiento
    hoy = timezone.localdate()
    lotes_criticos = LoteProducto.objects.filter(
        fecha_vencimiento__lte=hoy + timedelta(days=7),
        fecha_vencimiento__gte=hoy
    ).select_related('producto')
    lotes_vencidos = LoteProducto.objects.filter(fecha_vencimiento__lt=hoy).select_related('producto')

    for lote in lotes_criticos:
        if not _silenciada('vencimiento', lote.pk):
            alertas.append({'tipo': 'vencimiento', 'objeto_id': lote.pk, 'nivel': 'danger', 'mensaje': f'Por vencer: {lote.producto.nombre} - Lote {lote.numero_lote or lote.pk} vence el {lote.fecha_vencimiento}'})
    for lote in lotes_vencidos:
        if not _silenciada('vencimiento', lote.pk):
            alertas.append({'tipo': 'vencimiento', 'objeto_id': lote.pk, 'nivel': 'critical', 'mensaje': f'¡VENCIDO!: {lote.producto.nombre} - Lote {lote.numero_lote or lote.pk} venció el {lote.fecha_vencimiento}'})

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
    query = request.GET.get('q', '').strip()
    categoria_id = request.GET.get('categoria', '')
    proveedor_id = request.GET.get('proveedor', '')
    estado = request.GET.get('estado', 'activo')   # activo | inactivo | todos
    stock_bajo = request.GET.get('stock_bajo', '')  # '1' para filtrar solo stock bajo

    productos = Producto.objects.select_related('categoria', 'proveedor').order_by('nombre')

    if estado == 'activo':
        productos = productos.filter(activo=True)
    elif estado == 'inactivo':
        productos = productos.filter(activo=False)
    # 'todos' no filtra por activo

    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) |
            Q(codigo_barras__icontains=query) |
            Q(descripcion__icontains=query)
        )
    if categoria_id:
        productos = productos.filter(categoria_id=categoria_id)
    if proveedor_id:
        productos = productos.filter(proveedor_id=proveedor_id)
    if stock_bajo == '1':
        productos = [p for p in productos if p.stock_bajo]

    categorias = Categoria.objects.all()
    proveedores = Proveedor.objects.filter(activo=True)
    hay_filtros = any([query, categoria_id, proveedor_id, stock_bajo == '1', estado != 'activo'])

    return render(request, 'inventario/productos.html', {
        'productos': productos,
        'categorias': categorias,
        'proveedores': proveedores,
        'query': query,
        'categoria_sel': categoria_id,
        'proveedor_sel': proveedor_id,
        'estado': estado,
        'stock_bajo': stock_bajo,
        'hay_filtros': hay_filtros,
        'total_activos': Producto.objects.filter(activo=True).count(),
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
            if producto.stock_actual > 0:
                MovimientoInventario.objects.create(
                    producto=producto, tipo='entrada',
                    cantidad=producto.stock_actual, stock_anterior=0,
                    stock_nuevo=producto.stock_actual,
                    motivo='Stock inicial', usuario=request.user
                )
                LoteProducto.objects.create(
                    producto=producto,
                    numero_lote=form.cleaned_data.get('numero_lote_inicial') or '',
                    cantidad=producto.stock_actual,
                    fecha_vencimiento=form.cleaned_data.get('fecha_vencimiento_inicial'),
                    precio_compra=producto.precio_compra,
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

            # Si se ingresó en paquetes, calcular la cantidad en unidades
            ingresar_en_paquetes = form.cleaned_data.get('ingresar_en_paquetes')
            num_paquetes = form.cleaned_data.get('num_paquetes')
            if ingresar_en_paquetes and num_paquetes and producto.tiene_paquete:
                lote.cantidad = num_paquetes * producto.unidades_por_paquete
                motivo_extra = f' ({num_paquetes} {producto.nombre_paquete}s x {producto.unidades_por_paquete} uds.)'
            else:
                motivo_extra = ''

            lote.save()
            stock_anterior = producto.stock_actual
            producto.stock_actual += lote.cantidad
            producto.save()
            MovimientoInventario.objects.create(
                producto=producto, tipo='entrada', cantidad=lote.cantidad,
                stock_anterior=stock_anterior, stock_nuevo=producto.stock_actual,
                motivo=f'Entrada de lote {lote.numero_lote or lote.pk}{motivo_extra}', usuario=request.user
            )
            messages.success(request, f'Lote agregado: {lote.cantidad} unidades en stock.')
            return redirect('inventario:detalle_producto', pk=pk)
    else:
        form = LoteForm()
    return render(request, 'inventario/form_lote.html', {'form': form, 'producto': producto})


@login_required
def alertas_stock_bajo(request):
    from django.db.models import F
    productos = (
        Producto.objects
        .filter(activo=True, stock_actual__lte=F('stock_minimo'))
        .select_related('categoria', 'proveedor')
        .order_by('stock_actual')
    )
    return render(request, 'inventario/alertas_stock_bajo.html', {
        'productos': productos,
        'total': productos.count(),
    })


def _agrupar_lotes_por_producto(queryset):
    """
    Agrupa lotes por producto. Por cada producto devuelve un dict con:
    - producto: instancia del modelo
    - lotes: lista de lotes del producto en esa categoría
    - fecha_mas_critica: la fecha de vencimiento más próxima (o más antigua si vencidos)
    - cantidad_total: suma de unidades en esos lotes
    - num_lotes: cantidad de lotes distintos
    """
    grupos = {}
    for lote in queryset:
        pid = lote.producto_id
        if pid not in grupos:
            grupos[pid] = {
                'producto': lote.producto,
                'lotes': [],
                'fecha_mas_critica': lote.fecha_vencimiento,
                'cantidad_total': 0,
                'num_lotes': 0,
            }
        grupos[pid]['lotes'].append(lote)
        grupos[pid]['cantidad_total'] += lote.cantidad
        grupos[pid]['num_lotes'] += 1
        # Para vencidos: la más antigua (min). Para próximos: la más cercana (min también).
        if lote.fecha_vencimiento and lote.fecha_vencimiento < grupos[pid]['fecha_mas_critica']:
            grupos[pid]['fecha_mas_critica'] = lote.fecha_vencimiento
    return sorted(grupos.values(), key=lambda g: g['fecha_mas_critica'] or timezone.localdate())


@login_required
def alertas_vencimiento(request):
    hoy = timezone.localdate()

    lotes_vencidos = LoteProducto.objects.filter(
        fecha_vencimiento__lt=hoy
    ).select_related('producto').order_by('fecha_vencimiento')

    lotes_criticos = LoteProducto.objects.filter(
        fecha_vencimiento__range=[hoy, hoy + timedelta(days=7)]
    ).select_related('producto').order_by('fecha_vencimiento')

    lotes_proximos = LoteProducto.objects.filter(
        fecha_vencimiento__range=[hoy + timedelta(days=8), hoy + timedelta(days=30)]
    ).select_related('producto').order_by('fecha_vencimiento')

    return render(request, 'inventario/alertas_vencimiento.html', {
        'grupos_vencidos': _agrupar_lotes_por_producto(lotes_vencidos),
        'grupos_criticos': _agrupar_lotes_por_producto(lotes_criticos),
        'grupos_proximos': _agrupar_lotes_por_producto(lotes_proximos),
        'total_vencidos': lotes_vencidos.values('producto').distinct().count(),
        'total_criticos': lotes_criticos.values('producto').distinct().count(),
        'total_proximos': lotes_proximos.values('producto').distinct().count(),
    })


@login_required
@require_POST
def silenciar_alerta(request):
    """AJAX: oculta una alerta permanentemente o la pospone N días."""
    tipo = request.POST.get('tipo')
    objeto_id = request.POST.get('objeto_id')
    dias = request.POST.get('dias')  # None/'0' = permanente, número = posponer

    if tipo not in ('stock', 'vencimiento') or not objeto_id:
        return JsonResponse({'ok': False, 'error': 'Datos inválidos'}, status=400)

    pospuesto_hasta = None
    if dias and dias != '0':
        pospuesto_hasta = timezone.localdate() + timedelta(days=int(dias))

    AlertaSilenciada.objects.update_or_create(
        usuario=request.user,
        tipo=tipo,
        objeto_id=int(objeto_id),
        defaults={'pospuesto_hasta': pospuesto_hasta},
    )
    return JsonResponse({'ok': True})


# ── Proveedores ──────────────────────────────────────────────────────────────

def _solo_admin(user):
    return user.groups.filter(name__in=['Administrador', 'Gerente']).exists() or user.is_superuser


@login_required
def lista_proveedores(request):
    query = request.GET.get('q', '')
    solo_activos = request.GET.get('activos', '1')
    proveedores = Proveedor.objects.all()
    if solo_activos == '1':
        proveedores = proveedores.filter(activo=True)
    if query:
        proveedores = proveedores.filter(
            Q(nombre__icontains=query) | Q(contacto__icontains=query) |
            Q(telefono__icontains=query) | Q(ciudad__icontains=query)
        )
    return render(request, 'inventario/proveedores.html', {
        'proveedores': proveedores,
        'query': query,
        'solo_activos': solo_activos,
        'total': Proveedor.objects.count(),
        'activos': Proveedor.objects.filter(activo=True).count(),
    })


@login_required
def detalle_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    productos = proveedor.productos.filter(activo=True).order_by('nombre')
    return render(request, 'inventario/detalle_proveedor.html', {
        'proveedor': proveedor,
        'productos': productos,
    })


@login_required
def crear_proveedor(request):
    if not _solo_admin(request.user):
        messages.error(request, 'No tienes permisos para crear proveedores.')
        return redirect('inventario:lista_proveedores')
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre}" creado correctamente.')
            return redirect('inventario:detalle_proveedor', pk=proveedor.pk)
    else:
        form = ProveedorForm()
    return render(request, 'inventario/form_proveedor.html', {'form': form, 'titulo': 'Nuevo Proveedor'})


@login_required
def editar_proveedor(request, pk):
    if not _solo_admin(request.user):
        messages.error(request, 'No tienes permisos para editar proveedores.')
        return redirect('inventario:lista_proveedores')
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f'Proveedor "{proveedor.nombre}" actualizado.')
            return redirect('inventario:detalle_proveedor', pk=proveedor.pk)
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'inventario/form_proveedor.html', {
        'form': form, 'titulo': 'Editar Proveedor', 'proveedor': proveedor
    })


@login_required
def toggle_proveedor(request, pk):
    if not _solo_admin(request.user):
        messages.error(request, 'No tienes permisos.')
        return redirect('inventario:lista_proveedores')
    proveedor = get_object_or_404(Proveedor, pk=pk)
    proveedor.activo = not proveedor.activo
    proveedor.save()
    estado = 'activado' if proveedor.activo else 'desactivado'
    messages.success(request, f'Proveedor "{proveedor.nombre}" {estado}.')
    return redirect('inventario:detalle_proveedor', pk=pk)
