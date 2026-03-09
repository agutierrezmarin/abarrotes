from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    user = request.user
    if user.groups.filter(name='Vendedor').exists():
        return redirect('ventas:punto_venta')
    elif user.groups.filter(name='Administrador').exists():
        return redirect('inventario:dashboard')
    elif user.groups.filter(name='Gerente').exists():
        return redirect('reportes:gerente')
    elif user.is_superuser:
        return redirect('inventario:dashboard')
    return redirect('ventas:punto_venta')
