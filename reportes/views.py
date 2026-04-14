from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncDate
from datetime import timedelta
from ventas.models import Venta, ItemVenta
from inventario.models import Producto, LoteProducto


def solo_gerente_admin(user):
    return user.groups.filter(name__in=['Gerente', 'Administrador']).exists() or user.is_superuser


def solo_gerente(user):
    return user.groups.filter(name='Gerente').exists() or user.is_superuser


@login_required
def reporte_vendedor(request):
    """Reporte básico para vendedores: sus propias ventas del día"""
    hoy = timezone.localdate()
    ventas_hoy = Venta.objects.filter(
        vendedor=request.user, estado='completada',
        fecha_venta__date=hoy
    )
    total_hoy = ventas_hoy.aggregate(total=Sum('total'))['total'] or 0
    num_ventas = ventas_hoy.count()
    promedio = round(total_hoy / num_ventas, 2) if num_ventas else 0

    return render(request, 'reportes/vendedor.html', {
        'ventas_hoy': ventas_hoy,
        'total_hoy': total_hoy,
        'num_ventas': num_ventas,
        'promedio': promedio,
        'fecha': hoy,
    })


@login_required
def reporte_administrador(request):
    """Reporte para administrador: ventas generales, stock, alertas"""
    if not solo_gerente_admin(request.user):
        from django.contrib import messages
        messages.error(request, 'Acceso restringido.')
        return render(request, 'reportes/sin_acceso.html')

    hoy = timezone.localdate()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    inicio_mes = hoy.replace(day=1)

    ventas_hoy = Venta.objects.filter(estado='completada', fecha_venta__date=hoy)
    ventas_semana = Venta.objects.filter(estado='completada', fecha_venta__date__gte=inicio_semana)
    ventas_mes = Venta.objects.filter(estado='completada', fecha_venta__date__gte=inicio_mes)

    # Top productos más vendidos del mes
    top_productos = ItemVenta.objects.filter(
        venta__estado='completada', venta__fecha_venta__date__gte=inicio_mes
    ).values('producto__nombre').annotate(
        total_vendido=Sum('cantidad'), ingresos=Sum('subtotal')
    ).order_by('-total_vendido')[:10]

    # Stock bajo
    productos_stock_bajo = Producto.objects.filter(activo=True, stock_actual__lte=F('stock_minimo'))

    # Vencimientos
    lotes_alerta = LoteProducto.objects.filter(
        fecha_vencimiento__lte=hoy + timedelta(days=30),
        fecha_vencimiento__gte=hoy
    ).select_related('producto').order_by('fecha_vencimiento')

    # Tickets dados de baja del mes
    bajas_mes = Venta.objects.filter(
        estado='cancelada', fecha_baja__date__gte=inicio_mes
    ).select_related('vendedor', 'dado_de_baja_por').order_by('-fecha_baja')

    return render(request, 'reportes/administrador.html', {
        'resumen_hoy': {'ventas': ventas_hoy.count(), 'total': ventas_hoy.aggregate(t=Sum('total'))['t'] or 0},
        'resumen_semana': {'ventas': ventas_semana.count(), 'total': ventas_semana.aggregate(t=Sum('total'))['t'] or 0},
        'resumen_mes': {'ventas': ventas_mes.count(), 'total': ventas_mes.aggregate(t=Sum('total'))['t'] or 0},
        'top_productos': top_productos,
        'productos_stock_bajo': productos_stock_bajo,
        'lotes_alerta': lotes_alerta,
        'bajas_mes': bajas_mes,
        'hoy': hoy,
    })


@login_required
def reporte_gerente(request):
    """Reporte gerencial completo con utilidades y rendimiento por vendedor"""
    if not solo_gerente(request.user):
        from django.contrib import messages
        messages.error(request, 'Acceso restringido a Gerentes.')
        return render(request, 'reportes/sin_acceso.html')

    hoy = timezone.localdate()
    inicio_mes = hoy.replace(day=1)

    # Rendimiento por vendedor
    rendimiento_qs = Venta.objects.filter(
        estado='completada', fecha_venta__date__gte=inicio_mes
    ).values(
        'vendedor__username', 'vendedor__first_name', 'vendedor__last_name'
    ).annotate(
        num_ventas=Count('id'), total_ventas=Sum('total')
    ).order_by('-total_ventas')

    # Calcular promedio en Python (evita división en ORM)
    rendimiento_vendedores = []
    for v in rendimiento_qs:
        v['promedio'] = round(float(v['total_ventas']) / v['num_ventas'], 2) if v['num_ventas'] else 0
        rendimiento_vendedores.append(v)

    # Ventas por día del mes
    ventas_por_dia = Venta.objects.filter(
        estado='completada', fecha_venta__date__gte=inicio_mes
    ).annotate(dia=TruncDate('fecha_venta')).values('dia').annotate(
        total=Sum('total'), num=Count('id')
    ).order_by('dia')

    # Utilidad estimada — se calculan ingresos/costo primero, luego utilidad en segundo annotate
    utilidad_productos = ItemVenta.objects.filter(
        venta__estado='completada', venta__fecha_venta__date__gte=inicio_mes
    ).values('producto__nombre').annotate(
        ingresos=Sum('subtotal'),
        costo=Sum(ExpressionWrapper(
            F('cantidad') * F('producto__precio_compra'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )),
        cantidad=Sum('cantidad'),
    ).annotate(
        utilidad=F('ingresos') - F('costo')
    ).order_by('-ingresos')[:10]

    # Tickets dados de baja del mes
    bajas_mes = Venta.objects.filter(
        estado='cancelada', fecha_baja__date__gte=inicio_mes
    ).select_related('vendedor', 'dado_de_baja_por').order_by('-fecha_baja')

    return render(request, 'reportes/gerente.html', {
        'rendimiento_vendedores': rendimiento_vendedores,
        'ventas_por_dia': list(ventas_por_dia),
        'utilidad_productos': utilidad_productos,
        'bajas_mes': bajas_mes,
        'mes': inicio_mes,
        'hoy': hoy,
    })
