from django.contrib import admin
from .models import User
# Register your models here.


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'role', 'is_active', 'is_staff', 'data_criacao')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('nome', 'email')
    ordering = ('nome',)

    fieldsets = (
        ('Informacoes de Login', {
            'fields': ('email', 'password')
        }),
        ('Informacoes Pessoas', {
            'fields': ('nome', 'role')
        }),
        ('Permisoes', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Data Importantes', {
            'fields': ('last_login', 'data_criacao')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'role', 'password1', 'password2', 'is_active', 'is_staff')
        }),
    )
