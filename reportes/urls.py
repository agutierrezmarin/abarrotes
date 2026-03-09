from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('vendedor/', views.reporte_vendedor, name='vendedor'),
    path('administrador/', views.reporte_administrador, name='administrador'),
    path('gerente/', views.reporte_gerente, name='gerente'),
]
