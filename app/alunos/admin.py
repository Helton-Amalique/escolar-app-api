from django.contrib import admin
from alunos.models import Aluno
from core.admin_mixins.mixins import BaseAdmin


@admin.register(Aluno)
class AlunoAdmin(BaseAdmin):
    list_display = ('nome', 'encarregado', 'rota', 'data_nascimento')
    list_filter = ('rota',)
    search_fields = ('nome', 'encarregado__nome', 'endereco')
    date_hierarchy = 'data_nascimento'

    fieldsets = (
        ('Dados Pessoas', {
            'fields': ('nome', 'data_nascimento', 'encarregado', 'endereco')
        }),
        ('Trasporte', {
            'fields': ('rota',)
        }),
    )
