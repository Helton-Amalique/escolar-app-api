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

    def veiculos_count(self, obj):
        return obj.veiculos.count()
    veiculos_count.short_description = 'Veiculos'


@admin.register(Veiculo)
class VeiculoAdmin(BaseAdmin):
    list_display = ('placa_matricula', 'modelo_carro', 'capacidade', 'motorista', 'ativo')
    search_fields = ('placa_matricula', 'modelo_carro', 'motorista__user__nome')
    list_filter = ('capacidade', 'motorista', 'ativo')

    fieldsets = (
        ('Informacoes do Veiculo', {
            'fields': ('placa_matricula', 'modelo_carro', 'capacidade', 'motorista', 'ativo')
        }),
    )

    actions = ['ativar_veiculos', 'desativar_veiculos']

    def ativar_veiculos(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f"{updated} veicolo(s) ativado(s)")
    ativar_veiculos.short_description = "Ativar veiculos selecionados"

    def desativar_veiculos(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f"{updated} veicolo(s) desativado(s)")
    desativar_veiculos.short_description = "Desativar veiculos selecionados"


@admin.register(Rota)
class RotaAdmin(BaseAdmin):
    list_display = ('nome', 'veiculo', 'ativo')
    search_fields = ('nome', 'veiculo__placa_matricula')
    ordering = ('nome',)
    list_filter = ('ativo',)

    fieldsets = (
        ('Detalhes da Rota', {
            'fields': ('nome', 'descricao', 'veiculo', 'ativo')
        }),
    )

    actions = ['ativar_rotas', 'desativar_rotas']

    def ativar_rotas(self, request, queryset):
        updated = queryset.update(ativo=True)
        self.message_user(request, f"{updated} rota(s) ativada(s).")
    ativar_rotas.short_desciption = "Ativar rotas selecionadas"

    def desativar_rotas(self, request, queryset):
        updated = queryset.update(ativo=False)
        self.message_user(request, f"{updated} rota(s) ativada(s).")
    desativar_rotas.short_desciption = "Desativar rotas selecionadas"
