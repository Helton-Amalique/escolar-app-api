from django.contrib import admin
from django.utils import timezone
from datetime import date
from django.utils.html import format_html
from core.admin_mixins.mixins import BaseAdmin
from financeiro.models import Pagamento, Salario
from financeiro.management.services.alerta import enviar_alerta
from financeiro.utils import gerar_recibo


class StatusActionMixins:
    """mixin para ações em massa no admin"""

    def marcar_como_pago(self, request, queryset):
        # atualizado = queryset.update(status='PAGO', data_pagamento=timezone.now())
        # self.message_user(request, f'{atualizado} registros marcados como PAGO.')
        for obj in queryset:
            obj.status = "PAGO"
            if not obj.data_pagamento:
                obj.data_pagamento = timezone.now()
            obj.save()
        self.message_user(request, f"{queryset.count()} registro marcado como PAGO")
    marcar_como_pago.short_description = "Marcar como PAGO"

    def marcar_como_pendente(self, request, queryset):
        # atualizado = queryset.update(status='PENDENTE', data_pagamento=None)
        # self.message_user(request, f'{atualizado} registros marcados como PENDENTE')
        for obj in queryset:
            obj.status = "PENDENTE"
            obj.data_pagamento = None
            obj.save()
            self.message_user(request, f"{queryset.count()} registro marcado como PENDENTE")
    marcar_como_pendente.short_description = "Marcar como PENDENTE"

    def marcar_como_atrasado(self, request, queryset):
        # atualizado = queryset.update(status='ATRASADO', data_pagamento=timezone.now())
        # self.message_user(request, f'{atualizado} registros marcados como ATRASADO.')
        for obj in queryset:
            obj.status = "ATRASADO"
            obj.data_pagamento = None
            obj.save()
        self.message_user(request, f"{queryset.count()} registro marcado como ATRASADO")
    marcar_como_atrasado.short_description = "Marcar como ATRASADO"


class StatusListFilter(admin.SimpleListFilter):
    """Filtro lateral status de pagamentos"""
    title = 'Status'
    parameter_name = 'status_custom'

    def lookups(self, request, model_admin):
        return [
            ('PAGO', 'Pagos ✅'),
            ('PENDENTE', 'Pendentes ⏳'),
            ('ATRASADO', 'Atrasados ⛔'),
        ]

    def queryset(self, request, queryset):
        vencimento = date.today()
        if self.value() == 'PAGO':
            return queryset.filter(status='PAGO')
        elif self.value() == 'PENDENTE':
            return queryset.filter(status='PENDENTE')
        elif self.value() == 'ATRASADO':
            vencimento = date.today().replace(day=10)
            return queryset.filter(status='PENDENTE', mes_referente__lt=vencimento)
        return queryset


class BasePagamentoAdmin(StatusActionMixins, admin.ModelAdmin):
    """Base Admin comum"""
    # list_filter = ('status', 'mes_referente')
    readonly_fields = ('data_pagamento',)
    actions = ['marcar_como_pago', 'marcar_como_pendente', 'marcar_como_atrasado']

    def status_colorido(self, obj):
        hoje = date.today()
        if obj.status == 'PAGO':
            cor = '#d4edda'  # Verde claro
        else:
            if obj.status == 'PENDENTE' and obj.mes_referente < hoje.replace(day=10):
                cor = '#f8d7da'  # Vermelho claro
            else:
                cor = '#fff3cd'  # Amarelo claro

            return format_html(
                '<span style="background-color: {}; padding: 4px 8px; border-radius: 4px;">{}</span>',
                cor,
                obj.status
            )
    status_colorido.short_description = 'Status'

    def gerar_recibos(self, request, queryset):
        """Acao no admin para gerar recibos em PDF de pagamento selecionados"""
        if queryset.count() == 0:
            self.message_user(request, "Nenhum registro selecionado.")
            return
        for obj in queryset:
            gerar_recibo(obj)
        self.message_user(request, f'{queryset.count()} recibos gerados!')
    gerar_recibos.short_description = "Gerar recibo(s) em PDF"


@admin.register(Pagamento)
class PagamentoAdmin(BasePagamentoAdmin):
    list_display = ('aluno', 'valor', 'mes_referente', 'status_colorido', 'data_pagamento')
    list_filter = ('status', 'mes_referente', StatusListFilter)
    search_fields = ('aluno__nome',)
    readonly_fields = ('data_pagamento',)

    actions = ["gerar_recibos", 'enviar_alerta', 'marcar_como_pago']

    fieldsets = (
        ('Informações do Pagamento das Mensalidades', {
            'fields': ('aluno', 'mes_referente', 'valor', 'status')
        }),
        ('Informações do Sistema', {
            'fields': ('data_pagamento',),
        })
    )

    def enviar_alerta(self, request, queryset):
        reusltados = [enviar_alerta(p)
                      for p in queryset if p.status != 'PAGO']
        self.message_user(request, f"Alertas enviados: {len(reusltados)}")
    enviar_alerta.short_description = "Enviar alerta de pagamentos pendentes"


@admin.register(Salario)
class SalarioAdmin(BasePagamentoAdmin):
    list_display = ('id', 'funcionario', 'valor', 'mes_referente', 'status_colorido', 'data_pagamento')
    list_filter = ('status', 'mes_referente')
    search_fields = ('funcionario__nome',)

    # readonly_fields = ('data_pagamento',)

    # actions = ['marca_como_pago', 'marcar_como_pendente', 'marca_como_atrasado', 'gerar_recibos']

    fieldsets = (
        ('Informacoes do Pagamento dos Salario', {
            'fields': ('funcionario', 'mes_referente', 'valor', 'status', 'data_pagamento')
        }),
    )
