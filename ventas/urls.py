from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.punto_venta, name='punto_venta'),
    path('agregar/', views.agregar_item, name='agregar_item'),
    path('quitar/<int:item_id>/', views.quitar_item, name='quitar_item'),
    path('completar/', views.completar_venta, name='completar_venta'),
    path('ticket/<int:pk>/', views.ticket_venta, name='ticket'),
    path('historial/', views.historial_ventas, name='historial'),
    path('buscar/', views.buscar_producto_ajax, name='buscar_ajax'),
]
