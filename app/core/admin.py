from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import User
from core import models
from django.contrib.auth.models import Group
from core.forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = ('nome', 'email', 'role', 'salario', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('nome', 'email')
    ordering = ('nome',)

    readonly_fields = ('data_criacao', 'data_atualizacao', 'last_login')

    fieldsets = (
        ('Informações de Login', {
            'fields': ('email', 'password')
        }),
        ('Informações Pessoais', {
            'fields': ('nome', 'role')
        }),
        ('Permissões', {
            'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')
        }),
        ('Funcao e salario', {
            'fields': ('salario',)
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'data_criacao', 'data_atualizacao')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'role', 'password1', 'password2', 'is_active', 'is_staff')
        }),
    )

    def save_model(self, request, obj, form, change):
        """
        Salva o usuário e adiciona ao grupo correspondente ao role.
        """
        super().save_model(request, obj, form, change)
        """#so se role estiver difinido"""
        if obj.role:
            role_group = Group.objects.filter(name=obj.role.upper()).first()
            if role_group:
                # obj.groups.clear()
                # adiciona ao grupo do role sem apagar os outros
                obj.groups.add(role_group)
                obj.save()

    def role_display(self, obj):
        """Exibe o nime legivel da funcao"""
        return obj.get_role()
    role_display.short_description = 'Funcao'
