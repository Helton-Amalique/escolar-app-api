from django.contrib import admin
from alunos.models import Aluno, Encarregado
from core.admin_mixins.mixins import BaseAdmin


@admin.register(Aluno)
class AlunoAdmin(BaseAdmin):
    list_display = ('nome', 'data_nascimento', 'get_encarregado', 'escola_dest', 'classe', 'rota', 'activo')
    search_fields = ('nome', 'encarregado__user__nome', 'escola_dest', 'classe')
    list_filter = ("classe", "activo", "rota")
    autocomplete_fields = ("encarregado", "rota")
    # date_hierarchy = 'data_nascimento'

    fieldsets = (
        ('Dados Pessoas', {
            'fields': ('nome', 'data_nascimento', 'encarregado', 'escola_dest', 'classe', 'activo')
        }),
        ('Trasporte', {
            'fields': ('rota',)
        }),
    )

    def get_encarregado(self, obj):
        return obj.encarregado.user.nome
    get_encarregado.short_description = 'Encarregado'
    get_encarregado.admin_order_field = 'encarregado__user__nome'


@admin.register(Encarregado)
class EncarregadoAdmin(admin.ModelAdmin):
    list_display = ('get_user_nome', 'telefone', 'endereco')
    search_fields = ('user__nome', 'telefone', 'endereco')
    list_filter = ("user__role",)
    list_display_links = ('get_user_nome',)

    fieldsets = (
        (None, {
            'fields': ('user', 'telefone', 'endereco')
        }),
    )

    def get_user_nome(self, obj):
        return obj.user.nome
    get_user_nome.short_description = 'Nome do Encarregado'
    get_user_nome.admin_order_field = 'user__nome'
