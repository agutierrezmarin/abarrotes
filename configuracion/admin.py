from django.contrib import admin
from .models import ConfiguracionTienda


@admin.register(ConfiguracionTienda)
class ConfiguracionTiendaAdmin(admin.ModelAdmin):
    list_display = ['nombre_tienda', 'tema', 'color_primary']
