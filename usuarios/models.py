from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    foto = models.ImageField(upload_to='perfiles/', blank=True, null=True, verbose_name='Fotografía')
    fecha_nacimiento = models.DateField(blank=True, null=True, verbose_name='Fecha de nacimiento')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.CharField(max_length=250, blank=True, verbose_name='Dirección')
    bio = models.TextField(max_length=500, blank=True, verbose_name='Acerca de mí')
    numero_empleado = models.CharField(max_length=20, blank=True, verbose_name='N° de empleado')
    fecha_ingreso = models.DateField(blank=True, null=True, verbose_name='Fecha de ingreso')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'

    def __str__(self):
        return f'Perfil de {self.user.username}'

    @property
    def edad(self):
        if not self.fecha_nacimiento:
            return None
        hoy = date.today()
        return hoy.year - self.fecha_nacimiento.year - (
            (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )

    @property
    def antiguedad_años(self):
        if not self.fecha_ingreso:
            return None
        hoy = date.today()
        return hoy.year - self.fecha_ingreso.year - (
            (hoy.month, hoy.day) < (self.fecha_ingreso.month, self.fecha_ingreso.day)
        )


@receiver(post_save, sender=User)
def crear_o_guardar_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)
    else:
        # Si el perfil no existe aún (usuarios previos a la migración), lo crea
        Perfil.objects.get_or_create(user=instance)
