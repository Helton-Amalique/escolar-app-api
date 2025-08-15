from django.contrib import admin
from alunos.models import Aluno, Encarregado
from core.admin_mixins.mixins import BaseAdmin


@admin.register(Aluno)
class AlunoAdmin(BaseAdmin):
    list_display = ('nome', 'encarregado', 'escola_dest', 'classe', 'activo', 'rota')
    list_filter = ('classe','activo')
    search_fields = ('nome', 'escola_dest', 'classe')
    date_hierarchy = 'data_nascimento'

    fieldsets = (
        ('Dados Pessoas', {
            'fields': ('nome', 'data_nascimento', 'encarregado', 'escola_dest', 'classe', 'activo')
        }),
        ('Trasporte', {
            'fields': ('rota',)
        }),
    )

@admin.register(Encarregado)
class EncarregadoAdmin(admin.ModelAdmin):
    list_display = ('user','telefone','endereco')
    search_fields = ('user__nome', 'telefone', 'endereco')

    fieldsets = (
        (None, {
            'fields': ('user', 'telefone', 'endereco')
        }),
    )

