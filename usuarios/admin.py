from django.contrib import admin
from .models import Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ['user', 'telefono', 'numero_empleado', 'fecha_ingreso']
    search_fields = ['user__username', 'user__first_name', 'numero_empleado']
