from django.db import models


TEMAS = [('claro', 'Claro'), ('oscuro', 'Oscuro')]

PRESETS = {
    'verde':   {'primary': '#1a6b3c', 'primary_dark': '#124d2b', 'accent': '#f59e0b'},
    'azul':    {'primary': '#1d4ed8', 'primary_dark': '#1e3a8a', 'accent': '#f59e0b'},
    'violeta': {'primary': '#7c3aed', 'primary_dark': '#5b21b6', 'accent': '#f59e0b'},
    'rojo':    {'primary': '#dc2626', 'primary_dark': '#991b1b', 'accent': '#3b82f6'},
    'naranja': {'primary': '#ea580c', 'primary_dark': '#9a3412', 'accent': '#3b82f6'},
    'gris':    {'primary': '#475569', 'primary_dark': '#334155', 'accent': '#f59e0b'},
}


class ConfiguracionTienda(models.Model):
    nombre_tienda  = models.CharField('Nombre de la tienda', max_length=100, default='Tienda de Abarrotes')
    slogan         = models.CharField('Eslogan / subtítulo', max_length=200, blank=True, default='Sistema de Gestión')
    logo           = models.ImageField('Logo', upload_to='config/', blank=True, null=True)
    color_primary  = models.CharField('Color primario', max_length=7, default='#1a6b3c')
    color_primary_dark = models.CharField('Color primario oscuro', max_length=7, default='#124d2b')
    color_accent   = models.CharField('Color de acento', max_length=7, default='#f59e0b')
    tema           = models.CharField('Tema', max_length=10, choices=TEMAS, default='claro')

    class Meta:
        verbose_name = 'Configuración de Tienda'

    def save(self, *args, **kwargs):
        self.pk = 1  # singleton: solo existe un registro
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # no se puede eliminar

    @classmethod
    def get_config(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return self.nombre_tienda
