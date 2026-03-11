def config_tienda(request):
    from configuracion.models import ConfiguracionTienda
    return {'config_tienda': ConfiguracionTienda.get_config()}
