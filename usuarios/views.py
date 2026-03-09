from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CrearUsuarioForm, EditarUsuarioForm


def solo_admin(user):
    return user.groups.filter(name='Administrador').exists() or user.is_superuser


@login_required
def lista_usuarios(request):
    if not solo_admin(request.user):
        messages.error(request, 'Acceso restringido a administradores.')
        return redirect('home')

    usuarios = User.objects.all().prefetch_related('groups').order_by('username')
    return render(request, 'usuarios/lista.html', {'usuarios': usuarios})


@login_required
def crear_usuario(request):
    if not solo_admin(request.user):
        messages.error(request, 'Acceso restringido a administradores.')
        return redirect('home')

    if request.method == 'POST':
        form = CrearUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            messages.success(request, f'Usuario "{usuario.username}" creado correctamente.')
            return redirect('usuarios:lista')
    else:
        form = CrearUsuarioForm()

    return render(request, 'usuarios/form.html', {'form': form, 'titulo': 'Nuevo Usuario'})


@login_required
def editar_usuario(request, pk):
    if not solo_admin(request.user):
        messages.error(request, 'Acceso restringido a administradores.')
        return redirect('home')

    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario "{usuario.username}" actualizado.')
            return redirect('usuarios:lista')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'usuarios/form.html', {
        'form': form,
        'titulo': f'Editar Usuario: {usuario.username}',
        'usuario': usuario,
    })


@login_required
def toggle_activo(request, pk):
    if not solo_admin(request.user):
        messages.error(request, 'Acceso restringido a administradores.')
        return redirect('home')

    if request.method == 'POST':
        usuario = get_object_or_404(User, pk=pk)
        if usuario == request.user:
            messages.error(request, 'No puedes desactivar tu propia cuenta.')
        else:
            usuario.is_active = not usuario.is_active
            usuario.save()
            estado = 'activado' if usuario.is_active else 'desactivado'
            messages.success(request, f'Usuario "{usuario.username}" {estado}.')

    return redirect('usuarios:lista')
