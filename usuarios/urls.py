from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # Gestión (admin)
    path('', views.lista_usuarios, name='lista'),
    path('nuevo/', views.crear_usuario, name='crear'),
    path('<int:pk>/editar/', views.editar_usuario, name='editar'),
    path('<int:pk>/toggle/', views.toggle_activo, name='toggle'),
    path('<int:pk>/perfil/', views.perfil_usuario, name='perfil_usuario'),
    # Perfil propio (cualquier usuario)
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('mi-perfil/editar/', views.editar_perfil, name='editar_perfil'),
    path('mi-perfil/password/', views.cambiar_password, name='cambiar_password'),
]
