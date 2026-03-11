import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ConfiguracionTienda, PRESETS


@login_required
def configuracion(request):
    if not (request.user.is_superuser or
            request.user.groups.filter(name='Administrador').exists()):
        messages.error(request, 'No tienes permiso para acceder a la configuración.')
        return redirect('home')

    config = ConfiguracionTienda.get_config()

    if request.method == 'POST':
        action = request.POST.get('action', 'guardar')

        if action == 'eliminar_logo':
            if config.logo:
                config.logo.delete(save=False)
                config.logo = None
                config.save()
            messages.success(request, 'Logo eliminado.')
            return redirect('configuracion:configuracion')

        # Aplicar preset si se seleccionó uno
        preset_key = request.POST.get('preset', '')
        if preset_key and preset_key in PRESETS:
            p = PRESETS[preset_key]
            config.color_primary      = p['primary']
            config.color_primary_dark = p['primary_dark']
            config.color_accent       = p['accent']

        config.nombre_tienda      = request.POST.get('nombre_tienda', config.nombre_tienda).strip()
        config.slogan             = request.POST.get('slogan', config.slogan).strip()
        config.color_primary      = request.POST.get('color_primary', config.color_primary)
        config.color_primary_dark = request.POST.get('color_primary_dark', config.color_primary_dark)
        config.color_accent       = request.POST.get('color_accent', config.color_accent)
        config.tema               = request.POST.get('tema', config.tema)

        if 'logo' in request.FILES:
            if config.logo:
                config.logo.delete(save=False)
            config.logo = request.FILES['logo']

        config.save()
        messages.success(request, 'Configuración guardada correctamente.')
        return redirect('configuracion:configuracion')

    return render(request, 'configuracion/configuracion.html', {
        'config': config,
        'presets': PRESETS,
        'presets_json': json.dumps(PRESETS),
    })
