from django import forms
from core.models import User, Cargo
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    """Formulario usado para criar usuarios n admin"""
    role = forms.ModelChoiceField(queryset=Cargo.objects.all(), required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'nome', 'role', 'salario')


class CustomUserChangeForm(UserChangeForm):
    """ Formulario usado para editar usuarios n admin"""

    role = forms.ModelChoiceField(queryset=Cargo.objects.all(), required=True)

    class Meta:
        model = User
        fields = ('email', 'nome', 'role', 'salario', 'is_active', 'is_staff')
