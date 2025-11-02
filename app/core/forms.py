from django import forms
from core.models import User, Cargo
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


class CustomUserCreationForm(UserCreationForm):
    """Formulario usado para criar usuarios n admin"""
    role = forms.ModelChoiceField(queryset=Cargo.objects.all(), required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email', 'nome', 'apelido', 'role', 'salario')


    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields["email"].required = True
    #     self.fields["nome"].required = True
    #     self.fields["apelido"].required = True
    #     self.fields["role"].required = True

    #     if self.data.get("role") == "ENCARREGADO":
    #         self.fields["salario"].widget = forms.HiddenInput()

    # def save(self, commit=True):
    #     user = super().save(commit=False)

    #     if not user.salario and user.role in User.SALARIOS_PADRAO:
    #         user.salario = User.SALARIOS_PADRAO[user.role]
    #     if commit:
    #         user.save()
    #     return user


class CustomUserChangeForm(UserChangeForm):
    """ Formulario usado para editar usuarios n admin"""

    role = forms.ModelChoiceField(queryset=Cargo.objects.all(), required=True)

    class Meta:
        model = User
        fields = ('email', 'nome', 'apelido','role', 'salario', 'is_active', 'is_staff')
