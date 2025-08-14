from django.contrib import admin
from transporte.models import Motorista, Veiculo, Rota
from core.admin_mixins.mixins import BaseAdmin


@admin.register(Motorista)
class MotoristaAdmin(BaseAdmin):
    list_display = ('nome', 'telefone', 'carta_nr', 'validade_da_carta')
    search_fields = ('user__nome', 'telefone')

    def nome(self, obj):
        return obj.user.nome
    nome.admin_order_field = 'user__nome'
    nome.short_description = 'Nome'


@admin.register(Veiculo)
class VeiculoAdmin(BaseAdmin):
    list_display = ('placa_matricula', 'modelo_carro', 'capacidade', 'motorista')
    search_fields = ('placa_matricula', 'modelo_carro', 'motorista__nome')
    list_filter = ('capacidade',)

    fieldsets = (
        ('Informacoes do Veiculo', {
            'fields': ('placa_matricula', 'modelo_carro', 'capacidade', 'motorista')
        }),
    )


@admin.register(Rota)
class RotaAdmin(BaseAdmin):
    list_display = ('nome', 'veiculo')
    search_fields = ('nome', 'veiculo__placa_matricula')
    ordering = ('nome',)

    fieldsets = (
        ('Detalhes da Rota', {
            'fields': ('nome', 'descricao', 'veiculo')
        }),
    )
