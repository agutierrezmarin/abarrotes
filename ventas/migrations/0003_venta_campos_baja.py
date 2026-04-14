from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0002_itemventa_es_paquete_itemventa_unidades_descontadas"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="venta",
            name="observacion_baja",
            field=models.TextField(blank=True, verbose_name="Motivo de baja"),
        ),
        migrations.AddField(
            model_name="venta",
            name="dado_de_baja_por",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bajas_registradas",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Dado de baja por",
            ),
        ),
        migrations.AddField(
            model_name="venta",
            name="fecha_baja",
            field=models.DateTimeField(blank=True, null=True, verbose_name="Fecha de baja"),
        ),
    ]
