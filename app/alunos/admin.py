from django.contrib import admin
from alunos.models import Aluno, Encarregado
from core.admin_mixins.mixins import BaseAdmin


class AlunoInline(admin.TabularInline):
    model = Aluno
    extra = 0
    readonly_fields = ("id",)
    fields = ('nome', 'nrBI', 'data_nascimento', 'escola_dest', 'classe', 'rota', 'ativo', 'email', 'mensalidade')


@admin.register(Aluno)
class AlunoAdmin(BaseAdmin):
    list_display = ('id', 'nome', 'nrBI', 'data_nascimento', 'get_encarregado', 'escola_dest', 'classe', 'rota', 'ativo')
    search_fields = ('nome', 'nrBI', 'encarregado__user__nome')
    list_filter = ("classe", "ativo")
    ordering = ("nome",)
    readonly_fields = ("id",)
    autocomplete_fields = ("encarregado", "rota")
    date_hierarchy = 'data_nascimento'

    fieldsets = (
        ('Dados Pessoas', {
            'fields': ('nome', 'nrBI', 'data_nascimento', 'encarregado', 'escola_dest', 'classe', 'ativo', 'email', 'mensalidade')
        }),
        ('Trasporte', {
            'fields': ('rota',)
        }),
    )

    def get_encarregado(self, obj):
        return obj.encarregado.user.nome if obj.encarregado else '-'
    get_encarregado.short_description = 'Encarregado'
    get_encarregado.admin_order_field = 'encarregado__user__nome'


@admin.register(Encarregado)
class EncarregadoAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_nome', 'get_email', 'nrBI', 'telefone', 'endereco')
    search_fields = ('user__nome', 'user__email', 'nrBI', 'telefone')
    autocomplete_fields = ('user', )
    inlines = [AlunoInline]

    fieldsets = (
        ('Informacao do Usuario', {'fields': ('user',)}),
        ('Detalhes do Encarregado', {'fields': ('foto', 'telefone', 'nrBI', 'endereco')})
    )

    def get_user_nome(self, obj):
        return obj.user.nome if obj.user else '-'
    get_user_nome.short_description = 'Nome do Utilizador'
    get_user_nome.admin_order_field = 'user__nome'

    def get_email(self, obj):
        return obj.user.email if obj.user else '-'
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
