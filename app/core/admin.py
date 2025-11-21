from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import User, Cargo
from django.contrib.auth.models import Group
from core.forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'salario_padrao')
    search_fields = ('nome',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = User

    list_display = ('email', 'nome', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')

    search_fields = ('email', 'nome')
    ordering = ('email',)
    readonly_fields = ('data_criacao', 'data_atualizacao', 'last_login')

    fieldsets = (
        ('Informações de Login', {
            'fields': ('email', 'password')
        }),
        ('Informações Pessoais', {
            'fields': ('nome', 'role', 'salario')
        }),
        ('Permissões', {
            'fields': ('is_staff', 'is_superuser', 'is_active', 'groups', 'user_permissions')
        }),
        ('Datas Importantes', {
            'fields': ('last_login', 'data_criacao', 'data_atualizacao')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'role', 'salario', 'password1', 'password2', 'is_staff', 'is_active')
        }),
    )

    def save_model(self, request, obj, form, change):
        """ Salva o usuário e adiciona ao grupo correspondente ao role. """
        super().save_model(request, obj, form, change)
        if obj.role:
            role_group, created = Group.objects.get_or_create(name=obj.role.nome.upper())
            obj.groups.add(role_group)
