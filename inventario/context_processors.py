from django.utils import timezone
from datetime import timedelta
from django.db.models import F


def alertas_inventario(request):
    """Inyecta conteos de alertas en todos los templates para usuarios autenticados."""
    if not request.user.is_authenticated:
        return {}

    try:
        from .models import Producto, LoteProducto

        hoy = timezone.localdate()

        stock_bajo = Producto.objects.filter(
            activo=True, stock_actual__lte=F('stock_minimo')
        ).count()

        lotes_vencidos = LoteProducto.objects.filter(
            fecha_vencimiento__lt=hoy
        ).count()

        lotes_criticos = LoteProducto.objects.filter(
            fecha_vencimiento__range=[hoy, hoy + timedelta(days=7)]
        ).count()

        total_alertas = stock_bajo + lotes_vencidos + lotes_criticos

        return {
            'alerta_stock_bajo': stock_bajo,
            'alerta_lotes_vencidos': lotes_vencidos,
            'alerta_lotes_criticos': lotes_criticos,
            'alerta_total': total_alertas,
        }
    except Exception:
        return {}
