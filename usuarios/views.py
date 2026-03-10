from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from .forms import CrearUsuarioForm, EditarUsuarioForm, PerfilForm, DatosPersonalesForm, CambiarPasswordForm
from .models import Perfil


def solo_admin(user):
    return user.groups.filter(name='Administrador').exists() or user.is_superuser


# ── Gestión de usuarios (solo admins) ─────────────────────────────────────────

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


# ── Perfil de usuario (accesible por cualquier usuario autenticado) ────────────

@login_required
def mi_perfil(request):
    """Vista del perfil propio del usuario."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)
    return render(request, 'usuarios/perfil.html', {
        'perfil': perfil,
        'usuario': request.user,
        'es_propio': True,
    })


@login_required
def perfil_usuario(request, pk):
    """Vista del perfil de otro usuario (solo admins)."""
    if not solo_admin(request.user):
        messages.error(request, 'Acceso restringido.')
        return redirect('usuarios:mi_perfil')
    usuario = get_object_or_404(User, pk=pk)
    perfil, _ = Perfil.objects.get_or_create(user=usuario)
    return render(request, 'usuarios/perfil.html', {
        'perfil': perfil,
        'usuario': usuario,
        'es_propio': False,
    })


@login_required
def editar_perfil(request):
    """Edición del perfil propio: datos personales + datos de perfil."""
    perfil, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form_datos = DatosPersonalesForm(request.POST, instance=request.user)
        form_perfil = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form_datos.is_valid() and form_perfil.is_valid():
            form_datos.save()
            form_perfil.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:mi_perfil')
    else:
        form_datos = DatosPersonalesForm(instance=request.user)
        form_perfil = PerfilForm(instance=perfil)

    return render(request, 'usuarios/editar_perfil.html', {
        'form_datos': form_datos,
        'form_perfil': form_perfil,
    })


@login_required
def cambiar_password(request):
    """Cambio de contraseña propio."""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['password_actual']):
                form.add_error('password_actual', 'La contraseña actual es incorrecta.')
            else:
                request.user.set_password(form.cleaned_data['password_nueva'])
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Contraseña cambiada correctamente.')
                return redirect('usuarios:mi_perfil')
    else:
        form = CambiarPasswordForm()
    return render(request, 'usuarios/cambiar_password.html', {'form': form})
