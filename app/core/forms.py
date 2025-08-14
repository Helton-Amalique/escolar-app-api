from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from core.models import User


class CustomUserCreationForm(UserCreationForm):
    """Formulario usado para criar usuarios n admin"""
    class Meta:
        model = User
        fields = ('email', 'nome', 'role')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }


class CustomUserChangeForm(UserChangeForm):
    """ Formulario usado para editar usuarios n admin"""
    class Meta:
        model = User
        fields = ('email', 'nome', 'role', 'is_active', 'is_staff', 'is_superuser')
        widgets = {
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
