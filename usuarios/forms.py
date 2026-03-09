from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password


class CrearUsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Rol del usuario',
        empty_label='-- Selecciona un rol --',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre(s)',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['grupo']])
        return user


class EditarUsuarioForm(forms.ModelForm):
    password_nueva = forms.CharField(
        label='Nueva contraseña (dejar vacío para no cambiar)',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        required=False,
    )
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label='Rol del usuario',
        empty_label='-- Selecciona un rol --',
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre(s)',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'is_active': 'Usuario activo',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            grupo_actual = self.instance.groups.first()
            if grupo_actual:
                self.fields['grupo'].initial = grupo_actual

    def clean_password_nueva(self):
        password = self.cleaned_data.get('password_nueva')
        if password:
            validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        nueva = self.cleaned_data.get('password_nueva')
        if nueva:
            user.set_password(nueva)
        if commit:
            user.save()
            user.groups.set([self.cleaned_data['grupo']])
        return user
