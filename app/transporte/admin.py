from django.contrib import admin
from transporte.models import Motorista, Veiculo, Rota
from core.admin_mixins.mixins import BaseAdmin


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "telefone", "ativo", "validade_da_carta", "criado_em", "atualizado_em")
    list_filter = ("ativo", "validade_da_carta")
    search_fields = ("user__nome", "user__email", "telefone", "carta_nr")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("-criado_em",)

    def get_user_nome(self, obj):
        return getattr(obj.user, "nome", "")
    get_user_nome.short_description = "Nome do Usuario"

    def get_user_email(self, obj):
        return getattr(obj.user, "email", "")
    get_user_email.shot_description = "Email do Usuario"


@admin.register(Veiculo)
class VeiculoAdmin(admin.ModelAdmin):
    list_display = ("modelo", "matricula", "capacidade", "motorista", "ativo", "criado_em", "atualizado_em")
    list_filter =("ativo", "motorista", "capacidade")
    search_fields = ("modelo", "matricula")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("matricula",)

    def motorista_nome(self, obj):
        if obj.motorista:
            return obj.motorista.user.nome
        return "-"
    motorista_nome.shot_description = "Motorista"


@admin.register(Rota)
class RotaAdmin(BaseAdmin):
    list_display = ("nome", "veiculo", "motorista_atribuido", "ativo", "criado_em", "atualizado_em")
    list_filter = ("ativo", "veiculo__motorista", "veiculo__motorista__ativo")
    search_fields = ("nome", "descricao", "veiculo__placa_matricula", "veiculo__motorista__user__nome")
    readonly_fields = ("criado_em", "atualizado_em")
    ordering = ("nome",)

    def veiculo_nome(self, obj):
        if obj.veiculo:
            return obj.veiculo.modelo_carro
        return "-"
    veiculo_nome.short_description = "Veiculo"

    def get_placa_matricula(self, obj):
        if obj.veiculo:
            return obj.veiculo.placa_matricula
        return "-"
    get_placa_matricula.short_description = "Placa"

    def get_motorista_nome(self, obj):
        """exibo o motorista do veiculo associado a rota"""
        if obj.veiculo and obj.veiculo.motorista:
            return obj.veiculo.motorista.user.nome
        return "-"
    get_motorista_nome.short_description = "Motorista"
