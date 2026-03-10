from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.dashboard_inventario, name='dashboard'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/<int:pk>/', views.detalle_producto, name='detalle_producto'),
    path('productos/<int:pk>/editar/', views.editar_producto, name='editar_producto'),
    path('productos/<int:pk>/ajustar/', views.ajustar_stock, name='ajustar_stock'),
    path('productos/<int:pk>/lote/', views.agregar_lote, name='agregar_lote'),
    path('alertas/', views.alertas_vencimiento, name='alertas_vencimiento'),
    # Proveedores
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedores/nuevo/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedores/<int:pk>/', views.detalle_proveedor, name='detalle_proveedor'),
    path('proveedores/<int:pk>/editar/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedores/<int:pk>/toggle/', views.toggle_proveedor, name='toggle_proveedor'),
]
